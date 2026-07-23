"""Consistent plotting for the two thesis case studies."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_analysis(frame: pd.DataFrame, result: dict, destination: str | Path) -> None:
    destination = Path(destination)
    reynolds = frame["reynolds_number"].to_numpy(dtype=float)
    nusselt = frame["nusselt_number"].to_numpy(dtype=float)
    fig, axis = plt.subplots(figsize=(9.2, 6.0))
    axis.loglog(reynolds, nusselt, "o", color="#355C7D", markersize=4, alpha=0.68, label="Thesis-processed data")
    colors = ["#2A9D8F", "#E9C46A", "#E76F51"]
    prandtl_factor = result.get("prandtl_number", 1.0) ** (1 / 3)
    for color, region in zip(colors, result["regions"]):
        start, end = region["start_index"], region["end_index_exclusive"]
        x = reynolds[start:end]
        if result["case"] == "sphere":
            y = 2.0 + prandtl_factor * region["coefficient"] * x ** region["exponent"]
            equation = rf"$Nu=2+{region['coefficient']:.3f}Re^{{{region['exponent']:.3f}}}Pr^{{1/3}}$"
        else:
            y = region["coefficient"] * x ** region["exponent"]
            equation = rf"$Nu={region['coefficient']:.3g}Re^{{{region['exponent']:.3f}}}$"
        order = np.argsort(x)
        axis.loglog(x[order], y[order], "--", color=color, linewidth=2.2, label=f"{region['name']}: {equation}")
    if result["case"] == "flat_plate":
        for boundary in result["boundaries"]:
            axis.axvline(boundary, color="#555555", linestyle=":", linewidth=1.2)
    axis.set_xlabel("Reynolds number, Re")
    axis.set_ylabel("Nusselt number, Nu")
    axis.set_title("Flat-plate thesis reproduction" if result["case"] == "flat_plate" else "Rigid-sphere thesis reproduction")
    axis.grid(True, which="both", linestyle=":", linewidth=0.6, alpha=0.55)
    axis.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(destination, dpi=220)
    plt.close(fig)
