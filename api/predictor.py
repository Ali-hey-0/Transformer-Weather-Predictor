import os
import torch
import pandas as pd
import numpy as np
from model.model import TimeSeriesTransformer

# ⚙️ Settings (match your training configuration)
input_dim = 4
d_model = 48
nhead = 4
num_layers = 1
dropout = 0.1
output_window = 72
input_window = 96

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 🔃 Load the model
model = None
mean = None
std = None

def load_model():
    global model, mean, std
    if model is None:
        # Initialize model
        model = TimeSeriesTransformer(
            input_dim=input_dim,
            d_model=d_model,
            nhead=nhead,
            num_layers=num_layers,
            dropout=dropout,
            output_window=output_window
        ).to(device)
        
        # Load weights
        model_path = os.path.join(os.path.dirname(__file__), '..', 'checkpoints', 'final_transformer_model.pth')
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()
        
        # Load mean and std from dataset
        data_path = os.path.join(os.path.dirname(__file__), '..', 'weather.csv')
        df = pd.read_csv(data_path)
        df = df[['temperature', 'relative_humidity', 'wind_speed_10m (km/h)', 'pressure_msl (hPa)']]
        mean = df.mean()
        std = df.std()

# 📈 Prediction function
def predict_temperature():
    load_model()  # Ensure model is loaded
    
    # Load data
    data_path = os.path.join(os.path.dirname(__file__), '..', 'weather.csv')
    df = pd.read_csv(data_path)
    df = df[['temperature', 'relative_humidity', 'wind_speed_10m (km/h)', 'pressure_msl (hPa)']]
    
    # Normalize
    normalized_df = (df - mean) / std
    x = normalized_df.values[-input_window:].astype(np.float32)
    x = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(device)  # Add batch dimension
    
    # Predict
    with torch.no_grad():
        y_pred = model(x).squeeze().cpu().numpy()
    
    # Denormalize temperature predictions
    mean_temp = mean['temperature']
    std_temp = std['temperature']
    y_pred_denormalized = y_pred * std_temp + mean_temp
    
    return y_pred_denormalized.tolist()