#!/usr/bin/env python3
import logging
import random

import pandas as pd
import numpy as np
import tensorflow as tf

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

# Si tienes un modelo YOLO
from ultralytics import YOLO
# Si tienes un modelo de recomendación (dummy o real)
from models.recommend_model import RecommendModel

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# INICIALIZACIÓN DE MODELOS
# ------------------------------------------------------------------
yolo_model = YOLO("src/smartfood/models/yolov8x.pt") 
recommend_model = RecommendModel("data/clean/recommendation_model.pth", interactions_path="data/clean/clean_interactions.csv")

# Diccionario para almacenar datos temporales de usuarios
user_data_store = {}

# ------------------------------------------------------------------
# ESTADOS DEL CUADRO DE CONVERSACIÓN
# ------------------------------------------------------------------
(
    ASK_PREFERENCES,   # Estado para el cuestionario nutricional
    CHOOSE_MODE,       # Estado para elegir entre "Detectar" o "Recomendar manual"
) = range(2)

# ------------------------------------------------------------------
# LISTA DE CATEGORÍAS NUTRICIONALES
# ------------------------------------------------------------------
# Cada elemento es (clave_interno, etiqueta_pregunta)
NUTRI_CATEGORIES = [
    ("calories", "calorías"),
    ("total_fat", "grasas totales"),
    ("sugar", "azúcar"),
    ("sodium", "sodio"),
    ("protein", "proteína"),
    ("saturated_fat", "grasas saturadas"),
    ("carbs", "carbohidratos"),
]

