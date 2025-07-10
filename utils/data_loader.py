import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset

class TimeSeriesDataset(Dataset):
    def __init__(self, csv_path, input_window=96, output_window=72, split="train"):
        df = pd.read_csv(csv_path)
        df = df[['temperature', 'relative_humidity', 'wind_speed_10m (km/h)', 'pressure_msl (hPa)']]
        
        # Store normalization parameters
        self.mean = df.mean()
        self.std = df.std()
        
        # Normalize
        df = (df - self.mean) / self.std
        
        # Convert to array
        data = df.values.astype(np.float32)
        
        # Split data
        split_idx = int(len(data) * 0.8)
        if split == "train":
            data = data[:split_idx]
        else:
            data = data[split_idx - input_window - output_window:]
        
        # Precompute windows
        num_samples = len(data) - input_window - output_window
        self.X = np.zeros((num_samples, input_window, 4), dtype=np.float32)
        self.y = np.zeros((num_samples, output_window), dtype=np.float32)
        
        for i in range(num_samples):
            self.X[i] = data[i:i+input_window]
            self.y[i] = data[i+input_window:i+input_window+output_window, 0]
        
        # Convert to tensors
        self.X = torch.as_tensor(self.X)
        self.y = torch.as_tensor(self.y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
    
    def get_normalization_params(self):
        """Get mean and std for denormalization"""
        return self.mean, self.std