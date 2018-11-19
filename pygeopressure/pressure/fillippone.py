# -*- coding: utf-8 -*-
"""
Fillippone's method for Pore Pressure Prediction with seismic velocity
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

import numpy as np
from pygeopressure.velocity.conversion import (
    twt2depth, rms2int, int2avg, int2rms)


def fillippone(v_int, v_max, v_min, obp, n=1):
    """
    Pore Pressure Prediction with seismic velocity in depth domain

    Parameters
    ----------
    v_int : 1-d ndarray
        Interval velocity in depth domain
    v_max : 1-d ndarray
        Maximum velocity in depth domain
    v_min : 1-d ndarray
        Minimum velocity in depth domain
    obp : 1-d ndarray
        Overburden Pressure in depth domain
    n : float
        exponent for modified Fillippone equation

    Returns
    -------
    1-d ndarray
    """
    return fillippone_ratio(v_int, v_max, v_min, n) * obp


def fillippone_ratio(v_int, v_max, v_min, n=1):
    """
    Pore Pressure Prediction with seismic velocity in depth domain

    Parameters
    ----------
    v_int : 1-d ndarray
        Interval velocity in depth domain
    v_max : 1-d ndarray
        Maximum velocity in depth domain
    v_min : 1-d ndarray
        Minimum velocity in depth domain
    obp : 1-d ndarray
        Overburden Pressure in depth domain
    n : scalar
        exponent for modified Fillippone equation

    Returns
    -------
    1-d ndarray
    """
    return ((v_max - v_int) / (v_max - v_min))**n


# utils

def v_max_min(twt, v_rms, v0=1524):
    """
    Calculate maximum and minimum velocity for Fillippone's method

    Parameters
    ----------
    twt : 1-d ndarray
        two-way-time
    v_rms : 1-d ndarray
        RMS velocity in time domain
    v0 : scalar

    Returns
    -------
    v_max : 1-d ndarray
        maximum velocity in time domain
    v_min : 1-d ndarray
        minimum velocity in time domain
    """
    K = np.zeros_like(v_rms)
    K[1:] = (v_rms[1:] - v_rms[:-2]) / (twt[1:] - twt[:-2])

    v_max = 1.4 * v0 + 3 * K * twt
    v_min = 0.7 * v0 + 0.5 * K * twt

    return v_max, v_min


def fillippone_from_vint_time(
        twt, v_int_t, stepDepth, startDepth, endDepth, obp_d, n=1):
    """
    Calculate Fillippone Pressure with time domain interval velocity

    Parameters
    ----------
    twt : 1-d ndarray
        two-way-time
    v_int_t : 1-d ndarray
        Interval velocity in time domain
    stepDepth : scalar
    startDepth : scalar
    endDepth : scalar
    obp_d : 1-d ndarray
        Overburden Pressure in depth domain
    n : scalar
        exponent for modified Fillippone equation

    Returns
    -------
    depth : 1-d ndarray
    pressure_fillip : 1-d ndarray
    """
    v_rms_t = int2rms(twt, v_int_t)
    v_max_t, v_min_t = v_max_min(twt, v_rms_t)

    v_avg_t = int2avg(twt, v_int_t)

    depth, v_max = twt2depth(
        twt, v_avg_t, v_max_t,
        stepDepth=stepDepth, startDepth=startDepth, endDepth=endDepth)
    _, v_min = twt2depth(
        twt, v_avg_t, v_min_t,
        stepDepth=stepDepth, startDepth=startDepth, endDepth=endDepth)
    _, v_int = twt2depth(
        twt, v_avg_t, v_int_t,
        stepDepth=stepDepth, startDepth=startDepth, endDepth=endDepth)

    pressure_fillip = fillippone(v_int, v_max, v_min, obp_d, n)

    return depth, pressure_fillip
