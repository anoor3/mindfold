"""Data loading and preprocessing utilities."""
from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import settings
from .utils import generate_id


@dataclass
class DatasetMetadata:
    dataset_id: str
    name: str
    path: Path
    rows: int
    cols: int
    numeric_cols: list[str]
    categorical_cols: list[str]
    ignored_cols: list[str]
    missing_pct: float


@dataclass
class PreprocessConfig:
    missing_policy: str
    encode_categorical: bool
    standardize: bool
    treat_first_row_header: bool = True


@dataclass
class PreprocessResult:
    metadata: DatasetMetadata
    processed: pd.DataFrame
    scaler: StandardScaler | None
    encoder: OneHotEncoder | None
    feature_mapping: list[str]


def _infer_types(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    numeric_cols: list[str] = []
    categorical_cols: list[str] = []
    ignored_cols: list[str] = []
    for col in df.columns:
        series = df[col]
        if is_numeric_dtype(series):
            unique_ratio = series.nunique(dropna=True) / max(len(series), 1)
            if unique_ratio > 0.02:
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)
        else:
            categorical_cols.append(col)
    return numeric_cols, categorical_cols, ignored_cols


def load_csv(file_path: Path, *, dataset_name: str | None = None, max_rows: int | None = None) -> DatasetMetadata:
    df = pd.read_csv(file_path)
    if max_rows and len(df) > max_rows:
        df = df.sample(max_rows, random_state=0)
    numeric_cols, categorical_cols, ignored_cols = _infer_types(df)
    missing_pct = float(df.isna().sum().sum() / (df.size or 1))
    dataset_id = generate_id("ds")
    return DatasetMetadata(
        dataset_id=dataset_id,
        name=dataset_name or file_path.name,
        path=file_path,
        rows=len(df),
        cols=len(df.columns),
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        ignored_cols=ignored_cols,
        missing_pct=missing_pct,
    )


def preprocess(metadata: DatasetMetadata, cfg: PreprocessConfig) -> PreprocessResult:
    df = pd.read_csv(metadata.path)
    numeric_cols, categorical_cols, _ = _infer_types(df)
    if len(numeric_cols) < 2:
        raise ValueError("At least two numeric columns are required for analysis.")

    df = _apply_missing_policy(df, cfg.missing_policy)
    encoder: OneHotEncoder | None = None
    processed = df[numeric_cols].copy()

    if cfg.encode_categorical and categorical_cols:
        low_card_cols = [c for c in categorical_cols if df[c].nunique(dropna=True) < 50]
        encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")
        if low_card_cols:
            encoded = encoder.fit_transform(df[low_card_cols].fillna("missing"))
            encoded_cols = encoder.get_feature_names_out(low_card_cols).tolist()
            processed = pd.concat([
                processed.reset_index(drop=True),
                pd.DataFrame(encoded, columns=encoded_cols),
            ], axis=1)
        high_card = set(categorical_cols) - set(low_card_cols)
        processed.drop(columns=list(high_card), errors="ignore")

    scaler: StandardScaler | None = None
    if cfg.standardize:
        scaler = StandardScaler()
        processed = pd.DataFrame(scaler.fit_transform(processed), columns=processed.columns)

    feature_mapping = processed.columns.tolist()
    return PreprocessResult(
        metadata=metadata,
        processed=processed,
        scaler=scaler,
        encoder=encoder,
        feature_mapping=feature_mapping,
    )


def _apply_missing_policy(df: pd.DataFrame, policy: str) -> pd.DataFrame:
    if policy == "drop":
        return df.dropna()
    if policy == "median":
        numeric = df.select_dtypes(include=[np.number])
        df[numeric.columns] = numeric.fillna(numeric.median())
        non_numeric = df.select_dtypes(exclude=[np.number])
        df[non_numeric.columns] = non_numeric.fillna(non_numeric.mode().iloc[0]) if not non_numeric.empty else non_numeric
        return df
    if policy == "most_frequent":
        return df.fillna(df.mode().iloc[0])
    raise ValueError(f"Unsupported missing policy: {policy}")


def dataframe_preview(df: pd.DataFrame, rows: int = 100) -> list[dict[str, Any]]:
    return df.head(rows).to_dict(orient="records")
