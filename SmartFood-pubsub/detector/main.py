"""
Detector YOLO  Pub/Sub imagen -> Pub/Sub ingredientes
-------------------------------------------------------
Topic IN  : ingredientes_imagen    (TOPIC_IN)
Topic OUT : ingredientes_detectados (TOPIC_OUT)

Payload de entrada
------------------
{
  "chat_id"      : 123456,
  "file_id"      : "<telegram file_id>",   # viene del webhook
  "k"            : 5                       # nº de recetas a devolver
}

Variables de entorno
--------------------
MODEL_BUCKET   bucket donde está best.pt
MODEL_BLOB     ruta dentro del bucket
TG_TOKEN       token bot Telegram, para descargar la foto
"""

import base64, json, logging, os
from pathlib import Path
from typing import List

import functions_framework, torch
from ultralytics import YOLO
import requests
from google.cloud import pubsub_v1, storage, exceptions as gexc
import google.auth

# ---------- ENV ----------
MODEL_BUCKET = os.getenv("MODEL_BUCKET", "smartfood-models")
MODEL_BLOB   = os.getenv("MODEL_BLOB",   "yolo/best.pt")
TOPIC_OUT    = os.getenv("TOPIC_OUT",   "ingredientes_detectados")
TG_TOKEN     = os.environ["BOT_TOKEN"]

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or google.auth.default()[1]
TMP = Path("/tmp/yolo"); TMP.mkdir(exist_ok=True)

publisher = pubsub_v1.PublisherClient()
topic_out = publisher.topic_path(PROJECT_ID, TOPIC_OUT)

# ---------- Carga del modelo ----------
_MODEL: YOLO | None = None
def _get_model() -> YOLO:
    global _MODEL
    if _MODEL:
        return _MODEL
    dest = TMP / "best.pt"
    if not dest.exists():
        logging.info("⬇️  Descargando modelo YOLO desde GCS…")
        storage.Client().bucket(MODEL_BUCKET).blob(MODEL_BLOB).download_to_filename(dest)
    _MODEL = YOLO(str(dest))
    _MODEL.fuse()               
    return _MODEL

# ---------- utilidades ----------
def _download_telegram_file(file_id: str) -> Path:
    # 1) obtener path
    r = requests.get(f"https://api.telegram.org/bot{TG_TOKEN}/getFile",
                     params={"file_id": file_id}, timeout=15)
    r.raise_for_status()
    file_path = r.json()["result"]["file_path"]

    # 2) descargar binario
    url = f"https://api.telegram.org/file/bot{TG_TOKEN}/{file_path}"
    dest = TMP / Path(file_path).name
    with requests.get(url, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 14):
                f.write(chunk)
    return dest

def _detect(image_path: Path) -> List[str]:
    model = _get_model()
    results = model(image_path, verbose=False)[0]        
    return list({model.names[int(c)] for c in results.boxes.cls})

# ---------- entrypoint ----------
@functions_framework.cloud_event
def main(event):
    try:
        data = json.loads(base64.b64decode(event.data["message"]["data"]).decode())
        chat_id   = data["chat_id"]
        file_id   = data["file_id"]
        k         = int(data.get("k", 5))
    except Exception as e:                                  
        logging.error(f"Bad payload detector: {e}")
        return

    try:
        img_path = _download_telegram_file(file_id)
        ingredientes = _detect(img_path)
    except Exception as e:                                
        logging.exception(f"Detector failed: {e}")
        ingredientes = []

    payload = {
        "chat_id": chat_id,
        "ingredientes": ingredientes,
        "filters": data.get("filters", {}),
        "k": k,
    }
    publisher.publish(topic_out, json.dumps(payload).encode())
