# -*- coding: utf-8 -*-
"""
Routines to calculate pore pressure
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

import numpy as np


def bowers(v, obp, u, start_idx, a, b, vmax, end_idx=None):
    """
    Compute pressure using Bowers equation.

    Parameters
    ----------
    v : 1-d ndarray
        velocity array whose unit is m/s.
    obp : 1-d ndarray
        Overburden pressure whose unit is Pa.
    v0 : float, optional
        the velocity of unconsolidated regolith whose unit is m/s.
    a : float, optional
        coefficient a
    b : float, optional
        coefficient b

    Notes
    -----
    .. math:: P = S - \\left[\\frac{(V-V_{0})}{a}\\right]^{\\frac{1}{b}}

    [3]_

    .. [3] Bowers, G. L. (1994). Pore pressure estimation from velocity data:
       accounting from overpressure mechanisms besides undercompaction:
       Proceedings of the IADC/SPE drilling conference, Dallas, 1994,
       (IADC/SPE), 1994, pp 515–530. In International Journal of Rock
       Mechanics and Mining Sciences & Geomechanics Abstracts (Vol. 31,
       p. 276). Pergamon.
    """
    sigma_max = ((vmax-1524)/a)**(1/b)
    ves = ((v - 1524) / a)**(1.0 / b)
    ves_fe = sigma_max*(((v-1524)/a)**(1/b)/sigma_max)**u
    ves[start_idx: end_idx] = ves_fe[start_idx: end_idx]
    return obp - ves


def bowers_varu(v, obp, u, start_idx, a, b, vmax, buf=20,
                end_idx=None, end_buffer=10):
    """
    Bowers Method with buffer zone above unloading zone

    Parameters
    ----------
    v : 1-d ndarray
        velocity array whose unit is m/s.
    obp : 1-d ndarray
        Overburden pressure whose unit is Pa.
    u : float
        coefficient u
    start_idx : int
        index of start of fluid expansion
    a : float, optional
        coefficient a
    b : float, optional
        coefficient b
    vmax : float
    buf : int, optional
        len of buffer interval, buf should be smaller than start_idx
    end_idx : int
        end of fluid expasion
    end_buffer : int
        len of end buffer interval
    """
    u_array = np.ones(v.shape)
    u_array[start_idx: end_idx] = u
    # start buffer
    u_buffer = np.linspace(1, u, buf)
    u_array[start_idx-buf+1: start_idx + 1] = u_buffer
    # end buffer
    if end_idx is not None:
        u_array[end_idx: end_idx + end_buffer] = np.linspace(u, 1, end_buffer)
    sigma_max = ((vmax-1524)/a)**(1/b)
    ves = sigma_max*(((v-1524)/a)**(1/b)/sigma_max)**u_array
    return obp - ves


def virgin_curve(sigma, a, b):
    "Virgin curve in Bowers' method."
    v0 = 1524
    return v0 + a * sigma**b


def invert_virgin(v, a, b):
    "invert of virgin curve."
    v0 = 1524
    return ((v-v0)/a)**(1/b)


def unloading_curve(sigma, a, b, u, v_max):
    "Unloading curve in Bowers's method."
    sigma_max = ((v_max-1524)/a)**(1/b)
    independent = sigma_max*(sigma/sigma_max)**(1/u)
    return virgin_curve(independent, a, b)


def invert_unloading(v, a, b, u, v_max):
    "invert of Unloading curve in Bowers's method."
    sigma_max = invert_virgin(v_max, a, b)
    sigma_vc = invert_virgin(v, a, b)
    return sigma_max * (sigma_vc/sigma_max)**u


def power_bowers(sigma_vc_ratio, u):
    return sigma_vc_ratio**u
