from pathlib import Path

import numpy as np
import pandas as pd

from sm_thesis_code.data import load_dataset
from sm_thesis_code.preprocessing import prepare_flat_plate, prepare_sphere


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COLUMNS = [
    "source_row",
    "reynolds_number",
    "source_nusselt_number",
    "perturbation_factor",
    "nusselt_number",
]


def test_flat_plate_preprocessing_matches_seeded_thesis_scatter():
    source = load_dataset(ROOT / "data/source/flat_plate_literature_compiled.xlsx")
    result = prepare_flat_plate(source)
    assert list(result.columns) == EXPECTED_COLUMNS
    assert len(result) == 102
    np.random.seed(0)
    expected = 1.0 + 0.05 * np.random.randn(len(source))
    np.testing.assert_allclose(result["perturbation_factor"], expected, rtol=0, atol=1e-15)
    np.testing.assert_allclose(
        result["nusselt_number"], source["nusselt_number"] * expected, rtol=0, atol=1e-12
    )


def test_sphere_preprocessing_matches_seeded_thesis_scatter():
    source = load_dataset(ROOT / "data/source/sphere_literature_compiled.xlsx")
    result = prepare_sphere(source)
    assert list(result.columns) == EXPECTED_COLUMNS
    assert len(result) == 282
    np.testing.assert_array_equal(result.loc[:6, "perturbation_factor"], np.ones(7))
    rng = np.random.default_rng(0)
    beta = rng.beta(2, 8, size=len(source) - 7)
    expected_tail = 1.0 + (beta - beta.mean()) * 0.2
    np.testing.assert_allclose(result.loc[7:, "perturbation_factor"], expected_tail, rtol=0, atol=1e-15)


def test_committed_processed_tables_equal_regeneration():
    pairs = [
        ("flat_plate_literature_compiled.xlsx", "flat_plate_thesis_processed.csv", prepare_flat_plate),
        ("sphere_literature_compiled.xlsx", "sphere_thesis_processed.csv", prepare_sphere),
    ]
    for source_name, processed_name, function in pairs:
        source = load_dataset(ROOT / "data/source" / source_name)
        expected = function(source)
        actual = pd.read_csv(ROOT / "data/thesis_processed" / processed_name)
        pd.testing.assert_frame_equal(actual, expected, check_exact=False, rtol=1e-14, atol=1e-14)
