"""Validated annual series and the three ISTL diagnostic methods."""
from itertools import combinations
from pathlib import Path
import sys
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

# Frozen upstream Dynp/CostL2 subset, not a replacement estimator.
sys.path.insert(0, str(Path(__file__).parent / 'vendor'))
from ruptures import Dynp


def validate_series(years, values, *, min_years=3):
    x, y = np.asarray(years, dtype=float), np.asarray(values, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y) or len(x) < min_years:
        raise ValueError(f'Expected equally sized one-dimensional series, at least {min_years} years')
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Missing or nonfinite year/count; no zero imputation allowed')
    if (x != np.floor(x)).any() or (y != np.floor(y)).any() or (y < 0).any():
        raise ValueError('Years and nonnegative counts must be integers')
    if not (np.diff(x) == 1).all():
        raise ValueError('Years must be ordered, unique, consecutive; resolve gaps explicitly')
    return x.astype(int), y.astype(float)


def check_params(n, n_breaks, min_len):
    if isinstance(min_len, bool) or not isinstance(min_len, (int, np.integer)) or min_len < 3:
        raise ValueError('min_len must be an integer >= 3')
    if isinstance(n_breaks, bool) or not isinstance(n_breaks, (int, np.integer)) or n_breaks < 0:
        raise ValueError('n_breaks must be a nonnegative integer')
    if n < (n_breaks + 1) * min_len:
        raise ValueError('Insufficient years for the requested segmentation')


def intervals(years, cuts, min_len=3):
    if any(not isinstance(c, (int, np.integer)) for c in cuts):
        raise ValueError('Cuts must be integer split indices')
    if list(cuts) != sorted(set(cuts)) or any(c <= 0 or c >= len(years) for c in cuts):
        raise ValueError('Cuts must be ordered unique internal split indices')
    edges = [0, *cuts, len(years)]
    if min(np.diff(edges)) < min_len:
        raise ValueError('Segment shorter than min_len')
    return [dict(start=int(years[a]), end=int(years[b-1]), length=b-a)
            for a, b in zip(edges[:-1], edges[1:])]


def derivative_candidates(values, sigma=2.0, legacy_integer=False):
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError('sigma must be positive and finite')
    y = np.asarray(values, dtype=int if legacy_integer else float)
    smooth = gaussian_filter1d(y, sigma=sigma, mode='reflect', truncate=4.0)
    d1 = np.gradient(smooth, 1.0, edge_order=1)
    d2 = np.gradient(d1, 1.0, edge_order=1)
    threshold = float(np.std(d2, ddof=0))
    peaks, _ = find_peaks(np.abs(d2), height=threshold)
    return peaks.tolist(), smooth, d1, d2, threshold


def derivatives(years, values, min_len=3, sigma=2.0):
    x, y = validate_series(years, values)
    check_params(len(x), 0, min_len)
    peaks, smooth, d1, d2, threshold = derivative_candidates(y, sigma)
    # Explicit length constraint, not part of historical peak detection.
    # Retain strongest admissible peaks; ties prefer earlier year.
    selected, rejected = [], []
    for p in sorted(peaks, key=lambda p: (-abs(d2[p]), p)):
        proposal = sorted([*selected, p])
        if min(np.diff([0, *proposal, len(x)])) >= min_len:
            selected = proposal
        else:
            rejected.append(p)
    return selected, dict(sigma=sigma, mode='reflect', truncate=4.0,
        gradient_edge_order=1, sampling_years=1, height_rule='std(d2), ddof=0',
        height=threshold, min_len=min_len, n_breaks_input=None,
        candidate_indices=peaks, rejected_indices=sorted(rejected),
        length_rule='descending absolute d2, earlier index breaks ties'), smooth


def linear_sse(x, y):
    design = np.column_stack([np.ones(len(x)), x - x[0]])
    coef = np.linalg.lstsq(design, y, rcond=None)[0]
    return float(np.sum((y - design @ coef)**2))


def piecewise(years, values, n_breaks=2, min_len=3, legacy=False):
    x, y = validate_series(years, values)
    check_params(len(x), n_breaks, min_len)
    best, best_sse = None, np.inf
    for cuts in combinations(range(min_len, len(x)-min_len+1), n_breaks):
        edges = [0, *cuts, len(x)]
        if not legacy and min(np.diff(edges)) < min_len:
            continue
        score = sum(linear_sse(x[a:b], y[a:b]) for a,b in zip(edges[:-1], edges[1:]))
        if score < best_sse:
            best, best_sse = list(cuts), score
    return best, dict(n_breaks_input=n_breaks, min_len=min_len, objective='independent linear SSE',
                     continuity_constraint=False, sse=best_sse, tie_rule='first lexicographic combination')


def dynamic_l2(years, values, n_breaks=2, min_len=3, jump=1):
    x, y = validate_series(years, values)
    check_params(len(x), n_breaks, min_len)
    if isinstance(jump, bool) or not isinstance(jump, (int, np.integer)) or jump < 1:
        raise ValueError('jump must be a positive integer')
    model = Dynp(model='l2', min_size=min_len, jump=jump).fit(y)
    cuts = model.predict(n_bkps=n_breaks)[:-1]  # terminal n is not a change point
    intervals(x, cuts, min_len)
    return cuts, dict(n_breaks_input=n_breaks, model='l2', min_size=model.min_size,
                     jump=model.jump, sse=float(model.cost.sum_of_costs([*cuts, len(y)])),
                     backend='ruptures v1.1.10, frozen Dynp/CostL2 source subset')
