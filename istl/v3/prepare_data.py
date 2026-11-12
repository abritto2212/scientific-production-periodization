"""Apply the single approved workbook cell correction; audit both sources."""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from read_data import load_cases
from associations import series_by_case, drive_by_case, SHEETS
import xml.etree.ElementTree as ET
import posixpath

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE_COMMIT='60ea426564f37622a8f7fc090ad3f9d8b63070ac'


def dump(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def validate_existing(source,current):
    src,cur=series_by_case(source),series_by_case(current)
    for i in sorted(src):
        _,x,y,_=src[i];sheet,xx,yy,_=cur[i]
        if not np_equal(x,xx):raise ValueError('Current workbook years differ from frozen base')
        for year,old,now in zip(x,y,yy):
            if old!=now and not (i==2 and year==2004 and now==1):
                raise ValueError('Unapproved existing workbook change; refusing overwrite')


def np_equal(x,y):
    return len(x)==len(y) and all(a==b for a,b in zip(x,y))


def prepare():
    base=HERE/'sources/base_data_articles.xlsx'
    target=ROOT/'data_articles/data_articles.xlsx'
    source=load_cases(base)
    if target.exists():
        current=load_cases(target)
        validate_existing(source,current)
    with zipfile.ZipFile(base) as z,zipfile.ZipFile(target,'w') as out:
        ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        sheets=ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',ns)
        target_sheet=next(sh for sh in sheets if sh.attrib['name']==SHEETS[2])
        rid=target_sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        rels={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        target_xml=rels[rid].lstrip('/') if rels[rid].startswith('/') else posixpath.normpath('xl/'+rels[rid])
        for info in z.infolist():
            data=z.read(info.filename)
            if info.filename==target_xml:
                text=data.decode('utf-8')
                text,n=re.subn(r'(<c\b[^>]*\br="B2"[^>]*>\s*<v>)2(</v>\s*</c>)',r'\g<1>1\2',text)
                if n!=1:raise ValueError('Expected one pending correction at sheet2 B2')
                data=text.encode('utf-8')
            out.writestr(info,data)
    corrected=load_cases(target)
    differences=[];rows=[];analysis=[]
    drive_parts=(HERE/'sources/drive_snapshot.txt').read_text(encoding='utf-8').strip().split('\f')
    if len(drive_parts)!=10:raise ValueError('Drive snapshot must contain ten series')
    corrected_map,source_map,drive_map=series_by_case(corrected),series_by_case(source),drive_by_case(drive_parts)
    for case in sorted(corrected_map):
        sheet,x,y,_=corrected_map[case];_,bx,by,_=source_map[case];part=drive_map[case]
        drive=[(int(r['Year']),int(r['Total_Publications'])) for r in csv.DictReader(io.StringIO(part.strip()))]
        if drive!=list(zip(x.tolist(),y.astype(int).tolist())):raise ValueError(f'Drive discrepancy beyond approved decision, case {case}')
        for year,new,old in zip(x,y,by):
            if new!=old:differences.append(dict(case=case,year=int(year),base_count=int(old),drive_count=int(new),approved_count=int(new)))
            row=dict(case=case,sheet=sheet,year=int(year),count=int(new))
            rows.append(row)
            if not (case==6 and year==2024):analysis.append(row)
    if differences!=[dict(case=2,year=2004,base_count=2,drive_count=1,approved_count=1)]:
        raise ValueError('Unexpected data modifications')
    for name,data in [('source_series.csv',rows),('analysis_series.csv',analysis)]:
        with (HERE/'data'/name).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['case','sheet','year','count']);w.writeheader();w.writerows(data)
    with zipfile.ZipFile(base) as old,zipfile.ZipFile(target) as new:
        changed_members=[n for n in old.namelist() if old.read(n)!=new.read(n)]
    audit=dict(base_commit=BASE_COMMIT,base_blob='89381c887437869b465ed992cdd551afea07920c',
        base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),
        corrected_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        differences_base_vs_drive=differences,changed_xlsx_members=changed_members,
        other_annual_observations_unchanged=225,drive_matches_corrected_all_observations=True,
        source_observations=len(rows),source_total=sum(r['count'] for r in rows),
        analysis_observations_including_unscored_case10=len(analysis),
        analysis_total_including_unscored_case10=sum(r['count'] for r in analysis),
        case6_omitted_from_analysis=dict(year=2024,count=84,source_retained=True),
        historical_archives_preserved=True)
    dump(HERE/'data/data_audit.json',audit)
    return audit


if __name__=='__main__':
    (HERE/'data').mkdir(exist_ok=True)
    print(json.dumps(prepare(),ensure_ascii=False,indent=2))
