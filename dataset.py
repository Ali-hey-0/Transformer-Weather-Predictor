# dataset.py
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset

class TimeSeriesDataset(Dataset):
    def __init__(self, csv_path, input_window=168, output_window=72, split="train"):
        df = pd.read_csv(csv_path)
        df = df[['temperature', 'relative_humidity', 'wind_speed_10m (km/h)', 'pressure_msl (hPa)']]
        
        # Normalize
        self.mean = df.mean()
        self.std = df.std()
        df = (df - self.mean) / self.std
        
        # Convert To Array
        data = df.values.astype(np.float32)
        
        # Split Train/Test
        split_ratio = 0.8
        split_idx = int(len(data) * split_ratio)
        
        if split == "train":
            data = data[:split_idx]
        else:
            data = data[split_idx - input_window - output_window:]
        
        # Building Windows - pre-allocate arrays for better performance
        num_samples = len(data) - input_window - output_window
        self.X = np.zeros((num_samples, input_window, data.shape[1]), dtype=np.float32)
        self.y = np.zeros((num_samples, output_window), dtype=np.float32)
        
        for i in range(num_samples):
            self.X[i] = data[i:i+input_window]
            self.y[i] = data[i+input_window:i+input_window+output_window, 0]
        
        # Convert to tensors
        self.X = torch.tensor(self.X)
        self.y = torch.tensor(self.y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):  # Fixed method name (added double underscore)
        return self.X[idx], self.y[idx]