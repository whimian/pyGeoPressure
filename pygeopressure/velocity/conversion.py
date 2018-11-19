# -*- coding: utf-8 -*-
"""
Routines performing velocity type conversion
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import range

__author__ = "yuhao"

import numpy as np
from scipy import interpolate


def rms2int(twt, v_rms):
    r"""
    Convert rms velocity to interval velocity

    Parameters
    ----------
    twt : 1-d ndarray
        input two-way-time array, in ms
    rms : 1-d nadarray
        rms velocity array, in m/s

    Returns
    -------
    v_int : 1-d ndarray
        interval velocity array with the same length of twt and rms

    Notes
    -----
    This routine uses Dix equation to comput inverval velocity.

    .. math:: V_{int}[i]^2 = \frac{V_{rms}[i]^2 t_{i} - V_{rms}[i-1]^2 \
                t_{i-1}}{t_{i}-t_{i-1}}

    twt and rms should be of the same length of more than 2.

    Examples
    --------
    >>> a = np.arange(10)
    >>> twt = np.arange(10)
    >>> rms2int(twt, a)
    array([  0.        ,   1.        ,   2.64575131,   4.35889894,
             6.08276253,   7.81024968,   9.53939201,  11.26942767,
            13.        ,  14.73091986])
    """
    v_int = np.ones((len(twt), ))
    # v_int = np.copy(rms)
    twt = twt*0.001
    v_int[0] = v_rms[0]
    v_int[1:] = np.sqrt(
        (v_rms[1:]**2 * twt[1:] - v_rms[:-1]**2 * twt[:-1]) / \
        (twt[1:] - twt[:-1])
    )
    # for i in range(1, v_rms.shape[0]):
    #     v_int[i] = np.sqrt(
    #         (v_rms[i]**2 * twt[i] - v_rms[i-1]**2 * twt[i-1]) / \
    #         (twt[i] - twt[i-1])
    #     )

    return v_int


def int2rms(twt, v_int):
    """
    Parameters
    ----------
    twt : 1-d ndarray
    v_int : 1-d ndarray

    Returns
    -------
    v_rms : 1-d ndarray
    """
    v_rms = np.ones((len(twt), ))
    twt = twt*0.001
    v_rms[0] = v_int[0]
    # because of the accumulational effect of rms velocity, this func should
    # not use vectorized notation
    for i in range(1, v_int.shape[0]):
        v_rms[i] = np.sqrt(
            (v_int[i]**2 * (twt[i] - twt[i-1]) + v_rms[i-1]**2 * twt[i-1]) / twt[i]
        )

    return v_rms


def int2avg(twt, v_int):
    r"""
    Parameters
    ----------
    twt : 1-d ndarray

    v_int : 1-d ndarray

    Returns
    -------
    v_avg : 1-d ndarray

    Notes
    -----
    .. math:: V_{int}[i](t_{i} - t_{i-1}) = V_{avg}[i] t_{i} - \
              V_{avg}[i-1] t_{i-1}
    """
    v_avg = np.ones((len(twt), ))
    twt = twt * 0.001
    v_avg[0] = v_int[0]
    for i in range(1, v_int.shape[0]):
        v_avg[i] = (v_avg[i-1] * twt[i-1] + v_int[i] * (twt[i] - twt[i-1])) / \
            twt[i]
    return v_avg


def avg2int(twt, v_avg):
    """
    Parameters
    ----------
    twt : 1-d ndarray
    v_avg : 1-d ndarray

    Returns
    -------
    v_int : 1-d ndarray
    """
    v_int = np.ones((len(twt), ))
    twt = twt * 0.001
    v_int[0] = v_avg[0]
    v_int[1:] = (v_avg[1:]*twt[1:] - v_avg[:-1]*twt[:-1]) /\
        (twt[1:] - twt[:-1])

    return v_int


def twt2depth(twt, v_avg, prop_2_convert,
              stepDepth=4, startDepth=None, endDepth=None):
    """
    Parameters
    ----------
    twt : 1-d ndarray
    v_avg : 1-d ndarray
    prop_2_convert: 1-d ndarray
    stepDepth : scalar
    startDpeth (optional): scalar
    endDepth (optional): scalar

    Returns
    -------
    newDepth : 1-d ndarray
        new depth array
    new_prop_2_convert : 1-d ndarray
        average velocity in depth domain
    """
    depth = np.ones((len(twt), ))
    twt = twt * 0.001
    depth = twt * v_avg / 2.0
    startDepth = depth[0] if startDepth is None else startDepth
    endDepth = depth[-1] if endDepth is None else endDepth
    newDepth = np.arange(startDepth, endDepth+0.01, stepDepth)
    f = interpolate.interp1d(depth, prop_2_convert, kind='cubic')
    new_prop_2_convert = f(newDepth)

    return (newDepth, new_prop_2_convert)
