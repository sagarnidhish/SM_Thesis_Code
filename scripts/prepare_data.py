#!/usr/bin/env python3
"""Regenerate the exact processed data tables used by the thesis workflow."""

from pathlib import Path

from sm_thesis_code.data import load_dataset, validate_dataset
from sm_thesis_code.preprocessing import prepare_flat_plate, prepare_sphere


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    output = ROOT / "data/thesis_processed"
    output.mkdir(parents=True, exist_ok=True)
    cases = [
        ("flat_plate_literature_compiled.xlsx", "flat_plate_thesis_processed.csv", prepare_flat_plate),
        ("sphere_literature_compiled.xlsx", "sphere_thesis_processed.csv", prepare_sphere),
    ]
    for source_name, output_name, function in cases:
        source = load_dataset(ROOT / "data/source" / source_name)
        for warning in validate_dataset(source):
            print(f"{source_name}: note: {warning}")
        processed = function(source)
        destination = output / output_name
        processed.to_csv(destination, index=False, float_format="%.17g")
        print(f"wrote {len(processed)} rows to {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
