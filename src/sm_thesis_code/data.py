"""Dataset loading and non-destructive validation."""

from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ("reynolds_number", "nusselt_number")


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load a canonical XLSX or CSV dataset without changing row order."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        frame = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported dataset format: {path.suffix}")
    missing = [name for name in REQUIRED_COLUMNS if name not in frame.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")
    result = frame.loc[:, REQUIRED_COLUMNS].copy()
    for name in REQUIRED_COLUMNS:
        result[name] = pd.to_numeric(result[name], errors="raise")
    values = result.loc[:, REQUIRED_COLUMNS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Reynolds and Nusselt values must be finite")
    if (values <= 0).any():
        raise ValueError("Reynolds and Nusselt values must be positive")
    return result


def validate_dataset(frame: pd.DataFrame) -> list[str]:
    """Return reproducibility warnings without sorting or deduplicating."""
    reynolds = frame["reynolds_number"]
    warnings: list[str] = []
    duplicates = int(reynolds.duplicated().sum())
    decreases = int((np.diff(reynolds.to_numpy(dtype=float)) < 0).sum())
    if duplicates:
        warnings.append(f"{duplicates} duplicate Reynolds-number row(s)")
    if decreases:
        warnings.append(f"{decreases} decrease(s) in original Reynolds-number row order")
    return warnings
