"""Tests for CPTu class"""

import warnings

import numpy as np
import pandas as pd

import cptpy
from testtools import TestCase, unittest, get_full_path


class Test_CPT(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.full_path = get_full_path(__file__)

    def test_unit_weight(self):
        # Robertson and Cabal 2010, aka Robertson 2010
        g_on_gws = [1.4, 1.6, 1.8, 2.0, 2.2]
        path = f"{self.full_path}data/unit_weight/"
        fnames = [f"{path}g_on_gw_{x}.csv" for x in g_on_gws]

        for g_on_gw, fname in zip(g_on_gws, fnames):
            df = pd.read_csv(fname, names=["fs/qt", "qt/pa"])
            qt = df["qt/pa"].to_numpy()*cptpy.constants.PA
            fs = df["fs/qt"].to_numpy()*qt/100

            # Use u2 = 0, so qc=qt
            cpt = cptpy.CPTu(depth=[0]*len(qt), qc=qt, fs=fs,
                             u2=np.zeros_like(qt))
            gamma = cpt.unit_weight(procedure="Robertson and Cabal 2010")
            returned = gamma/cptpy.constants.GAMMA_W
            expected = g_on_gw * np.ones_like(returned)
            self.assertArrayAlmostEqual(expected, returned, places=1)


if __name__ == "__main__":
    unittest.main()
