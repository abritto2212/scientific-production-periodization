import unittest
import io
import zipfile
from itertools import combinations
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter1d
from periodization import (validate_series, intervals, derivatives, derivative_candidates,
                          piecewise, dynamic_l2, Dynp)
from read_data import load_cases


class ValidationTests(unittest.TestCase):
    def test_invalid_data(self):
        for x,y in [([2000,2000,2001],[1,2,3]),([2002,2001,2000],[1,2,3]),
                    ([2000,2001,2003],[1,2,3]),([2000,2001,2002],[1,None,3]),
                    ([2000,2001,2002],[1,-1,3]),([2000,2001,2002],[1,.5,3]),
                    ([2000,2001,np.nan],[1,2,3]),([2000,2001,2002],[1,np.inf,3])]:
            with self.subTest(x=x,y=y),self.assertRaises(ValueError): validate_series(x,y)

    def test_zero_is_observed(self):
        _,y=validate_series([2000,2001,2002],[0,1,0]); self.assertEqual(y.tolist(),[0,1,0])

    def test_smoothing_keeps_decimals(self):
        y=np.array([0,0,1,0,1,8,10,20,21])
        _,s,*_=derivative_candidates(y)
        self.assertEqual(s.dtype.kind,'f')
        np.testing.assert_allclose(s,gaussian_filter1d(y.astype(float),sigma=2))
        self.assertTrue(np.any(s!=np.floor(s)))
        self.assertFalse(np.array_equal(s,gaussian_filter1d(y,sigma=2)))

    def test_boundary_convention(self):
        x=np.arange(2000,2009)
        self.assertEqual(intervals(x,[3,6]),[dict(start=2000,end=2002,length=3),
            dict(start=2003,end=2005,length=3),dict(start=2006,end=2008,length=3)])
        c,_=dynamic_l2(x,[0,0,0,10,10,10,20,20,20])
        self.assertEqual(c,[3,6]); self.assertEqual(x[c].tolist(),[2003,2006])

    def test_impossible_segmentation(self):
        for fn in (piecewise,dynamic_l2):
            with self.assertRaises(ValueError): fn(np.arange(8),np.arange(8))
            with self.assertRaises(ValueError): fn(np.arange(9),np.arange(9),n_breaks=-1)

    def test_all_segments_and_original_regression_bug(self):
        cases=load_cases(Path(__file__).resolve().parents[1]/'data_articles/data_articles.xlsx')
        self.assertEqual(sum(len(x) for _,x,_,_ in cases),226)
        for _,x,y,_ in cases:
            for cuts in [piecewise(x,y)[0],dynamic_l2(x,y)[0],derivatives(x,y)[0]]:
                spans=intervals(x,cuts)
                self.assertTrue(all(s['length']>=3 for s in spans))
                covered=[yr for s in spans for yr in range(s['start'],s['end']+1)]
                self.assertEqual(covered,x.tolist())
        _,x,y,_=cases[8]
        old,_=piecewise(x,y,legacy=True)
        self.assertEqual(np.diff([0,*old,len(x)]).tolist(),[18,2,3])
        self.assertTrue(min(np.diff([0,*piecewise(x,y)[0],len(x)]))>=3)

    def test_dynp_annual_candidates_and_global_optimum(self):
        self.assertEqual(Dynp().jump,5)
        x=np.arange(12); y=np.array([0]*4+[10]*4+[20]*4)
        c,p=dynamic_l2(x,y)
        self.assertEqual(c,[4,8]); self.assertEqual(p['jump'],1)
        costs=[]
        for cuts in combinations(range(3,10),2):
            edges=[0,*cuts,len(y)]
            if min(np.diff(edges))>=3:
                costs.append(sum(np.sum((y[a:b]-np.mean(y[a:b]))**2) for a,b in zip(edges[:-1],edges[1:])))
        self.assertAlmostEqual(p['sse'],min(costs))

    def test_zero_breaks_and_constant_series(self):
        x=np.arange(12); y=np.zeros(12)
        self.assertEqual(derivatives(x,y)[0],[])
        for fn in (piecewise,dynamic_l2): self.assertEqual(fn(x,y,n_breaks=0)[0],[])

    def test_derivative_length_filter_is_explicit(self):
        x=np.arange(24); y=np.array([0]*20+[10,50,200,500])
        c,p,_=derivatives(x,y)
        self.assertEqual(sorted(c+p['rejected_indices']),p['candidate_indices'])
        self.assertTrue(min(np.diff([0,*c,len(x)]))>=3)

    def test_xlsx_reader_rejects_missing_cells_and_duplicate_years(self):
        source=Path(__file__).resolve().parents[1]/'data_articles/data_articles.xlsx'
        # Modify temporary copies only; original data bytes are preserved.
        for before,after in [('<v>2001</v>','<v>2000</v>'),
                             ('<v>2001</v>',''),('<v>5</v>','')]:
            with self.subTest(after=after):
                target=io.BytesIO()
                with zipfile.ZipFile(source) as zin,zipfile.ZipFile(target,'w') as zout:
                    for entry in zin.infolist():
                        data=zin.read(entry.filename)
                        if entry.filename=='xl/worksheets/sheet1.xml':
                            data=data.decode().replace(before,after,1).encode()
                        zout.writestr(entry,data)
                target.seek(0)
                with self.assertRaises(ValueError): load_cases(target)

    def test_regression_global_optimum(self):
        x=np.arange(12); y=np.array([2,3,1,5,8,6,6,9,20,5,3,2])
        cuts,p=piecewise(x,y)
        scores=[]
        for a,b in combinations(range(3,10),2):
            if b-a>=3 and len(y)-b>=3:
                scores.append(sum(float(np.sum((v-np.polyval(np.polyfit(t,v,1),t))**2))
                    for t,v in [(x[:a],y[:a]),(x[a:b],y[a:b]),(x[b:],y[b:])]))
        self.assertAlmostEqual(p['sse'],min(scores))


if __name__=='__main__': unittest.main()
