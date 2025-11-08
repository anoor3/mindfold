"""FastAPI application for AFCS."""
from __future__ import annotations

import shutil
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from afcs_core import pipeline
from afcs_core.config import settings
from afcs_core.preprocessing import PreprocessConfig
from afcs_core.samples import generate_demo_csv
from afcs_core.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    CompressRequest,
    CompressResponse,
    DatasetInfo,
    JobStatus,
    ResultInfo,
    UploadResponse,
)
from afcs_core.utils import generate_id

app = FastAPI(title="Adaptive Feature Compression System", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/plots", StaticFiles(directory=settings.plots_dir), name="plots")


@app.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...), demo: bool = False) -> UploadResponse:
    if demo:
        dataset_path = generate_demo_csv()
        metadata = pipeline.register_dataset(dataset_path, dataset_name="afcs_demo.csv")
    else:
        if file.content_type not in {"text/csv", "application/vnd.ms-excel"}:
            raise HTTPException(status_code=400, detail="Only CSV uploads are supported")
        dest = settings.uploads_dir / f"{generate_id('upload')}.csv"
        with dest.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        metadata = pipeline.register_dataset(dest, dataset_name=file.filename or dest.name)

    info = DatasetInfo(
        id=metadata.dataset_id,
        name=metadata.name,
        rows=metadata.rows,
        cols=metadata.cols,
        numeric_cols=len(metadata.numeric_cols),
        categorical_cols=len(metadata.categorical_cols),
        missing_pct=metadata.missing_pct,
    )
    return UploadResponse(dataset=info)


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    cfg = PreprocessConfig(
        missing_policy=request.missing_policy,
        encode_categorical=request.encode_categorical,
        standardize=request.standardize,
    )
    try:
        data = pipeline.analyze_dataset(request.dataset_id, cfg)
    except KeyError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return AnalyzeResponse(**data)


@app.post("/compress", response_model=CompressResponse)
async def compress(request: CompressRequest) -> CompressResponse:
    try:
        job_id = pipeline.start_compression_job(
            request.dataset_id,
            method=request.method,
            pca_variance=request.pca_variance,
            ae_latent_dim=request.ae_latent_dim,
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate,
            clustering=request.clustering,
            random_state=request.random_state,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return CompressResponse(job_id=job_id, status="queued")


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def job_status(job_id: str) -> JobStatus:
    try:
        job = pipeline.get_job(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**job)


@app.get("/results/{result_id}", response_model=ResultInfo)
async def fetch_result(result_id: str) -> ResultInfo:
    try:
        record = pipeline.get_result(result_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Result not found")
    return ResultInfo(
        result_id=record.result_id,
        method=record.method,
        latent_shape=list(record.latent_shape),
        recon_error=record.recon_error,
        explained_variance=record.explained_variance,
        feature_importance=record.feature_importance,
        plots=record.plots,
        artifacts=record.artifacts,
        cluster_labels=record.cluster_labels,
    )


@app.get("/download/{result_id}/{artifact_name}")
async def download_artifact(result_id: str, artifact_name: str):
    path = settings.artifacts_dir / result_id / artifact_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(path)


@app.delete("/results/{result_id}", status_code=204)
async def delete_result(result_id: str) -> None:
    pipeline.delete_result(result_id)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
