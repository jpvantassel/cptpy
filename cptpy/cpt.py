"""CPT class definition."""

import warnings

import numpy as np


class CPT():
    _ncols_in_cpt = 3
    attrs = ["depth", "qc", "fs"]

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
        self._cpt = np.empty((len(depth), self._ncols_in_cpt), dtype=np.double)
        self._cpt[:, 0] = self._prep(depth, depth_to_m)
        self._cpt[:, 1] = self._prep(qc, qc_to_kpa)
        self._cpt[:, 2] = self._prep(fs, fs_to_kpa)

    @property
    def depth(self):
        return self._cpt[:, 0]

    @property
    def qc(self):
        return self._cpt[:, 1]

    @property
    def fs(self):
        return self._cpt[:, 2]

    @staticmethod
    def _prep(values, converter):
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
        values = converter(values)
        return values

    def _safety_check(self):
        """Check state of `CPT`.

        Perform's various checks on `CPT` including: length of all
        `self.attrs` are equal, 

        """
        # Check all attributes are the same length.
        master_length = len(self)
        for attr in self.attrs:
            if len(getattr(self, attr)) != master_length:
                raise ValueError("Length of attributes are inconsistent.")

    def sanity_check(self, apply_fixes="prompt"):
        """Perform's various sanity checks on the provided `CPT` data.

        Sanity checks include: depth values are strictly greater than
        zero, depth values increases monotonically, `qc` and `fs` are
        greater than zero at all depths.

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

        # Depth less than or equal to zero.
        if np.any(self.depth <= 0):
            indices_to_delete = []
            problematic_indices = np.argwhere(self.depth <= 0)
            for index in problematic_indices:
                msg = "A reading at a depth less than zero was found: "
                msg += f"{np.round(self._cpt[index])}"
                warnings.warn(msg)

                response = "n"
                if apply_fixes == "prompt":
                    response = input("Discard zero depth reading? (y/n) ")

                if response == "y" or apply_fixes == "yes":
                    indices_to_delete.append(index)

            del self[indices_to_delete]

        # Depth increases monotonically.
        diff = self.depth[1:] - self.depth[:-1]
        if np.any(diff <= 0):
            warnings.warn("Depths readings do not increase monotonically.")

            response = "n"
            if apply_fixes == "prompt":
                response = input("Sort readings by depth? (y/n) ")
            
            if response == "y" or apply_fixes == "yes":
                self._cpt = self._cpt[np.argsort(self.depth), :]

        # No duplicate depth measurements.
        diff = self.depth[1:] - self.depth[:-1]
        if np.any(diff < 1E-6):

            indices_to_delete = []
            problematic_indices = np.argwhere(diff < 1E-6)
            for index in problematic_indices:
                msg = "A duplicate depth reading has been found: "
                msg += f"{np.round(self._cpt[index])}"
                warnings.warn(msg)

                response = "n"
                if apply_fixes == "prompt":
                    response = input("Discard extra depth reading? (y/n) ")

                if response == "y" or apply_fixes == "yes":
                    indices_to_delete.append(index+1)

            del self[indices_to_delete]

        # qc and fs are greater than zero at all depths.
        if np.any(self._cpt <= 0):
            indices_to_delete = []
            problematic_indices = np.argwhere(np.logical_or(self._cpt[:, 1] <= 0, self._cpt[:, 2] <= 0))
            for index in problematic_indices:
                msg = "A qc and/or fs value was found to be less than or equal to zero: "
                msg += f"{np.round(self._cpt[index],1)}"
                warnings.warn(msg)

                response = "n"
                if apply_fixes == "prompt":
                    response = input("Discard reading? (y/n) ")

                if response == "y" or apply_fixes == "yes":
                    indices_to_delete.append(index)

            del self[indices_to_delete]

    @property
    def rf(self):
        """Alias for `friction_ratio`."""
        return self.friction_ratio

    @property
    def friction_ratio(self):
        """CPT friction ratio (Rf)."""
        return (self.fs / self.qc) * 100

    def __len__(self):
        """Define len (i.e., len(self)) operation."""
        return self._cpt.shape[0]

    def __delitem__(self, key):
        """Define del (i.e., del self[key]) operation."""
        self._cpt = np.delete(self._cpt, key, axis=0)

    def __getitem__(self, key):
        """Define slice (i.e., self[key]) operation."""
        kwargs = {}
        for attr in ["depth", "qc", "fs"]:
            kwargs[attr] = getattr(self, attr)[key]
        return CPT(**kwargs)

    def is_similar(self, other):
        """Determine if an object is similar to the current CPT.

        Check if another object is similar to the current `CPT`, but
        without checking if the two are identical. Comparison is based
        on: whether the `other` object it is an instance of `CPT` and
        its length.

        Parameters
        ----------
        other : object
            Another object with the __len__ defined (i.e., `len(object)`
            ) must be able to be run successfully.

        Returns
        -------
        bool
            Indicating the result of the comparison.

        """
        if not isinstance(other, (CPT,)):
            return False

        if len(self) != len(other):
            return False

        return True

    def __eq__(self, other):
        if not self.is_similar(other):
            return False

        if not np.allclose(self._cpt, other._cpt):
            return False

        return True
