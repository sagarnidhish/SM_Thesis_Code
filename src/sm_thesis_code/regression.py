"""Sparse log-domain fits used in the thesis case studies."""

import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

from .segmentation import flat_plate_segments, sphere_segments


PARAMETERS = {"alpha": [1e-6, 1e-4, 1e-2, 1e-1], "l1_ratio": [1.0]}


def _arrays(frame: pd.DataFrame):
    required = {"reynolds_number", "nusselt_number"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")
    reynolds = frame["reynolds_number"].to_numpy(dtype=float)
    nusselt = frame["nusselt_number"].to_numpy(dtype=float)
    if len(frame) < 10 or not np.isfinite(reynolds).all() or not np.isfinite(nusselt).all():
        raise ValueError("At least ten finite observations are required")
    if (reynolds <= 0).any() or (nusselt <= 0).any():
        raise ValueError("Reynolds and Nusselt values must be positive")
    return reynolds, nusselt


def _elastic_fit(x: np.ndarray, y: np.ndarray, one_standard_error: bool):
    scaler = StandardScaler()
    scaled = scaler.fit_transform(x.reshape(-1, 1))
    base = ElasticNet(random_state=0, max_iter=10000, tol=1e-4)
    grid = GridSearchCV(base, PARAMETERS, cv=5, scoring="neg_mean_squared_error", error_score="raise")
    if one_standard_error:
        outer = KFold(n_splits=5, shuffle=True, random_state=42)
        cross_val_score(grid, scaled, y.reshape(-1, 1), cv=outer, scoring="neg_mean_squared_error")
        grid.fit(scaled, y.reshape(-1, 1))
        results = grid.cv_results_
        mean_mse = -results["mean_test_score"]
        best = grid.best_index_
        threshold = mean_mse[best] + results["std_test_score"][best]
        candidates = []
        for index, mse in enumerate(mean_mse):
            if mse <= threshold:
                model = ElasticNet(random_state=0, max_iter=10000, tol=1e-4, **results["params"][index])
                model.fit(scaled, y.reshape(-1, 1))
                candidates.append((np.count_nonzero(model.coef_), mse, results["params"][index]))
        parameters = min(candidates, key=lambda item: (item[0], item[1]))[2]
    else:
        grid.fit(scaled, y.reshape(-1, 1))
        parameters = grid.best_params_
    model = ElasticNet(random_state=0, max_iter=10000, tol=1e-4, **parameters)
    model.fit(scaled, y.reshape(-1, 1))
    exponent = float(model.coef_.ravel()[0] / scaler.scale_[0])
    intercept = float(np.asarray(model.intercept_).ravel()[0] - exponent * scaler.mean_[0])
    return intercept, exponent


def analyze_flat_plate(frame: pd.DataFrame) -> dict:
    reynolds, nusselt = _arrays(frame)
    spans, boundary_indices = flat_plate_segments(reynolds, nusselt)
    names = ["laminar", "transition", "turbulent"]
    regions = []
    for name, (start, end) in zip(names, spans):
        training_x, _, training_y, _ = train_test_split(
            np.log(reynolds[start:end]),
            np.log(nusselt[start:end]),
            test_size=0.2,
            random_state=42,
        )
        intercept, exponent = _elastic_fit(training_x, training_y, True)
        regions.append(
            {
                "name": name,
                "start_index": start,
                "end_index_exclusive": end,
                "re_min": float(reynolds[start]),
                "re_max": float(reynolds[end - 1]),
                "intercept": intercept,
                "coefficient": float(np.exp(intercept)),
                "exponent": exponent,
            }
        )
    return {"case": "flat_plate", "boundaries": [float(reynolds[i]) for i in boundary_indices], "regions": regions}


def analyze_sphere(frame: pd.DataFrame) -> dict:
    reynolds, nusselt = _arrays(frame)
    spans, zones = sphere_segments(reynolds, nusselt)
    prandtl_factor = 0.71 ** (1 / 3)
    regions = []
    fitted_index = 0
    for start, end in spans:
        if end - start < 14:
            continue
        fitted_index += 1
        target = np.log(np.maximum((nusselt[start:end] - 2.0) / prandtl_factor, 1e-12))
        intercept, exponent = _elastic_fit(np.log(reynolds[start:end]), target, False)
        regions.append(
            {
                "name": f"region_{fitted_index}",
                "start_index": start,
                "end_index_exclusive": end,
                "re_min": float(reynolds[start]),
                "re_max": float(reynolds[end - 1]),
                "intercept": intercept,
                "coefficient": float(np.exp(intercept)),
                "exponent": exponent,
            }
        )
    return {"case": "sphere", "prandtl_number": 0.71, "transition_zones": zones, "regions": regions}
