import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np

from istl.equal_k import equal_k
from istl.run_equal_k import OUTPUT, case_results, load_inputs, reproduce, summaries


# Transcription of manuscript Table D1, independent of the integrated inputs.
TABLE_D1 = {
    1: (2000, 2023, 4, [2007, 2013, 2019], [2006, 2012, 2018], 1.0),
    2: (2004, 2021, 3, [2014, 2020], [2010, 2016], 4.0),
    3: (2000, 2022, 3, [2009, 2017], [2008, 2016], 1.0),
    4: (2000, 2023, 3, [2011, 2017], [2008, 2016], 2.0),
    5: (2003, 2024, 3, [2012, 2018], [2011, 2018], 0.5),
    6: (2003, 2023, 3, [2011, 2018], [2010, 2017], 1.0),
    7: (2000, 2022, 3, [2013, 2020], [2008, 2016], 4.5),
    8: (2000, 2022, 3, [2009, 2017], [2008, 2016], 1.0),
    9: (2000, 2022, 2, [2012], [2012], 0.0),
}


class EqualKTests(unittest.TestCase):
    def assert_partition(self, result, years, lengths, minimum):
        self.assertTrue(result['algorithm_feasible'])
        self.assertIsNone(result['reason'])
        segments = result['intervals']
        self.assertEqual(len(segments), len(lengths))
        self.assertEqual([segment['length'] for segment in segments], lengths)
        self.assertGreaterEqual(min(lengths), minimum)
        self.assertEqual([year for segment in segments
                          for year in range(segment['start'], segment['end'] + 1)],
                         list(years))
        self.assertEqual(result['cut_years'], [segment['start'] for segment in segments[1:]])
        self.assertEqual(result['cut_years'], [years[i] for i in result['cut_indices']])

    def test_coverage_minimum_and_remainder_order(self):
        for n, k, lengths in [(11, 4, [3, 3, 3, 2]), (12, 4, [3, 3, 3, 3]), (2, 1, [2])]:
            with self.subTest(n=n, k=k):
                years = range(2000, 2000 + n)
                self.assert_partition(equal_k(years, k, 2), years, lengths, 2)

    def test_invalid_inputs_raise(self):
        for years in ([], [2000, 2002], [2000, 2000], [2001, 2000],
                      [2000, 2001.5], [2000, np.nan], [[2000, 2001]]):
            with self.subTest(years=years), self.assertRaises(ValueError):
                equal_k(years, 1, 2)
        for k, minimum in ((0, 2), (True, 2), (1.5, 2), (1, 1), (1, 2.5), (1, False)):
            with self.subTest(k=k, minimum=minimum), self.assertRaises(ValueError):
                equal_k([2000, 2001], k, minimum)

    def test_infeasible_retains_parameters(self):
        for n, k, minimum in [(1, 1, 2), (7, 3, 3), (2, np.int64(2**62), 4)]:
            with self.subTest(n=n, k=k, minimum=minimum):
                result = equal_k(range(2000, 2000 + n), k, minimum)
                self.assertFalse(result['algorithm_feasible'])
                self.assertIn('Insufficient observations', result['reason'])
                for key in ('cut_indices', 'cut_years', 'intervals'):
                    self.assertIsNone(result[key])
                self.assertEqual(result['parameters']['n_periods'], k)
                self.assertEqual(result['parameters']['min_period_length'], minimum)

    def test_manuscript_cases_and_aggregates(self):
        years, references = load_inputs()
        # Reverse reference order to verify the case-ID join.
        results = case_results(years, dict(reversed(list(references.items()))))
        for case, (start, end, k, published, cuts, mae) in TABLE_D1.items():
            with self.subTest(case=case):
                row = results[case]
                self.assertEqual((row['analysis_year_start'], row['analysis_year_end'],
                                  row['n_periods'], row['reference_cut_years']),
                                 (start, end, k, published))
                self.assertEqual(row['equal_k']['cut_years'], cuts)
                self.assertEqual(row['agreement']['mae_years'], mae)
                q, r = divmod(end - start + 1, k)
                self.assert_partition(row['equal_k'], years[case],
                                      [q + 1] * r + [q] * (k - r), 2)
        self.assertEqual(results[1]['scope'], 'descriptive_only')
        self.assertIsNone(results[10]['equal_k'])
        self.assertIsNone(results[10]['agreement'])
        self.assertEqual(
            [(a['cases'], a['min_period_length'], a['n_cases'], a['n_boundaries'],
              a['macro_mae_years'], a['exact_matches']) for a in summaries(results)],
            [(list(range(2, 10)), 2, 8, 15, 1.75, 2),
             ([4, 7, 8, 9], 2, 4, 7, 1.875, 1),
             ([4, 6, 7, 8, 9], 2, 5, 9, 1.70, 1)],
        )

    def test_versioned_outputs_are_reproducible(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            reproduce(output)
            for name in ('case_results.json', 'aggregates.json', 'table_d1.csv',
                         'table_d2_equal_k.csv'):
                self.assertEqual((output / name).read_bytes(), (OUTPUT / name).read_bytes(), name)
            with (output / 'table_d1.csv').open(encoding='utf-8', newline='') as source:
                d1 = [(int(row['case']), row['window'], int(row['k']), row['reference_cuts'],
                       row['equal_k_cuts'], float(row['case_mae_years']))
                      for row in csv.DictReader(source)]
            self.assertEqual(d1, [(case, f'{start}–{end}', k, ', '.join(map(str, reference)),
                                  ', '.join(map(str, equal_cuts)), mae)
                                 for case, (start, end, k, reference, equal_cuts, mae)
                                 in TABLE_D1.items()])
            with (output / 'table_d2_equal_k.csv').open(encoding='utf-8', newline='') as source:
                actual = [(int(row['case']), float(row['equal_k_mae_years']))
                          for row in csv.DictReader(source)]
            self.assertEqual(actual, [(case, TABLE_D1[case][-1]) for case in range(2, 10)])


if __name__ == '__main__':
    unittest.main()
