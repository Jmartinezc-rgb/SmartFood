"""
Recomendador PyKEEN Pub/Sub ➜ Pub/Sub
---------------------------------------

Topic de entrada : ingredientes_detectados
    Llegan mensajes del webhook (texto) y del detector YOLO (imagen).  
    Formato del payload entrante:

        {
          "chat_id"      : 123456,           # ID del chat de Telegram
          "ingredientes" : ["potato", …],    # etiquetas normalizadas en minúscula
          "filters"      : {                 # preferencias nutricionales → entidad
                              "has_calories" : "normal_calories",
                              "has_saturated": "low_saturated_fat",
                              …
                           },
          "k"            : 5                 # nº de recetas a devolver
        }

Topic de salida  : mensaje_respuesta
    Se publica un mensaje con las k recetas top-k que lee la función
       mensajero para enviarlas a Telegram.

Variables de entorno (se inyectan en el despliegue)
---------------------------------------------------
MODEL_BUCKET     bucket GCS con los artefactos 
MODEL_BLOB       ruta al `.pkl` entrenado
CSV_BLOB         ruta al CSV triples
TOPIC_MENSAJERO  nombre del topic de salida
"""


import base64, json, logging, os
from pathlib import Path
from typing import Dict, List

import google.auth
import functions_framework
import pandas as pd
import torch
from google.cloud import pubsub_v1, storage
from pykeen.triples import TriplesFactory

# ───── ENV ─────
MODEL_BUCKET    = os.getenv("MODEL_BUCKET",   "smartfood-models")
MODEL_BLOB      = os.getenv("MODEL_BLOB",     "kge/trained_model.pkl")
CSV_BLOB        = os.getenv("CSV_BLOB",       "kge/new_triplets20_optimized.csv")
TOPIC_MENSAJERO = os.getenv("TOPIC_MENSAJERO", "mensaje_respuesta")

PROJECT_ID = (
    os.getenv("GOOGLE_CLOUD_PROJECT")
    or os.getenv("GCLOUD_PROJECT")
    or os.getenv("GCP_PROJECT")
)
if not PROJECT_ID:
    _, PROJECT_ID = google.auth.default()

TMP = Path("/tmp/kge_assets"); TMP.mkdir(exist_ok=True)
DEVICE = torch.device("cpu")

# ---- cache ----
_MODEL: torch.nn.Module | None = None
_TF: TriplesFactory | None = None
_RECIPE_IDX: torch.Tensor | None = None       

publisher = pubsub_v1.PublisherClient()
topic_out = publisher.topic_path(PROJECT_ID, TOPIC_MENSAJERO)

# ───────── helpers ─────────
def _download(bucket: str, blob: str, dest: Path) -> Path:
    if dest.exists():
        return dest
    storage.Client().bucket(bucket).blob(blob).download_to_filename(dest)
    return dest

def _load_assets() -> None:
    """Carga modelo y TriplesFactory (una sola vez)."""
    global _MODEL, _TF, _RECIPE_IDX
    if _MODEL and _TF is not None and _RECIPE_IDX is not None:
        return

    model_path = _download(MODEL_BUCKET, MODEL_BLOB, TMP / "model.pkl")
    csv_path   = _download(MODEL_BUCKET, CSV_BLOB,   TMP / "triples.csv")

    _MODEL = torch.load(model_path, map_location=DEVICE)
    _MODEL.eval()

    df = (
        pd.read_csv(csv_path, dtype=str, header=0, low_memory=False)
          .applymap(str.strip)
    )
    _TF = TriplesFactory.from_labeled_triples(
        df[["head", "relation", "tail"]].to_numpy(),
        create_inverse_triples=True,
    )

    # ids de entidades que participan como head en "has_ingredient" de recetas
    rel_id_ing = _TF.relation_to_id["has_ingredient"]
    mask       = _TF.mapped_triples[:, 1] == rel_id_ing
    _RECIPE_IDX = torch.unique(_TF.mapped_triples[mask][:, 0])

def _score_safe(rel: str, tail: str) -> torch.Tensor:
    """Vector de scores (ceros si rel/tail no existen)."""
    if rel not in _TF.relation_to_id or tail not in _TF.entity_to_id:
        logging.warning(f"[Recomendador] label desconocido – rel:{rel} tail:{tail}")
        return torch.zeros(_TF.num_entities, device=DEVICE)
    r = _TF.relation_to_id[rel]
    t = _TF.entity_to_id[tail]
    with torch.no_grad():
        return _MODEL.score_h(torch.tensor([[r, t]], device=DEVICE)).squeeze(0)

def _recommend(ingredientes: List[str],
               filters: Dict[str, str],
               k: int) -> List[Dict]:
    combined = torch.zeros(_TF.num_entities, device=DEVICE)

    for ing in ingredientes:
        combined += _score_safe("has_ingredient", ing)

    for rel, ent in filters.items():
        combined += _score_safe(rel, ent)

    # Filtrar solo las entidades-receta
    recipe_scores = combined[_RECIPE_IDX]
    top_s, top_pos = torch.topk(recipe_scores, k=min(k, recipe_scores.numel()))
    top_ids = _RECIPE_IDX[top_pos]

    return [
        {"dish": _TF.entity_id_to_label[int(i)], "score": float(s)}
        for i, s in zip(top_ids.tolist(), top_s.tolist())
    ]

# ───────── entry-point ─────────
@functions_framework.cloud_event
def main(event):
    _load_assets()

    data = json.loads(base64.b64decode(event.data["message"]["data"]).decode())
    chat_id   = data["chat_id"]
    ingr      = data["ingredientes"]          
    filters   = data.get("filters", {})
    k         = int(data.get("k", 5))

    recs = _recommend(ingr, filters, k)

    publisher.publish(
        topic_out,
        json.dumps({
            "chat_id": chat_id,
            "ingredientes": ingr,         
            "recomendaciones": recs,
        }).encode(),
    )
