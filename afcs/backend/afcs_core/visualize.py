"""Visualization utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="darkgrid")


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def feature_importance_plot(scores: Iterable[tuple[str, float]], path: Path) -> None:
    names, values = zip(*scores)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=list(values), y=list(names), ax=ax, palette="viridis")
    ax.set_xlabel("Importance score")
    ax.set_ylabel("Feature")
    _save(fig, path)


def correlation_heatmap(corr: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation heatmap")
    _save(fig, path)


def scree_plot(explained: list[float], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(range(1, len(explained) + 1), np.cumsum(explained), marker="o")
    ax.set_xlabel("Components")
    ax.set_ylabel("Cumulative variance")
    _save(fig, path)


def recon_error_hist(errors: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(errors, bins=30, ax=ax)
    ax.set_xlabel("Reconstruction error")
    _save(fig, path)


def latent_scatter(latent: np.ndarray, labels: np.ndarray | None, path2d: Path, path3d: Path | None = None) -> None:
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig2d, ax2d = plt.subplots(figsize=(6, 5))
    if latent.shape[1] >= 2:
        scatter = ax2d.scatter(latent[:, 0], latent[:, 1], c=labels, cmap="viridis", alpha=0.8)
        ax2d.set_xlabel("Latent 1")
        ax2d.set_ylabel("Latent 2")
        if labels is not None:
            fig2d.colorbar(scatter, ax=ax2d, label="Cluster")
    _save(fig2d, path2d)

    if path3d and latent.shape[1] >= 3:
        fig3d = plt.figure(figsize=(6, 5))
        ax = fig3d.add_subplot(111, projection="3d")
        scatter = ax.scatter(latent[:, 0], latent[:, 1], latent[:, 2], c=labels, cmap="viridis", alpha=0.8)
        ax.set_xlabel("Latent 1")
        ax.set_ylabel("Latent 2")
        ax.set_zlabel("Latent 3")
        if labels is not None:
            fig3d.colorbar(scatter, ax=ax, label="Cluster")
        _save(fig3d, path3d)
