"""Feature ranking implementation."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA


@dataclass
class FeatureScore:
    name: str
    score: float
    variance: float
    redundancy: float
    loading: float


@dataclass
class RankingResult:
    scores: list[FeatureScore]
    correlation: pd.DataFrame


def rank_features(data: pd.DataFrame, n_components: int | None = None) -> RankingResult:
    if data.empty:
        raise ValueError("Cannot rank features on an empty dataframe")

    corr = data.corr(numeric_only=True).fillna(0.0)
    variances = data.var().replace(0, np.nan)
    variance_norm = (variances - variances.min()) / (variances.max() - variances.min() + 1e-9)

    max_corr = corr.abs().where(~np.eye(len(corr), dtype=bool), 0).max(axis=1)
    redundancy_norm = (max_corr - max_corr.min()) / (max_corr.max() - max_corr.min() + 1e-9)

    pca = PCA(n_components=min(n_components or data.shape[1], data.shape[1]))
    pca.fit(data)
    loadings = np.mean(np.abs(pca.components_), axis=0)
    loading_norm = (loadings - loadings.min()) / (loadings.max() - loadings.min() + 1e-9)

    raw_scores = []
    features: list[FeatureScore] = []
    for idx, col in enumerate(data.columns):
        score = 0.45 * variance_norm.iloc[idx] + 0.45 * loading_norm[idx] - 0.30 * redundancy_norm.iloc[idx]
        raw_scores.append(score)
        features.append(
            FeatureScore(
                name=col,
                score=float(score),
                variance=float(variance_norm.iloc[idx]),
                redundancy=float(redundancy_norm.iloc[idx]),
                loading=float(loading_norm[idx]),
            )
        )

    raw_scores = np.array(raw_scores)
    raw_scores = (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min() + 1e-9)
    for feature, norm_score in zip(features, raw_scores):
        feature.score = float(np.clip(norm_score, 0.0, 1.0))

    features.sort(key=lambda f: f.score, reverse=True)
    return RankingResult(scores=features, correlation=corr)
