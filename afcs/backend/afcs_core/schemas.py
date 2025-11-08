"""Pydantic schemas for API communication."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class DatasetInfo(BaseModel):
    id: str
    name: str
    rows: int
    cols: int
    numeric_cols: int
    categorical_cols: int
    missing_pct: float


class UploadResponse(BaseModel):
    dataset: DatasetInfo


class AnalyzeRequest(BaseModel):
    dataset_id: str
    missing_policy: Literal["drop", "median", "most_frequent"] = "median"
    encode_categorical: bool = True
    standardize: bool = True


class AnalyzeResponse(BaseModel):
    stats: dict
    inferred_types: dict[str, Literal["numeric", "categorical"]]
    missingness: dict[str, float]
    preview_rows: int


class CompressRequest(BaseModel):
    dataset_id: str
    method: Literal["pca", "autoencoder"] = "pca"
    pca_variance: float = Field(default=0.95, ge=0.8, le=0.99)
    ae_latent_dim: int = Field(default=4, ge=2, le=16)
    epochs: int = Field(default=30, ge=1, le=200)
    batch_size: int = Field(default=32, ge=4, le=512)
    learning_rate: float = Field(default=1e-3, gt=0)
    clustering: Literal["kmeans", "none"] = "kmeans"
    random_state: int = 42


class CompressResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "done", "error"]


class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "running", "done", "error"]
    progress: int
    message: Optional[str] = None
    result_id: Optional[str] = None


class ArtifactRef(BaseModel):
    name: str
    url: str


class PlotRef(BaseModel):
    name: str
    url: str


class FeatureImportance(BaseModel):
    name: str
    score: float


class ResultInfo(BaseModel):
    result_id: str
    method: str
    latent_shape: list[int]
    recon_error: float
    explained_variance: Optional[list[float]] = None
    feature_importance: list[FeatureImportance]
    plots: list[PlotRef]
    artifacts: list[ArtifactRef]
    cluster_labels: Optional[list[int]] = None
