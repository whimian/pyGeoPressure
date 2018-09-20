# -*- coding: utf-8 -*-
"""
Function to calculate hydrostatic pressure

Created on Fri Nov 11 2016
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np

from pygeopressure.basic.well_log import Log


def hydrostatic_pressure(depth, kelly_bushing=0, depth_w=0, rho_f=1., rho_w=1.):
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
    depth = np.array(depth)
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


def hydrostatic_well(depth, kb=0, wd=0, rho_f=1., rho_w=1.):
    """
    Returns
    -------
    Log
        Hydrostatic pressure as a Log
    """
    hydrostatic = hydrostatic_pressure(
        depth, kelly_bushing=kb, depth_w=wd, rho_f=rho_f, rho_w=rho_w)

    hydro_log = Log()
    hydro_log.depth = np.array(depth)
    hydro_log.data = hydrostatic
    hydro_log.name = 'log_hydro'
    hydro_log.descr = "Hydrostatic_Pressure"
    hydro_log.units = "MPa"

    return hydro_log


def hydrostatic_trace(depth, rho=1.01, g=9.8, shift=0):
    mask = depth <= shift
    hydro = (depth - shift) * rho * g * 0.001
    hydro[mask] = 0
    return hydro
