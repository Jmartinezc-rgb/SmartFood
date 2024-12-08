from ultralytics import YOLO
import torch

def main():
    # Ruta al archivo de configuración de datos y modelo preentrenado
    data_yaml = "foodseg103.yaml"
    model_weights = "yolov8s.pt"  # Cambia a un modelo más pequeño para reducir el uso de memoria

    # Vaciar la caché de GPU antes de inicializar el modelo
    torch.cuda.empty_cache()

    # Establecer configuración para evitar fragmentación de memoria
    torch.backends.cudnn.benchmark = True  # Acelera entrenamientos con datos de entrada consistentes

    # Inicializa el modelo
    model = YOLO(model_weights)

    # Configura el entrenamiento
    model.train(
        data=data_yaml,
        epochs=10,        # Reducción del número de épocas
        imgsz=320,        # Resolución más baja para reducir el uso de memoria
        batch=24,          # Tamaño de batch reducido
        device=0,         # Usa la GPU (CUDA:0)       # Reducir número de workers para minimizar problemas de memoria
    )

if __name__ == "__main__":
    main()
