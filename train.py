from ultralytics import YOLO
import torch

def main():
    # Ruta al archivo de configuración de datos y modelo preentrenado
    data_yaml = "foodseg103.yaml"
    model_weights = "yolov8m.pt"

    # Vaciar la caché de GPU antes de inicializar el modelo
    torch.cuda.empty_cache()

    # Establecer configuración para evitar fragmentación de memoria
    torch.backends.cudnn.benchmark = True  # Acelera entrenamientos con datos consistentes

    # Inicializa el modelo
    model = YOLO(model_weights)

    # Configura el entrenamiento
    model.train(
        data=data_yaml,
        epochs=100,       # Aumentar el número de épocas para un mejor entrenamiento
        imgsz=640,        # Resolución de imagen
        batch=16,         # Tamaño de batch equilibrado para 12GB de VRAM
        device=0,         # Usa la GPU
        workers=4,        # Número de workers para carga de datos
        mosaic=1.0,       # Activar mosaico con un nivel alto de mezcla
        name="train_with_adam",  # Nombre del experimento
        save_period=10,   # Guardar pesos cada 10 épocas
        optimizer="Adam", # Cambiar optimizador: Adam
        lr0=0.001,        # Tasa de aprendizaje inicial (ajustar según el optimizador)
        weight_decay=0.0005,  # Descomposición de pesos para regularización
        momentum=0.9      # Momentum (si se usa SGD, pero también puede beneficiar Adam)
    )

if __name__ == "__main__":
    main()
