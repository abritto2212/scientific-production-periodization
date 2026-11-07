"""Entrega03: approved series, one analytical window per case, fixed K."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/'v2'))
from conditioned import segment,native_derivative,ordered_distance
from read_data import load_cases
from periodization import piecewise,dynamic_l2

METHODS=('derivative_k_provisional','piecewise_linear_k','dynamic_l2_k')
CUTS={1:[2007,2013,2019],2:[2014,2020],3:[2009,2017],4:[2011,2017],
      5:[2012,2018],6:[2011,2018],7:[2013,2020],8:[2009,2017],9:[2012],10:None}


def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def csv_write(path,rows):
    if not rows:return
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
        for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()})


def inputs():
    cases=load_cases(ROOT/'data_articles/data_articles.xlsx')
    old=json.loads((HERE.parent/'v2/results/references_normalized.json').read_text(encoding='utf-8'))
    inherited=json.loads((HERE.parent/'integration/evidence_status_v0.2.json').read_text(encoding='utf-8'))['cases']
    refs=[];analytical=[]
    for i,((sheet,x,y,_),previous,status) in enumerate(zip(cases,old,inherited),1):
        mask=x<=2023 if i==6 else np.ones(len(x),dtype=bool)
        xx,yy=x[mask],y[mask];cuts=CUTS[i]
        edges=[int(xx[0]),*(cuts or []),int(xx[-1])+1]
        periods=[dict(start=a,end=b-1,length=b-a) for a,b in zip(edges[:-1],edges[1:])] if cuts else []
        verified=status['complete_label_match'] or i in (2,3,6,7,8,9)
        total=int(y.sum());published_total=previous['published_total']
        ref=dict(case=i,sheet=sheet,phases=None if cuts is None else len(cuts)+1,
            cut_years=cuts,published_intervals=periods,
            source=previous['source'],reference=previous['reference'],
            evidence_location='Discussion p.116; Figure 1 p.109' if i==7 else previous['evidence_location'],
            source_year_start=int(x[0]),source_year_end=int(x[-1]),source_total=total,
            analysis_year_start=int(xx[0]),analysis_year_end=int(xx[-1]),analysis_total=int(yy.sum()),
            omitted_analysis_years=[2024] if i==6 else [],omitted_analysis_count=84 if i==6 else 0,
            published_declared_total=published_total,source_minus_published_declared=total-published_total,
            total_difference_explanation='unresolved; subtraction does not allocate the difference to omitted years',
            annual_figure_counts_verified=verified,primary_bibliographic_records_audited=False,
            annual_verification_basis='21 labels checked in chat02 v0.2 + 2004=7 confirmed by Sebastian/Direction' if i==6 else
                '18 annual counts reviewed by Sebastian; 2004 corrected to1, 2005=1 and later retained' if i==2 else
                '23 annual figure counts confirmed in entrega03 instruction' if i in (7,8,9) else
                '23 labels matched to repository Excel by Direction on 2026-11-07; Figure 2, p.409' if i==3 else 'inherited Direction integration status',
            verification_origin='Sebastian and Direction, instruction for entrega03 (2026-11-06)' if i in (2,6,7,8,9)
                else 'Direction direct figure verification, 2026-11-07' if i==3 else 'Direction integration evidence_status_v0.2, commit 60ea426',
            historical_evidence_class=previous['evidence_class'],
            boundary_authority='published textual phases; approved by Direction' if i in (7,8,9) else 'published phases; approved reference table',
            textual_vs_graphical_header_conflict=dict(reported=True,decision='use textual phases',
                verbatim_graphical_heading=None,transcription_status='not supplied in this chat or integration record; do not reconstruct') if i in (7,8,9) else None,
            partial_last_year_note='2024 partial; source query 2024-10-05' if i==5 else None)
        refs.append(ref);analytical.append((sheet,xx,yy,[]))
    return cases,analytical,refs


def record(ref,x,y,method,m):
    valid_ref=ref['phases'] is not None and min(p['length'] for p in ref['published_intervals'])>=m
    r=dict(case=ref['case'],sheet=ref['sheet'],version='entrega03',method=method,min_len=m,
        configuration=f'published_K_min{m}',window=[int(x[0]),int(x[-1])],n_years=len(x),total=int(y.sum()),
        phases_input=ref['phases'],reference_cut_years=ref['cut_years'],
        reference_satisfies_minimum=None if ref['phases'] is None else valid_ref,
        annual_figure_counts_verified=ref['annual_figure_counts_verified'],
        primary_bibliographic_records_audited=False,metrics=None,eligible=False,metric_exclusion_reasons=[])
    if ref['phases'] is None:
        r.update(algorithm_feasible=None,reason='no complete published partition; K unknown',
                 cut_indices=None,cut_years=None,intervals=None,parameters=None)
    else:r.update(segment(x,y,method,ref['phases'],m))
    if not valid_ref:r['metric_exclusion_reasons'].append('reference missing or incompatible with minimum')
    if r['algorithm_feasible'] is not True:r['metric_exclusion_reasons'].append(r['reason'])
    if not r['metric_exclusion_reasons']:
        r['eligible']=True;r['metrics']=ordered_distance(r['cut_years'],ref['cut_years'])
    return r


def summaries(records):
    eligible={(m,method):{r['case'] for r in records if r['min_len']==m and r['method']==method and r['eligible']}
              for m in (2,3) for method in METHODS}
    common={m:set.intersection(*(eligible[m,method] for method in METHODS)) for m in (2,3)}
    both=common[2]&common[3]
    verified={r['case'] for r in records if r['annual_figure_counts_verified']}
    ss=[]
    for m in (2,3):
        scopes={'common_three_methods':(common[m],METHODS),
                'common_three_methods_both_minima':(both,METHODS),
                'figure_checked_common_three_methods':(common[m]&verified,METHODS),
                'common_linear_dynp':(eligible[m,METHODS[1]]&eligible[m,METHODS[2]],METHODS[1:])}
        for scope,(cases,methods) in scopes.items():
            for method in methods:
                rr=[r for r in records if r['min_len']==m and r['method']==method and r['case'] in cases]
                errors=[e for r in rr for e in r['metrics']['absolute_errors_years']]
                ss.append(dict(configuration=f'published_K_min{m}',min_len=m,scope=scope,method=method,
                    cases=sorted(cases),n_cases=len(rr),n_boundaries=len(errors),
                    macro_mae_years=float(np.mean([r['metrics']['mae_years'] for r in rr])) if rr else None,
                    pooled_mae_years=float(np.mean(errors)) if errors else None,
                    exact_count=sum(e==0 for e in errors),pooled_exact_rate=sum(e==0 for e in errors)/len(errors) if errors else None,
                    macro_exact_rate=float(np.mean([r['metrics']['exact_rate'] for r in rr])) if rr else None,
                    scope_limit='published-reference agreement, not historical validity; annual figure verification completed for case3'))
    return ss


def plot(out,cases,refs,records):
    plt.rcParams.update({'svg.hashsalt':'istl-entrega03','svg.fonttype':'none'})
    for m in (2,3):
        fig,axes=plt.subplots(5,2,figsize=(13,17),layout='constrained')
        for i,((sheet,x,y,_),ref) in enumerate(zip(cases,refs),1):
            ax=axes.flat[i-1];ax.plot(x,y,'o-',ms=3,color='#555555',label='Annual publications')
            for j,cut in enumerate(ref['cut_years'] or []):ax.axvline(cut,color='black',alpha=.5,lw=2,label='Published textual boundary' if j==0 else None)
            notes=[]
            for method,color,style,label in zip(METHODS,['#009E73','#D55E00','#0072B2'],[':','--','-.'],['Derivative-K','Linear-K','Dynp-L2-K']):
                r=next(r for r in records if r['case']==i and r['min_len']==m and r['method']==method)
                if r['algorithm_feasible']:
                    for j,c in enumerate(r['cut_years']):ax.axvline(c,color=color,ls=style,lw=1.4,label=label if j==0 else None)
                elif i!=10:notes.append(label+': infeasible')
            if i==2 and m==3:notes.append('Published last phase: 2 years; no score')
            if i==6:notes.append('Comparison: 2003-2023; 2024 retained in source')
            if i==10:notes.append('No complete reference; separate diagnostic only')
            ax.text(.02,.95,'\n'.join(notes),transform=ax.transAxes,va='top',fontsize=7,bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
            ax.set_title(f"Case {i}: K={ref['phases'] if ref['phases'] else '?'}",fontsize=10)
            ax.set_xlabel('Year');ax.set_ylabel('Publications');ax.xaxis.set_major_locator(MaxNLocator(integer=True,nbins=6));ax.grid(alpha=.15)
            ax.legend(fontsize=7,loc='center left')
        fig.suptitle(f'Entrega03 | published K | minimum {m} years | case 6: approved 2003-2023 window',fontsize=12)
        fig.savefig(out/f'comparison_min{m}.svg',metadata={'Date':None});fig.savefig(out/f'comparison_min{m}.png',dpi=110);plt.close(fig)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'results');args=p.parse_args()
    out=args.output;out.mkdir(exist_ok=True,parents=True);(out/'figures').mkdir(exist_ok=True)
    full,analysis,refs=inputs();records=[record(ref,x,y,method,m) for ref,(_,x,y,_) in zip(refs,analysis) for m in (2,3) for method in METHODS]
    ss=summaries(records);diagnostic=[]
    _,x,y,_=full[9]
    for m in (2,3):
        diagnostic.append(dict(case=10,configuration='separate two-cut diagnostic, no published K',min_len=m,
            derivative_automatic=native_derivative(x,y,m),
            piecewise_two_cut_diagnostic=segment(x,y,'piecewise_linear_k',3,m),
            dynp_two_cut_diagnostic=segment(x,y,'dynamic_l2_k',3,m),metrics=None))
    dump(out/'results.json',records);dump(out/'references_and_evidence.json',refs);dump(out/'common_set_summaries.json',ss)
    dump(out/'case10_separate_diagnostic.json',diagnostic)
    csv_write(out/'results.csv',records);csv_write(out/'common_set_summaries.csv',ss)
    pairs=[]
    for r in records:
        if r['metrics']:
            for j,(pred,truth) in enumerate(zip(r['cut_years'],r['reference_cut_years']),1):
                pairs.append(dict(case=r['case'],method=r['method'],min_len=r['min_len'],boundary_order=j,
                    predicted_year=pred,reference_year=truth,signed_error=pred-truth,absolute_error=abs(pred-truth)))
    csv_write(out/'paired_boundaries.csv',pairs)
    old=json.loads((HERE.parent/'v2/results/conditioned_results.json').read_text(encoding='utf-8'))
    delta=[]
    for r in records:
        previous=next(a for a in old if a['case']==r['case'] and a['method']==r['method'] and a['min_len']==r['min_len'] and a['scenario']=='full_window')
        delta.append(dict(case=r['case'],method=r['method'],min_len=r['min_len'],
            old_window=[previous['input_start'],previous['input_end']],new_window=r['window'],
            old_K=previous['phases_input'],new_K=r['phases_input'],
            old_cuts=previous['cut_years'],new_cuts=r['cut_years'],
            old_metric_eligible=previous['eligible_provisional_metrics'],new_metric_eligible=r['eligible'],
            change_context='window changed; not a pure algorithm comparison' if r['case']==6 else
                'new published reference and eligibility' if r['case']==7 else 'one count corrected' if r['case']==2 else 'unchanged input and parameters'))
    dump(out/'delta_vs_entrega02.json',delta)
    dump(out/'provenance.json',dict(version='entrega03',base_commit='60ea426564f37622a8f7fc090ad3f9d8b63070ac',
        input_sha256=hashlib.sha256((ROOT/'data_articles/data_articles.xlsx').read_bytes()).hexdigest(),
        code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [HERE/'run.py',HERE/'prepare_data.py',HERE.parent/'v2/conditioned.py',HERE.parent/'periodization.py']},
        python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__,
        boundary_convention='first year of next period',minimums=[2,3],publication_attempted=False))
    plot(out/'figures',analysis,refs,records)
    fig,axes=plt.subplots(2,1,figsize=(10,8),layout='constrained')
    _,x,y,_=full[9]
    for ax,d in zip(axes,diagnostic):
        ax.plot(x,y,'o-',ms=3,color='#555555',label='Annual publications')
        for cuts,color,label in [(d['derivative_automatic']['cut_years'],'#009E73','Automatic derivative'),
            (d['piecewise_two_cut_diagnostic']['cut_years'],'#D55E00','Linear, 2 diagnostic cuts'),
            (d['dynp_two_cut_diagnostic']['cut_years'],'#0072B2','Dynp, 2 diagnostic cuts')]:
            for j,c in enumerate(cuts):ax.axvline(c,color=color,ls='--',label=label if j==0 else None)
        ax.set_title(f"Case10: separate diagnostic, minimum {d['min_len']} years; no reference or score")
        ax.set_xlabel('Year');ax.set_ylabel('Publications');ax.legend(fontsize=8);ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    fig.savefig(out/'figures/case10_diagnostic.svg',metadata={'Date':None});fig.savefig(out/'figures/case10_diagnostic.png',dpi=110);plt.close(fig)
    print('60 case-method-configuration records; case10 unscored; comparison case6=2003-2023')
    for row in ss:
        if row['scope'] in ('common_three_methods','common_three_methods_both_minima'):
            print(row['min_len'],row['scope'],row['method'],row['cases'],row['n_boundaries'],row['macro_mae_years'],row['exact_count'])


if __name__=='__main__':main()
