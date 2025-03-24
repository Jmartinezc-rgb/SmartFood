import pandas as pd

# Cargar los datos
recipes = pd.read_csv("data/train/RAW_recipes.csv")
interactions = pd.read_csv("data/train/interactions_train.csv")

# Seleccionar columnas relevantes
recipes = recipes[["id", "name", "tags", "ingredients", "steps", "description"]]
interactions = interactions[["user_id", "recipe_id", "rating"]]

# Combinar datos
merged_data = pd.merge(interactions, recipes, left_on="recipe_id", right_on="id")

# Preprocesar datos
def preprocess_data(df):
    df["input_text"] = (
        "Preferencias: " + df["tags"].astype(str) + " | " +
        "Ingredientes: " + df["ingredients"].astype(str) + " | " +
        "Descripción: " + df["description"].astype(str)
    )
    df["output_text"] = df["name"]  # El nombre de la receta será el objetivo
    return df

processed_data = preprocess_data(merged_data)

# Guardar datos procesados en un archivo CSV
processed_data[["input_text", "output_text"]].to_csv("data/train/processed_data.csv", index=False)

print("Datos preprocesados guardados en 'data/train/processed_data.csv'")
