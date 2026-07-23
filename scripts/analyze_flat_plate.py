#!/usr/bin/env python3
"""Reproduce the flat-plate analysis from the committed processed table."""

import argparse
import json
from pathlib import Path

import pandas as pd

from sm_thesis_code.plotting import plot_analysis
from sm_thesis_code.regression import analyze_flat_plate


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "data/thesis_processed/flat_plate_thesis_processed.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    result = analyze_flat_plate(frame)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "flat_plate_results.json"
    figure_path = args.output_dir / "flat_plate_analysis.png"
    json_path.write_text(json.dumps(result, indent=2) + "\n")
    plot_analysis(frame, result, figure_path)
    for region in result["regions"]:
        print(f"{region['name']}: ln(Nu) = {region['intercept']:.5f} + {region['exponent']:.5f} ln(Re)")
    print(f"wrote {json_path}")
    print(f"wrote {figure_path}")


if __name__ == "__main__":
    main()
