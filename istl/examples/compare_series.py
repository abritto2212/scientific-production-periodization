"""Run from repository root: python -m istl.examples.compare_series."""
from pathlib import Path
from pprint import pprint
from istl.compare_periodizations import compare_periodizations
from istl.read_data import load_cases


def main():
    # Reuse the existing reader; the public function receives arrays, not files.
    root = Path(__file__).resolve().parents[2]
    sheet, years, counts, _ = load_cases(root/'data_articles/data_articles.xlsx')[4]
    print(sheet)
    pprint(compare_periodizations(years, counts, n_periods=3, min_period_length=2))


if __name__ == '__main__':
    main()
