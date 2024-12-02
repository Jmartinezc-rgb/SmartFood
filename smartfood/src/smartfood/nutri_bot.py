from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from ultralytics import YOLO  # Importar YOLOv8

# Inicializar el modelo YOLOv8
yolo_model = YOLO("../models/yolov8x.pt") 

# Función para el comando /start
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Identificar Plato", callback_data='identify')],
        [InlineKeyboardButton("Recomendación", callback_data='recommend')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Hola, ¿qué deseas hacer?", reply_markup=reply_markup)

# Función para manejar las opciones del menú
async def handle_option(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'identify':
        print("Aquí actuaría YOLO para identificar el plato.")
        keyboard = [[InlineKeyboardButton("Volver atrás", callback_data='back_to_start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Por favor, envía una imagen del plato a identificar.", reply_markup=reply_markup)
    elif query.data == 'recommend':
        print("Aquí el modelo generaría una recomendación.")
        keyboard = [[InlineKeyboardButton("Volver atrás", callback_data='back_to_start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Te recomiendo el plato XXXXXXXXXX.", reply_markup=reply_markup)

# Función para manejar imágenes enviadas por el usuario
async def handle_photo(update: Update, context):
    # Descargar la imagen enviada por Telegram
    photo = await update.message.photo[-1].get_file()
    photo_path = "file_0.jpg"
    await photo.download_to_drive(photo_path)  # Corregido: Descarga la imagen

    print(f"Imagen descargada: {photo_path}")

    # Realizar la inferencia con YOLOv8
    results = yolo_model(photo_path)

    # Procesar los resultados manualmente
    detections = results[0].boxes  # Acceder a las detecciones de la primera imagen
    if detections is None or len(detections) == 0:
        await update.message.reply_text("No pude identificar ningún plato en la imagen. Inténtalo de nuevo.")
        return

    # Construir la respuesta con los resultados
    response = "Identifiqué los siguientes elementos:\n"
    for box in detections:
        cls = int(box.cls[0])  # Clase detectada
        confidence = float(box.conf[0])  # Confianza de la detección
        label = yolo_model.names[cls]  # Obtener el nombre de la clase
        response += f"- {label} (Confianza: {confidence:.3f})\n"

    await update.message.reply_text(response)

    # Preguntar al usuario si quiere una receta
    keyboard = [
        [InlineKeyboardButton("Sí, enviar receta", callback_data='send_recipe')],
        [InlineKeyboardButton("No, gracias", callback_data='no_recipe')],
        [InlineKeyboardButton("Volver atrás", callback_data='back_to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("¿Quieres que te envíe la receta?", reply_markup=reply_markup)

# Función para manejar la elección de receta
async def handle_recipe_choice(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'send_recipe':
        print("Aquí se enviaría la receta del plato identificado.")
        keyboard = [[InlineKeyboardButton("Volver atrás", callback_data='back_to_start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            "1. Calienta las tortillas en un comal o sartén durante 1-2 minutos por cada lado.\n"
            "2. Cocina la carne (res, cerdo o pollo) en un sartén con sal y especias al gusto hasta que esté bien dorada.\n"
            "3. Pica cebolla y cilantro fresco finamente para el aderezo.\n"
            "4. Prepara una salsa con tomates, chiles, ajo y sal, y licúala hasta obtener una textura homogénea.\n"
            "5. Coloca la carne cocida en el centro de las tortillas calientes.\n"
            "6. Agrega cebolla, cilantro y un poco de salsa sobre la carne.\n"
            "7. Sirve con una rodaja de limón y acompaña con tu bebida favorita.", 
            reply_markup=reply_markup
        )
    elif query.data == 'no_recipe':
        print("El usuario no quiere la receta.")
        keyboard = [[InlineKeyboardButton("Volver atrás", callback_data='back_to_start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "¡Entendido! Si necesitas algo más, no dudes en pedírmelo.",
            reply_markup=reply_markup
        )

# Función para manejar "Volver atrás"
async def handle_back(update: Update, context):
    query = update.callback_query
    await query.answer()
    # Muestra nuevamente las opciones iniciales
    keyboard = [
        [InlineKeyboardButton("Identificar Plato", callback_data='identify')],
        [InlineKeyboardButton("Recomendación", callback_data='recommend')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Hola, ¿qué deseas hacer?", reply_markup=reply_markup)

# Inicialización del bot
def main():
    app = ApplicationBuilder().token("8123112117:AAFUg_u4_jM2xjB1kuvww_XAcQ4Ohi08MZo").build()
    
    # Agregar manejadores
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_option, pattern='identify|recommend'))
    app.add_handler(CallbackQueryHandler(handle_back, pattern='back_to_start'))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_recipe_choice, pattern='send_recipe|no_recipe'))

    print("Bot en ejecución...")
    app.run_polling()

if __name__ == '__main__':
    main()
