"""
Mensajero entrega las recomendaciones al usuario (Telegram)
------------------------------------------------------------
Trigger  : Pub/Sub topic 'mensaje_respuesta'
Payload  : {
    "chat_id": 123456,
    "ingredientes": ["potato", "egg", "butter"],
    "recomendaciones": [
        {"dish": "quickandeasy", "score": -5.69},
    ]
}
"""

import base64, json, logging, os

import functions_framework
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]         
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def _send(chat_id: int, text: str) -> None:
    try:
        requests.post(
            TELEGRAM_API,
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
    except Exception as e:                   
        logging.error(f"Telegram error: {e}")

@functions_framework.cloud_event
def main(event):
    logging.info("💬 Mensajero triggered")

    try:
        data_b64 = event.data["message"]["data"]
        payload = json.loads(base64.b64decode(data_b64).decode())
        chat_id = payload["chat_id"]
        ingredientes = payload.get("ingredientes", [])      
        recs = payload.get("recomendaciones", [])
    except Exception as e:                                  
        logging.error(f"Payload malformado: {e}")
        return "Bad payload", 400

    if ingredientes:
        ingredientes_fmt = ", ".join(ing.title() for ing in ingredientes)
        _send(chat_id, f"🔎 *Ingredientes detectados*: {ingredientes_fmt}")

    if not recs:
        _send(chat_id, "Lo siento, no encontré recetas para esos parámetros.")
        return "OK", 200

    lines = ["🥗 *Recetas recomendadas*"]
    for i, r in enumerate(recs, 1):
        dish = r["dish"].replace("_", " ").title()
        lines.append(f"{i}. {dish}")
    _send(chat_id, "\n".join(lines))

    return "OK", 200
