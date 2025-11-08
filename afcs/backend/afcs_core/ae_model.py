"""Autoencoder compression implementation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from .utils import save_joblib


class AutoEncoder(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.LayerNorm(128),
            nn.Linear(128, latent_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        latent = self.encoder(x)
        recon = self.decoder(latent)
        return recon

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            return self.encoder(x)


@dataclass
class AutoEncoderResult:
    latent: np.ndarray
    reconstruction: np.ndarray
    recon_error: float
    model: AutoEncoder


def train_autoencoder(
    data: np.ndarray,
    latent_dim: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    device: str = "cpu",
) -> AutoEncoderResult:
    tensor_data = torch.from_numpy(data.astype(np.float32))
    dataset = TensorDataset(tensor_data)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = AutoEncoder(data.shape[1], latent_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    best_loss = float("inf")
    best_state: dict[str, Any] | None = None
    patience = 10
    patience_counter = 0

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for (batch,) in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            recon = model(batch)
            loss = criterion(recon, batch)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * len(batch)
        epoch_loss = running_loss / len(dataset)

        if epoch_loss < best_loss - 1e-6:
            best_loss = epoch_loss
            best_state = model.state_dict()
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        recon = model(tensor_data.to(device)).cpu().numpy()
        latent = model.encode(tensor_data.to(device)).cpu().numpy()
    mse = float(np.mean((data - recon) ** 2))
    return AutoEncoderResult(latent=latent, reconstruction=recon, recon_error=mse, model=model)


def export_autoencoder(model: AutoEncoder, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)


def export_scaler(scaler: Any, path: Path) -> None:
    save_joblib(scaler, path)
