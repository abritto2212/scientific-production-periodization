from copy import deepcopy
import csv
import json
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
import unittest

from istl.run_table_6 import (
    CASES, METHODS, MINIMUM, OUTPUT, OUTPUT_FILES, ROOT, aggregate, case_results,
    file_sha256, read_inputs, reproduce,
)


class Table6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = read_inputs(ROOT)
        cls.rows = case_results(*cls.inputs)

    def test_windows_k_and_chronological_pairs(self):
        expected = {
            4: (2000, 2023, 3, [2011, 2017]),
            6: (2003, 2023, 3, [2011, 2018]),
            7: (2000, 2022, 3, [2013, 2020]),
            8: (2000, 2022, 3, [2009, 2017]),
            9: (2000, 2022, 2, [2012]),
        }
        self.assertEqual([(row['case'], row['method']) for row in self.rows],
                         [(case, method) for case in CASES for method in METHODS])
        for row in self.rows:
            with self.subTest(case=row['case'], method=row['method']):
                self.assertEqual((row['analysis_year_start'], row['analysis_year_end'],
                                  row['k'], row['reference_cut_years']), expected[row['case']])
                self.assertTrue(row['algorithm_feasible'])
                self.assertTrue(row['reference_satisfies_minimum'])
                self.assertEqual(row['min_period_length'], MINIMUM)
                diffs = [cut - ref for cut, ref in
                         zip(row['estimated_cut_years'], row['reference_cut_years'], strict=True)]
                self.assertEqual(row['signed_errors_years'], diffs)
                self.assertEqual(row['mae_years'], sum(map(abs, diffs)) / len(diffs))

    def test_manuscript_aggregates_and_denominators(self):
        # Transcribed from Table 6. The production script never reads these values.
        expected = [(3.60, 2), (3.70, 2), (4.40, 0), (1.70, 1)]
        for row, (mae, exact) in zip(aggregate(self.rows), expected, strict=True):
            with self.subTest(method=row['method']):
                self.assertEqual((row['cases'], row['n_cases'], row['n_boundaries']),
                                 ([4, 6, 7, 8, 9], 5, 9))
                self.assertAlmostEqual(row['macro_mae_years'], mae)
                self.assertEqual(row['exact_matches'], exact)
        self.assertEqual(sum(row['n_cuts'] for row in self.rows if row['method'] == 'equal_k'), 9)
        self.assertEqual(
            [(row['method'], row['case'], predicted) for row in self.rows
             for predicted, error in zip(row['estimated_cut_years'], row['signed_errors_years'])
             if error == 0],
            [('derivative_k_provisional', 4, 2017), ('piecewise_linear_k', 6, 2018),
             ('derivative_k_provisional', 7, 2020), ('piecewise_linear_k', 7, 2013),
             ('equal_k', 9, 2012)],
        )

    def test_reordering_all_inputs_and_outputs(self):
        rng = Random(12)
        shuffled = [list(records) for records in self.inputs]
        for records in shuffled:
            rng.shuffle(records)
        self.assertEqual(case_results(*shuffled), self.rows)
        self.assertEqual(aggregate(list(reversed(self.rows))), aggregate(self.rows))

    def test_uses_archived_cuts_and_ignores_archived_metrics(self):
        analysis, references, archive = deepcopy(self.inputs)
        for row in archive:
            row['metrics'] = {'mae_years': 1000, 'exact_count': 1000}
        self.assertEqual(case_results(analysis, references, archive), self.rows)

    def test_rejects_missing_duplicate_or_incompatible_inputs(self):
        analysis, references, archive = self.inputs
        target = next(row for row in archive if row['case'] == 4 and row['min_len'] == MINIMUM)
        with self.assertRaisesRegex(ValueError, 'Duplicate record'):
            case_results(analysis, references, [*archive, target])
        with self.assertRaisesRegex(ValueError, 'Expected all three archived methods'):
            case_results(analysis, references, [row for row in archive if row is not target])
        for change, message in (
            ({'window': [2001, 2023]}, 'window'),
            ({'phases_input': 2}, 'window, K'),
            ({'algorithm_feasible': False}, 'no feasible partition'),
            ({'cut_years': [2001, 2017]}, 'shorter than min_len'),
        ):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, message):
                case_results(analysis, references, [
                    dict(row, **change) if row is target else row for row in archive
                ])
        with self.assertRaisesRegex(ValueError, 'reference: Segment shorter than min_len'):
            case_results(analysis, [dict(ref, cut_years=[2001, 2017]) if ref['case'] == 4
                                    else ref for ref in references], archive)

    def test_equal_k_matches_verified_archive(self):
        archived = json.loads((ROOT / 'istl/equal_k_results/v1/case_results.json')
                              .read_text(encoding='utf-8'))
        cuts = {row['case']: row['equal_k']['cut_years'] for row in archived if row['case'] in CASES}
        actual = {row['case']: row['estimated_cut_years'] for row in self.rows
                  if row['method'] == 'equal_k'}
        self.assertEqual(actual, cuts)

    def test_reproduces_versioned_files_and_hashes(self):
        with TemporaryDirectory() as directory:
            fresh = Path(directory)
            reproduce(fresh)
            for name in (*OUTPUT_FILES, 'provenance.json'):
                self.assertEqual((fresh / name).read_bytes(), (OUTPUT / name).read_bytes(), name)
            manifest = json.loads((fresh / 'provenance.json').read_text(encoding='utf-8'))
            for key, base in [('input_sha256', ROOT), ('code_sha256', ROOT), ('output_sha256', fresh)]:
                for path, expected in manifest[key].items():
                    self.assertEqual(file_sha256(base / path), expected)
            for name, count in [('case_results.csv', 20), ('aggregates.csv', 4)]:
                with (fresh / name).open(encoding='utf-8', newline='') as stream:
                    self.assertEqual(len(list(csv.DictReader(stream))), count)


if __name__ == '__main__':
    unittest.main()
