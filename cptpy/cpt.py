"""CPT class definition."""

import warnings

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

    def sanity_check(self, apply_fixes="prompt"):
        """Perform's various sanity checks on the provided `CPT` data.

        Sanity checks include: depth values are strictly greater than
        zero, depth increases monotonically, `qc` and `fs` is greater
        than zero at all depths,  

        Parameters
        ----------
        apply_fixes : {"yes", "no", "prompt"}, optional
            Most of the sanity checks have simple solutions
            preprogrammed. To automatically apply the fixes pass `"yes"`
            , to ingore the fixes pass `"no"`, to have the program
            prompt for authorization use `"prompt"`, the default is 
            `"prompt"`.

        Returns
        -------
        None
            May update `CPT` state if `apply_fixes` is `"yes"` or
            `"prompt"`.

        """
        if apply_fixes not in ["yes", "no", "prompt"]:
            msg = f"apply_fixes='{apply_fixes}' is not recognized try: "
            msg += "'yes', 'no', or 'prompt' instead."
            raise ValueError(msg)

        # Depth of zero.
        if np.any(self.depth == 0):
            indices_to_delete = []
            for index in np.argwhere(self.depth == 0):
                msg =  "                                    Depth, qc, fs\n"             
                msg += "A reading at zero depth was found: "
                msg += f"{np.round(self.depth,2)}, {np.round(self.qc,2)}, {np.round(self.fs,2)}"
                warings.warn(msg)

                response = "n"
                if apply_fixes == "prompt":
                    response = input("Discard zero depth reading? (y/n) ")
                
                if response == "y" or apply_fixes = "yes":
                    indices_to_delete.append(index)
            
                

        # Depth increases monotonically.
        diff = self.depth[:-1] - self.depth[1:] 
        if np.any(diff <= 0)

        # qc and fs are greater than zero at all depths.

        #

    def __delitem__(self, key):
        for attr in ["depth", "qc", "fs"]:
            setattr(self, attr, getattr(self, attr)[key])
    
    # def __getitem__(self, key):
