"""From repository root: python istl/v2/run_conditioned.py."""
import argparse
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent))
from read_data import load_cases
from conditioned import segment,native_derivative,ordered_distance
from references import load_references

METHODS=('derivative_k_provisional','piecewise_linear_k','dynamic_l2_k')


def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def run_record(ref,x,y,method,min_len,scenario):
    truncated=scenario=='case6_truncated_2023'
    coverage=bool(ref['published_intervals']) and ref['published_intervals'][0]['start']==int(x[0]) and ref['published_intervals'][-1]['end']==int(x[-1])
    reference_feasible=None if ref['phases'] is None else min(p['length'] for p in ref['published_intervals'])>=min_len
    r=dict(case=ref['case'],sheet=ref['sheet'],method=method,min_len=min_len,
        scenario=scenario,result_family='K-conditioned provisional v2',
        input_start=int(x[0]),input_end=int(x[-1]),input_n=len(x),input_total=int(y.sum()),
        input_omitted_years=[2024] if truncated else [],
        phases_input=ref['phases'],reference_cut_years=ref['cut_years'],
        reference_state=ref['reference_state'],annual_series_verified=False,
        reference_full_window_coverage=coverage,reference_satisfies_minimum=reference_feasible,
        reference_intervals=ref['published_intervals'],reference_source=ref['source'],
        metrics=None,metric_exclusion_reasons=[],eligible_provisional_metrics=False,
        cut_convention='first year of new period; inclusive nonoverlapping intervals')
    if ref['phases'] is None:
        r.update(algorithm_feasible=None,reason='K unknown; not run',parameters=None,
                 cut_indices=None,cut_years=None,intervals=None)
    else:
        r.update(segment(x,y,method,ref['phases'],min_len))
    if not coverage: r['metric_exclusion_reasons'].append('no complete reference on this input window')
    if reference_feasible is False: r['metric_exclusion_reasons'].append('published partition violates this minimum; algorithm may still be feasible')
    if r['algorithm_feasible'] is not True: r['metric_exclusion_reasons'].append(r['reason'])
    if not r['metric_exclusion_reasons']:
        r['eligible_provisional_metrics']=True
        r['metrics']=ordered_distance(r['cut_years'],ref['cut_years'])
    r['aggregation_role']='case6 separate window sensitivity' if truncated else 'common full-window scenario'
    return r


def summarize(records,scopes):
    summary=[]
    scenarios=sorted(set((r['scenario'],r['min_len']) for r in records))
    common_both={}
    for scenario in sorted({r['scenario'] for r in records}):
        groups=[{r['case'] for r in records if r['scenario']==scenario and r['min_len']==m
                 and r['method']==method and r['eligible_provisional_metrics']}
                for m in (2,3) for method in METHODS]
        common_both[scenario]=set.intersection(*groups)
    for scenario,m in scenarios:
        rr=[r for r in records if r['scenario']==scenario and r['min_len']==m]
        eligible={method:{r['case'] for r in rr if r['method']==method and r['eligible_provisional_metrics']} for method in METHODS}
        common=set.intersection(*eligible.values())
        for scope,allowed in scopes.items():
            for method in METHODS:
                target=common if scope=='common_all_methods' else common_both[scenario] if scope=='common_all_methods_both_minima' else allowed
                selected=[r for r in rr if r['method']==method and r['eligible_provisional_metrics'] and r['case'] in target]
                errors=[e for r in selected for e in r['metrics']['absolute_errors_years']]
                summary.append(dict(scenario=scenario,min_len=m,scope=scope,method=method,
                    cases=[r['case'] for r in selected],n_cases=len(selected),n_reference_cuts=len(errors),
                    macro_mae_years=None if not selected else float(np.mean([r['metrics']['mae_years'] for r in selected])),
                    pooled_mae_years=None if not errors else float(np.mean(errors)),
                    macro_exact_rate=None if not selected else float(np.mean([r['metrics']['exact_rate'] for r in selected])),
                    pooled_exact_rate=None if not errors else sum(e==0 for e in errors)/len(errors),
                    interpretation='provisional published-reference proximity; unequal denominators must not be ranked'))
    return summary


def write_csv(path,rows):
    if not rows: return
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader()
        for r in rows:
            w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})


