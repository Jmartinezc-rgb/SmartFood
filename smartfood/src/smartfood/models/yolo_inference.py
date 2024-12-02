from ultralytics import YOLO
import pandas as pd

class YOLOv8Model:
    def __init__(self, weights_path="yolov8s.pt"):
        """
        Inicializa el modelo YOLOv8 con los pesos preentrenados.
        """
        self.model = YOLO(weights_path)

    def predict(self, image_path):
        """
        Realiza la inferencia en una imagen.
        :param image_path: Ruta a la imagen
        :return: DataFrame con los resultados (categoría, confianza, coordenadas)
        """
        results = self.model(image_path)
        predictions = results.pandas().xyxy[0]  # Formato de salida como DataFrame
        return predictions

# Función para manejar imágenes enviadas desde Telegram
async def handle_photo(update, context, yolo_model):
    # Descargar la imagen enviada por Telegram
    photo = await update.message.photo[-1].get_file()
    photo_path = await photo.download()  # Descargar la imagen al servidor
    
    print(f"Imagen descargada en: {photo_path}")
    
    # Realizar la predicción con YOLOv8
    predictions = yolo_model.predict(photo_path)
    
    # Verificar si hay resultados
    if predictions.empty:
        await update.message.reply_text("No pude identificar ningún objeto en la imagen.")
    else:
        # Construir una respuesta con los resultados
        response = "Identifiqué los siguientes elementos:\n"
        for _, row in predictions.iterrows():
            response += f"- {row['name']} (Confianza: {row['confidence']:.2f})\n"
        await update.message.reply_text(response)

# Ejemplo de uso con Telegram
if __name__ == "__main__":
    yolo = YOLOv8Model(weights_path="../models/yolov8s.pt")
    # Suponiendo que `update` y `context` provienen de Telegram
    # await handle_photo(update, context, yolo)
