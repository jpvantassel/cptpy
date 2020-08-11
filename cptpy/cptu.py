"""CPTu class definition."""

from cptpy import CPT


class CPTu(CPT):

    def __init__(self, qc, fs, u2, gwt=None, qc_to_kpa=lambda qc: qc,
                 fs_to_kpa=lambda fs: fs, u2_to_kpa=lambda fs: fs):
        """Initialize a `CPTu` object from `qc`, `fs`, and `u2`.

        Parameters
        ----------
        qc : iterable of floats
            Measured cone tip resistance in kPa. If data are not in units
            of kPa pass a conversion function using the `qc_to_kPa`
            parameter.
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
        qc_to_kpa, fs_to_kpa, u2_to_kpa : function, optional
            User defined conversion function(s) applied to the `qc`,
            `fs`, and `u2` data respectively to convert it to units of
            kPa, default involves no modification.

        Returns
        -------
        CPTu
            Initialized `CPTu` object.
        
        """
        
