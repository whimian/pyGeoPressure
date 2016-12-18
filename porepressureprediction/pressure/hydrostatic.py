# -*- coding: utf-8 -*-
"""
A straightforward 2D kriging program

Created on Fri Nov 11 2016
"""
import numpy as np


def hydrostatic_pressure(depth, kelly_bushing=41, depth_w=82, rho_f=1.174, rho_w=1.01):
    """
    Parameters
    ----------
    depth : scalar or 1-d ndarray
        measured depth, unit: meter
    rho_f : scalar
        density of pore fluid, g/cm3
    kelly_bushing : scalar
        kelly bushing elevation, in meter
    depth_w : scalar
        sea water depth
    rho_w : scalar
        sea water density

    Returns
    -------
    pressure : scalar or 1-d ndarray
        unit: mPa
    """
    rho_f *= 1000  # kg/m3
    rho_w *= 1000  # kg/m3
    acceleration = 9.80665  # m/s2
    density = np.full_like(depth, rho_f)
    # sea level to sea bottom
    mask = depth < (kelly_bushing + depth_w)
    density[mask] = rho_w
    # kelly bushing to sea level
    mask = depth < kelly_bushing
    density[mask] = 0
    delta_depth = np.full_like(depth, np.nan)
    delta_depth[1:] = depth[1:] - depth[:-1]
    delta_depth[0] = 0
    hydrostatic = delta_depth * density * acceleration / 1000000  # mPa
    hydrostatic = np.cumsum(hydrostatic)
    return hydrostatic
