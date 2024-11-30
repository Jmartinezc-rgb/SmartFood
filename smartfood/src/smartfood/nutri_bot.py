from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

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

# Manejador de imágenes (placeholder de momento)
async def handle_photo(update: Update, context):
    print("Aquí YOLO procesaría la imagen enviada para identificar el plato.")
    # Mensaje al usuario con placeholder de detección
    await update.message.reply_text("Recibí tu imagen, puedo ver que es XXXXXXXXXX.")
    
    # Pregunta al usuario si quiere la receta
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
            "1. Calienta las tortillas en un comal o sartén durante 1-2 minutos por cada lado.\n2. Cocina la carne (res, cerdo o pollo) en un sartén con sal y especias al gusto hasta que esté bien dorada.\n3. Pica cebolla y cilantro fresco finamente para el aderezo.\n4. Prepara una salsa con tomates, chiles, ajo y sal, y licúala hasta obtener una textura homogénea.\n5. Coloca la carne cocida en el centro de las tortillas calientes.\n6. Agrega cebolla, cilantro y un poco de salsa sobre la carne.\n7. Sirve con una rodaja de limón y acompaña con tu bebida favorita.", 
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
