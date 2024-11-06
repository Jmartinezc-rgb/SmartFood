from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import io

'''
Config del bot
Para obtener el TOKEN del bot:
Abrir Telegram y buscar BotFather.
Escribir el comando /newbot y siguir las instrucciones para crear un nuevo bot.
Una vez creado, BotFather me da el token. Tengo que sustituir 'caca' en el código por el token proporcionado.
'''

TOKEN = 'caca' # Sustituir 'caca' por el token generado de BotFather
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Teclado principal con opciones
button_info = KeyboardButton("📖 Información Nutricional")
button_recommend = KeyboardButton("🍲 Recomendaciones")
keyboard_main = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_info, button_recommend)

# Aquí iría la función para cargar el modelo de Transfer Learning
# def load_model()
# Aquí iría la función para predecir el tipo de alimento y devolver información nutricional
# def predict_food()

# Comando /start y /help para mostrar el teclado principal
@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    await message.reply("¡Hola! Soy tu asistente de nutrición. Puedes enviarme una foto de comida para obtener información nutricional o pedir recomendaciones.", reply_markup=keyboard_main)

# Manejador para recibir una imagen (aquí es donde se integrará el modelo en el futuro)
@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    photo_bytes = await photo.download(destination_file=io.BytesIO())

    # Función predict_food para obtener el alimento y su información
    # food_item, info = predict_food()

    # Respuesta simulada
    await message.reply("La función esta en desarrollo.")

# Manejador de respuestas a botones de texto
@dp.message_handler()
async def handle_text(message: types.Message):
    if message.text == '📖 Información Nutricional':
        await message.reply("Esta función permitirá obtener información nutricional de la comida en tus fotos. Próximamente estará activa.")
    elif message.text == '🍲 Recomendaciones':
        await message.reply("En el futuro, esta función te ofrecerá recomendaciones basadas en la información nutricional de tus alimentos.")
    else:
        await message.reply("No entendí eso. Usa los botones o envíame una foto de tu comida para ayudarte.")

# Ejecución del bot
if __name__ == '__main__':
    executor.start_polling(dp)
