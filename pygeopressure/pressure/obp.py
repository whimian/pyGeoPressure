# -*- coding: utf-8 -*-
"""
Functions related to density and Overburden Pressrue Calculation
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np
from pygeopressure.basic.well_log import Log


def traugott(z, a, b):
    r"""
    estimate density with depth

    Parameters
    ----------
    depth : 1-d ndarray
    a, b: scalar

    Notes
    -----
    .. math:: \overline{\rho (h)}=16.3+{h/3125}^{0.6}

    gives the average sediment density in pounds per gallon (ppg) mud weight
    equivalent between the sea floor and depth h (in feet) below the sea floor.

    So, density variation with depth takes the form [2]_:

    .. math:: \rho(z) = {\rho}_{0} + a{z}^{b}

    .. [2] Traugott, Martin. "Pore/fracture pressure determinations in deep
       water." World Oil 218.8 (1997): 68-70.
    """
    # rho0 = 2.65
    return 1.70 + a * z**b


def traugott_trend(depth, a, b, kb=0, wd=0):
    depth_shift = np.array(depth) - kb - wd
    density = traugott(depth_shift, a, b)
    mask = depth_shift < 0
    density[mask] = np.nan
    return density


def gardner(v, c, d):
    r"""
    Estimate density with velocity

    Parameters
    ----------
    v : 1-d ndarray
        interval velocity array
    c : float, optional
        coefficient a
    d : float, optional
        coefficient d

    Returns
    -------
    out : 1-d ndarray
        density array

    Notes
    -----
    .. math:: \rho = c{V}^{d}

    typical values for a and b in GOM coast are a=0.31, b=0.25 [1]_.

    .. [1] G. Gardner, L. Gardner, and A. Gregory, "Formation velocity and density -
       the diagnostic basics for stratigraphic traps," Geophysics, vol. 39,
       no. 6, pp. 770-780, 1974.
    """
    return c * v**d


def overburden_pressure(depth, rho, kelly_bushing=41, depth_w=82, rho_w=1.01):
    """
    Calculate Overburden Pressure

    Parameters
    ----------
    depth : 1-d ndarray
    rho : 1-d ndarray
        density in g/cm3
    kelly_bushing : scalar
        kelly bushing elevation in meter
    depth_w : scalar
        from sea level to sea bottom (a.k.a mudline) in meter
    rho_w : scalar
        density of sea water - depending on the salinity of sea water
        (1.01-1.05g/cm3)

    Returns
    -------
    obp : 1-d ndarray
        overburden pressure in mPa
    """
    g = 9.80665  # m/s2
    depth = np.array(depth)
    rho = np.array(rho)
    rho = 1000 * rho  # convert unit from g/cm3 to kg/m3
    rho_w = 1000 * rho_w
    # sea bottom to sea level
    mask = depth < (kelly_bushing + depth_w)
    rho[mask] = rho_w
    mask = depth < kelly_bushing
    rho[mask] = 0
    delta_h = np.full_like(depth, np.nan)
    delta_h[1:] = depth[1:] - depth[:-1]
    delta_h[0] = 0
    obp = rho * delta_h * g
    obp = np.cumsum(obp)
    return obp / 1000000  # mPa


def obp_well(den_log, kb=41, wd=82, rho_w=1.01):
    """
    Compute Overburden Pressure for a Log

    Parameters
    ----------
    den_log : Log
        density log (extrapolated)
    kb : scalar
        kelly bushing elevation in meter
    wd : scalar
        from sea level to sea bottom (a.k.a mudline) in meter
    rho_w : scalar
        density of sea water - depending on the salinity of sea water
        (1.01-1.05g/cm3)

    Returns
    -------
    out : Log
        Log containing overburden pressure in mPa
    """
    depth = np.array(den_log.depth)
    rho = np.array(den_log.data)
    obp = overburden_pressure(
        depth, rho, kelly_bushing=kb, depth_w=wd, rho_w=rho_w)

    obp_log = Log()
    obp_log.depth = depth
    obp_log.data = obp
    obp_log.name = "log_obp"
    obp_log.descr = "Overburden_Pressure"
    obp_log.units = "MPa"

    return obp_log


def obp_trace(rho, step):
    """
    Compute Overburden Pressure for a trace

    Parameters
    ----------
    rho : 1-d array
        density in g/cc

    Returns
    -------
    out : 1-d ndarray
        overburden pressure in mPa
    """
    data = np.array(rho)
    return np.cumsum(data * 9.8 * step * 0.001)
