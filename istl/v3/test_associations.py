import json
import random
from copy import deepcopy
import unittest
import numpy as np
from run import inputs, HERE, ROOT
from read_data import load_cases
from associations import join_inputs, series_by_case, records_by_case, drive_by_case
from prepare_data import validate_existing

class AssociationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series=load_cases(ROOT/'data_articles/data_articles.xlsx')
        cls.refs=json.loads((HERE.parent/'v2/results/references_normalized.json').read_text(encoding="utf-8"))
        cls.evidence=json.loads((HERE.parent/'integration/evidence_status_v0.2.json').read_text(encoding="utf-8"))['cases']

    def test_current_identity_matches_archived(self):
        refs=inputs()[2]
        self.assertEqual(refs,json.loads((HERE/'results/references_and_evidence.json').read_text(encoding="utf-8")))
        self.assertTrue(all(i==r['case']==e['case'] and s[0]==r['sheet']
            for i,s,r,e in join_inputs(self.series,self.refs,self.evidence)))

    def test_independent_permutations(self):
        baseline=inputs()
        for seed in range(20):
            args=[list(x) for x in (self.series,self.refs,self.evidence)]
            rng=random.Random(seed)
            for arg in args:rng.shuffle(arg)
            current=inputs(*args)
            self.assertEqual(current[2],baseline[2])
            for actual,expected in zip(current[1],baseline[1],strict=True):
                self.assertEqual(actual[0],expected[0])
                np.testing.assert_array_equal(actual[1],expected[1])
                np.testing.assert_array_equal(actual[2],expected[2])

    def test_invalid_reference_and_evidence_keys(self):
        for pos in (1,2):
            for mode in ('missing','duplicate','null','extra','wrong_sheet'):
                args=deepcopy([self.series,self.refs,self.evidence])
                rows=args[pos]
                if mode=='missing':rows.pop()
                elif mode=='duplicate':rows.append(deepcopy(rows[0]))
                elif mode=='null':rows[0]['case']=None
                elif mode=='extra':rows[0]['case']=11
                else:rows[0]['sheet']='wrong sheet'
                with self.subTest(pos=pos,mode=mode),self.assertRaises(ValueError):inputs(*args)

    def test_invalid_series_keys(self):
        for series in (self.series[:-1],self.series+[self.series[0]],
                       [('unknown',*self.series[0][1:]),*self.series[1:]]):
            with self.assertRaises(ValueError):series_by_case(series)

    def test_wrong_source_rejected(self):
        refs=deepcopy(self.refs);refs[0]['source']=refs[1]['source']
        with self.assertRaises(ValueError):inputs(self.series,refs,self.evidence)

    def test_preparation_and_drive_reordering(self):
        base=load_cases(HERE/'sources/base_data_articles.xlsx')
        validate_existing(base[::-1],self.series[3:]+self.series[:3])
        parts=(HERE/'sources/drive_snapshot.txt').read_text(encoding="utf-8").strip().split('\f')
        self.assertEqual(drive_by_case(parts),drive_by_case(parts[::-1]))
        for bad in (parts[:-1],parts+[parts[0]],[parts[0]+'x',*parts[1:]]):
            with self.assertRaises(ValueError):drive_by_case(bad)

if __name__=='__main__':unittest.main()
