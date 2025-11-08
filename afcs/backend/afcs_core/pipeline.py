"""Pipeline orchestration for AFCS."""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from .ae_model import export_autoencoder, export_scaler, train_autoencoder
from .config import settings
from .pca_model import export_pca, run_pca
from .preprocessing import PreprocessConfig, PreprocessResult, dataframe_preview, load_csv, preprocess
from .ranking import RankingResult, rank_features
from .utils import generate_id, job_registry, save_json, seed_all, write_dataframe_csv
from .visualize import correlation_heatmap, feature_importance_plot, latent_scatter, recon_error_hist, scree_plot


@dataclass
class DatasetContext:
    metadata: DatasetMetadata
    preprocess_cfg: PreprocessConfig | None = None
    preprocess_result: PreprocessResult | None = None
    ranking: RankingResult | None = None
    preview: list[dict[str, Any]] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultRecord:
    result_id: str
    method: str
    latent_shape: tuple[int, int]
    recon_error: float
    explained_variance: list[float] | None
    feature_importance: list[dict[str, float]]
    plots: list[dict[str, str]]
    artifacts: list[dict[str, str]]
    cluster_labels: list[int] | None
    metadata_path: Path


_dataset_store: dict[str, DatasetContext] = {}
_results_store: dict[str, ResultRecord] = {}


def register_dataset(file_path: Path, *, dataset_name: str | None = None) -> DatasetMetadata:
    metadata = load_csv(file_path, dataset_name=dataset_name, max_rows=settings.max_rows)
    df = pd.read_csv(metadata.path)
    preview = dataframe_preview(df)
    stats = {
        "shape": [metadata.rows, metadata.cols],
        "describe": df.describe(include="all").fillna(0).to_dict(),
        "missing": df.isna().sum().to_dict(),
    }
    _dataset_store[metadata.dataset_id] = DatasetContext(metadata=metadata, preview=preview, stats=stats)
    return metadata


def get_dataset(dataset_id: str) -> DatasetContext:
    if dataset_id not in _dataset_store:
        raise KeyError(f"Unknown dataset: {dataset_id}")
    return _dataset_store[dataset_id]


def analyze_dataset(dataset_id: str, cfg: PreprocessConfig) -> dict[str, Any]:
    context = get_dataset(dataset_id)
    df = pd.read_csv(context.metadata.path)
    preproc = preprocess(context.metadata, cfg)
    ranking = rank_features(preproc.processed)

    context.preprocess_cfg = cfg
    context.preprocess_result = preproc
    context.ranking = ranking

    inferred_types = {col: ("numeric" if col in context.metadata.numeric_cols else "categorical") for col in df.columns}

    response = {
        "stats": context.stats,
        "inferred_types": inferred_types,
        "missingness": df.isna().mean().to_dict(),
        "preview_rows": len(context.preview),
    }
    return response


def _choose_k(latent: np.ndarray) -> int:
    inertias: list[float] = []
    ks = list(range(2, min(8, latent.shape[0] - 1) + 1))
    for k in ks:
        km = KMeans(n_clusters=k, random_state=0)
        km.fit(latent)
        inertias.append(km.inertia_)
    if len(inertias) < 2:
        return 2
    deltas = np.diff(inertias)
    knee = int(np.argmin(deltas)) + 2
    return knee


def _cluster_latent(latent: np.ndarray, random_state: int) -> np.ndarray:
    if latent.shape[0] < 4:
        return np.zeros(latent.shape[0], dtype=int)
    k = _choose_k(latent)
    km = KMeans(n_clusters=k, random_state=random_state)
    return km.fit_predict(latent)


def start_compression_job(dataset_id: str, *, method: str, pca_variance: float, ae_latent_dim: int, epochs: int, batch_size: int, learning_rate: float, clustering: str, random_state: int) -> str:
    context = get_dataset(dataset_id)
    if context.preprocess_result is None:
        raise RuntimeError("Dataset must be analyzed before compression.")

    job = job_registry.create()

    thread = threading.Thread(
        target=_run_compression_job,
        args=(job.job_id, context, method, pca_variance, ae_latent_dim, epochs, batch_size, learning_rate, clustering, random_state),
        daemon=True,
    )
    thread.start()
    return job.job_id


