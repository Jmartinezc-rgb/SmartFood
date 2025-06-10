from PIL import Image
from ultralytics import YOLO
import os

MODEL_PATH = "smartfood/src/smartfood/models/yolov8m.pt" 

def load_model():
    """Carga el modelo YOLO desde el archivo .pt"""
    if not os.path.exists(MODEL_PATH):
        print(f"Error: No se encuentra el modelo YOLO en {MODEL_PATH}")
        return None
    try:
        model = YOLO(MODEL_PATH)
        print("Modelo YOLO cargado exitosamente.")
        return model
    except Exception as e:
        print(f"Error al cargar el modelo YOLO: {e}")
        return None

def detect(model: YOLO, image: Image.Image) -> list[str]:
    """
    Recibe un modelo cargado y una imagen, y devuelve una lista de nombres de ingredientes.
    """
    if not model:
        return ["El modelo YOLO no está disponible"]
    
    # YOLOv8 puede predecir directamente desde un objeto de imagen de PIL
    results = model(image)
    
    # Nombres de las detecciones
    detected_ingredients = []
    if results:
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            detected_ingredients.append(label.lower())
            
    return detected_ingredients