import hashlib
import json
from pathlib import Path
import unittest
import zipfile
import numpy as np
from run import inputs,record,summaries,METHODS,CUTS,HERE,ROOT
from read_data import load_cases
from prepare_data import validate_existing


class Delivery03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full,cls.analysis,cls.refs=inputs()
        cls.records=[record(ref,x,y,method,m) for ref,(_,x,y,_) in zip(cls.refs,cls.analysis)
                     for m in (2,3) for method in METHODS]

    def test_single_approved_correction_and_source_match(self):
        old=load_cases(HERE/'sources/base_data_articles.xlsx')
        changed=[(i,int(a),int(b),int(c)) for i,((_,x,y,_),(_,xx,yy,_)) in enumerate(zip(old,self.full),1)
                 for a,b,c in zip(x,y,yy) if b!=c]
        self.assertEqual(changed,[(2,2004,2,1)])
        _,x,y,_=self.full[1]
        self.assertEqual(y[:2].tolist(),[1,1]);self.assertEqual(int(y.sum()),1693)
        audit=json.loads((HERE/'data/data_audit.json').read_text(encoding='utf-8'))
        self.assertTrue(audit['drive_matches_corrected_all_observations'])
        self.assertEqual(audit['other_annual_observations_unchanged'],225)

    def test_xlsx_only_one_xml_member_changed(self):
        with zipfile.ZipFile(HERE/'sources/base_data_articles.xlsx') as a,zipfile.ZipFile(ROOT/'data_articles/data_articles.xlsx') as b:
            self.assertEqual(a.namelist(),b.namelist())
            self.assertEqual([n for n in a.namelist() if a.read(n)!=b.read(n)],['xl/worksheets/sheet2.xml'])

    def test_preparation_refuses_unapproved_existing_changes(self):
        old=load_cases(HERE/'sources/base_data_articles.xlsx')
        validate_existing(old,self.full)
        bad=[(s,x.copy(),y.copy(),b) for s,x,y,b in self.full]
        bad[1][2][2]+=1
        with self.assertRaises(ValueError):validate_existing(old,bad)

    def test_case6_window_and_totals_all_methods(self):
        _,x,y,_=self.full[5];_,ax,ay,_=self.analysis[5]
        self.assertEqual(y[x==2004].tolist(),[7]);self.assertEqual(y[x==2024].tolist(),[84])
        self.assertEqual(int(y.sum()),796);self.assertEqual(int(ay.sum()),712)
        self.assertEqual(ax.tolist(),list(range(2003,2024)))
        for r in self.records:
            if r['case']==6:self.assertEqual((r['window'],r['total']),([2003,2023],712))

    def test_approved_subtotals_and_reference_boundaries(self):
        for case,expected in [(7,[62,109,102]),(9,[98,385])]:
            _,x,y,_=self.analysis[case-1];ref=self.refs[case-1]
            subtotals=[int(y[(x>=p['start'])&(x<=p['end'])].sum()) for p in ref['published_intervals']]
            self.assertEqual(subtotals,expected)
        self.assertEqual(int(self.full[6][2].sum()),273)
        self.assertEqual(int(self.full[7][2].sum()),1004)
        self.assertEqual(int(self.full[8][2].sum()),483)
        for r in self.refs:self.assertEqual(r['cut_years'],CUTS[r['case']])

    def test_separate_viability_reference_conflict_and_unknown_K(self):
        for r in self.records:
            if r['case']==2 and r['min_len']==3:
                self.assertTrue(r['algorithm_feasible']);self.assertFalse(r['reference_satisfies_minimum'])
                self.assertIsNone(r['metrics'])
            if r['case']==10:self.assertIsNone(r['algorithm_feasible']);self.assertIsNone(r['metrics']);self.assertIsNone(r['cut_years'])
            if r['case']==1 and r['method']==METHODS[0]:self.assertFalse(r['algorithm_feasible']);self.assertIsNone(r['cut_years'])

    def test_segments_K_length_and_no_overlap(self):
        for r in self.records:
            if r['algorithm_feasible']:
                self.assertEqual(len(r['cut_years']),r['phases_input']-1)
                self.assertTrue(all(p['length']>=r['min_len'] for p in r['intervals']))
                covered=[yr for p in r['intervals'] for yr in range(p['start'],p['end']+1)]
                self.assertEqual(covered,list(range(r['window'][0],r['window'][1]+1)))

    def test_only_common_set_aggregates_and_expected_denominators(self):
        ss=summaries(self.records)
        for m in (2,3):
            groups={a['scope'] for a in ss if a['min_len']==m}
            for scope in groups:
                rows=[a for a in ss if a['min_len']==m and a['scope']==scope]
                self.assertTrue(all(a['cases']==rows[0]['cases'] for a in rows))
                self.assertTrue(all(a['n_boundaries']==rows[0]['n_boundaries'] for a in rows))
        for a in ss:
            if a['scope']=='common_three_methods':
                self.assertEqual(a['cases'],[2,3,4,5,6,7,8,9] if a['min_len']==2 else [4,7,8,9])
                self.assertEqual(a['n_boundaries'],15 if a['min_len']==2 else 7)
            if a['scope']=='common_three_methods_both_minima':self.assertEqual(a['cases'],[4,7,8,9])

    def test_verification_scope_not_bibliographic_audit(self):
        for r in self.refs:self.assertFalse(r['primary_bibliographic_records_audited'])
        self.assertTrue(self.refs[2]['annual_figure_counts_verified'])
        for i in (1,5,6,7,8):self.assertTrue(self.refs[i]['annual_figure_counts_verified'])
        for i in (6,7,8):
            self.assertEqual(self.refs[i]['boundary_authority'],'published textual phases; approved by Direction')
            self.assertIsNone(self.refs[i]['textual_vs_graphical_header_conflict']['verbatim_graphical_heading'])

    def test_frozen_remote_files_preserved_except_corrected_workbook(self):
        manifest=json.loads((HERE/'sources/base_repository_manifest.json').read_text(encoding='utf-8'))
        count=0
        for entry in manifest['files']:
            p=ROOT/entry['path']
            if not p.is_file() or entry['path']=='data_articles/data_articles.xlsx':continue
            b=p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
            self.assertEqual(actual,entry['git_blob_sha'],entry['path']);count+=1
        self.assertGreater(count,50)


if __name__=='__main__':unittest.main()
