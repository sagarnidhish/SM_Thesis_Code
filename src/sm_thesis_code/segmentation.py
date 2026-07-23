"""Regime segmentation matching the thesis figure-generation scripts."""

import warnings

import numpy as np
import ruptures as rpt
from scipy.signal import find_peaks


def flat_plate_segments(reynolds: np.ndarray, nusselt: np.ndarray):
    log_re = np.log(reynolds)
    log_nu = np.log(nusselt)
    # The archived table contains one repeated Reynolds number. The historical
    # NumPy calculation yields NaN locally but remains deterministic.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        curvature = np.gradient(np.gradient(log_nu, log_re), log_re)
    peaks, _ = find_peaks(np.abs(curvature), distance=10)
    ranked = peaks[np.argsort(np.abs(curvature[peaks]))[::-1]]
    if len(ranked) < 2:
        raise ValueError("At least two curvature peaks are required")
    top = np.sort(ranked[:2])
    windows = [(max(int(p) - 2, 0), min(int(p) + 2, len(reynolds) - 1)) for p in top]
    first, second = windows[0][0], windows[1][1]
    return [(0, first), (first, second), (second, len(reynolds))], [first, second]


def sphere_segments(reynolds: np.ndarray, nusselt: np.ndarray):
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.divide(np.gradient(np.log(nusselt)), np.gradient(np.log(reynolds)))
    raw[~np.isfinite(raw)] = 0.0
    n = len(raw)
    window = max(3, int(np.ceil(n * 0.02)))
    smooth = np.convolve(raw, np.ones(window) / window, mode="same")
    candidates, scores = [], []
    for k in range(1, min(6, max(1, n // 10)) + 1):
        algorithm = rpt.Dynp(model="l2", min_size=3, jump=1).fit(smooth.reshape(-1, 1))
        try:
            breakpoints = algorithm.predict(n_bkps=k + 1)
        except Exception:
            continue
        previous, residual = 0, 0.0
        for end in breakpoints:
            segment = smooth[previous:end]
            if len(segment):
                residual += float(((segment - segment.mean()) ** 2).sum())
            previous = end
        sigma2 = residual / n
        scores.append(n * np.log(sigma2 + 1e-12) + (len(breakpoints) - 1) * np.log(n))
        candidates.append(breakpoints)
    if not candidates:
        raise ValueError("Sphere segmentation failed")
    breaks = sorted({b for b in candidates[int(np.argmin(scores))] if 0 < b < n})
    minimum_gap = max(2, int(0.03 * n))
    merged, index = [], 0
    while index < len(breaks):
        if index + 1 < len(breaks) and breaks[index + 1] - breaks[index] < minimum_gap:
            merged.append(int(round((breaks[index] + breaks[index + 1]) / 2)))
            index += 2
        else:
            merged.append(breaks[index])
            index += 1
    width = max(1, int(0.01 * n))
    zones = [(max(0, b - width), min(n, b + width)) for b in sorted(set(merged))]
    regions, current = [], 0
    for start, end in zones:
        if start - current >= 3:
            regions.append((current, start))
        current = end
    if n - current >= 3:
        regions.append((current, n))
    return regions, zones