def figures(out,cases,refs,records):
    plt.rcParams.update({'svg.hashsalt':'istl-v2-conditioned','svg.fonttype':'none'})
    for m in (2,3):
        fig,axes=plt.subplots(5,2,figsize=(13,17),layout='constrained')
        for i,(sheet,x,y,_) in enumerate(cases):
            ax=axes.flat[i]; ref=refs[i]
            ax.plot(x,y,'o-',ms=3,lw=1,color='#505050',label='Annual counts')
            for j,year in enumerate(ref['cut_years'] or []):
                ax.axvline(year,color='black',lw=2,alpha=.5,label='Published boundary' if j==0 else None)
            if ref['case']==6: ax.axvspan(2023.5,2024.5,color='#e69f00',alpha=.22,label='2024 not assigned in source')
            annotations=[]
            for method,color,ls,short in [('derivative_k_provisional','#009E73',':','Derivative-K'),('piecewise_linear_k','#D55E00','--','Linear-K'),('dynamic_l2_k','#0072B2','-.','Dynp-K')]:
                r=next(r for r in records if r['case']==ref['case'] and r['min_len']==m and r['scenario']=='full_window' and r['method']==method)
                if r['algorithm_feasible'] is True:
                    for j,year in enumerate(r['cut_years']):
                        ax.axvline(year,color=color,ls=ls,lw=1.3,label=short if j==0 else None)
                elif r['phases_input'] is not None: annotations.append(short+': no admissible peak subset')
            if ref['phases'] is None: annotations=['K unknown: no conditioned run']
            if ref['case']==2 and m==3: annotations.append('Published final phase: 2 years; no score')
            ax.text(.02,.95,'\n'.join(annotations),transform=ax.transAxes,va='top',fontsize=8,bbox=dict(facecolor='white',alpha=.8,edgecolor='none'))
            ax.set_title(f"Case {i+1}: K={ref['phases'] if ref['phases'] else '?'} ({ref['evidence_class']})",fontsize=10)
            ax.set_xlabel('Year');ax.set_ylabel('Publications');ax.xaxis.set_major_locator(MaxNLocator(integer=True,nbins=6))
            ax.grid(alpha=.15);ax.legend(fontsize=7,loc='center left')
        fig.suptitle(f'Provisional published-K comparison | minimum {m} years | original counts not fully verified',fontsize=12)
        fig.savefig(out/f'conditioned_min{m}.svg',metadata={'Date':None})
        fig.savefig(out/f'conditioned_min{m}.png',dpi=110)
        plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE/'results')
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    (out/'figures').mkdir(exist_ok=True)
    cases=load_cases(ROOT/'data_articles/data_articles.xlsx');refs=load_references(cases)
    records=[];native=[]
    for ref,(_,x,y,_) in zip(refs,cases):
        for m in (2,3):
            for method in METHODS: records.append(run_record(ref,x,y,method,m,'full_window'))
            native.append(dict(case=ref['case'],published_phases=ref['phases'],**native_derivative(x,y,m)))
    ref=refs[5]; _,x,y,_=cases[5]
    for m in (2,3):
        for method in METHODS: records.append(run_record(ref,x[x<=2023],y[x<=2023],method,m,'case6_truncated_2023'))
    summaries=summarize(records,dict(available_by_method=set(range(1,11)),
        common_all_methods=set(),common_all_methods_both_minima=set(),
        class_A={5,9},class_B={1,2,3,4,6,8}))
    dump(out/'references_normalized.json',refs)
    dump(out/'conditioned_results.json',records)
    dump(out/'native_derivative_diagnostic.json',native)
    dump(out/'summary.json',summaries)
    write_csv(out/'summary.csv',summaries)
    table=[];pairs=[]
    for r in records:
        table.append({k:r[k] for k in ['case','method','scenario','min_len','phases_input','algorithm_feasible',
            'reference_full_window_coverage','reference_satisfies_minimum','eligible_provisional_metrics',
            'cut_years','reference_cut_years','intervals','parameters','metrics','metric_exclusion_reasons']})
        if r['metrics']:
            for j,(p,t) in enumerate(zip(r['cut_years'],r['reference_cut_years']),1):
                pairs.append(dict(case=r['case'],method=r['method'],scenario=r['scenario'],min_len=r['min_len'],
                    boundary_order=j,predicted_year=p,reference_year=t,signed_error=p-t,absolute_error=abs(p-t),exact=p==t))
    write_csv(out/'conditioned_cuts.csv',table);write_csv(out/'paired_boundaries.csv',pairs)
    figures(out/'figures',cases,refs,records)
    dump(out/'provenance.json',dict(version='entrega02',base_remote_commit='81da0fb072ed46ce0d64b6bea1eb55edc186873c',
        first_package_sha256='d64e43eee4ba4e6f922e9f2ef38e6907bd16588572bd12be2e13bc109c0fe96d',
        input_sha256=hashlib.sha256((ROOT/'data_articles/data_articles.xlsx').read_bytes()).hexdigest(),
        reference_snapshots={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((HERE/'references').iterdir()) if p.is_file()},
        implementation_sha256={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
            for name in ('conditioned.py','references.py','run_conditioned.py','test_conditioned.py')},
        python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__,
        methods=list(METHODS),minimums=[2,3],n_full_records=60,n_case6_sensitivity_records=6,
        publication_attempted=False,reference_series_pointwise_verified=False))
    print('Conditioned records:',len(records),'| native diagnostics:',len(native))
    for a in summaries:
        if a['scope'] in ('available_by_method','common_all_methods'):
            print(a['scenario'],a['min_len'],a['scope'],a['method'],a['cases'],a['n_reference_cuts'],a['macro_mae_years'],a['pooled_exact_rate'])


if __name__=='__main__':main()
