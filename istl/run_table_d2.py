"""Regenerate Table D2 from archived method boundaries and verified Equal-K."""
import argparse
from collections import defaultdict
import csv
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean

from .equal_k import equal_k
from .periodization import intervals
from .v2.conditioned import ordered_distance

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'istl/table_d2_results/v1'
BASE_COMMIT = 'f6035039618b6eec500a99bde633aedc1676053d'
CASES = tuple(range(2, 10))
MINIMUM = 2
METHODS = {
    'derivative_k_provisional': 'Derivative-K',
    'piecewise_linear_k': 'Linear-K',
    'dynamic_l2_k': 'Dynp L2-K',
    'equal_k': 'Equal-K',
}
ANALYSIS = 'istl/v3/data/analysis_series.csv'
REFERENCES = 'istl/v3/results/references_and_evidence.json'
ARCHIVE = 'istl/v3/results/results.json'
INPUT_FILES = (ANALYSIS, REFERENCES, ARCHIVE)
CODE_FILES = ('istl/run_table_d2.py', 'istl/equal_k.py',
              'istl/periodization.py', 'istl/v2/conditioned.py')
OUTPUT_FILES = ('case_results.csv', 'case_results.json', 'aggregates.csv', 'aggregates.json', 'table_d2.csv')


def read_inputs(root):
    with (root / ANALYSIS).open(encoding='utf-8-sig', newline='') as source:
        analysis = list(csv.DictReader(source))
    references = json.loads((root / REFERENCES).read_text(encoding='utf-8'))
    archive = json.loads((root / ARCHIVE).read_text(encoding='utf-8'))
    return analysis, references, archive


def index_unique(rows, key):
    indexed = {}
    for row in rows:
        identifier = key(row)
        if identifier in indexed:
            raise ValueError(f'Duplicate record for {identifier}')
        indexed[identifier] = row
    return indexed


def checked_intervals(years, cuts, k, context):
    if cuts is None or len(cuts) != k - 1 or any(cut not in years for cut in cuts):
        raise ValueError(f'{context}: invalid cut years for window or K')
    indices = [cut - years[0] for cut in cuts]
    try:
        return indices, intervals(years, indices, MINIMUM)
    except ValueError as error:
        raise ValueError(f'{context}: {error}') from error


def case_results(analysis, references, archive):
    years_by_case = defaultdict(list)
    for row in analysis:
        case = int(row['case'])
        if case in CASES:
            years_by_case[case].append(int(row['year']))
    refs = index_unique((row for row in references if row['case'] in CASES),
                        lambda row: row['case'])
    archived_methods = tuple(method for method in METHODS if method != 'equal_k')
    archived = index_unique(
        (row for row in archive if row['case'] in CASES and row['min_len'] == MINIMUM
         and row['method'] in archived_methods),
        lambda row: (row['case'], row['method']),
    )
    if refs.keys() != set(CASES) or years_by_case.keys() != set(CASES):
        raise ValueError('Expected one reference and an analytical window for each Table D2 case')
    if archived.keys() != {(case, method) for case in CASES for method in archived_methods}:
        raise ValueError('Expected all three archived methods at minimum two for each Table D2 case')

    results = []
    for case in CASES:
        ref = refs[case]
        start, end = ref['analysis_year_start'], ref['analysis_year_end']
        k, published = ref['phases'], ref['cut_years']
        years = sorted(years_by_case[case])
        if years != list(range(start, end + 1)):
            raise ValueError(f'Case {case}: incomplete or inconsistent analytical window')
        _, reference_intervals = checked_intervals(years, published, k, f'Case {case} reference')
        if reference_intervals != ref['published_intervals']:
            raise ValueError(f'Case {case}: inconsistent published intervals')

        equal = equal_k(years, k, MINIMUM)
        for method, label in METHODS.items():
            context = f'Case {case} {label}'
            origin = 'verified_equal_k_implementation' if method == 'equal_k' else 'archived_boundaries'
            record = equal if method == 'equal_k' else archived[case, method]
            if method != 'equal_k' and (
                record['window'] != [start, end] or record['n_years'] != len(years)
                or record['phases_input'] != k or record['reference_cut_years'] != published
                or record['reference_satisfies_minimum'] is not True
                or record['eligible'] is not True
            ):
                raise ValueError(f'{context}: archive differs from the window, K or reference eligibility')
            if record['algorithm_feasible'] is not True:
                raise ValueError(f'{context}: no feasible partition')
            predicted = record['cut_years']
            indices, periods = checked_intervals(years, predicted, k, context)
            if indices != record['cut_indices'] or periods != record['intervals']:
                raise ValueError(f'{context}: cuts, indices and intervals disagree')
            agreement = ordered_distance(predicted, published)
            results.append(dict(
                case=case, method=method, method_label=label, boundary_origin=origin,
                analysis_year_start=start, analysis_year_end=end, n_years=len(years),
                k=k, min_period_length=MINIMUM, algorithm_feasible=True,
                reference_satisfies_minimum=True, reference_cut_years=published,
                estimated_cut_years=predicted, **agreement,
            ))
    return results