# ------------------------------------------------------------------
# MANEJO DE FLUJO PRINCIPAL
# ------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mensaje de bienvenida y arranque directo del cuestionario.
    """
    await update.message.reply_text(
        "¡Hola! Bienvenido/a a SmartFood Bot.\n"
        "Primero vamos a hacerte unas preguntas sobre tus preferencias nutricionales."
    )

    # Inicializamos la estructura de preferencias y el índice de preguntas
    context.user_data['preferences'] = {}
    context.user_data['question_index'] = 0

    # Llamamos a la función que hace la primera pregunta
    return await ask_next_preference(update, context)

async def ask_next_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Función que pregunta por la siguiente categoría nutricional, o pasa al resumen si ya terminamos.
    """
    q_index = context.user_data['question_index']

    if q_index < len(NUTRI_CATEGORIES):
        # Aún hay preguntas por hacer
        key, label = NUTRI_CATEGORIES[q_index]
        await update.message.reply_text(
            f"¿Cuál es tu preferencia en {label}? (bajo/normal/alto)"
        )
        return ASK_PREFERENCES
    else:
        # Ya preguntamos todo: construir el resumen
        summary = "Resumen de tus preferencias:\n"
        for k, v in context.user_data['preferences'].items():
            summary += f"- {k}: {v}\n"

        summary += "\nAhora, elige cómo quieres obtener tus recomendaciones:\n"
        keyboard = [
            [InlineKeyboardButton("Detectar ingredientes (foto)", callback_data='mode_detect')],
            [InlineKeyboardButton("Introducir ingredientes manualmente", callback_data='mode_manual')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(summary, reply_markup=reply_markup)
        return CHOOSE_MODE

async def handle_preference_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Captura la respuesta del usuario y avanza a la siguiente pregunta o finaliza el cuestionario.
    """
    text = update.message.text.strip().lower()
    q_index = context.user_data['question_index']

    # Guardar la respuesta
    if q_index < len(NUTRI_CATEGORIES):
        key, _ = NUTRI_CATEGORIES[q_index]
        context.user_data['preferences'][key] = text
        context.user_data['question_index'] += 1

    # Llamar de nuevo a ask_next_preference para la siguiente o terminar
    return await ask_next_preference(update, context)

async def handle_mode_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recoge la elección del usuario (detectar ingredientes vs. introducir manualmente).
    """
    query = update.callback_query
    await query.answer()
    mode = query.data

    if mode == 'mode_detect':
        await query.message.reply_text("Por favor, envía una foto del plato para detectar ingredientes.")
    elif mode == 'mode_manual':
        await query.message.reply_text(
            "Escribe los ingredientes separados por comas o deja vacío para usar solo tus preferencias."
        )
    return ConversationHandler.END

# ------------------------------------------------------------------
# MANEJO DE FOTO (DETECCIÓN DE INGREDIENTES)
# ------------------------------------------------------------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Detecta ingredientes con YOLO y recomienda según preferencias + ingredientes detectados.
    """
    photo_file = await update.message.photo[-1].get_file()
    photo_path = "src/smartfood/file_0.jpg"
    await photo_file.download_to_drive(photo_path)

    results = yolo_model(photo_path)
    detections = results[0].boxes

    if not detections or len(detections) == 0:
        await update.message.reply_text("No pude identificar ingredientes en la imagen. Inténtalo de nuevo.")
        return

    detected_ing = []
    response = "Identifiqué los siguientes ingredientes:\n"
    for box in detections:
        cls = int(box.cls[0])
        label = yolo_model.names[cls]
        conf = float(box.conf[0])
        response += f"- {label} (conf: {conf:.2f})\n"
        detected_ing.append(label.strip().lower())

    # Obtener preferencias y generar recomendaciones
    preferences = context.user_data.get('preferences', {})
    recommendations = recommend_model.recommend(
        user_id=random.randint(0, 99999),
        preferences=preferences,
        ingredients=detected_ing
    )

    if recommendations:
        rec_text = "\nRecomendaciones basadas en tus preferencias + ingredientes detectados:\n"
        for idx, rec in enumerate(recommendations, 1):
            details = recommend_model.get_recipe_details(rec)
            title = details.get('title', 'Desconocido')
            rec_text += f"{idx}. {title}\n"
    else:
        rec_text = "\nLo siento, no pude generar recomendaciones en este momento."

    await update.message.reply_text(response + rec_text)

# ------------------------------------------------------------------
# MANEJO DE INGREDIENTES MANUALES
# ------------------------------------------------------------------
async def process_manual_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Toma los ingredientes escritos por el usuario y genera recomendaciones.
    """
    text = update.message.text.strip()
    if not text:
        ing_list = []
    else:
        ing_list = [ing.strip().lower() for ing in text.split(",")]

    preferences = context.user_data.get('preferences', {})
    recommendations = recommend_model.recommend(
        user_id=random.randint(0, 99999),
        preferences=preferences,
        ingredients=ing_list
    )

    if recommendations:
        rec_text = "Recomendaciones basadas en tus preferencias y los ingredientes que ingresaste:\n"
        for idx, rec in enumerate(recommendations, 1):
            details = recommend_model.get_recipe_details(rec)
            title = details.get('title', 'Desconocido')
            rec_text += f"{idx}. {title}\n"
    else:
        rec_text = "Lo siento, no pude generar recomendaciones en este momento."

    await update.message.reply_text(rec_text)

# ------------------------------------------------------------------
# CANCELAR
# ------------------------------------------------------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    TOKEN = "8123112117:AAFUg_u4_jM2xjB1kuvww_XAcQ4Ohi08MZo"

    app = ApplicationBuilder().token(TOKEN).build()

    # Conversación para el cuestionario
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PREFERENCES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_preference_answer)
            ],
            CHOOSE_MODE: [
                CallbackQueryHandler(handle_mode_choice, pattern='^(mode_detect|mode_manual)$')
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Handler para foto
    photo_handler = MessageHandler(filters.PHOTO, handle_photo)
    # Handler para ingredientes manuales
    manual_ing_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, process_manual_ingredients)

    app.add_handler(conv_handler)
    app.add_handler(photo_handler)
    app.add_handler(manual_ing_handler)

    logger.info("Bot en ejecución...")
    app.run_polling()

if __name__ == "__main__":
    main()