"""Reproduce the Equal-K results from the integrated delivery 03."""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
from statistics import mean

from .equal_k import equal_k
from .periodization import intervals
from .v2.conditioned import ordered_distance

HERE = Path(__file__).resolve().parent
DELIVERY = HERE / 'v3'
OUTPUT = HERE / 'equal_k_results' / 'v1'
MINIMUM = 2
BASE_COMMIT = 'b8bdb75f85a1155c2aedfa9788ea71ab831904d0'
CASE_SETS = {
    'primary_common_set': list(range(2, 10)),
    'four_case_common_subset': [4, 7, 8, 9],
    'excluding_overlapping_authorship': [4, 6, 7, 8, 9],
}


def load_inputs():
    years_by_case = defaultdict(list)
    with (DELIVERY / 'data/analysis_series.csv').open(encoding='utf-8-sig', newline='') as source:
        for row in csv.DictReader(source):
            years_by_case[int(row['case'])].append(int(row['year']))

    path = DELIVERY / 'results/references_and_evidence.json'
    references = {}
    for row in json.loads(path.read_text(encoding='utf-8')):
        case = row['case']
        if case in references:
            raise ValueError(f'Duplicate reference case {case}')
        references[case] = row
    if years_by_case.keys() != references.keys() or set(references) != set(range(1, 11)):
        raise ValueError('Expected matching series and reference IDs for cases 1–10')
    return years_by_case, references


def case_results(years_by_case, references):
    results = {}
    for case, reference in sorted(references.items()):
        years = years_by_case[case]
        start, end = reference['analysis_year_start'], reference['analysis_year_end']
        if years != list(range(start, end + 1)):
            raise ValueError(f'Case {case}: series does not match the reference analysis window')
        k, published = reference['phases'], reference['cut_years']
        row = dict(case=case, analysis_year_start=start, analysis_year_end=end,
                   n_years=len(years), n_periods=k, min_period_length=MINIMUM,
                   reference_cut_years=published)
        if case == 10:
            if k is not None or published is not None:
                raise ValueError('Case 10 is expected to lack a complete published partition')
            results[case] = dict(**row, scope='excluded_no_complete_reference',
                                 equal_k=None, agreement=None)
            continue

        partition = equal_k(years, k, MINIMUM)
        intervals(years, [years.index(cut) for cut in published], MINIMUM)
        agreement = (ordered_distance(partition['cut_years'], published)
                     if partition['algorithm_feasible'] else None)
        scope = 'descriptive_only' if case == 1 else 'primary_common_set'
        results[case] = dict(**row, scope=scope, equal_k=partition, agreement=agreement)
    return results


def summaries(results):
    output = []
    for name, cases in CASE_SETS.items():
        scores = [results[case]['agreement'] for case in cases]
        if any(score is None or score['mae_years'] is None for score in scores):
            raise ValueError(f'Incomplete Equal-K agreement for {name}')
        output.append(dict(set=name, cases=cases, min_period_length=MINIMUM,
                           n_cases=len(cases),
                           n_boundaries=sum(score['n_cuts'] for score in scores),
                           macro_mae_years=mean(score['mae_years'] for score in scores),
                           exact_matches=sum(score['exact_count'] for score in scores)))
    return output


def write_csv(path, header, rows):
    with path.open('w', encoding='utf-8', newline='') as target:
        writer = csv.writer(target, lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def write_json(path, payload):
    path.write_bytes((json.dumps(payload, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))


def format_cuts(cuts):
    return ', '.join(map(str, cuts))


def reproduce(output_dir=OUTPUT):
    cases = case_results(*load_inputs())
    aggregates = summaries(cases)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / 'case_results.json', list(cases.values()))
    write_json(output_dir / 'aggregates.json', dict(
        base_commit=BASE_COMMIT,
        method='equal_k',
        macro_mae_definition='arithmetic mean of case-level MAEs',
        boundary_convention='first year of the next period',
        input_files=['istl/v3/data/analysis_series.csv',
                     'istl/v3/results/references_and_evidence.json'],
        sets=aggregates,
    ))
    write_csv(output_dir / 'table_d1.csv',
              ['case', 'window', 'k', 'reference_cuts', 'equal_k_cuts', 'case_mae_years'],
              [(case, f"{row['analysis_year_start']}–{row['analysis_year_end']}",
                row['n_periods'], format_cuts(row['reference_cut_years']),
                format_cuts(row['equal_k']['cut_years']), f"{row['agreement']['mae_years']:.2f}")
               for case, row in cases.items() if row['agreement'] is not None])
    write_csv(output_dir / 'table_d2_equal_k.csv', ['case', 'equal_k_mae_years'],
              [(case, f"{cases[case]['agreement']['mae_years']:.2f}")
               for case in CASE_SETS['primary_common_set']])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=OUTPUT)
    reproduce(parser.parse_args().output_dir)
