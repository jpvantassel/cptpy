"""Tests for CPT class"""

import warnings

import numpy as np
import pandas as pd

import cptpy
from testtools import TestCase, unittest, get_full_path


class Test_CPT(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.full_path = get_full_path(__file__)

        cls.dp = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        cls.qc = np.array([10, 10.1, 10.3, 10.2, 10.5])*1000
        cls.fs = np.array([100., 120, 130, 110, 140])

    def test_init(self):
        cpt = cptpy.CPT(self.dp, self.qc, self.fs)

        for exp, ret in [("dp", "depth"), ("qc", "qc"), ("fs", "fs")]:
            expected = getattr(self, exp)
            returned = getattr(cpt, ret)
            self.assertArrayEqual(expected, returned)

    def test_converter_functions(self):
        def depth_to_m(depth):
            return depth*2. + 1

        def qc_to_kpa(qc):
            return qc * 1.1 - 0.2

        def fs_to_kpa(fs):
            return fs / 1.1 + 0.2

        cpt = cptpy.CPT(self.dp, self.qc, self.fs, depth_to_m=depth_to_m,
                        qc_to_kpa=qc_to_kpa, fs_to_kpa=fs_to_kpa)

        for exp, ret, func in [("dp", "depth", depth_to_m),
                               ("qc", "qc", qc_to_kpa),
                               ("fs", "fs", fs_to_kpa)]:
            expected = func(np.array(getattr(self, exp)))
            returned = getattr(cpt, ret)
            self.assertArrayEqual(expected, returned)
    
    def test_sanity_check(self):
            
        # Depths less than zero
        depth = [-0.1, 0, 0.1, 0.2, 0.3]
        returned = cptpy.CPT(depth, self.qc, self.fs)
        returned.sanity_check(apply_fixes="yes")

        expected = cptpy.CPT(depth, self.qc, self.fs)[2:]
        self.assertEqual(expected, returned)

        # Depth out of order
        depth = [0.1, 0.2, 0.3, 0.5, 0.4]
        returned = cptpy.CPT(depth, self.qc, self.fs)
        returned.sanity_check(apply_fixes="yes")

        expected = cptpy.CPT(depth, self.qc, self.fs)
        expected._cpt = expected._cpt[[0, 1, 2, 4, 3], :]
        self.assertEqual(expected, returned)

        # Duplicate depth measurement
        depth = [0.1,0.2,0.2,0.3,0.4]
        returned = cptpy.CPT(depth, self.qc, self.fs)
        returned.sanity_check(apply_fixes="yes")

        expected = cptpy.CPT(depth, self.qc, self.fs)
        del expected[2]
        self.assertEqual(expected, returned)

        # qc and/or fs less than zero
        troublesome_values = [-1, 0]
        expected = cptpy.CPT(self.dp, self.qc, self.fs)
        del expected[1]

        for value in troublesome_values:
            qc = np.array(self.qc)
            qc[1] = value            
            returned = cptpy.CPT(self.dp, qc, self.fs)
            returned.sanity_check(apply_fixes="yes")
            self.assertEqual(expected, returned)

            fs = np.array(self.fs)
            fs[1] = value
            returned = cptpy.CPT(self.dp, self.qc, fs)
            returned.sanity_check(apply_fixes="yes")
            self.assertEqual(expected, returned)

            returned = cptpy.CPT(self.dp, qc, fs)
            returned.sanity_check(apply_fixes="yes")
            self.assertEqual(expected, returned)

    # def test_rf(self):
    #     df = pd.read_csv(self.full_path + "/data/isbt/input.csv")
    #     cpt = cptpy.CPT(depth=df.depth, qc=df.qc, fs=df.fs)
    #     returned = cpt.friction_ratio
    #     df2 = pd.read_csv(self.full_path + "/data/isbt/results.csv")
    #     expected = df2.fr.to_numpy()
    #     self.assertArrayAlmostEqual(expected, returned, places=2)

    def test_isbt_robertson_2010(self):
        # Based on Figure 3 from Robertson 2010
        df = pd.read_csv(self.full_path + "data/isbt/input.csv")
        cpt = cptpy.CPT(depth=df.depth, qc=df.qc, fs=df.fs)
        returned = cpt.isbt(procedure="Robertson 2010")

        df2 = pd.read_csv(self.full_path + "data/isbt/isbt.csv")
        expected = df2.isbt.to_numpy()
        self.assertArrayAlmostEqual(expected, returned, places=2)

    def test_len(self):
        cpt = cptpy.CPT(self.dp, self.qc, self.fs)
        expected = self.dp.size
        returned = len(cpt)
        self.assertEqual(expected, returned)

    def test_del(self):
        # Single
        cpt = cptpy.CPT(self.dp, self.qc, self.fs)
        del cpt[1]

        for exp, ret in [("dp", "depth"), ("qc", "qc"), ("fs", "fs")]:
            index = np.array([0, 2, 3, 4], dtype=int)
            expected = np.array(getattr(self, exp))[index]
            returned = getattr(cpt, ret)
            self.assertArrayEqual(expected, returned)

    def test_getitem(self):
        for s in [slice(0), slice(0, 2), slice(0, 4, 2)]:
            cpt = cptpy.CPT(self.dp, self.qc, self.fs)
            returned = cpt[s]
            expected = cptpy.CPT(self.dp[s], self.qc[s], self.fs[s])
            self.assertEqual(expected, returned)

if __name__ == "__main__":
    unittest.main()
