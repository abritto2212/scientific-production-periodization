"""Public equal-duration reference partition for annual series."""
from itertools import accumulate

import numpy as np

from .periodization import intervals, validate_series
from .v2.conditioned import InsufficientObservations, validate_condition


def equal_k(years, n_periods, min_period_length):
    """Split consecutive years into K periods, allocating extra years first.

    K must be a positive integer and the minimum must be an integer >= 2.
    Invalid inputs raise a validation error. Valid requests with too few years
    return an infeasible record. Intervals are inclusive, and each cut is the
    first year of the next period.
    """
    years = np.asarray(years)
    # The shared series validator requires a second vector. These placeholders
    # are independent of publication counts and are never used in the partition.
    x, _ = validate_series(years, np.zeros(years.shape), min_years=1)
    try:
        validate_condition(len(x), n_periods, min_period_length)
    except InsufficientObservations as exc:
        reason = str(exc)
    else:
        reason = None

    n_periods, min_period_length = int(n_periods), int(min_period_length)
    q, r = divmod(len(x), n_periods)
    parameters = dict(n_years=len(x), n_periods=n_periods,
                      min_period_length=min_period_length, q=q, r=r)
    if reason is not None:
        return dict(method='equal_k', algorithm_feasible=False, reason=reason,
                    cut_indices=None, cut_years=None, intervals=None,
                    parameters=parameters)

    lengths = [q + 1] * r + [q] * (n_periods - r)
    cuts = list(accumulate(lengths[:-1]))
    return dict(method='equal_k', algorithm_feasible=True, reason=None,
                cut_indices=cuts, cut_years=[int(x[i]) for i in cuts],
                intervals=intervals(x, cuts, min_period_length), parameters=parameters)
