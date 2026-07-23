from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_contains_complete_quick_start_and_provenance():
    text = (ROOT / "README.md").read_text()
    for required in [
        "pip install -e .",
        "python scripts/prepare_data.py",
        "python scripts/analyze_flat_plate.py",
        "python scripts/analyze_sphere.py",
        "manually digitized experimental",
        "synthetic perturbation",
        "data/thesis_processed",
    ]:
        assert required in text
    assert "This repository reproduces two thesis case studies" in text
    assert "Using the datasets in further work" in text


def test_data_readme_documents_every_column_and_known_quirks():
    text = (ROOT / "data/README.md").read_text()
    for required in [
        "reynolds_number",
        "nusselt_number",
        "source_nusselt_number",
        "perturbation_factor",
        "source_row",
        "duplicate",
        "out-of-order",
    ]:
        assert required in text
    assert "Recommended reproduction input" in text


def test_public_repo_excludes_personal_and_internal_metadata():
    assert not (ROOT / "CITATION.cff").exists()
    assert not (ROOT / "docs").exists()
    license_text = (ROOT / "LICENSE").read_text().lower()
    assert "sm thesis code contributors" in license_text
