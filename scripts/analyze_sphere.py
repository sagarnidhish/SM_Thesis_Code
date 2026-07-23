#!/usr/bin/env python3
"""Reproduce the rigid-sphere analysis from the committed processed table."""

import argparse
import json
from pathlib import Path

import pandas as pd

from sm_thesis_code.plotting import plot_analysis
from sm_thesis_code.regression import analyze_sphere


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "data/thesis_processed/sphere_thesis_processed.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    result = analyze_sphere(frame)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "sphere_results.json"
    figure_path = args.output_dir / "sphere_analysis.png"
    json_path.write_text(json.dumps(result, indent=2) + "\n")
    plot_analysis(frame, result, figure_path)
    for region in result["regions"]:
        print(f"{region['name']}: Nu = 2 + {region['coefficient']:.5f} Re^{region['exponent']:.5f} Pr^(1/3)")
    print(f"wrote {json_path}")
    print(f"wrote {figure_path}")


if __name__ == "__main__":
    main()
