import os

import torch
import pandas as pd
from .train_model import AccessLevelModel


def load_model():
    model = AccessLevelModel(input_size=4)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(BASE_DIR, "ml/ml_models/trained_model.pt")

    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
    else:
        raise FileNotFoundError(f"Model file not found at {model_path}")

    model.eval()
    return model


def predict_access(data_path):
    model = load_model()
    data = pd.read_excel(data_path)
    features = data[["access_level", "activity_score", "violations", "days_since_last_login"]].values
    features = torch.tensor(features, dtype=torch.float32)

    with torch.no_grad():
        predictions = model(features).squeeze().numpy()
        data["recommend_change"] = (predictions > 0.5).astype(int)

    return data
