#!/bin/bash
# ============================================================
#  despliegue.sh – Despliega las 4 Cloud Functions de SmartFood
#  Webhook (HTTP)           – Telegram a Pub/Sub
#  Recomendador (Pub/Sub)   – KG (PyKEEN)
#  Mensajero (Pub/Sub)      – Pub/Sub a Telegram
#  Detector YOLO (HTTP)     – Imagen a ingredientes
# ============================================================

# Para proteger de errores comunes
set -euo pipefail

# ------------ CONFIGURACIÓN EDITABLE ------------------------
REGION="europe-west1"
PROJECT="smartfood-462714"

# Topics Pub/Sub
TOPIC_INGREDIENTES="ingredientes_detectados"   # salida Webhook / Detector
TOPIC_RESPUESTA="mensaje_respuesta"            # entrada Mensajero

# Bucket + artefactos
BUCKET_MODELOS="smartfood-models"
KGE_MODEL_BLOB="kge/trained_model.pkl"
KGE_CSV_BLOB="kge/new_triplets20_optimized.csv"
YOLO_BLOB="yolo/best.pt"

# Telegram
BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN" # esta en un .env
# ------------------------------------------------------------

echo "Creando topics (si no existen)…"
gcloud pubsub topics create "$TOPIC_INGREDIENTES" --project="$PROJECT" --quiet || true
gcloud pubsub topics create "$TOPIC_RESPUESTA"    --project="$PROJECT" --quiet || true


# 1) Webhook
echo "Desplegando Webhook…"
gcloud functions deploy webhook \
  --gen2 --runtime python310 --region "$REGION" \
  --source ./webhook --entry-point main \
  --trigger-http --allow-unauthenticated \
  --memory 1Gi --timeout 120s \
  --set-env-vars "BOT_TOKEN=$BOT_TOKEN,TOPIC_RECOMENDAR=$TOPIC_INGREDIENTES"


# 2) Recomendador(Pub/Sub)
echo "Desplegando Recomendador…"
gcloud functions deploy recomendador \
  --gen2 --runtime python310 --region "$REGION" \
  --source ./recomendador --entry-point main \
  --trigger-topic "$TOPIC_INGREDIENTES" \
  --memory 3Gi --timeout 300s \
  --set-env-vars "MODEL_BUCKET=$BUCKET_MODELOS,MODEL_BLOB=$KGE_MODEL_BLOB,CSV_BLOB=$KGE_CSV_BLOB,TOPIC_MENSAJERO=$TOPIC_RESPUESTA"


# 3) Mensajero(Pub/Sub)
echo "Desplegando Mensajero…"
gcloud functions deploy mensajero \
  --gen2 --runtime python310 --region "$REGION" \
  --source ./mensajero --entry-point main \
  --trigger-topic "$TOPIC_RESPUESTA" \
  --memory 256MB --timeout 60s \
  --set-env-vars "BOT_TOKEN=$BOT_TOKEN"


# 4) Detector YOLO
echo "Desplegando Detector YOLO…"
gcloud functions deploy detector \
  --gen2 --runtime python310 --region "$REGION" \
  --source ./detector --entry-point main \
  --trigger-http --allow-unauthenticated \
  --memory 2Gi --timeout 180s \
  --set-env-vars "MODEL_BUCKET=$BUCKET_MODELOS,YOLO_MODEL_BLOB=$YOLO_BLOB,TOPIC_SALIDA=$TOPIC_INGREDIENTES"

echo "Despliegue de las 4 funciones completado"