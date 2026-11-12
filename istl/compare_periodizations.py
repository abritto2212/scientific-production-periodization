"""Public wrapper for the three verified fixed-period methods."""
from .v2.conditioned import segment, validate_condition, validate_series

_METHODS = ('derivative_k_provisional', 'piecewise_linear_k', 'dynamic_l2_k')
_INSUFFICIENT = 'Insufficient observations for K phases at this minimum'


def compare_periodizations(years, counts, n_periods, min_period_length):
    """Return one uniform record per method, without ranking or file writes.

    Inputs are validated by the existing study validators. Invalid data or
    parameter types raise ValueError (conversion errors may raise TypeError).
    Valid requests with insufficient observations return three infeasible
    records. Missing feasible derivative peak subsets remain infeasible.
    Cut years denote the first year of the next period; intervals are inclusive.
    All algorithm parameters, including Gaussian smoothing, stay fixed.
    """
    x, y = validate_series(years, counts)
    insufficient = None
    try:
        validate_condition(len(x), n_periods, min_period_length)
    except ValueError as exc:
        if str(exc) != _INSUFFICIENT:
            raise
        insufficient = str(exc)

    results = {}
    for method in _METHODS:
        if insufficient is None:
            result = segment(x, y, method, n_periods, min_period_length)
        else:
            result = dict(algorithm_feasible=False, reason=insufficient,
                          cut_indices=None, cut_years=None, intervals=None,
                          parameters=dict(phases_input=n_periods,
                                          n_cuts_input=n_periods-1,
                                          min_len=min_period_length))
        results[method] = dict(method=method, n_periods=n_periods,
                               min_period_length=min_period_length,
                               executed=insufficient is None, **result)
    return results
