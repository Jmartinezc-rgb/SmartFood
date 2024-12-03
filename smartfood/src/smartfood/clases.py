import os

def get_classes_from_labels(labels_dir):
    """
    Obtiene la lista de clases únicas en los archivos de etiquetas.
    Args:
        labels_dir (str): Ruta al directorio de etiquetas.
    Returns:
        set: Conjunto de clases únicas encontradas.
    """
    classes = set()
    for label_file in os.listdir(labels_dir):
        label_path = os.path.join(labels_dir, label_file)
        with open(label_path, "r") as f:
            for line in f:
                class_id = int(line.split()[0])  # Extrae la primera columna (class_id)
                classes.add(class_id)
    return classes

# Cambia esta ruta según tu proyecto
train_labels_dir = "data/train/labels"
validation_labels_dir = "data/validation/labels"

# Obtén las clases únicas del conjunto de entrenamiento y validación
train_classes = get_classes_from_labels(train_labels_dir)
validation_classes = get_classes_from_labels(validation_labels_dir)

# Combina las clases de ambos conjuntos
all_classes = train_classes.union(validation_classes)

print(f"Clases únicas encontradas: {sorted(all_classes)}")
print(f"Número total de clases: {len(all_classes)}")
