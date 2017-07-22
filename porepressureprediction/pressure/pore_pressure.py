# -*- coding: utf-8 -*-
"""
Routines to calculate pore pressure
"""
from __future__ import division, print_function, absolute_import

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
    .. math:: P = OBP - [\\frac{(V-V_{0})}{a}]^{\\frac{1}{b}}
    """
    sigma_max = ((vmax-1524)/a)**(1/b)
    ves = ((v - 1524) / a)**(1.0 / b)
    ves_fe = sigma_max*(((v-1524)/a)**(1/b)/sigma_max)**u
    ves[start_idx: end_idx] = ves_fe[start_idx: end_idx]
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


def eaton(v, vn, hydrostatic, lithostatic, n=3):
    """
    Compute pore pressure using Eaton equation.

    Parameters
    ----------
    v : 1-d ndarray
        velocity array whose unit is m/s.
    vn : 1-d ndarray
        normal velocity array whose unit is m/s.
    hydrostatic : 1-d ndarray
        hydrostatic pressure in mPa
    lithostatic : 1-d ndarray
        Overburden pressure whose unit is mPa.
    v0 : float, optional
        the velocity of unconsolidated regolith whose unit is ft/s.
    n : float, optional
        eaton exponent

    Notes
    -----
    .. math:: P = OBP - VES_{n}* a (\\frac{V}{V_{n}})^{b}
    """
    ves = (lithostatic - hydrostatic) * (v / vn)**n
    pressure = lithostatic - ves
    return pressure


def fillipino():
    pass


def invert_multivariate_virgin(vel, phi, vsh, a_0, a_1, a_2, a_3, B):
    """
    Calculate effective stress using multivariate virgin curve

    Parameters
    ----------
    vel : 1-d ndarray
        velocity array whose unit is m/s.
    phi : 1-d ndarray
        porosity array
    vsh : 1-d ndarray
        shale volume
    a_0, a_1, a_2, a_3 : scalar
        coefficients

    Returns
    -------
    sigma: 1-d ndarray
    """
    return ((vel - a_0 + a_1 * phi + a_2 * vsh) / a_3)**(1 / B)


def multivariate_virgin(sigma, phi, vsh, a_0, a_1, a_2, a_3, B):
    """
    Calculate velocity using multivariate virgin curve
    """
    return a_0 - a_1 * phi - a_2 * vsh + a_3 * sigma**B


def multivariate_unloading(sigma, phi, vsh, a_0, a_1, a_2, a_3, B, U, vmax):
    """
    Calculate velocity using multivariate unloading curve
    """
    sigma_max = invert_multivariate_virgin(vmax, phi, vsh, a_0, a_1, a_2, a_3, B)
    sigma_vc = sigma_max*(sigma/sigma_max)**(1/U)
    return multivariate_virgin(sigma_vc, phi, vsh, a_0, a_1, a_2, a_3, B)


def invert_multivariate_unloading(vel, phi, vsh, a_0, a_1, a_2, a_3, B, U, vmax):
    """
    Calculate effective stress using multivariate unloading curve
    """
    sigma_max = invert_multivariate_virgin(vmax, phi, vsh, a_0, a_1, a_2, a_3, B)
    sigma_vc = invert_multivariate_virgin(vel, phi, vsh, a_0, a_1, a_2, a_3, B)
    return sigma_max * (sigma_vc/sigma_max)**U


def effective_stress_multivariate(vel, phi, vsh, a_0, a_1, a_2, a_3, B, U, vmax, start_idx, end_idx=None):
    ves = invert_multivariate_virgin(vel, phi, vsh, a_0, a_1, a_2, a_3, B)
    unloading = invert_multivariate_unloading(vel, phi, vsh, a_0, a_1, a_2, a_3, B, U, vmax)
    ves[start_idx: end_idx] = unloading[start_idx: end_idx]
    return ves


def pressure_multivariate(obp, vel, phi, vsh, a_0, a_1, a_2, a_3, B, U, vmax, start_idx, end_idx=None):
    """
    Pressure Prediction using multivariate model
    """
    ves = effective_stress_multivariate(
        vel, phi, vsh, a_0, a_1, a_2, a_3, B, U, vmax, start_idx, end_idx)
    return obp - ves
