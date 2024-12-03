from datasets import load_dataset

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

if __name__ == "__main__":
    # Ejemplo de uso
    train, validation = load_foodseg_dataset()
    print(f"Train Dataset: {train}")
    print(f"Validation Dataset: {validation}")
