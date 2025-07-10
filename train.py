import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from dataset import TimeSeriesDataset
from model.model import TimeSeriesTransformer
import os
import time

def train_model():
    # ⚙️ Settings
    input_dim = 4
    d_model = 48
    nhead = 4
    num_layers = 1
    dropout = 0.1
    output_window = 72
    input_window = 96
    batch_size = 256
    epochs = 1
    lr = 1e-3
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 🔧 Performance optimizations
    torch.set_num_threads(os.cpu_count())  # Use all CPU cores
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True  # Only enable for CUDA

    # Dataset And DataLoader with optimizations
    train_dataset = TimeSeriesDataset("./weather.csv", input_window=input_window, output_window=output_window, split="train")
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,  # Disable multiprocessing for Windows compatibility
        pin_memory=True if device.type == 'cuda' else False
    )

    # 🧠 Model
    model = TimeSeriesTransformer(
        input_dim=input_dim,
        d_model=d_model,
        nhead=nhead,
        num_layers=num_layers,
        dropout=dropout,
        output_window=output_window
    ).to(device)

    # Skip torch.compile for Windows compatibility
    # if hasattr(torch, 'compile'):
    #     model = torch.compile(model)
    #     print("Using torch.compile for model optimization")

    # Loss + Optimizer
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # 📊 Training monitoring
    start_time = time.time()

    # Train Loop with optimizations
    for epoch in range(epochs):
        epoch_start = time.time()
        model.train()
        total_loss = 0.0
        
        for batch_idx, (x, y) in enumerate(train_loader):
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y)
            loss.backward()
            
            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            total_loss += loss.item()
            
            # Print batch progress
            if batch_idx % 10 == 0:
                print(f"Epoch {epoch+1} | Batch {batch_idx}/{len(train_loader)} | Loss: {loss.item():.4f}")
        
        epoch_time = time.time() - epoch_start
        avg_loss = total_loss / len(train_loader)
        print(f"[{epoch+1}/{epochs}] Loss: {avg_loss:.4f} | Time: {epoch_time:.2f}s")

    # Saving Model
    os.makedirs("./checkpoints", exist_ok=True)
    torch.save(model.state_dict(), "./checkpoints/final_transformer_model.pth")

    # ⏱️ Total training time
    total_time = time.time() - start_time
    print(f"Model Saved | Total Training Time: {total_time:.2f} seconds")

if __name__ == '__main__':
    train_model()