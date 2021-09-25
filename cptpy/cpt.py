"""CPT class definition."""

import warnings

import numpy as np

from .constants import PA, GAMMA_W


class CPT():
    _ncols_in_cpt = 3
    attrs = ["depth", "qc", "fs"]
    units = ["m", "kpa", "kpa"]

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

    def sanity_check(self, apply_fixes="prompt", window_pts=3, reject_nstd=6):
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
        window_pts : int, optional
            Select the number of points before and after the point of
            interest to determine if it is an outlier, default is 3
            (i.e., 6 point in total will be considered).
        reject_nstd : float, optional
            Set threshold by which a point is designated an outlier,
            default is 6 standard deviations. Note that the point of
            interest is not considered in calculating the regions
            statistics.

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

        def pretty_print_row(row):
            pretty_row = ""
            for attr, value, unit in zip(self.attrs, row, self.units):
                pretty_row += f" {attr}={value:.2f} {unit} |"
            print(pretty_row)

        def handle_problematic_indices(problematic_indices, apply_fixes, msg):
            indices_to_delete = []
            for index in problematic_indices:
                print(msg)
                pretty_print_row(self._cpt[index])

                response = "n"
                if apply_fixes == "prompt":
                    response = input("Discard zero depth reading? (y/n) ")

                if response == "y" or apply_fixes == "yes":
                    indices_to_delete.append(index)
                print()
            return indices_to_delete

        # no depth less than or equal to zero.
        if np.any(self._cpt[:,0] <= 0):
            problematic_indices = np.argwhere(self.depth <= 0).flatten()
            msg = "A reading at a depth less than zero was found:\n"
            indices_to_delete = handle_problematic_indices(problematic_indices, apply_fixes, msg)
            del self[indices_to_delete]

        # depth increases monotonically.
        diff = self.depth[1:] - self.depth[:-1]
        if np.any(diff <= 0):
            print("Depths readings do not increase monotonically.")

            response = "n"
            if apply_fixes == "prompt":
                response = input("Sort readings by depth? (y/n) ")

            if response == "y" or apply_fixes == "yes":
                self._cpt = self._cpt[np.argsort(self.depth), :]

        # no duplicate depth measurements.
        diff = self.depth[1:] - self.depth[:-1]
        if np.any(diff < 1E-6):
            problematic_indices = np.argwhere(diff < 1E-6).flatten()
            msg = "A duplicate depth reading has been found: "
            indices_to_delete = handle_problematic_indices(problematic_indices, apply_fixes, msg)
            del self[indices_to_delete]

        # qc and fs are greater than zero at all depths.
        if np.any(self._cpt[:, 1:3] <= 0):
            problematic_indices = np.argwhere(np.logical_or(self._cpt[:, 1] <= 0, self._cpt[:, 2] <= 0)).flatten()
            msg = "A qc and/or fs value was found to be less than or equal to zero: "
            indices_to_delete = handle_problematic_indices(problematic_indices, apply_fixes, msg)
            del self[indices_to_delete]

        # qc and fs should be "locally" smooth.
        problematic_indices = []
        for index, (_qc, _fs) in enumerate(self._cpt[window_pts:-window_pts, 1:3], start=window_pts):
            region = self._cpt[index-window_pts:index+window_pts+1, 1:3]
            region = np.delete(region, window_pts, axis=0)
            (qc_mean, fs_mean) = np.mean(region, axis=0)
            (qc_std, fs_std) = np.std(region, axis=0, ddof=1)
            qc_z = np.abs(_qc - qc_mean)/qc_std
            fs_z = np.abs(_fs - fs_mean)/fs_std
            if (qc_z > reject_nstd) or (fs_z > reject_nstd):
                problematic_indices.append(index)

        msg = "A qc and/or fs value was found to be greater than\n"
        msg += f"{reject_nstd} standard deviations beyond the background:"
        indices_to_delete = handle_problematic_indices(problematic_indices, apply_fixes, msg)
        del self[indices_to_delete]

    @property
    def rf(self):
        """Alias for `friction_ratio`."""
        return self.friction_ratio

    @property
    def friction_ratio(self):
        """CPT friction ratio (Rf)."""
        return (self.fs / self.qc) * 100

    def isbt(self, procedure="Robertson 2010"):
        """Calculate the Non-Normalized Soil Behavior Type Index (Isbt).

        Parameters
        ----------
        procedure : {'Robertson 2010'}, optional
            Define the procedure for defining the Isbt, default is
            Robertson (2010). Full citations provided below.

        Return
        ------
        ndarray
            Containing Isbt at each depth.

        References
        ----------
        Robertson, P.K., 2010. Soil behavior type from the CPT: an
        update, in: 2nd International Symposium on Cone Penetration
        Testing. Presented at the CPT ’10, Huntington Beach, CA, USA,
        pp. 575–583.

        """
        register = {"Robertson 2010": self._isbt_robertson_2010}
        return register[procedure]()

    def _isbt_robertson_2010(self):
        """Compute Isbt using Robertson (2010)."""
        a = (3.47 - np.log10(self.qc/PA))
        b = (1.22 + np.log10(self.rf))
        isbt = np.sqrt(a*a + b*b)
        return isbt

    def sbt(self, procedure="Robertson 2010"):
        """Determine the Non-Normalized Soil Behavior Type (SBT).

        Parameters
        ----------
        procedure : {'Robertson 2010'}, optional
            Define the procedure for defining the SBT, default is
            Robertson (2010). Full citations provided below.

        Return
        ------
        tuple
            Of the form `(Isbt, SBT)` where `Isbt` is an `ndarray` of
            Soil Behavior Type Index values and `SBT` is an `ndarray` of
            Soil Behavior Types.

        References
        ----------
        Robertson, P.K., 2010. Soil behavior type from the CPT: an
        update, in: 2nd International Symposium on Cone Penetration
        Testing. Presented at the CPT ’10, Huntington Beach, CA, USA,
        pp. 575–583.

        """
        isbt = self.isbt(procedure=procedure)

        register = {"Robertson 2010": CPT._isbt_to_sbt_robertson_2010}
        decoder = register[procedure]
        sbt = decoder(isbt)

        return (isbt, sbt)

    def _isbt_to_sbt_robertson_2010(self, isbt):
        """Translate isbt to sbt."""
        zone = np.empty(len(self), dtype=int)
        sbt = np.empty(len(self), dtype=str)
        rfs = self.rf
        eqas = qc/PA >= 1/(0.006*(rfs-0.9) - 0.004*(rfs-0.9)*(rfs-0.9) - 0.005)
        qc_on_pas = qc/PA
        for i, (qc_on_pa, rf, eqa) in enumerate(zip(qc_on_pas, rfs, eqas)):
            if rf > 1.5 and rf < 4.5 and eqa:
                zone[i] = 8
                sbt[i] = "Stiff Sand to Clayed Sand"
            elif rf > 4.5 and eqa:
                zone[i] = 9
                sbt[i] = "Stiff Fine-Grained"
            elif qc_on_pa < 12*np.exp(-1.4*rf):
                zone[i] = 1
                sbt[i] = "Sensitive Fine-Grained"
            elif isbt > 3.6:
                zone[i] = 2
                sbt[i] = "Organic Soils"
            elif isbt > 2.95:
                zone[i] = 3
                sbt[i] = "Clays"
            elif isbt > 2.6:
                zone[i] = 4
                sbt[i] = "Silt Mixtures"
            elif isbt > 2.05:
                zone[i] = 5
                sbt[i] = "Sand Mixtures"
            elif isbt > 1.31:
                zone[i] = 6
                sbt[i] = "Sands"
            elif isbt < 1.31:
                zone[i] = 7
                sbt[i] = "Gravelly to Dense Sand"
            else:
                zone[i] = 0
                sbt[i] = "Unknown Soil Type"
                warnings.warn(f"Unknown soil type encountered at index={i}")
        return (zone, sbt)

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
            Object to be compared.

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
