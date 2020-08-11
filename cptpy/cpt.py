"""CPT class definition."""

import numpy as np

class CPT():

    def __init__(self, qc, fs, qc_to_kpa=lambda qc:qc, fs_to_kpa=lambda fs:fs):
        """Initialize a `CPT` object from `qc` and `fs`.

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
        qc_to_kpa : function
            User defined conversion function applied `qc` data to
            convert it to units of kPa.
        fs_to_kpa : function
            User defined conversion function applied to `fs` data to
            convert it to units of kPa.

        Returns
        -------
        CPT
            Initialized `CPT` object.
        
        """
        self.qc = self._check_input(qc, qc_to_kpa)
        self.fs = self._check_input(fs, fs_to_kpa)

    def _prepper(self, values, converter):
        """Prepare function inputs.

        Parameters
        ----------
        values : iterable of floats
            Values to be prepared.
        converter : function
            Function to be applied to `values`.

        Returns
        -------
        ndarray
            Values which have been properly prepared.

        """
        values = np.array(values, dtype=np.double)
        values = qc_to_kpa(values)
        return values
