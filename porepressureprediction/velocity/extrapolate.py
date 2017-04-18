# -*- coding: utf-8 -*-
"""
Functions relating velocity trend extrapolation
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np

v0 = 1600  # take values larger than 1500


def set_v0(v):
    """
    set global variable v0 for slotnick()
    """
    global v0
    v0 = v


def normal(x, a, b):
    """
    Extrapolate velocity using normal trend.

    Parameters
    ----------
    x : 1-d ndarray
        depth to convert
    a, b : scalar
        coefficents

    Returns
    -------
    out : 1-d ndarray
        esitmated velocity

    Notes
    -----
    .. math:: \log d{t}_{Normal}=a-bz

    is transformed to

    .. math:: v={e}^{bz-a}

    **Note** that the exponential relation is unphysical especially in depth
    bellow the interval within which the equation is calibrated.

    References
    ----------
    .. [1] C. Hottmann, R. Johnson, and others, "Estimation of formation
       pressures from log-derived shale properties," Journal of Petroleum
       Technology, vol. 17, no. 6, pp. 717-722, 1965.

    """
    return np.exp(x*b - a)


def slotnick(x, k):
    """
    Relation between velocity and depth

    Parameters
    ----------
    x : 1-d ndarray
        Depth to convert
    k : scalar
        velocity gradient

    Notes
    -----
    typical values of velocity gradient k falls in the range 0.6-1.0s-1

    References
    ----------
    .. [1] M. Slotnick, "On seismic computations, with applications, I,"
       Geophysics, vol. 1, no. 1, pp. 9-22, 1936.
    """
    global v0
    return v0 + k*x


def normal_dt(x, a, b):
    """
    normal trend of transit time

    Parameters
    ----------
    x : 1-d ndarray
        depth to convert
    """
    return a - b * x
