"""Unit weight relationships."""

import logging

import numpy as np

from .constants import GAMMA_W, PA
from .register import CPTUnitWeightRegistry, CPTuUnitWeightRegistry
from .geotech_tools import vertical_effective_stress

logger = logging.getLogger("cptpy.par_unit_weight")

@CPTuUnitWeightRegistry.register("Robertson and Cabal 2010")
def robertson_and_cabal_2010(cptu, **kwargs):
    """Estimate unit weight from Robertson and Cabal (2010) eq2."""
    gs = kwargs.get("gs", 2.65)
    return GAMMA_W*(0.27*np.log10(cptu.rf) + 0.36*np.log10(cptu.qt()/PA) + 1.236)*gs/2.65


@CPTuUnitWeightRegistry.register("Robertson 2010")
def robertson_2010(cptu, **kwargs):
    """Common alternate name for Robertson and Cabal (2010)"""
    return robertson_and_cabal_2010(cptu, **kwargs)


@CPTUnitWeightRegistry.register("Mayne et al. 2010")
def mayne_et_al_2010_cpt(cpt, **kwargs):
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
    unit_weight = np.ones_like(cpt.depth)*19.5
    pore_pressure = cpt.u0
    for citeration in range(kwargs["niterations"]):
        ves = vertical_effective_stress(cpt.depth, unit_weight, pore_pressure)
        new_unit_weight = 1.95*GAMMA_W*np.power((ves/PA), 0.06)*np.power((cpt.fs/PA), 0.06)
        max_diff = np.max(np.abs(new_unit_weight - unit_weight))
        unit_weight = new_unit_weight
        if max_diff < 0.01:
            break
    if max_diff > 0.01:
        msg = "Unit weight formula from Mayne et al. (2010) did not"
        msg += "converge. Maximum difference between iterations was"
        msg += "{max_diff:.4f} kN/m3. Try increasing niterations."
        raise RuntimeError(msg)
    return unit_weight

@CPTuUnitWeightRegistry.register("Mayne et al. 2010")
def mayne_et_al_2010_cptu(cptu, **kwargs):
    return mayne_et_al_2010_cpt(cptu, **kwargs)

@CPTUnitWeightRegistry.register("Mayne 2014")
def mayne_and_peuchen_2012_cpt(cpt, **kwargs):
    """Estimate unit weight from Mayne (2014)."""
    return 12 + 1.5*np.log(cpt.fs + 1)

@CPTUnitWeightRegistry.register("Mayne 2014")
def mayne_and_peuchen_2012_cptu(cptu, **kwargs):
    return mayne_and_peuchen_2012_cpt(cptu, **kwargs)