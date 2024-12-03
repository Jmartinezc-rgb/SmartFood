import os
from datasets import load_dataset
from PIL import Image

def load_foodseg_dataset():
    """
    Descarga el dataset FoodSeg103 desde Hugging Face y separa en train y validation.

    Returns:
        tuple: (train_dataset, validation_dataset)
    """
    # Descarga el dataset desde Hugging Face
    dataset = load_dataset("EduardoPacheco/FoodSeg103")
    
    # Separa los datos en train y validation
    train_dataset = dataset['train']
    validation_dataset = dataset['validation']
    
    return train_dataset, validation_dataset


def convert_to_yolo_format(dataset, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    annotations_dir = os.path.join(output_dir, "labels")
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(annotations_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    for idx, sample in enumerate(dataset):
        # Guarda la imagen
        image = sample['image']
        image_path = os.path.join(images_dir, f"{idx}.jpg")
        image.save(image_path)

        # Maneja las etiquetas
        bboxes = sample['classes_on_image']
        label = sample['id']
        with open(os.path.join(annotations_dir, f"{idx}.txt"), "w") as f:
            for bbox in bboxes:
                if isinstance(bbox, list) and len(bbox) == 4:
                    # Formato esperado [x_min, y_min, x_max, y_max]
                    x_min, y_min, x_max, y_max = bbox
                    x_center = (x_min + x_max) / 2 / image.width
                    y_center = (y_min + y_max) / 2 / image.height
                    box_width = (x_max - x_min) / image.width
                    box_height = (y_max - y_min) / image.height
                    f.write(f"{label} {x_center} {y_center} {box_width} {box_height}\n")
                elif isinstance(bbox, int):  # Si es un entero (clase)
                    f.write(f"{bbox} 0.5 0.5 1.0 1.0\n")  # Bounding box genérico
                else:
                    print(f"Formato inesperado para bbox: {bbox}")






if __name__ == "__main__":
    # Descarga y carga los datasets
    train, validation = load_foodseg_dataset()
    
    # Convierte y guarda en formato YOLO
    print("Convirtiendo el dataset de entrenamiento...")
    convert_to_yolo_format(train, "data/train")
    print("Convirtiendo el dataset de validación...")
    convert_to_yolo_format(validation, "data/validation")
    print("Conversión completada.")
