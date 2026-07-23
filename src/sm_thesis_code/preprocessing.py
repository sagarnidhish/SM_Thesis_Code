"""Deterministic reconstruction of the values plotted in the thesis."""

import numpy as np
import pandas as pd


OUTPUT_COLUMNS = (
    "source_row",
    "reynolds_number",
    "source_nusselt_number",
    "perturbation_factor",
    "nusselt_number",
)


def _assemble(source: pd.DataFrame, factors: np.ndarray) -> pd.DataFrame:
    source_nu = source["nusselt_number"].to_numpy(dtype=float)
    return pd.DataFrame(
        {
            "source_row": np.arange(1, len(source) + 1),
            "reynolds_number": source["reynolds_number"].to_numpy(dtype=float),
            "source_nusselt_number": source_nu,
            "perturbation_factor": factors,
            "nusselt_number": source_nu * factors,
        },
        columns=OUTPUT_COLUMNS,
    )


def prepare_flat_plate(source: pd.DataFrame) -> pd.DataFrame:
    """Apply the seed-0, 5% Gaussian multiplier used by the thesis script."""
    state = np.random.RandomState(0)
    factors = 1.0 + 0.05 * state.randn(len(source))
    return _assemble(source, factors)


def prepare_sphere(source: pd.DataFrame) -> pd.DataFrame:
    """Apply the seed-0 centered Beta multiplier used by the thesis script."""
    factors = np.ones(len(source), dtype=float)
    if len(source) > 7:
        rng = np.random.default_rng(0)
        beta = rng.beta(2, 8, size=len(source) - 7)
        factors[7:] = 1.0 + (beta - beta.mean()) * 0.2
    return _assemble(source, factors)
