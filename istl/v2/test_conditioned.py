import unittest
from itertools import combinations
from pathlib import Path
import numpy as np
from conditioned import (segment, native_derivative, admissible_subsets,
                         ordered_distance, validate_condition)
from periodization import derivative_candidates, piecewise, dynamic_l2, derivatives
from read_data import load_cases
from references import load_references
from run_conditioned import run_record, summarize, METHODS


class ConditionedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=load_cases(Path(__file__).resolve().parents[2]/'data_articles/data_articles.xlsx')
        cls.refs=load_references(cls.cases)

    def test_reference_number_and_convention(self):
        self.assertEqual(self.refs[0]['phases'],4)
        self.assertEqual(self.refs[0]['cut_years'],[2007,2013,2019])
        self.assertEqual(self.refs[8]['phases'],2)
        self.assertEqual(self.refs[8]['cut_years'],[2012])
        self.assertEqual([r['case'] for r in self.refs if r['provisional_concordance_eligible']],[1,2,3,4,5,8,9])

    def test_two_year_phase_is_reference_conflict_not_algorithm_failure(self):
        ref=self.refs[1];_,x,y,_=self.cases[1]
        self.assertEqual(ref['published_intervals'][-1],dict(start=2020,end=2021,length=2))
        a=run_record(ref,x,y,'piecewise_linear_k',2,'full_window')
        b=run_record(ref,x,y,'piecewise_linear_k',3,'full_window')
        self.assertTrue(a['eligible_provisional_metrics'])
        self.assertTrue(b['algorithm_feasible'])
        self.assertFalse(b['reference_satisfies_minimum'])
        self.assertIsNone(b['metrics'])
        self.assertEqual(a['reference_cut_years'],b['reference_cut_years'])

    def test_unknown_K_never_becomes_two_cuts_or_zero_error(self):
        for i in (6,9):
            for method in METHODS:
                _,x,y,_=self.cases[i]
                a=run_record(self.refs[i],x,y,method,2,'full_window')
                self.assertIsNone(a['phases_input']);self.assertIsNone(a['algorithm_feasible'])
                self.assertIsNone(a['cut_years']);self.assertIsNone(a['metrics'])

    def test_case6_no_silent_extension(self):
        ref=self.refs[5];_,x,y,_=self.cases[5]
        self.assertEqual(ref['published_intervals'][-1]['end'],2023)
        self.assertEqual(ref['omitted_input_years'],[2024])
        full=run_record(ref,x,y,'dynamic_l2_k',2,'full_window')
        limited=run_record(ref,x[x<=2023],y[x<=2023],'dynamic_l2_k',2,'case6_truncated_2023')
        self.assertFalse(full['eligible_provisional_metrics']);self.assertIsNone(full['metrics'])
        self.assertTrue(limited['eligible_provisional_metrics'])
        self.assertEqual(limited['input_omitted_years'],[2024])
        self.assertEqual(full['input_total']-limited['input_total'],84)

    def test_fixed_K_length_and_coverage(self):
        for ref,(_,x,y,_) in zip(self.refs,self.cases):
            if ref['phases'] is None:continue
            for m in (2,3):
                for method in METHODS:
                    a=segment(x,y,method,ref['phases'],m)
                    if a['algorithm_feasible']:
                        self.assertEqual(len(a['cut_years']),ref['phases']-1)
                        covered=[year for p in a['intervals'] for year in range(p['start'],p['end']+1)]
                        self.assertEqual(covered,x.tolist())
                        self.assertTrue(all(p['length']>=m for p in a['intervals']))

    def test_v1_equivalence_when_K_and_minimum_match(self):
        for _,x,y,_ in self.cases:
            self.assertEqual(segment(x,y,'piecewise_linear_k',3,3)['cut_indices'],piecewise(x,y)[0])
            self.assertEqual(segment(x,y,'dynamic_l2_k',3,3)['cut_indices'],dynamic_l2(x,y)[0])
            self.assertEqual(native_derivative(x,y,3)['cut_years'],[int(x[i]) for i in derivatives(x,y)[0]])

    def test_derivative_K_subsets_use_original_peaks_and_objective(self):
        for ref,(_,x,y,_) in zip(self.refs,self.cases):
            if ref['phases'] is None:continue
            for m in (2,3):
                r=segment(x,y,'derivative_k_provisional',ref['phases'],m)
                peaks,_,_,d2,h=derivative_candidates(y)
                options=list(admissible_subsets(peaks,len(x),ref['phases']-1,m))
                self.assertEqual(r['parameters']['candidate_indices'],peaks)
                self.assertEqual(r['parameters']['height'],h)
                if options:
                    expected=max(options,key=lambda c:sum(abs(d2[i]) for i in c))
                    self.assertEqual(r['cut_indices'],list(expected))
                else:self.assertFalse(r['algorithm_feasible'])
        a=segment(self.cases[0][1],self.cases[0][2],'derivative_k_provisional',4,2)
        self.assertFalse(a['algorithm_feasible']);self.assertIsNone(a['cut_years'])

    def test_global_SSE_optima_minimum_two(self):
        x=np.arange(10);y=np.array([1,2,8,4,5,20,6,7,15,30],dtype=float)
        for method in ('piecewise_linear_k','dynamic_l2_k'):
            r=segment(x,y,method,3,2);costs=[]
            for c in combinations(range(2,9),2):
                edges=[0,*c,10]
                if min(np.diff(edges))<2:continue
                score=0.
                for a,b in zip(edges[:-1],edges[1:]):
                    t,v=x[a:b],y[a:b]
                    fitted=np.polyval(np.polyfit(t,v,1),t) if method=='piecewise_linear_k' else np.mean(v)
                    score+=float(np.sum((v-fitted)**2))
                costs.append(score)
            self.assertAlmostEqual(r['parameters']['sse'],min(costs))

    def test_chronological_matching_and_unequal_K_guard(self):
        r=ordered_distance([2017,2021],[2009,2017])
        self.assertEqual(r['absolute_errors_years'],[8,4])
        self.assertEqual(r['mae_years'],6.0)
        self.assertEqual(r['exact_count'],0)
        with self.assertRaises(ValueError):ordered_distance([2017],[2009,2017])
        self.assertIsNone(ordered_distance([],[])['mae_years'])

    def test_summary_denominators_and_common_set(self):
        records=[]
        for ref,(_,x,y,_) in zip(self.refs,self.cases):
            for method in METHODS:records.append(run_record(ref,x,y,method,2,'full_window'))
        ss=summarize(records,dict(available_by_method=set(range(1,11)),common_all_methods=set()))
        for r in ss:
            if r['scope']=='common_all_methods':
                self.assertEqual(r['cases'],[2,3,4,5,8,9]);self.assertEqual(r['n_reference_cuts'],11)
            elif r['method']!='derivative_k_provisional':
                self.assertEqual(r['n_cases'],7);self.assertEqual(r['n_reference_cuts'],14)
        for r in records:
            if r['case'] in (6,7,10):self.assertIsNone(r['metrics'])

    def test_invalid_conditions_and_insufficient_data(self):
        for k,m in [(True,2),(3,1),(0,2),(2,2.5)]:
            with self.assertRaises(ValueError):validate_condition(20,k,m)
        with self.assertRaises(ValueError):validate_condition(5,3,2)

    def test_common_sample_across_minima_is_fixed(self):
        rows=[run_record(ref,x,y,method,m,'full_window')
              for ref,(_,x,y,_) in zip(self.refs,self.cases) for m in (2,3) for method in METHODS]
        ss=summarize(rows,dict(common_all_methods_both_minima=set()))
        self.assertEqual(len(ss),6)
        for r in ss:
            self.assertEqual(r['cases'],[4,8,9]);self.assertEqual(r['n_reference_cuts'],5)


if __name__=='__main__':unittest.main()
