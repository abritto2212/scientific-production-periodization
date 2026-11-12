"""Provisional K-conditioned comparison. V1 implementations remain untouched.

K = published number of phases, not a parameter selected by agreement.
The derivative-K subset rule is an explicit provisional adaptation.
"""
import sys
from pathlib import Path
from itertools import combinations
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from periodization import (validate_series, derivative_candidates, linear_sse,
                           intervals, Dynp)


class InsufficientObservations(ValueError):
    """A valid period count and minimum exceed the available observations."""


def validate_condition(n, phases, min_len):
    for name, value, lower in [('phases', phases, 1), ('min_len', min_len, 2)]:
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < lower:
            raise ValueError(f'{name} must be an integer >= {lower}')
    if n < int(phases) * int(min_len):
        raise InsufficientObservations('Insufficient observations for K phases at this minimum')


def admissible_subsets(candidates, n, n_cuts, min_len):
    for c in combinations(sorted(candidates), n_cuts):
        if min(np.diff([0, *c, n])) >= min_len:
            yield c


def segment(years, values, method, phases, min_len):
    x, y = validate_series(years, values)
    validate_condition(len(x), phases, min_len)
    n_cuts = phases - 1
    params = dict(phases_input=phases, n_cuts_input=n_cuts, min_len=min_len,
                  data='original annual counts, float64; no normalization')
    if method == 'piecewise_linear_k':
        best_cuts, best_score = None, np.inf
        for c in admissible_subsets(range(min_len, len(x)-min_len+1), len(x), n_cuts, min_len):
            edges = [0, *c, len(x)]
            score = sum(linear_sse(x[a:b], y[a:b]) for a,b in zip(edges[:-1],edges[1:]))
            if score < best_score:
                best_cuts, best_score = list(c), score
        cuts = best_cuts
        params.update(objective='independent linear SSE', sse=best_score,
                      continuity_constraint=False, tie_rule='first lexicographic combination')
    elif method == 'dynamic_l2_k':
        model = Dynp(model='l2', min_size=min_len, jump=1).fit(y)
        cuts = model.predict(n_bkps=n_cuts)[:-1]
        params.update(objective='within-segment mean SSE', jump=model.jump,
                      min_size=model.min_size, model='l2',
                      backend='frozen ruptures v1.1.10 Dynp/CostL2 subset',
                      sse=float(model.cost.sum_of_costs([*cuts,len(x)])))
    elif method == 'derivative_k_provisional':
        candidates, smooth, d1, d2, threshold = derivative_candidates(y, sigma=2.0)
        best_cuts, best_score = None, -np.inf
        feasible_subsets = 0
        for c in admissible_subsets(candidates, len(x), n_cuts, min_len):
            feasible_subsets += 1
            score = float(sum(abs(d2[p]) for p in c))
            if score > best_score:
                best_cuts, best_score = list(c), score
        cuts = best_cuts
        params.update(sigma=2.0, mode='reflect', truncate=4.0, gradient_edge_order=1,
            sampling_years=1, height_rule='std(d2), ddof=0', height=threshold,
            candidate_indices=candidates, candidate_years=[int(x[p]) for p in candidates],
            candidate_heights=[float(abs(d2[p])) for p in candidates],
            feasible_subset_count=feasible_subsets,
            adaptation='provisional fixed-K subset of unchanged thresholded peaks',
            objective='maximize sum(abs(d2)) over feasible K-1 peak subsets',
            tie_rule='first lexicographic combination',
            selected_strength=None if cuts is None else best_score)
    else:
        raise ValueError('Unknown method')
    if cuts is None:
        return dict(algorithm_feasible=False, reason='no feasible K-1 subset of original peaks',
                    parameters=params, cut_indices=None, cut_years=None, intervals=None)
    return dict(algorithm_feasible=True, reason=None, parameters=params,
                cut_indices=cuts, cut_years=[int(x[p]) for p in cuts],
                intervals=intervals(x,cuts,min_len=min_len))


def native_derivative(years, values, min_len):
    """Automatic count, original greedy length rule; NEVER a fixed-K result."""
    x,y = validate_series(years, values)
    validate_condition(len(x),1,min_len)
    candidates,s,d1,d2,h = derivative_candidates(y)
    cuts=[]
    for p in sorted(candidates,key=lambda i:(-abs(d2[i]),i)):
        trial=sorted([*cuts,p])
        if min(np.diff([0,*trial,len(x)]))>=min_len:
            cuts=trial
    return dict(cut_years=[int(x[i]) for i in cuts], n_phases=len(cuts)+1,
                candidate_years=[int(x[i]) for i in candidates],
                min_len=min_len, sigma=2.0, height=h,
                intervals=intervals(x,cuts,min_len),
                phases_input=None, interpretation='automatic-count diagnostic, no concordance score')


def ordered_distance(predicted, reference):
    """One-to-one chronological matching; no nearest-neighbor reuse."""
    for values in (predicted,reference):
        if list(values)!=sorted(set(values)):
            raise ValueError('Expected ordered, unique cut years')
    if len(predicted)!=len(reference):
        raise ValueError('Cannot score unequal cut counts in the K-conditioned protocol')
    signed=[int(p-r) for p,r in zip(predicted,reference)]
    absolute=list(map(abs,signed))
    return dict(n_cuts=len(reference),signed_errors_years=signed,absolute_errors_years=absolute,
                mae_years=None if not absolute else float(np.mean(absolute)),
                exact_count=sum(e==0 for e in absolute),
                exact_rate=None if not absolute else sum(e==0 for e in absolute)/len(absolute))
