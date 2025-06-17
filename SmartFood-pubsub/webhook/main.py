"""
Telegram Webhook guarda preferencias y publica ingredientes a Pub/Sub
----------------------------------------------------------------------
Topic texto  : TOPIC_RECOMENDAR   (ingredientes_detectados)
Topic imagen : TOPIC_DETECT_IMG  (ingredientes_imagen)
Firestore    : users  (doc.id = chat_id)
"""

import json
import logging
import os
from typing import Dict

import functions_framework
import google.auth
import requests
from google.cloud import firestore, pubsub_v1

# ─────────── Config ────────────
BOT_TOKEN = os.environ["BOT_TOKEN"]

PROJECT_ID = (
    os.getenv("GOOGLE_CLOUD_PROJECT")
    or os.getenv("GCLOUD_PROJECT")
    or os.getenv("GCP_PROJECT")
)
if not PROJECT_ID:
    _, PROJECT_ID = google.auth.default()

TOPIC_RECOMENDAR = os.getenv("TOPIC_RECOMENDAR", "ingredientes_detectados")  # texto
TOPIC_DETECT_IMG = os.getenv("TOPIC_DETECT_IMG", "ingredientes_imagen")      # imagen

db = firestore.Client()
publisher = pubsub_v1.PublisherClient()
topic_text_path = publisher.topic_path(PROJECT_ID, TOPIC_RECOMENDAR)
topic_img_path  = publisher.topic_path(PROJECT_ID, TOPIC_DETECT_IMG)

QUESTIONS = [
    ("has_calories",  "¿Preferencia en calorías? (bajo/normal/alto)"),
    ("has_total",     "¿Preferencia en grasas totales? (bajo/normal/alto)"),
    ("has_sugar",     "¿Preferencia en azúcar? (bajo/normal/alto)"),
    ("has_sodium",    "¿Preferencia en sodio? (bajo/normal/alto)"),
    ("has_protein",   "¿Preferencia en proteína? (bajo/normal/alto)"),
    ("has_saturated", "¿Preferencia en grasas saturadas? (bajo/normal/alto)"),
    ("has_carbs",     "¿Preferencia en carbohidratos? (bajo/normal/alto)"),
]
OPCIONES = {"bajo": "low", "normal": "normal", "alto": "high"}

SUFIJOS = {
    "has_calories":  "calories",
    "has_total":     "fat",
    "has_sugar":     "sugar",
    "has_sodium":    "sodium",
    "has_protein":   "protein",
    "has_saturated": "saturated_fat",
    "has_carbs":     "carbs",
}

# ───────── helpers ─────────
def _send(chat_id: int, text: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )

def _pref_entity(rel: str, answer: str) -> str:
    prefix = OPCIONES.get(answer.lower())
    if not prefix or rel not in SUFIJOS:
        raise ValueError
    return f"{prefix}_{SUFIJOS[rel]}"

# ───────── entry-point HTTP ─────────
@functions_framework.http
def main(request):
    update = request.get_json(silent=True) or {}
    msg = update.get("message")
    if not msg:
        return "OK", 200

    chat_id = msg["chat"]["id"]
    text    = msg.get("text", "").strip()

    # estado del usuario
    doc  = db.collection("users").document(str(chat_id))
    user: Dict = doc.get().to_dict() or {
        "state_index": 0,
        "prefs": {},
        "state": "awaiting",
    }

    # ───────── /start ─────────
    if text == "/start":
        user = {"state_index": 0, "prefs": {}, "state": "awaiting"}
        doc.set(user)
        _send(chat_id, QUESTIONS[0][1])         # ① solo la 1ª pregunta
        return "OK", 200

    # ───────── cuestionario ─────────
    if user["state"] != "ready":
        idx = user["state_index"]
        try:
            rel, _ = QUESTIONS[idx]
            user["prefs"][rel] = _pref_entity(rel, text)
            idx += 1
            if idx >= len(QUESTIONS):
                user.update({"state": "ready", "state_index": idx})
                doc.set(user)
                _send(
                    chat_id,
                    "✅ Preferencias guardadas.\n"
                    "*¿Cómo quieres darme los ingredientes?*\n"
                    "• Escríbelos separados por comas, *o*\n"
                    "• envíame una *foto* del plato/ingredientes."
                )
            else:
                user["state_index"] = idx
                doc.set(user)
                _send(chat_id, QUESTIONS[idx][1])
        except ValueError:
            _send(chat_id, "Responde únicamente *bajo*, *normal* o *alto*.")
        return "OK", 200

    # ───────── foto ─────────
    if "photo" in msg:
        file_id = msg["photo"][-1]["file_id"]
        publisher.publish(
            topic_img_path,
            json.dumps({
                "chat_id": chat_id,
                "file_id": file_id,
                "filters": user["prefs"],
                "k": 5,
            }).encode()
        )
        _send(chat_id, "📷 Imagen recibida, detectando ingredientes…")
        return "OK", 200

    # ───────── texto (lista ingredientes) ─────────
    ingredientes = [i.strip().lower() for i in text.split(",") if i.strip()]
    if not ingredientes:
        _send(chat_id, "❗ No he reconocido ingredientes. Inténtalo de nuevo.")
        return "OK", 200

    publisher.publish(
        topic_text_path,
        json.dumps({
            "chat_id": chat_id,
            "ingredientes": ingredientes,
            "filters": user["prefs"],
            "k": 5,
        }).encode()
    )
    _send(chat_id, "🍳 ¡Recibido! Buscando recetas…")
    return "OK", 200
