"""CPTu class definition."""

from cptpy import CPT
from cptpy.constants import GAMMA_W


class CPTu(CPT):

    def __init__(self, depth, qc, fs, u2, gwt=None,
                 depth_to_m=lambda depth: depth, qc_to_kpa=lambda qc: qc,
                 fs_to_kpa=lambda fs: fs, u2_to_kpa=lambda fs: fs):
        """Initialize a `CPTu` object from `qc`, `fs`, and `u2`.

        Parameters
        ----------
        depth : iterable of floats
            Depth for each reading in m. If data are not in units of m
            pass a conversion function using the `depth_to_m` parameter.
        qc : iterable of floats
            Measured cone tip resistance in kPa. If data are not in
            units of kPa pass a conversion function using the
            `qc_to_kPa` parameter.
        fs : iterable of floats
            Measured sleeve friction in kPa. If data are not in units
            of kPa pass a conversion function using the `fs_to_kPa`
            parameter.
        u2 : iterable of floats
            Measured pore water pressure in kPa. If data are not in
            units of kPa pass a conversion function using the
            `u2_to_kPa` parameter.
        gwt : float, optional
            Depth to the ground water table in meters, default is `None`
            indicating it will be requested if/when it is required.
        depth_to_m, qc_to_kpa, fs_to_kpa, u2_to_kpa : function, optional
            User defined conversion function(s) applied to the `depth`,
            `qc`, `fs`, and `u2` data respectively to convert it to
            the correct unit, default involves no modification.




        """
        super().__init__(depth, qc, fs, depth_to_m=depth_to_m,
                         qc_to_kpa=qc_to_kpa, fs_to_kpa=fs_to_kpa)
        self.u2 = self._prepper(u2, u2_to_kpa)
        self._u0 = None
        self.gwt = float(gwt) if gwt is not None else None

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

    def sanity_check(self):
        """Perform's various sanity checks on the provided CPTu data.
        
        Sanity checks include: depth increases monotonically, 2)


        """
        # Depth increases monotonically
