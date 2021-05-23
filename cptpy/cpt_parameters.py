"""Analysis Parameters for CPT"""

from .cptu import CPT
from .constants import GAMMA_W, PA
from .register import CPTUnitWeightRegistry

class CPT_Parameters():

    def __init__(self, cpt, gwt=None):
        """

        gwt : float, optional
            Depth to the ground water table in meters, default is `None`
            indicating it will be requested if/when it is required.

        """
        if not isinstance(cpt, CPT):
            msg = f"cpt must an instance of CPT, not {type(cpt)}."
            raise ValueError(msg)
        self.gwt = float(gwt) if gwt is not None else None
        self.cpt = cpt
    
    @property
    def u0(self):
        """Hydrostatic pore water pressure."""
        try:
            self._u0 = (self.depth - self.gwt)*GAMMA_W
        except AttributeError:
            msg = "The calculation you requested requires the definition "
            msg += "of hydrostatic pore water pressure (u0), however the "
            msg += "ground water table (gwt) is not defined. Define `gwt` "
            msg += "before re-attempting."
            raise ValueError(msg)
        else:
            self._u0[self.depth <= self.gwt] = 0
        return self._u0

    def unit_weight(self, procedure="Robertson and Cabal 2010", gs=2.65,
                    niterations=10):
        """Estimate soil unit weight.

        Parameters
        ----------
        procedure : {"Robertson and Cabal 2010", "Robertson 2010", "Mayne et al. 2010", "Mayne 2014"}, optional
            Select the desired procedure for estimating soil unit
            weight.
        gs : float, optional
            Specific gravity of solids, default is 2.65.
        niterations : int, optional
            Maximum number of allowed iterations for recursive methods,
            default is 10. The recursive techniques are
            Mayne et al. 2010, other may be added in the future.

        Returns
        -------
        ndarray
            Containing the estimated unit weights.

        References
        ----------
        Robertson, P. K., & Cabal, K. L. (2010). Estimating soil unit
        weight from CPT. 2nd International Symposium on Cone Penetration
        Testing.

        Mayne, P.W., Peuchen, J., & Bouwmeester, D. (2010). Soil unit
        weight estimation from CPTs. Presented at the 2nd International
        Symposium on Cone Penetration Testing (CPT10), Omnipress,
        Huntington Beach, CA, USA, pp. 169–176.

        Mayne, P.W. (2014). Interpretation of geotechnical parameters
        from seismic piezocone tests. Presented at the 3rd International
        Symposium on Cone Pentration Testing (CPT’14), Las Vegas,
        Nevada, USA, pp. 47–73.

        Notes
        -----
        Robertson and Cabal (2010) is regularly cited as Robertson
        (2010) (e.g., in Robertson-Gregg Guide to CPT testing for
        Geotechnical Engineering 5th ed), so Robertson (2010) is
        included here as an alias to Robertson and Cabal (2010).

        """
        return CPTUnitWeightRegistry[procedure](cpt, gs=gs, niterations=niterations)

