"""CPT class definition."""

import numpy as np


class CPT():

    def __init__(self, depth, qc, fs, depth_to_m=lambda depth: depth,
                 qc_to_kpa=lambda qc: qc, fs_to_kpa=lambda fs: fs):
        """Initialize a `CPT` object from `depth`, `qc`, and `fs`.

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
        depth_to_m, qc_to_kpa, fs_to_kpa : function, optional
            User defined conversion function(s) applied to the `depth`,
            `qc`, and `fs` data respectively to convert it to
            the correct unit, default involves no modification.

        Returns
        -------
        CPT
            Initialized `CPT` object.

        """
        self.depth = self._prepper(depth, depth_to_m)
        self.qc = self._prepper(qc, qc_to_kpa)
        self.fs = self._prepper(fs, fs_to_kpa)

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
        # TODO (jpv): Is the assumption of an elemental function good here?
        values = qc_to_kpa(values)
        return values
