"""Run from repository root: python istl/run.py."""
import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from periodization import derivatives, derivative_candidates, piecewise, dynamic_l2, intervals
from read_data import load_cases

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = '81da0fb072ed46ce0d64b6bea1eb55edc186873c'


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'istl/results')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    (out/'figures').mkdir(exist_ok=True)
    source = ROOT/'data_articles/data_articles.xlsx'
    cases = load_cases(source)
    results, comparisons, audit, series = [], [], [], []
    fig, axes = plt.subplots(5, 2, figsize=(13, 17), layout='constrained')
    for case, (name,x,y,blanks) in enumerate(cases, 1):
        d, dp, smooth = derivatives(x,y)
        l, lp = piecewise(x,y)
        r, rp = dynamic_l2(x,y)
        records = []
        for method,cuts,params in [('derivatives',d,dp),('piecewise_linear',l,lp),('dynamic_l2',r,rp)]:
            record = dict(case=case, sheet=name, method=method,
                comparison='diagnostic; not expert agreement', parameters=params,
                cut_indices=cuts, cut_years=[int(x[c]) for c in cuts],
                n_cuts=len(cuts), intervals=intervals(x,cuts),
                cut_convention='first year of new period; inclusive nonoverlapping intervals')
            results.append(record)
            records.append(record)
        old_d = derivative_candidates(y, legacy_integer=True)[0]
        float_d = derivative_candidates(y)[0]
        old_l, old_lp = piecewise(x,y,legacy=True)
        old_r, old_rp = dynamic_l2(x,y,jump=5)
        comparisons.append(dict(case=case,
            derivatives_integer_candidates=[int(x[c]) for c in old_d],
            derivatives_float_candidates=[int(x[c]) for c in float_d],
            derivatives_constrained_cuts=[int(x[c]) for c in d],
            smoothing_changes_candidates=old_d != float_d,
            piecewise_legacy_indices=old_l,
            piecewise_legacy_labels=[int(x[c-1]) for c in old_l],
            piecewise_legacy_labels_common_convention=[int(x[c]) for c in old_l],
            piecewise_legacy_lengths=np.diff([0,*old_l,len(x)]).tolist(),
            piecewise_corrected_cuts=[int(x[c]) for c in l],
            piecewise_legacy_sse=old_lp['sse'], piecewise_corrected_sse=lp['sse'],
            dynamic_legacy_jump5_cuts=[int(x[c]) for c in old_r],
            dynamic_corrected_jump1_cuts=[int(x[c]) for c in r],
            dynamic_legacy_sse=old_rp['sse'], dynamic_corrected_sse=rp['sse']))
        audit.append(dict(case=case,sheet=name,start=int(x[0]),end=int(x[-1]),n=len(x),
            total=int(y.sum()),peak_years=x[y==max(y)].tolist(),max_count=int(max(y)),
            mean=float(y.mean()),zeros=int(np.sum(y==0)),trailing_blank_rows_ignored=blanks,
            ordered=True,duplicates=0,missing_years=0,missing_counts=0,imputed_values=0))
        series.extend(dict(case=case,sheet=name,year=int(a),count=int(b)) for a,b in zip(x,y))
        ax = axes.flat[case-1]
        ax.plot(x,y,'o-',color='#34495e',ms=3,lw=1,label='Annual publications')
        ax.plot(x,smooth,color='#8c8c8c',lw=1.2,label='Gaussian (float)')
        for method,cuts,color,style in [('Derivatives',d,'#009E73',':'),('Linear SSE',l,'#D55E00','--'),('Dynamic L2',r,'#0072B2','-.')]:
            for j,c in enumerate(cuts):
                ax.axvline(x[c],color=color,ls=style,lw=1.4,label=method if j==0 else None)
        ax.set_title(f'Case {case}: {name}',fontsize=10)
        ax.set_xlabel('Year'); ax.set_ylabel('Publications')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
        ax.grid(alpha=.18); ax.legend(fontsize=7)
    fig.suptitle('Diagnostic comparison: 2 cuts for linear SSE / dynamic L2; derivative count estimated',fontsize=12)
    plt.rcParams['svg.hashsalt']='istl-2026-validation'
    plt.rcParams['svg.fonttype']='none'
    fig.savefig(out/'figures/diagnostic.svg',metadata={'Date':None})
    fig.savefig(out/'figures/diagnostic.png',dpi=120)
    plt.close(fig)
    # Derivative audit: threshold and all candidates before/after length constraint.
    fig, axes = plt.subplots(5,2,figsize=(13,16),layout='constrained')
    for case,(name,x,y,_) in enumerate(cases,1):
        p,s,d1,d2,h = derivative_candidates(y)
        cuts,_,_ = derivatives(x,y)
        ax=axes.flat[case-1]; ax.plot(x,np.abs(d2),color='#009E73')
        ax.axhline(h,color='gray',ls='--',label='std(d2)')
        ax.scatter(x[p],np.abs(d2)[p],facecolors='none',edgecolors='#D55E00',s=65,label='Candidates')
        ax.scatter(x[cuts],np.abs(d2)[cuts],color='#0072B2',s=20,label='Length >= 3 retained')
        ax.set_title(f'Case {case}',fontsize=10); ax.set_xlabel('Year'); ax.set_ylabel('|second derivative|')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
        ax.legend(fontsize=7)
    fig.savefig(out/'figures/derivative_candidates.svg',metadata={'Date':None})
    fig.savefig(out/'figures/derivative_candidates.png',dpi=120)
    plt.close(fig)
    dump(out/'results.json',results)
    dump(out/'before_after.json',comparisons)
    dump(out/'data_audit.json',audit)
    dump(out/'provenance.json',dict(base_commit=BASE_COMMIT,
        source='data_articles/data_articles.xlsx',sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__,
        total_publications=sum(a['total'] for a in audit),total_year_observations=len(series),
        mean_series_length=float(np.mean([a['n'] for a in audit])),
        expert_reference_status='not verified; no accuracy metrics computed'))
    with (out/'series.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['case','sheet','year','count']); w.writeheader(); w.writerows(series)
    with (out/'cuts.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['case','method','parameters_json','cut_years','intervals','lengths'])
        for a in results:
            w.writerow([a['case'],a['method'],json.dumps(a['parameters'],ensure_ascii=False),
                ';'.join(map(str,a['cut_years'])),';'.join(f"{s['start']}-{s['end']}" for s in a['intervals']),
                ';'.join(str(s['length']) for s in a['intervals'])])
    print(f'{len(results)} case-method results; {len(series)} annual observations; total {sum(a["total"] for a in audit)}')
    print('Integer-to-float candidate changes:',[a['case'] for a in comparisons if a['smoothing_changes_candidates']])
    print('Case 9:',comparisons[8])


if __name__ == '__main__':
    main()
