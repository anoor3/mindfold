"""PCA-based compression."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from .utils import save_joblib


@dataclass
class PCAResult:
    latent: np.ndarray
    reconstruction: np.ndarray
    recon_error: float
    explained_variance: list[float]
    pca: PCA


def run_pca(data: pd.DataFrame, variance_threshold: float = 0.95) -> PCAResult:
    if not 0 < variance_threshold <= 1:
        raise ValueError("variance_threshold must be between 0 and 1")
    pca = PCA(n_components=variance_threshold, svd_solver="full")
    latent = pca.fit_transform(data)
    reconstruction = pca.inverse_transform(latent)
    mse = float(np.mean((data.to_numpy() - reconstruction) ** 2))
    return PCAResult(
        latent=latent,
        reconstruction=reconstruction,
        recon_error=mse,
        explained_variance=pca.explained_variance_ratio_.tolist(),
        pca=pca,
    )


def export_pca(result: PCAResult, path: Path, metadata: dict[str, Any]) -> None:
    payload = {
        "pca": result.pca,
        "metadata": metadata,
    }
    save_joblib(payload, path)
