import numpy as np
import pandas as pd

from afcs_core.pca_model import run_pca
from afcs_core.ae_model import train_autoencoder


def test_pca_reduces_reconstruction_error():
    rng = np.random.default_rng(0)
    data = pd.DataFrame(rng.normal(size=(200, 5)), columns=[f"f{i}" for i in range(5)])
    result = run_pca(data, variance_threshold=0.9)
    assert result.latent.shape[1] <= 5
    assert result.recon_error >= 0


def test_autoencoder_training_runs():
    rng = np.random.default_rng(0)
    data = rng.normal(size=(100, 6)).astype(np.float32)
    result = train_autoencoder(data, latent_dim=3, epochs=3, batch_size=16, learning_rate=1e-3)
    assert result.latent.shape == (100, 3)
    assert result.reconstruction.shape == data.shape
