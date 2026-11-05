"""Normalize the chat 02 snapshots; do not fill unverified boundaries."""
import csv
import io
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent


def load_references(cases):
    matrix=(HERE/'references/02_Matriz_evidencia_snapshot.txt').read_text(encoding='utf-8')
    rows=list(csv.reader(io.StringIO(matrix.split('\f')[0])))
    header_at=next(i for i,r in enumerate(rows) if len(r)>2 and r[1:3]==['Caso','Hoja original'])
    fields=rows[header_at][1:]
    details={int(r[1]):dict(zip(fields,r[1:])) for r in rows[header_at+1:] if len(r)>1 and r[1].isdigit()}
    with (HERE/'references/02_Cortes_publicados_v0.1.csv').open(encoding='utf-8-sig',newline='') as source:
        source_rows=list(csv.DictReader(source))
    grouped={i:[] for i in range(1,11)}
    for r in source_rows:
        grouped[int(r['caso'])].append(r)
    if set(details)!=set(grouped) or len(cases)!=10:
        raise ValueError('Reference matrix must cover all ten cases')
    result=[]
    for case,(sheet,x,y,_) in enumerate(cases,1):
        d=details[case]
        if int(d['N Excel'])!=int(y.sum()):
            raise ValueError('Snapshot and input series totals disagree')
        if d['Hoja original']!=sheet or any(r['hoja']!=sheet for r in grouped[case]):
            raise ValueError('Case/sheet identity mismatch')
        bounds=[]
        for r in grouped[case]:
            close,open_=r['cierre_anterior'],r['apertura_siguiente']
            if bool(close)!=bool(open_):
                raise ValueError('Partially missing reference boundary')
            if open_:
                if int(open_)!=int(close)+1:
                    raise ValueError('Nonadjacent published frontier')
                bounds.append(int(open_))
        if bounds!=sorted(set(bounds)):
            raise ValueError('Duplicate or unordered reference cuts')
        published=[dict(start=int(a),end=int(b),length=int(b)-int(a)+1)
                   for a,b in re.findall(r'(\d{4})[–-](\d{4})',d['Divisiones explícitas'])] if bounds else []
        if bounds:
            if len(published)!=len(bounds)+1 or [p['start'] for p in published[1:]]!=bounds:
                raise ValueError('CSV cuts and matrix intervals disagree')
            if any(a['end']+1!=b['start'] for a,b in zip(published[:-1],published[1:])):
                raise ValueError('Published intervals overlap or leave interior gaps')
        complete=bool(published) and published[0]['start']==int(x[0]) and published[-1]['end']==int(x[-1])
        reasons=[]
        if not bounds: reasons.append('no verified complete published partition / K unknown')
        elif not complete: reasons.append('published coverage does not cover full input window; do not extend last phase')
        result.append(dict(case=case,sheet=sheet,reference_state=d['Estado'],
            evidence_class=d['Estado'][0], phases=len(bounds)+1 if bounds else None,
            cut_years=bounds if bounds else None,published_intervals=published,
            full_input_coverage=complete,provisional_concordance_eligible=complete,
            exclusion_reasons=reasons,annual_series_verified=False,
            source=d['DOI / enlace editorial'],reference=d['Referencia APA 7'],
            evidence_location=d['Ubicación'],evidence=d['Evidencia de vínculo'],
            pending=d['Pendientes / consulta a Britto'],matrix_total=int(d['N Excel']),
            published_total=int(d['N artículo']),
            input_start=int(x[0]),input_end=int(x[-1]),
            omitted_input_years=[int(a) for a in x if published and (a<published[0]['start'] or a>published[-1]['end'])]))
    return result
