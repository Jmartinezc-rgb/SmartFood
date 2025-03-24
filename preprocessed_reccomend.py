import pandas as pd
import os

# Rutas de los archivos originales y destino
RAW_RECIPES_PATH = "data/train/RAW_recipes.csv"
INTERACTIONS_TRAIN_PATH = "data/train/interactions_train.csv"
INTERACTIONS_TEST_PATH = "data/train/interactions_test.csv"
INTERACTIONS_VALIDATION_PATH = "data/train/interactions_validation.csv"
CLEAN_DIR = "data/clean"

# Crear carpeta clean si no existe
os.makedirs(CLEAN_DIR, exist_ok=True)

def preprocess_raw_recipes():
    """Procesa el archivo RAW_recipes.csv."""
    recipes = pd.read_csv(RAW_RECIPES_PATH)
    recipes["nutrition"] = recipes["nutrition"].apply(eval)  # Convertir cadenas a listas
    recipes["calories"] = recipes["nutrition"].apply(lambda x: x[0])  # Extraer calorías
    recipes = recipes[["id", "name", "minutes", "tags", "ingredients", "calories"]]
    recipes.to_csv(os.path.join(CLEAN_DIR, "clean_recipes.csv"), index=False)
    print("Archivo clean_recipes.csv generado.")

def preprocess_interactions():
    """Combina y transforma los archivos de interacciones."""
    train = pd.read_csv(INTERACTIONS_TRAIN_PATH)
    test = pd.read_csv(INTERACTIONS_TEST_PATH)
    validation = pd.read_csv(INTERACTIONS_VALIDATION_PATH)

    # Añadir una columna indicando el tipo de conjunto
    train["split"] = "train"
    test["split"] = "test"
    validation["split"] = "validation"

    # Concatenar todos los conjuntos
    interactions = pd.concat([train, test, validation])
    interactions = interactions[["user_id", "recipe_id", "rating", "split"]]
    interactions.to_csv(os.path.join(CLEAN_DIR, "clean_interactions.csv"), index=False)
    print("Archivo clean_interactions.csv generado.")

if __name__ == "__main__":
    preprocess_raw_recipes()
    preprocess_interactions()
