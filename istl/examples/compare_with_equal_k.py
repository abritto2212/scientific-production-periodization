"""Run from repository root: python -m istl.examples.compare_with_equal_k."""
import csv
from pathlib import Path

from istl.compare_periodizations import compare_periodizations
from istl.equal_k import equal_k


def main():
    istl_dir = Path(__file__).resolve().parents[1]
    with (istl_dir / 'v3/data/analysis_series.csv').open(encoding='utf-8-sig', newline='') as source:
        case = [row for row in csv.DictReader(source) if row['case'] == '6']
    years = [int(row['year']) for row in case]
    counts = [int(row['count']) for row in case]
    settings = dict(n_periods=3, min_period_length=2)
    methods = compare_periodizations(years, counts, **settings)
    benchmark = equal_k(years, **settings)
    for result in [*methods.values(), benchmark]:
        print(result['method'], result['cut_years'] if result['algorithm_feasible']
              else result['reason'])


if __name__ == '__main__':
    main()
