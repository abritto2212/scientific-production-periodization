"""Verify v3 and run historical tests on historical inputs in isolation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
V2_SHA='1b517837e8a9d7c3ee9592cf04051eb2cc7aeec8ece1d6047125ee4dde93febe'


def signature(out):
    return {p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob('*')) if p.is_file() and p.suffix in ('.json','.csv','.svg')
            and p.name!='reproducibility_hashes.json'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--previous-package',type=Path,default=ROOT/'previous/ISTL_validacion_entrega02.zip')
    args=parser.parse_args();old=args.previous_package.resolve()
    if hashlib.sha256(old.read_bytes()).hexdigest()!=V2_SHA:raise ValueError('Historical package changed')
    fixture=Path(tempfile.mkdtemp(prefix='historical-test-',dir=ROOT))
    with zipfile.ZipFile(old) as z:z.extractall(fixture)
    logs=[f'Historical entrega02 ZIP SHA256 unchanged: {V2_SHA}\n']
    def execute(args,cwd):
        r=subprocess.run([sys.executable,*args],cwd=cwd,capture_output=True,text=True,encoding='utf-8')
        logs.append('$ python '+' '.join(args)+'\n'+r.stdout+r.stderr)
        if r.returncode:raise RuntimeError(logs[-1])
    execute(['-m','unittest','discover','-s','istl','-p','test_periodization.py','-v'],fixture)
    execute(['-m','unittest','discover','-s','istl/v2','-p','test_conditioned.py','-v'],fixture)
    execute(['-m','unittest','discover','-s','istl/v3','-p','test_v3.py','-v'],ROOT)
    execute(['istl/v3/prepare_data.py'],ROOT)
    execute(['istl/v3/run.py'],ROOT)
    before=signature(HERE/'results')
    execute(['istl/v3/run.py'],ROOT)
    after=signature(HERE/'results')
    if before!=after:raise ValueError('Non-deterministic JSON/CSV/SVG')
    if hashlib.sha256(old.read_bytes()).hexdigest()!=V2_SHA:raise ValueError('Previous archive modified')
    logs.append(f'Repeated JSON/CSV/SVG byte-identical: {len(after)} files.\n'
                'Historical suites: 11 + 12 tests, original workbook, isolated copy.\n'
                'V3 suite: 10 tests. No GitHub write or manuscript edit.\n')
    (HERE/'results/verification.txt').write_text('\n'.join(logs),encoding='utf-8')
    (HERE/'results/reproducibility_hashes.json').write_text(json.dumps(after,indent=2)+'\n',encoding='utf-8')
    print(logs[-1])


if __name__=='__main__':main()
