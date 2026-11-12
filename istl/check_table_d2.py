"""Compare regenerated D2 with a dated native-document table snapshot."""
import json
from pathlib import Path
from .run_table_d2 import ROOT, OUTPUT, METHODS, reproduce, file_sha256, write_json

SNAPSHOT = ROOT / 'istl/r17_manuscript_tables.json'

def matrix(table):
    return [[next(c['text'] for c in table['cells']
                  if c['rowNumber'] == r and c['columnNumber'] == col)
             for col in range(1, table['columnCount'] + 1)]
            for r in range(1, table['rowCount'] + 1)]

def check(output_dir=OUTPUT):
    summaries = reproduce(output_dir)
    rows = json.loads((output_dir / 'case_results.json').read_text())
    snap = json.loads(SNAPSHOT.read_text())
    tables = {t['tableNumber']: matrix(t) for t in snap['tables']}
    d2 = tables[12]
    expected_header = ['Case', *METHODS.values()]
    if d2[0] != expected_header or [int(r[0]) for r in d2[1:]] != list(range(2,10)):
        raise ValueError('Snapshot D2 headers or cases do not match')
    index = {(r['case'], r['method_label']): r for r in rows}
    comparisons = []
    for row in d2[1:]:
        for method, value in zip(d2[0][1:], row[1:], strict=True):
            actual = index[int(row[0]), method]['mae_years']
            comparisons.append(dict(case=int(row[0]), method=method,
                manuscript=float(value), calculated=actual, matches=actual == float(value)))
    if not all(r['matches'] for r in comparisons):
        raise ValueError('Table D2 mismatch')
    # Cross-check each original algorithm boundary against manuscript Table 3.
    for row in tables[3][1:]:
        case = int(row[0])
        if case == 1:
            continue
        refs = [int(x.strip()) for x in row[1].split(',')]
        for method, cuts in zip(list(METHODS.values())[:3], row[2:], strict=True):
            r = index[case, method]
            assert r['reference_cut_years'] == refs
            assert r['estimated_cut_years'] == [int(x.strip()) for x in cuts.split(',')]
    # Check Equal-K cuts and errors against Table D1 for the eight D2 cases.
    for row in tables[11][1:]:
        case = int(row[0])
        if case == 1:
            continue
        r = index[case, 'Equal-K']
        assert r['estimated_cut_years'] == [int(x.strip()) for x in row[4].split(',')]
        assert r['mae_years'] == float(row[5])
    # Independently recompute all metrics, without the shared distance function.
    for r in rows:
        errors = [abs(a-b) for a,b in zip(r['estimated_cut_years'],r['reference_cut_years'],strict=True)]
        assert r['mae_years'] == sum(errors)/len(errors)
        assert r['exact_count'] == sum(e == 0 for e in errors)
    for a, expected in zip(summaries, [(3.6875,3),(3.1875,3),(4.3125,1),(1.75,2)],strict=True):
        assert (a['macro_mae_years'],a['exact_matches']) == expected
        assert (a['n_cases'],a['n_boundaries']) == (8,15)
    result = dict(document_id=snap['documentId'], revision_id=snap['revisionId'],
        snapshot_sha256=file_sha256(SNAPSHOT), snapshot_date='2026-11-12',
        cells_checked=len(comparisons), mismatches=0, comparisons=comparisons,
        table_3_boundary_comparisons=24, table_d1_equal_k_comparisons=8,
        scope='Metrics regenerated from archived boundaries; original algorithms not rerun.')
    write_json(output_dir / 'manuscript_comparison.json', result)
    return result

if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
