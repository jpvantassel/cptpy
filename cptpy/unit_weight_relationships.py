"""Unit weight relationships."""

import numpy as np

from .constants import GAMMA_W, PA
from .register import UnitWeightRegistry


@UnitWeightRegistry.register("Robertson and Cabal 2010")
def robertson_and_cabal_2010(self, **kwargs):
    """Estimate unit weight from Robertson and Cabal (2010) eq2."""
    gs = kwargs.get("gs", 2.65)
    return GAMMA_W*(0.27*np.log10(self.rf) + 0.36*np.log10(self.qt()/PA) + 1.236)*gs/2.65


@UnitWeightRegistry.register("Robertson 2010")
def robertson_2010(self, **kwargs):
    """Common alternate name for Robertson and Cabal (2010)"""
    return robertson_and_cabal_2010(self, **kwargs)


@UnitWeightRegistry.register("Mayne et al. 2010")
def mayne_et_al_2010(self, **kwargs):
    """Estimate unit weight from Mayne et al. (2010)."""
    # Simple but less than ideal b/c use of z rather than VEZ - eq 7.
    # gamma_t =  11.46 + 0.33*np.log10(self.depth) + 3.10*np.log10(self.fs) + 0.70*np.log10(self.qt)

    # Complex but more accurate - eq 8.
    # gamma_t = 1.81*GAMMA_W*\
    #           np.power(self.ves/PA, 0.05)*\
    #           np.power((self.qt - self.sigma_v)/PA, 0.017)*\
    #           np.power(self.fs/PA, 0.073)*\
    #           np.power(self.bq + 1, 0.16)

    # Simple, but recursive - eq 9.
    # TODO (jpv): Finish recursion.
    self.gamma_t


    return 1.95*GAMMA_W*np.power((self.ves/PA), 0.06)*np.power((self.fs/PA), 0.06)


@UnitWeightRegistry.register("Mayne and Peuchen 2012")
def mayne_and_peuchen_2012(self, **kwargs):
    """Estimate unit weight from Mayne et al. (2010)."""
    return 12 + 1.5*np.log(self.fs + 1)
