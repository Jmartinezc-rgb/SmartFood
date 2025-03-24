import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau


class RecipeDataset(Dataset):
    def __init__(self, interactions):
        self.interactions = interactions

    def __len__(self):
        return len(self.interactions)

    def __getitem__(self, idx):
        user_id = self.interactions.iloc[idx]["user_id"]
        recipe_id = self.interactions.iloc[idx]["recipe_id"]
        rating = self.interactions.iloc[idx]["rating"]
        return torch.tensor(user_id, dtype=torch.long), torch.tensor(recipe_id, dtype=torch.long), torch.tensor(rating, dtype=torch.float)


class RecommendationModel(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim, dropout=0.4):
        super(RecommendationModel, self).__init__()

        # Embeddings
        self.user_embeddings = nn.Embedding(num_users, embedding_dim)
        self.item_embeddings = nn.Embedding(num_items, embedding_dim)

        # Fully connected layers
        self.mlp = nn.Sequential(
            nn.Linear(embedding_dim * 2, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 1)
        )

        self.embedding_regularization = 1e-4

        # Initialize embeddings
        nn.init.normal_(self.user_embeddings.weight, std=0.01)
        nn.init.normal_(self.item_embeddings.weight, std=0.01)

    def forward(self, user_ids, item_ids):
        user_embeds = self.user_embeddings(user_ids)
        item_embeds = self.item_embeddings(item_ids)
        x = torch.cat([user_embeds, item_embeds], dim=1)
        return self.mlp(x).squeeze(1)

    def regularization_loss(self):
        return self.embedding_regularization * (
            self.user_embeddings.weight.norm(2) + self.item_embeddings.weight.norm(2)
        )


def normalize_ids(interactions):
    """Normaliza los IDs de usuarios y recetas para que sean consecutivos."""
    user_mapping = {user_id: idx for idx, user_id in enumerate(interactions["user_id"].unique())}
    recipe_mapping = {recipe_id: idx for idx, recipe_id in enumerate(interactions["recipe_id"].unique())}

    interactions["user_id"] = interactions["user_id"].map(user_mapping)
    interactions["recipe_id"] = interactions["recipe_id"].map(recipe_mapping)

    return interactions, user_mapping, recipe_mapping


def main():
    # Cargar los datos
    interactions = pd.read_csv("data/clean/clean_interactions.csv")

    # Normalizar IDs de usuarios y recetas
    interactions, user_mapping, recipe_mapping = normalize_ids(interactions)

    # Configuración del modelo
    num_users = interactions["user_id"].nunique()
    num_items = interactions["recipe_id"].nunique()
    embedding_dim = 256

    # Crear dataset y dividir en entrenamiento/validación
    dataset = RecipeDataset(interactions)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False)

    # Modelo, pérdida y optimizador
    model = RecommendationModel(num_users, num_items, embedding_dim, dropout=0.3)
    criterion = nn.SmoothL1Loss()
    optimizer = optim.AdamW(model.parameters(), lr=0.002, weight_decay=1e-4)
    scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=5)

    # Dispositivo
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Entrenamiento
    num_epochs = 100
    patience = 20
    best_val_loss = float("inf")
    epochs_no_improve = 0

    for epoch in range(num_epochs):
        model.train()
        total_train_loss = 0

        for user_ids, recipe_ids, ratings in train_loader:
            user_ids, recipe_ids, ratings = user_ids.to(device), recipe_ids.to(device), ratings.to(device)

            # Forward pass
            predictions = model(user_ids, recipe_ids)
            loss = criterion(predictions, ratings) + model.regularization_loss()

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_train_loss += loss.item()

        # Validación
        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for user_ids, recipe_ids, ratings in val_loader:
                user_ids, recipe_ids, ratings = user_ids.to(device), recipe_ids.to(device), ratings.to(device)
                predictions = model(user_ids, recipe_ids)
                loss = criterion(predictions, ratings)
                total_val_loss += loss.item()

        avg_train_loss = total_train_loss / len(train_loader)
        avg_val_loss = total_val_loss / len(val_loader)

        # Imprimir métricas
        current_lr = optimizer.param_groups[0]["lr"]
        print(f"Epoch {epoch + 1}/{num_epochs}, Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}, LR: {current_lr:.6f}")

        # Scheduler
        scheduler.step(avg_val_loss)

        # Early stopping
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            epochs_no_improve = 0
            torch.save(model.state_dict(), "data/clean/recommendation_model.pth")
            print(f"Modelo mejorado guardado en epoch {epoch + 1}")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print("Early stopping activado")
                break

    print("Entrenamiento finalizado.")


if __name__ == "__main__":
    main()
