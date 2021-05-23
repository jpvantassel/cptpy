"""Geotechnical helper functions."""

import numpy as np

def vertical_stress(depth, unit_weight):
    """Calculate total vertical stress.
    
    Parameters
    ----------
    depth : ndarray
        Depth values, one per depth, in m.
    unit_weight : ndarray
        Unit weight, one per depth, in kN/m3.

    Returns
    -------
    ndarray
        Total vertical stress in kPa.

    """
    if np.any(depth <= 0):
        raise ValueError("No depth can be <= 0.")
    if np.any(unit_weight <= 0):
        raise ValueError("No unit_weight can be <= 0.")
    vstress = np.empty_like(depth)
    vstress[0] = depth[0]*unit_weight[0]
    vstress[1:] = (depth[1:] - depth[:-1])*unit_weight[1:]
    return vstress        

def vertical_effective_stress(depth, unit_weight, pore_pressure):
    """Calculate vertical effective stress.

    Parameters
    ----------
    depth : ndarray
        Depth values, one per depth, in m.
    unit_weight : ndarray
        Unit weight, one per depth, in kN/m3.
    pore_pressure : ndarray
        Pore pressure, one per depth, in kPa.

    Returns
    -------
    ndarray
        Vertical effective stress in kPa.

    """
    vstress = calculate_vertical_stress(depth, unit_weight)
    vestress = vstress - pore_pressure
    return vestress 
