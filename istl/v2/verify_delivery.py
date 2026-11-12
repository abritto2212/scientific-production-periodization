"""Verify frozen v1 files, both suites and deterministic v2 JSON/CSV/SVG.

Use --initial-package PATH when the v1 ZIP is not under previous/.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
EXPECTED_V1='d64e43eee4ba4e6f922e9f2ef38e6907bd16588572bd12be2e13bc109c0fe96d'


def signature(out):
    return {p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob('*')) if p.is_file() and p.name!='reproducibility_hashes.json'
            and p.suffix in ('.json','.csv','.svg')}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--initial-package',type=Path,default=ROOT/'previous/ISTL_validacion_entrega01.zip')
    args=parser.parse_args();initial=args.initial_package.resolve()
    if hashlib.sha256(initial.read_bytes()).hexdigest()!=EXPECTED_V1:
        raise ValueError('Initial package differs from frozen v1')
    with zipfile.ZipFile(initial) as z:
        names=z.namelist()
        differences=[n for n in names if not (ROOT/n).is_file() or (ROOT/n).read_bytes()!=z.read(n)]
        patch_hash=hashlib.sha256(z.read('ISTL_revision_entrega01.patch')).hexdigest()
    if differences:raise ValueError('Frozen v1 files changed: '+str(differences))
    logs=[f'Initial ZIP SHA256: {EXPECTED_V1}\nInitial patch SHA256: {patch_hash}\n'
          f'Initial ZIP members preserved byte-for-byte: {len(names)}/{len(names)}\n']
    commands=[['-m','unittest','discover','-s','istl','-p','test_periodization.py','-v'],
              ['-m','unittest','discover','-s','istl/v2','-p','test_conditioned.py','-v'],
              ['istl/v2/run_conditioned.py']]
    for command in commands:
        r=subprocess.run([sys.executable,*command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        logs.append('$ python '+' '.join(command)+'\n'+r.stdout+r.stderr)
        if r.returncode:raise RuntimeError(logs[-1])
    before=signature(HERE/'results')
    repeat=subprocess.run([sys.executable,'istl/v2/run_conditioned.py'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if repeat.returncode:raise RuntimeError(repeat.stderr)
    after=signature(HERE/'results')
    if before!=after:raise ValueError('Repeated JSON/CSV/SVG hashes differ')
    with zipfile.ZipFile(initial) as z:
        if any((ROOT/n).read_bytes()!=z.read(n) for n in z.namelist()):
            raise ValueError('Verification modified v1 files')
    logs.append(f'Repeated JSON/CSV/SVG deterministic: {len(after)} files match.\n'
                'V1 files still unchanged after tests and runs.\nNo GitHub publication attempted in v2.\n')
    (HERE/'results/verification.txt').write_text('\n'.join(logs),encoding='utf-8')
    (HERE/'results/reproducibility_hashes.json').write_text(json.dumps(after,indent=2)+'\n',encoding='utf-8')
    print('\n'.join(logs))


if __name__=='__main__':main()
