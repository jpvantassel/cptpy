"""Tests for CPT class"""

import numpy as np

import cptpy
from testtools import TestCase, unittest


class Test_CPT(TestCase):

    @classmethod
    def setUpClass(cls):
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

        # Multiple -> TypeError
        cpt = cptpy.CPT(self.dp, self.qc, self.fs)
        self.assertRaises(TypeError, cpt.__delitem__,
                          np.array([0, 2, 4], dtype=int))

    def test_getitem(self):
        for s in [slice(0), slice(0, 2), slice(0, 4, 2)]:
            cpt = cptpy.CPT(self.dp, self.qc, self.fs)
            returned = cpt[s]
            expected = cptpy.CPT(self.dp[s], self.qc[s], self.fs[s])
            self.assertEqual(expected, returned)

if __name__ == "__main__":
    unittest.main()