def aggregate(results):
    summaries = []
    for method, label in METHODS.items():
        scores = index_unique((row for row in results if row['method'] == method),
                              lambda row: row['case'])
        if scores.keys() != set(CASES):
            raise ValueError(f'{label}: expected exactly the eight Table D2 cases')
        ordered = [scores[case] for case in CASES]
        boundaries = sum(row['n_cuts'] for row in ordered)
        if boundaries != 15:
            raise ValueError(f'{label}: expected fifteen reference boundaries, got {boundaries}')
        summaries.append(dict(
            method=method, method_label=label, cases=list(CASES), n_cases=len(CASES),
            min_period_length=MINIMUM, n_boundaries=boundaries,
            macro_mae_years=mean(row['mae_years'] for row in ordered),
            exact_matches=sum(row['exact_count'] for row in ordered),
        ))
    return summaries


def write_rows(output_dir, name, rows):
    write_json(output_dir / f'{name}.json', rows)
    with (output_dir / f'{name}.csv').open('w', encoding='utf-8', newline='') as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows({key: json.dumps(value) if isinstance(value, (list, bool)) else value
                          for key, value in row.items()} for row in rows)


def write_json(path, value):
    path.write_bytes((json.dumps(value, indent=2) + '\n').encode('utf-8'))


def file_sha256(path):
    return sha256(path.read_bytes()).hexdigest()


def reproduce(output_dir=OUTPUT, root=ROOT):
    rows = case_results(*read_inputs(root))
    summaries = aggregate(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_rows(output_dir, 'case_results', rows)
    write_rows(output_dir, 'aggregates', summaries)
    with (output_dir / 'table_d2.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(['Case', *METHODS.values()])
        lookup = {(r['case'], r['method']): r['mae_years'] for r in rows}
        for case in CASES:
            writer.writerow([case, *[f'{lookup[case, m]:.2f}' for m in METHODS]])
    write_json(output_dir / 'provenance.json', dict(
        base_commit=BASE_COMMIT, branch='revision/istl', cases=list(CASES),
        min_period_length=MINIMUM,
        manuscript='https://docs.google.com/document/d/1_nLm1OJWoDa7ZdUyaapyqc8u1h8QA3gIYhCWivcoy04/edit',
        reproduction_command='python -m istl.run_table_d2',
        scope='Archived boundaries for Derivative-K, Linear-K and Dynp L2-K. Equal-K is computed.',
        boundary_convention='First year of the next period, matched in chronological order.',
        macro_mae_definition='Unweighted arithmetic mean of the eight case MAEs.',
        input_sha256={path: file_sha256(root / path) for path in INPUT_FILES},
        code_sha256={path: file_sha256(root / path) for path in CODE_FILES},
        output_sha256={path: file_sha256(output_dir / path) for path in OUTPUT_FILES},
    ))
    return summaries


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=OUTPUT)
    for row in reproduce(parser.parse_args().output_dir):
        print(f"{row['method_label']}: macro MAE {row['macro_mae_years']:.2f} years, "
              f"{row['exact_matches']}/{row['n_boundaries']} exact matches, {row['n_cases']} cases")
