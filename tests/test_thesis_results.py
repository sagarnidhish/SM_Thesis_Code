from pathlib import Path
import json
import subprocess
import sys

import pandas as pd
import pytest

from sm_thesis_code.regression import analyze_flat_plate, analyze_sphere


ROOT = Path(__file__).resolve().parents[1]


def test_flat_plate_reproduces_historical_script_results():
    frame = pd.read_csv(ROOT / "data/thesis_processed/flat_plate_thesis_processed.csv")
    result = analyze_flat_plate(frame)
    assert result["boundaries"] == pytest.approx([504988.444782053, 856434.400046759])
    expected = [(-0.54208, 0.50337), (-26.07864, 2.45452), (-4.43024, 0.87378)]
    for region, (intercept, exponent) in zip(result["regions"], expected):
        assert region["intercept"] == pytest.approx(intercept, abs=2e-5)
        assert region["exponent"] == pytest.approx(exponent, abs=2e-5)


def test_sphere_reproduces_thesis_table_coefficients():
    frame = pd.read_csv(ROOT / "data/thesis_processed/sphere_thesis_processed.csv")
    result = analyze_sphere(frame)
    expected = [(0.39536, 0.49757), (0.40669, 0.55318), (0.14925, 0.66175)]
    assert len(result["regions"]) == 3
    for region, (coefficient, exponent) in zip(result["regions"], expected):
        assert region["coefficient"] == pytest.approx(coefficient, abs=2e-5)
        assert region["exponent"] == pytest.approx(exponent, abs=2e-5)


def test_analyses_reject_missing_columns():
    invalid = pd.DataFrame({"reynolds_number": [1.0, 2.0]})
    with pytest.raises(ValueError, match="nusselt_number"):
        analyze_flat_plate(invalid)
    with pytest.raises(ValueError, match="nusselt_number"):
        analyze_sphere(invalid)


@pytest.mark.parametrize("case", ["flat_plate", "sphere"])
def test_analysis_cli_writes_json_and_figure(case, tmp_path):
    command = ROOT / "scripts" / f"analyze_{case}.py"
    completed = subprocess.run(
        [sys.executable, str(command), "--output-dir", str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result_path = tmp_path / f"{case}_results.json"
    figure_path = tmp_path / f"{case}_analysis.png"
    assert result_path.exists()
    assert figure_path.stat().st_size > 10_000
    assert json.loads(result_path.read_text())["case"] == case
    assert "wrote" in completed.stdout


@pytest.mark.parametrize("case", ["flat_plate", "sphere"])
def test_repository_includes_reproducible_example_outputs(case):
    result_path = ROOT / "outputs" / f"{case}_results.json"
    figure_path = ROOT / "outputs" / f"{case}_analysis.png"
    assert result_path.exists()
    assert figure_path.stat().st_size > 10_000
    result = json.loads(result_path.read_text())
    assert result["case"] == case
    assert len(result["regions"]) == 3
