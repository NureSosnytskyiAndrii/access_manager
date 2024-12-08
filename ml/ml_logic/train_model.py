import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from sklearn.preprocessing import StandardScaler

class AccessLevelModel(nn.Module):
    def __init__(self, input_size):
        super(AccessLevelModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 16)
        self.fc2 = nn.Linear(16, 8)
        self.fc3 = nn.Linear(8, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x


class AccessLevelDataset(Dataset):
    def __init__(self, data):
        self.features = torch.tensor(data[["access_level", "activity_score", "violations", "days_since_last_login"]].values, dtype=torch.float32)
        self.targets = torch.tensor((data["access_level"] > 3).astype(int).values, dtype=torch.float32)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]

def train_model(data_path):

    data = pd.read_excel(data_path)

    scaler = StandardScaler()
    features = data[["access_level", "activity_score", "violations", "days_since_last_login"]].values
    features = scaler.fit_transform(features)

    targets = (data["access_level"] > 3).astype(int).values
    features = torch.tensor(features, dtype=torch.float32)
    targets = torch.tensor(targets, dtype=torch.float32)

    dataset = AccessLevelDataset(data)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = AccessLevelModel(input_size=features.shape[1])
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    epochs = 100
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for inputs, targets in train_loader:
            optimizer.zero_grad()

            outputs = model(inputs).squeeze()
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print(f"Epoch {epoch + 1}/{epochs}, Loss: {running_loss / len(train_loader)}")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(BASE_DIR, "ml/ml_models/trained_model.pt")

    if not os.path.exists(os.path.dirname(model_path)):
        os.makedirs(os.path.dirname(model_path))

    torch.save(model.state_dict(), model_path)
    print(f"Model saved in {model_path}")

data_path = "C:/NURE/ТБЧ/access_manager/ml/ml_logic/user_data.xlsx"
train_model(data_path)
