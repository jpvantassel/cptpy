"""CPTu class definition."""

from cptpy import CPT
from cptpy.constants import GAMMA_W


class CPTu(CPT):
    _ncols_in_cpt = 4
    attrs = ["depth", "qc", "fs", "u2"]

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

        Returns
        -------
        CPTu
            Initialized `CPTu` object.

        """
        super().__init__(depth, qc, fs, depth_to_m=depth_to_m,
                         qc_to_kpa=qc_to_kpa, fs_to_kpa=fs_to_kpa)
        self._cpt[:, 3] = self._prep(u2, u2_to_kpa)
        self.gwt = float(gwt) if gwt is not None else None

    @property
    def u2(self):
        return self._cpt[:, 3]

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

    @property
    def du(self):
        """Excess pore water pressure."""
        return self.u2 - self.u0

    def qt(self, an=0.8):
        """Corrected total cone tip resistance.

        Parameters
        ---------
        an : float, optional
            Net area ratio, according to the Robertson-Gregg CPT Guide
            (2012) `an` can vary between 0.7 - 0.85. ASTM D5778
            recommends 0.8. The ASTM recommendation is provided as the
            default value.
        
        """
        an = float(an)
        if an < 0.7 or an > 0.85:
            msg = "an is outside the recommended range of 0.7-0.85."
            warnings.warn(msg)
        return self.qc + self.u2 * (1-an)

    @property
    def ft(self):
        """Corrected total sleeve friction, alias for fs."""
        return self.fs
