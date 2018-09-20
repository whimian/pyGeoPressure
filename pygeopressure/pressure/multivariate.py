# -*- coding: utf-8 -*-
"""
Routines for multivariate pressure prediction

Created on Sep 20 2018
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np


def multivariate_virgin(sigma, phi, vsh, a_0, a_1, a_2, a_3, B):
    """
    Calculate velocity using multivariate virgin curve

    Parameters
    ----------
    sigma : 1-d ndarray
        effective pressure
    phi : 1-d ndarray
        effective porosity
    vsh : 1-d ndarray
        shale volume
    a_0, a_1, a_2, a_3 : float
        coefficients of equation
    B : float
        effective pressure exponential

    Returns
    -------
    out : 1-d ndarray
        velocity array

    Notes
    -----
    .. math:: V = a_0 + a_1\\phi + a_2{V}_{sh} + a_3 {\\sigma}^{B}

    [5]_

    .. [5] Sayers, C., Smit, T., van Eden, C., Wervelman, R., Bachmann, B.,
       Fitts, T., et al. (2003). Use of reflection tomography to predict
       pore pressure in overpressured reservoir sands. In submitted for
       presentation at the SEG 2003 annual meeting.
    """
    return a_0 - a_1 * phi - a_2 * vsh + a_3 * sigma**B


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


def multivariate_unloading(sigma, phi, vsh, a_0, a_1, a_2, a_3, B, U, vmax):
    """
    Calculate velocity using multivariate unloading curve
    """
    sigma_max = invert_multivariate_virgin(
        vmax, phi, vsh, a_0, a_1, a_2, a_3, B)

    sigma_vc = sigma_max*(sigma/sigma_max)**(1/U)

    return multivariate_virgin(sigma_vc, phi, vsh, a_0, a_1, a_2, a_3, B)


def invert_multivariate_unloading(vel, phi, vsh, a_0, a_1, a_2, a_3,
                                  B, U, vmax):
    """
    Calculate effective stress using multivariate unloading curve
    """
    sigma_max = invert_multivariate_virgin(
        vmax, phi, vsh, a_0, a_1, a_2, a_3, B)

    sigma_vc = invert_multivariate_virgin(
        vel, phi, vsh, a_0, a_1, a_2, a_3, B)

    return sigma_max * (sigma_vc/sigma_max)**U


def effective_stress_multivariate(vel, phi, vsh, a_0, a_1, a_2, a_3,
                                  B, U, vmax, start_idx, end_idx=None):
    ves = invert_multivariate_virgin(vel, phi, vsh, a_0, a_1, a_2, a_3, B)
    unloading = invert_multivariate_unloading(
        vel, phi, vsh, a_0, a_1, a_2, a_3, B, U, vmax)
    ves[start_idx: end_idx] = unloading[start_idx: end_idx]
    return ves


def pressure_multivariate(obp, vel, phi, vsh, a_0, a_1, a_2, a_3,
                          B, U, vmax, start_idx, end_idx=None):
    """
    Pressure Prediction using multivariate model
    """
    ves = effective_stress_multivariate(
        vel, phi, vsh, a_0, a_1, a_2, a_3, B, U, vmax, start_idx, end_idx)
    return obp - ves


def pressure_multivariate_varu(obp, vel, phi, vsh, a_0, a_1, a_2, a_3,
                               B, U, vmax, start_idx, buf=20,
                               end_idx=None, end_buffer=10):
    """
    Pressure Prediction using multivariate model
    """
    ves = effective_stress_multivariate_varu(
        vel, phi, vsh, a_0, a_1, a_2, a_3,
        B, U, vmax, start_idx, buf, end_idx, end_buffer)
    return obp - ves


def effective_stress_multivariate_varu(vel, phi, vsh, a_0, a_1, a_2, a_3,
                                       B, U, vmax, start_idx, buf=20,
                                       end_idx=None, end_buffer=10):
    u_array = np.ones(vel.shape)
    u_array[start_idx: end_idx] = U
    # start buffer
    u_buffer = np.linspace(1, U, buf)
    u_array[start_idx-buf+1: start_idx + 1] = u_buffer
    # end buffer
    if end_idx is not None:
        u_array[end_idx: end_idx + end_buffer] = np.linspace(U, 1, end_buffer)
    ves = invert_multivariate_unloading(vel, phi, vsh, a_0, a_1, a_2, a_3,
                                        B, u_array, vmax)
    return ves
