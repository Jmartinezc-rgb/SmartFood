# smartfood/src/smartfood/recommender_service.py
import os
from .models.recommend_model import RecommendModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas relativas 
MODEL_PATH = os.path.join(BASE_DIR, "models", "trained_pykeen_model.pkl")
INTERACTIONS_PATH = os.path.join(BASE_DIR, "assets", "clean_interactions.csv")

def load_model():
    """Carga el modelo de recomendación."""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(INTERACTIONS_PATH):
        print(f"Error: Faltan archivos para el recomendador.")
        return None
    try:
        model = RecommendModel(MODEL_PATH, interactions_path=INTERACTIONS_PATH)
        print("Modelo de recomendación cargado exitosamente.")
        return model
    except Exception as e:
        print(f"Error al cargar el modelo de recomendación: {e}")
        return None

def get_recommendations(model: RecommendModel, preferences: dict, ingredients: list[str], user_id: int) -> list[dict]:
    """
    Genera y devuelve una lista de recetas con sus detalles.
    """
    if not model:
        return [{"title": "Error", "details": "El modelo de recomendación no está disponible"}]
        
    # 1. Obtenemos los IDs de las recetas recomendadas
    recommendation_ids = model.recommend(
        user_id=user_id,
        preferences=preferences,
        ingredients=ingredients
    )
    
    if not recommendation_ids:
        return []
        
    # 2. Obtenemos los detalles de cada receta
    recommendations_with_details = []
    for rec_id in recommendation_ids:
        details = model.get_recipe_details(rec_id
        recommendations_with_details.append({
            "id": rec_id,
            "title": details.get('title', 'Título no disponible'),
            "calories": details.get('calories', 0)
        })
        
    return recommendations_with_details