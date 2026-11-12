"""Explicit identities for the ten approved cases; reject ambiguous joins."""
import hashlib
import json
from pathlib import Path

MANIFEST = json.loads((Path(__file__).with_name('case_manifest.json')).read_text(encoding="utf-8"))
SHEETS = {r['case']: r['sheet'] for r in MANIFEST}
IDS = set(SHEETS)

def unique(rows, key, expected, label):
    result = {}
    for row in rows:
        value = key(row)
        if value is None or value in result:
            raise ValueError(f'{label}: null or duplicate key {value}')
        result[value] = row
    if set(result) != set(expected):
        raise ValueError(f'{label}: missing {set(expected)-set(result)}; extra {set(result)-set(expected)}')
    return result

def series_by_case(cases):
    sheets = unique(cases, lambda r:r[0], SHEETS.values(), 'series sheets')
    return {i:sheets[SHEETS[i]] for i in sorted(IDS)}

def records_by_case(rows, label):
    if any(type(r.get('case')) is not int for r in rows):
        raise ValueError(f'{label}: case must be an integer')
    result = unique(rows, lambda r:r['case'], IDS, label)
    for i,r in result.items():
        if 'sheet' in r and r['sheet'] != SHEETS[i]:
            raise ValueError(f'{label}: conflicting sheet for case {i}')
    return result

def drive_by_case(parts):
    expected = {r['drive_section_sha256']:r['case'] for r in MANIFEST}
    indexed = unique(parts, lambda p:hashlib.sha256(p.strip().encode()).hexdigest(), expected, 'frozen Drive sections')
    return {i:indexed[h] for h,i in expected.items()}

def join_inputs(cases, references, evidence):
    series=series_by_case(cases)
    refs=records_by_case(references,'references')
    status=records_by_case(evidence,'evidence')
    for item in MANIFEST:
        if refs[item['case']]['source'] != item['source']:
            raise ValueError('Reference source differs from approved identity')
    return [(i,series[i],refs[i],status[i]) for i in sorted(IDS)]

def paired_series(cases, refs):
    series=series_by_case(cases)
    references=records_by_case(refs,'analysis references')
    return [(i,series[i],references[i]) for i in sorted(IDS)]
