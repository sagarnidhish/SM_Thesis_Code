# SM Thesis Code: Convective Heat-Transfer Correlations

This repository reproduces two thesis case studies on data-driven convective heat-transfer correlations: forced convection over a flat plate and forced convection around a rigid sphere.

## Quick start

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Verify or regenerate the exact processed tables.
python scripts/prepare_data.py

# Reproduce both case studies.
python scripts/analyze_flat_plate.py
python scripts/analyze_sphere.py

# Run all integrity and numerical-reproduction checks.
python -m pytest -v
```

Figures and JSON summaries are written to `outputs/`. The commands under `scripts/` are the documented interface.

## Repository design

The analysis code is separated into reusable scientific logic and executable workflows:

- `src/sm_thesis_code/` is the calculation engine. It contains the functions for loading and preprocessing data, fitting the regional models, and creating results. These functions can be imported by tests, notebooks, or new analyses.
- `scripts/` contains the command-line entry points. These scripts call the reusable functions to prepare the datasets and reproduce the figures and JSON summaries.

For example:

```text
scripts/analyze_flat_plate.py
        ↓ imports and calls
src/sm_thesis_code/regression.py
        ↓ uses
src/sm_thesis_code/segmentation.py and plotting.py
```

Keeping the two layers separate avoids duplicated analysis code, makes the numerical methods directly testable, and allows the package to be extended without copying an entire workflow script.

## What the data represent

The source workbooks are literature-compiled data, including manually digitized experimental measurements. The values were transcribed from published results because machine-readable raw datasets were unavailable; they are not raw instrument files.

The thesis plotting workflow then applied a deterministic synthetic perturbation:

- flat plate: a seed-0 multiplicative Gaussian perturbation with standard deviation 5%;
- rigid sphere: a seed-0 centered Beta(2, 8) multiplicative perturbation after leaving the first seven rows unchanged.

The repository therefore preserves two explicit layers:

```text
published literature / digitized measurements
                    ↓
data/source/*.xlsx                     (compiled values, unchanged)
                    ↓ scripts/prepare_data.py
data/thesis_processed/*.csv            (exact inputs used by analysis)
                    ↓ analysis scripts
outputs/*_results.json and figures
```

See [data/README.md](data/README.md) for schemas, row counts, ranges, and known quirks.

## Reproduced results

The flat-plate workflow detects boundaries at approximately `5.05e5` and `8.56e5`. With the archived seed-0 perturbation and historical train/test split, the fitted log-domain relations are approximately:

| Regime | Reproduced relation |
|---|---|
| Laminar | `ln(Nu) = -0.54208 + 0.50337 ln(Re)` |
| Transition | `ln(Nu) = -26.07864 + 2.45452 ln(Re)` |
| Turbulent | `ln(Nu) = -4.43024 + 0.87378 ln(Re)` |

The rigid-sphere workflow reproduces the coefficient/exponent pairs reported in the thesis table:

| Regime | Reproduced relation, with Pr = 0.71 |
|---|---|
| 1 | `Nu = 2 + 0.39536 Re^0.49757 Pr^(1/3)` |
| 2 | `Nu = 2 + 0.40669 Re^0.55318 Pr^(1/3)` |
| 3 | `Nu = 2 + 0.14925 Re^0.66175 Pr^(1/3)` |

The fixed preprocessing seeds, archived analysis inputs, and tested implementation define the numerical reproduction presented in this repository. Tests lock those results against accidental drift.

## Using the datasets in further work

For additional analyses or extensions:

1. Read one of the CSV files in `data/thesis_processed/`.
2. Use `reynolds_number` as the independent variable and `nusselt_number` as the target.
3. Preserve all rows for exact thesis reproduction; do not silently sort or deduplicate.
4. Use `source_row` to map any result back to the corresponding workbook entry.
5. Report any alternative cleaning or sorting as a sensitivity analysis.

Both analysis commands accept `--input PATH` and `--output-dir PATH`, making it straightforward to run variants without modifying repository files.

## Literature provenance stated in the thesis

- J. H. Lienhard, “Heat transfer in flat-plate boundary layers: A correlation for laminar, transitional, and turbulent flow,” *Journal of Heat Transfer* 142(6), 061805 (2020).
- S. Whitaker, “Forced convection heat transfer correlations for flow in pipes, past flat plates, single cylinders, single spheres, and for flow in packed beds and tube bundles,” *AIChE Journal* 18(2), 361–371 (1972).
- The sphere chapter also identifies measurements by Will and Venner as a source of the high-Reynolds-number data. The archived thesis bibliography does not provide a complete machine-verifiable record for that citation, so this repository does not invent missing publication metadata.

## Reproducibility notes

- Source numeric values and original row order are preserved.
- Duplicate and out-of-order Reynolds-number rows are intentional archival features and generate visible notes.
- `scripts/prepare_data.py` is idempotent and never overwrites the source workbooks.
- Regression hyperparameters, cross-validation splits, random states, and the sphere Prandtl number are encoded in tested functions under `src/sm_thesis_code/`.

## License and citation

Code is provided under the MIT License. Literature-derived data retain the attribution and use considerations of their original publications.
