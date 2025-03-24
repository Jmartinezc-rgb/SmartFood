# Archivo: models/recommend_model.py
class RecommendModel:
    def __init__(self, model_path=None, interactions_path=None):
        print("Usando modelo de recomendación dummy.")
    
    def recommend(self, user_id, preferences={}, ingredients=[]):
        # Devuelve una lista de IDs de recetas dummy
        return ["recipe_dummy1", "recipe_dummy2", "recipe_dummy3"]
    
    def get_recipe_details(self, recipe_id):
        # Devuelve detalles dummy para una receta
        return {"title": f"Receta {recipe_id}", "description": "Descripción de la receta dummy"}
    
    def get_popular_recipes(self, top_n=5):
        # Devuelve una lista dummy de recetas populares
        return [f"recipe_dummy{i}" for i in range(1, top_n + 1)]
    
    def rate_recipe(self, recipe_id, rating):
        print(f"Receta {recipe_id} calificada con {rating} estrellas.")
