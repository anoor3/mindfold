"""Configuration helpers for AFCS backend."""
from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    data_dir: Path = Path(os.environ.get("AFCS_DATA_DIR", (Path.home() / ".afcs")))
    uploads_dir: Path = data_dir / "uploads"
    artifacts_dir: Path = data_dir / "artifacts"
    plots_dir: Path = data_dir / "plots"
    max_upload_size_mb: int = 50
    max_rows: int = 250_000
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        frozen = True


settings = Settings()

# Ensure directories exist at import time so the service can start cleanly.
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
settings.plots_dir.mkdir(parents=True, exist_ok=True)
