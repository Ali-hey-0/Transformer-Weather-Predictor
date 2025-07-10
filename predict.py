import torch
import matplotlib.pyplot as plt
from dataset import TimeSeriesDataset
from model.model import TimeSeriesTransformer
from torch.utils.data import DataLoader
from sklearn.metrics import mean_absolute_error
import numpy as np

# ⚙️ Use the same settings as in train.py
input_dim = 4
d_model = 48  # Must match training
nhead = 4
num_layers = 1  # Must match training
dropout = 0.1
output_window = 72
input_window = 96  # Must match training
batch_size = 1

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 🧠 Model with same architecture as training
model = TimeSeriesTransformer(
    input_dim=input_dim,
    d_model=d_model,
    nhead=nhead,
    num_layers=num_layers,
    dropout=dropout,
    output_window=output_window
).to(device)

# 🔃 Load saved weights
model.load_state_dict(torch.load("./checkpoints/final_transformer_model.pth", map_location=device))
model.eval()

# 📦 Test dataset with same input_window
test_dataset = TimeSeriesDataset(
    "weather.csv", 
    input_window=input_window,  # Must match training
    output_window=output_window, 
    split="test"
)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# 🔍 Predict on a sample
with torch.no_grad():
    for x, y in test_loader:
        x, y = x.to(device), y.to(device)
        y_pred = model(x)
        y_pred = y_pred.squeeze().cpu().numpy()
        y_true = y.squeeze().cpu().numpy()

        # 📊 Plot results
        plt.figure(figsize=(12, 5))
        plt.plot(y_true, label="Real")
        plt.plot(y_pred, label="Predicted")
        plt.title("Transformer Model Forecast")
        plt.xlabel("Hour")
        plt.ylabel("Temperature")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("forecast.png")  # Save instead of show
        plt.close()
        print("Forecast plot saved as forecast.png")

        # 🎯 Evaluate
        mae = mean_absolute_error(y_true, y_pred)
        print(f"MAE: {mae:.4f}")
        break