def _run_compression_job(job_id: str, context: DatasetContext, method: str, pca_variance: float, ae_latent_dim: int, epochs: int, batch_size: int, learning_rate: float, clustering: str, random_state: int) -> None:
    try:
        seed_all(random_state)
        job_registry.update(job_id, status="running", progress=5, message="Loading dataset")

        preproc = context.preprocess_result
        assert preproc is not None

        data = preproc.processed
        job_registry.update(job_id, progress=30, message="Ranking features")
        ranking = context.ranking or rank_features(data)

        result_id = generate_id("result")
        artifacts_dir = settings.artifacts_dir / result_id
        plots_dir = settings.plots_dir / result_id

        job_registry.update(job_id, progress=60, message="Running compression")
        if method == "pca":
            comp = run_pca(data, variance_threshold=pca_variance)
            explained = comp.explained_variance
            reconstruction = comp.reconstruction
            latent = comp.latent
            recon_error = comp.recon_error
        else:
            comp = train_autoencoder(
                data.to_numpy(),
                latent_dim=ae_latent_dim,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate,
            )
            explained = None
            reconstruction = comp.reconstruction
            latent = comp.latent
            recon_error = comp.recon_error

        job_registry.update(job_id, progress=80, message="Clustering latent space")
        labels: np.ndarray | None = None
        if clustering == "kmeans":
            labels = _cluster_latent(latent, random_state)

        job_registry.update(job_id, progress=90, message="Generating visualisations")
        feature_scores = context.ranking.scores if context.ranking else ranking.scores
        feature_importance_plot([(fs.name, fs.score) for fs in feature_scores], plots_dir / "feature_importance.png")
        correlation_heatmap(ranking.correlation, plots_dir / "correlation_heatmap.png")
        if method == "pca" and explained is not None:
            scree_plot(explained, plots_dir / "pca_scree.png")
        per_row_error = np.mean((data.to_numpy() - reconstruction) ** 2, axis=1)
        recon_error_hist(per_row_error, plots_dir / "recon_hist.png")
        latent_scatter(latent, labels, plots_dir / "latent_scatter_2d.png", plots_dir / "latent_scatter_3d.png")

        job_registry.update(job_id, progress=95, message="Saving artifacts")
        latent_df = pd.DataFrame(latent, columns=[f"z{i+1}" for i in range(latent.shape[1])])
        write_dataframe_csv(latent_df, artifacts_dir / "compressed.csv")

        metadata_payload = {
            "dataset": {
                "id": context.metadata.dataset_id,
                "name": context.metadata.name,
                "rows": context.metadata.rows,
                "cols": context.metadata.cols,
            },
            "method": method,
            "random_state": random_state,
            "preprocess": {
                "missing_policy": context.preprocess_cfg.missing_policy if context.preprocess_cfg else None,
                "encode_categorical": context.preprocess_cfg.encode_categorical if context.preprocess_cfg else None,
                "standardize": context.preprocess_cfg.standardize if context.preprocess_cfg else None,
            },
            "feature_importance": [
                {"name": fs.name, "score": fs.score}
                for fs in feature_scores
            ],
            "reconstruction_error": recon_error,
        }
        metadata_path = artifacts_dir / "metadata.json"
        save_json(metadata_path, metadata_payload)

        artifact_links = [
            {"name": "compressed.csv", "url": f"/download/{result_id}/compressed.csv"},
            {"name": "metadata.json", "url": f"/download/{result_id}/metadata.json"},
        ]

        if method == "pca":
            export_pca(comp, artifacts_dir / "pipeline.joblib", metadata_payload)
            artifact_links.append({"name": "pipeline.joblib", "url": f"/download/{result_id}/pipeline.joblib"})
        else:
            export_autoencoder(comp.model, artifacts_dir / "ae.pt")
            artifact_links.append({"name": "ae.pt", "url": f"/download/{result_id}/ae.pt"})
            if preproc.scaler:
                export_scaler(preproc.scaler, artifacts_dir / "scaler.joblib")
                artifact_links.append({"name": "scaler.joblib", "url": f"/download/{result_id}/scaler.joblib"})

        plots = [
            {"name": "feature_importance", "url": f"/static/plots/{result_id}/feature_importance.png"},
            {"name": "correlation_heatmap", "url": f"/static/plots/{result_id}/correlation_heatmap.png"},
            {"name": "latent_scatter_2d", "url": f"/static/plots/{result_id}/latent_scatter_2d.png"},
            {"name": "recon_hist", "url": f"/static/plots/{result_id}/recon_hist.png"},
        ]
        if method == "pca":
            plots.append({"name": "pca_scree", "url": f"/static/plots/{result_id}/pca_scree.png"})
        if latent.shape[1] >= 3:
            plots.append({"name": "latent_scatter_3d", "url": f"/static/plots/{result_id}/latent_scatter_3d.png"})

        record = ResultRecord(
            result_id=result_id,
            method=method,
            latent_shape=latent.shape,
            recon_error=recon_error,
            explained_variance=explained,
            feature_importance=[{"name": fs.name, "score": fs.score} for fs in feature_scores],
            plots=plots,
            artifacts=artifact_links,
            cluster_labels=labels.tolist() if labels is not None else None,
            metadata_path=metadata_path,
        )
        _results_store[result_id] = record
        job_registry.update(job_id, status="done", progress=100, message="Completed", result_id=result_id)
    except Exception as exc:  # pragma: no cover - protective
        job_registry.update(job_id, status="error", message=str(exc))
        raise


def get_job(job_id: str) -> dict[str, Any]:
    job = job_registry.get(job_id)
    if not job:
        raise KeyError(f"Unknown job: {job_id}")
    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "message": job.message,
        "result_id": job.result_id,
    }


def get_result(result_id: str) -> ResultRecord:
    if result_id not in _results_store:
        raise KeyError(f"Unknown result: {result_id}")
    return _results_store[result_id]


def delete_result(result_id: str) -> None:
    record = _results_store.pop(result_id, None)
    if not record:
        return
    artifacts_dir = settings.artifacts_dir / result_id
    plots_dir = settings.plots_dir / result_id
    for directory in [artifacts_dir, plots_dir]:
        if directory.exists():
            for item in directory.glob("*"):
                item.unlink()
            directory.rmdir()
