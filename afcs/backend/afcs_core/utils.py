"""Utility helpers for AFCS."""
from __future__ import annotations

import json
import math
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import torch
from joblib import dump

from .config import settings


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def seed_all(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


@dataclass
class JobState:
    job_id: str
    status: str = "queued"
    progress: int = 0
    message: str | None = None
    result_id: str | None = None
    updated: float = field(default_factory=time.time)


class JobRegistry:
    """Thread-safe in-process job registry."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobState] = {}
        self._lock = threading.Lock()

    def create(self) -> JobState:
        job = JobState(job_id=generate_id("job"))
        with self._lock:
            self._jobs[job.job_id] = job
        return job

    def update(self, job_id: str, *, status: str | None = None, progress: int | None = None, message: str | None = None, result_id: str | None = None) -> JobState:
        with self._lock:
            job = self._jobs[job_id]
            if status is not None:
                job.status = status
            if progress is not None:
                job.progress = max(0, min(100, progress))
            if message is not None:
                job.message = message
            if result_id is not None:
                job.result_id = result_id
            job.updated = time.time()
            return job

    def get(self, job_id: str) -> JobState | None:
        with self._lock:
            return self._jobs.get(job_id)

    def delete(self, job_id: str) -> None:
        with self._lock:
            self._jobs.pop(job_id, None)


job_registry = JobRegistry()


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=_json_default)


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, (np.ndarray, pd.Index)):
        return obj.tolist()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)!r} is not JSON serializable")


def write_dataframe_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_joblib(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dump(obj, path)


def human_readable_bytes(num_bytes: int) -> str:
    if num_bytes == 0:
        return "0B"
    units = ["B", "KB", "MB", "GB", "TB"]
    power = min(int(math.log(num_bytes, 1024)), len(units) - 1)
    value = num_bytes / (1024 ** power)
    return f"{value:.1f}{units[power]}"


def timed_step(job_id: str, progress: int, message: str, func: Callable[[], Any]) -> Any:
    job_registry.update(job_id, status="running", progress=progress, message=message)
    return func()
