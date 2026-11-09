import csv
import io
import json
from pathlib import Path
import unittest
import numpy as np
from istl.compare_periodizations import compare_periodizations

ROOT = Path(__file__).resolve().parents[2]


class PublicWrapperTests(unittest.TestCase):
    def test_equivalence_to_integrated_results(self):
        rows = list(csv.DictReader(io.StringIO(
            (ROOT/'istl/v3/data/analysis_series.csv').read_text(encoding='utf-8-sig'))))
        saved = json.loads((ROOT/'istl/v3/results/results.json').read_text(encoding='utf-8'))
        refs = json.loads((ROOT/'istl/v3/results/references_and_evidence.json').read_text(encoding='utf-8'))
        self.assertTrue(refs[2]['annual_figure_counts_verified'])
        comparisons = 0
        for case in range(1,10):
            source = [r for r in rows if int(r['case'])==case]
            years = [int(r['year']) for r in source]
            counts = [int(r['count']) for r in source]
            for minimum in (2,3):
                actual = compare_periodizations(years, counts, refs[case-1]['phases'], minimum)
                for method, result in actual.items():
                    expected = next(r for r in saved if r['case']==case and r['min_len']==minimum and r['method']==method)
                    with self.subTest(case=case,minimum=minimum,method=method):
                        for key in ('algorithm_feasible','reason','cut_indices','cut_years','intervals'):
                            self.assertEqual(result[key],expected[key])
                        self.assertEqual(set(result['parameters']),set(expected['parameters']))
                        for key,value in result['parameters'].items():
                            old=expected['parameters'][key]
                            if isinstance(value,float):
                                self.assertTrue(np.isclose(value,old,rtol=1e-12,atol=1e-10),key)
                            elif isinstance(value,list) and value and isinstance(value[0],float):
                                np.testing.assert_allclose(value,old,rtol=1e-12,atol=1e-10)
                            else:self.assertEqual(value,old)
                    comparisons += 1
        self.assertEqual(comparisons,54)

    def test_insufficient_length_retains_all_methods(self):
        results=compare_periodizations([2000,2001,2002],[1,2,3],2,2)
        self.assertEqual(len(results),3)
        for r in results.values():
            self.assertFalse(r['algorithm_feasible']);self.assertFalse(r['executed'])
            self.assertIsNone(r['cut_years']);self.assertTrue(r['reason'])

    def test_existing_validation_and_no_input_mutation(self):
        for years,counts in [([2000,2002,2003],[1,2,3]),([2000,2000,2001],[1,2,3]),
                             ([2000,2001,2002],[1,None,3]),([2000,2001,2002],[1,-1,3])]:
            with self.assertRaises(ValueError):compare_periodizations(years,counts,1,2)
        for periods,minimum in [(True,2),(2,1),(0,2),(2,2.5)]:
            with self.assertRaises(ValueError):compare_periodizations([2000,2001,2002],[1,2,3],periods,minimum)
        x=np.arange(2000,2006);y=np.arange(6);before=(x.copy(),y.copy())
        compare_periodizations(x,y,2,2)
        np.testing.assert_array_equal(x,before[0]);np.testing.assert_array_equal(y,before[1])


if __name__=='__main__':unittest.main()
