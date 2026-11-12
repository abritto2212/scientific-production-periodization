from copy import deepcopy
import json
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
import unittest
from istl.run_table_d2 import ROOT, OUTPUT, OUTPUT_FILES, read_inputs, case_results, aggregate, reproduce
from istl.check_table_d2 import check

class TableD2Tests(unittest.TestCase):
    def test_manuscript_and_independent_arithmetic(self):
        with TemporaryDirectory() as d:
            report = check(Path(d))
            self.assertEqual((report['cells_checked'],report['mismatches']), (32,0))

    def test_reordering_and_archived_metrics_ignored(self):
        inputs = read_inputs(ROOT)
        expected = case_results(*inputs)
        altered = deepcopy(inputs)
        for records in altered:
            Random(17).shuffle(records)
        for row in altered[2]:
            row['metrics'] = {'mae_years':9999,'exact_count':9999}
        self.assertEqual(case_results(*altered), expected)
        self.assertEqual(aggregate(expected[::-1]),aggregate(expected))

    def test_missing_duplicate_records_rejected(self):
        a,r,h = read_inputs(ROOT)
        item = next(x for x in h if x['case']==2 and x['min_len']==2)
        with self.assertRaises(ValueError):
            case_results(a,r,[*h,item])
        with self.assertRaises(ValueError):
            case_results(a,r,[x for x in h if x is not item])

    def test_byte_reproduction(self):
        with TemporaryDirectory() as d:
            fresh = Path(d)
            check(fresh)
            for name in (*OUTPUT_FILES,'provenance.json','manuscript_comparison.json'):
                self.assertEqual((fresh/name).read_bytes(),(OUTPUT/name).read_bytes(),name)

if __name__ == '__main__':
    unittest.main()
