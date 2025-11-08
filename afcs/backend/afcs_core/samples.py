"""Synthetic dataset generator for demos."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import settings


def generate_demo_csv(path: Path | None = None, rows: int = 2000, random_state: int = 42) -> Path:
    rng = np.random.default_rng(random_state)
    base = rng.normal(0, 1, size=(rows, 4))
    features = {
        "feature_a": base[:, 0],
        "feature_b": base[:, 0] * 0.8 + rng.normal(0, 0.2, rows),
        "feature_c": base[:, 1] * 1.2,
        "feature_d": base[:, 1] * -0.5 + rng.normal(0, 0.5, rows),
        "feature_e": base[:, 2] + base[:, 3] * 0.3,
        "feature_f": rng.normal(0, 1, rows),
    }
    categories = rng.integers(0, 3, rows)
    features.update(
        {
            "segment": pd.Categorical.from_codes(categories, categories=["silver", "gold", "platinum"]),
            "region": pd.Categorical(rng.choice(["north", "south", "west"], size=rows, p=[0.3, 0.4, 0.3])),
        }
    )
    df = pd.DataFrame(features)
    df["target_like"] = df["feature_a"] * 1.5 + df["feature_e"] * -0.8 + rng.normal(0, 0.5, rows)
    df.loc[rng.choice(rows, size=int(rows * 0.05), replace=False), "feature_f"] = np.nan

    dest = path or settings.data_dir / "demo.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    return dest
