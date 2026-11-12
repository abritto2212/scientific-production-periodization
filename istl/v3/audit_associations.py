"""Read-only association audit; writes only to an explicit output directory."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
import numpy as np
import run
import prepare_data
from associations import series_by_case, drive_by_case, join_inputs, paired_series

def compare_records(actual, expected):
    import math
    differences = []
    allowed = {'candidate_heights', 'height', 'selected_strength', 'sse'}

    def check(a, b, path='records', tolerant=False):
        if isinstance(a, dict) and isinstance(b, dict):
            if a.keys() != b.keys():
                raise AssertionError(path)
            for key in a:
                permit = path.endswith('.parameters') and key in allowed
                check(a[key], b[key], path + '.' + key, permit)
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                raise AssertionError(path)
            for i, (x, y) in enumerate(zip(a, b)):
                check(x, y, f'{path}[{i}]', tolerant)
        elif a != b:
            if not (tolerant and isinstance(a, float) and isinstance(b, float)
                    and math.isfinite(a) and math.isfinite(b)
                    and math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)):
                raise AssertionError((path, a, b))
            differences.append(dict(path=path, recalculated=a, archived=b))

    check(actual, expected)
    return differences

def audit(output):
    output.mkdir(parents=True,exist_ok=True)
    full,analysis,refs=run.inputs()
    sources=series_by_case(full); analytical=series_by_case(analysis)
    old=json.loads((run.HERE.parent/'v2/results/references_normalized.json').read_text(encoding="utf-8"))
    evidence=json.loads((run.HERE.parent/'integration/evidence_status_v0.2.json').read_text(encoding="utf-8"))['cases']
    sections=drive_by_case((run.HERE/'sources/drive_snapshot.txt').read_text(encoding="utf-8").strip().split('\f'))
    report=[]
    for ref in refs:
        case=ref['case'];sheet,x,y,_=sources[case];_,ax,ay,_=analytical[case]
        drive=list(csv.DictReader(io.StringIO(sections[case].strip())))
        assert [(int(r['Year']),int(r['Total_Publications'])) for r in drive] == list(zip(x.astype(int),y.astype(int)))
        for name,xx,yy in [('source_series.csv',x,y),('analysis_series.csv',ax,ay)]:
            with (run.HERE/'data'/name).open(encoding="utf-8", newline="") as f: csvrows=[r for r in csv.DictReader(f) if int(r['case'])==case]
            assert all(r['sheet']==sheet for r in csvrows)
            assert [(int(r['year']),int(r['count'])) for r in csvrows]==list(zip(xx.astype(int),yy.astype(int)))
        assert len(ax)==len(set(ax)) and np.all(np.diff(ax)==1)
        report.append(dict(case=case,sheet=sheet,source=ref['source'],
            source_window=[int(x[0]),int(x[-1])],source_total=int(y.sum()),
            analysis_window=[int(ax[0]),int(ax[-1])],analysis_total=int(ay.sum()),
            K=ref['phases'],reference_cuts=ref['cut_years'],
            associations_match=True,annual_csv_and_frozen_drive_match=True))
    assert refs==json.loads((run.HERE/'results/references_and_evidence.json').read_text(encoding="utf-8"))
    records=[run.record(ref,x,y,method,m) for _,(_,x,y,_),ref in paired_series(analysis,refs)
             for m in (2,3) for method in run.METHODS]
    decimal_differences = compare_records(records, json.loads((run.HERE/'results/results.json').read_text(encoding="utf-8")))
    assert run.summaries(records)==json.loads((run.HERE/'results/common_set_summaries.json').read_text(encoding="utf-8"))
    # Demonstrate the original positional hazard without rewriting any input.
    positional_mismatches=sum(s[0]!=r['sheet'] for s,r in zip(full,old[::-1],strict=True))
    assert positional_mismatches==10
    # Exercise data preparation in a disposable copy, never on the source tree.
    saved_here,saved_root=prepare_data.HERE,prepare_data.ROOT
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);here=root/'istl/v3'
        shutil.copytree(run.HERE/'sources',here/'sources')
        (here/'data').mkdir();(root/'data_articles').mkdir()
        shutil.copy(run.ROOT/'data_articles/data_articles.xlsx',root/'data_articles/data_articles.xlsx')
        try:
            prepare_data.HERE,prepare_data.ROOT=here,root
            preparation=prepare_data.prepare()
        finally:
            prepare_data.HERE,prepare_data.ROOT=saved_here,saved_root
        with zipfile.ZipFile(root/'data_articles/data_articles.xlsx') as a,zipfile.ZipFile(run.ROOT/'data_articles/data_articles.xlsx') as b:
            assert a.namelist()==b.namelist()
            assert all(a.read(n)==b.read(n) for n in a.namelist())
        for name in ['source_series.csv','analysis_series.csv']:
            with (here/'data'/name).open(encoding="utf-8", newline="") as a,(run.HERE/'data'/name).open(encoding="utf-8", newline="") as b:
                assert list(csv.DictReader(a))==list(csv.DictReader(b))
    paths=['data_articles/data_articles.xlsx','istl/v2/results/references_normalized.json',
        'istl/integration/evidence_status_v0.2.json','istl/v3/sources/drive_snapshot.txt',
        'istl/v3/data/source_series.csv','istl/v3/data/analysis_series.csv',
        'istl/v3/results/references_and_evidence.json','istl/v3/results/results.json',
        'istl/v3/run.py','istl/v3/prepare_data.py','istl/v3/associations.py',
        'istl/v3/case_manifest.json','istl/v3/audit_associations.py']
    result=dict(base_commit='e29e91254e0bb174e77ec00af725091697114620',
        cases=report,case_count=10,archived_records_reproduced=60,
        numerical_comparison=dict(
            relative_tolerance=1e-12, absolute_tolerance=1e-12,
            allowed_parameters=['candidate_heights', 'height', 'selected_strength', 'sse'],
            decimal_differences=decimal_differences, other_fields_exact=True),
        references_and_aggregates_identical=True,
        legacy_reversed_reference_misassociations=positional_mismatches,
        preparation_preserves_workbook_members_and_csv_values=True,
        scope='Internal association audit against archived evidence and frozen Drive series; no new source-figure or bibliographic-record audit.',
        sha256={p:hashlib.sha256((run.ROOT/p).read_bytes()).hexdigest() for p in paths})
    run.dump(output/'audit.json',result)
    run.csv_write(output/'case_associations.csv',report)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    result=audit(p.parse_args().output)
    print('10 case associations verified; 60 archived records and aggregates reproduced.')
