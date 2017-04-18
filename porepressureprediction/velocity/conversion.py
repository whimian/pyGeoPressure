# -*- coding: utf-8 -*-
"""
Routines performing velocity type conversion
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np
from scipy import interpolate


def rms2int(twt, rms):
    """
    Convert rms velocity to interval velocity

    Parameters
    ----------
    twt : 1-d ndarray
        input two-way-time array
    rms : 1-d nadarray
        rms velocity array

    Returns
    -------
    v_int : 1-d ndarray
        interval velocity array with the same length of twt and rms

    Notes
    -----
    This routine uses Dix equation to comput inverval velocity.

    .. math:: V_{int}[i]^2 = \\frac{V_{rms}[i]^2 t_{i} - V_{rms}[i-1]^2 \
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
    v_int[0] = rms[0]
    v_int[1:] = np.sqrt((rms[1:]**2 * twt[1:] - rms[:-1]**2 * twt[:-1]) /
                        (twt[1:] - twt[:-1]))

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
    v_rms[0] = v_int[0]
    v_rms[1:] = np.sqrt(
                    (v_int[1:]**2 * (twt[:-1] - twt[1:]) +
                     v_rms[:-1]**2 * twt[:-1]) / twt[1:]
                    )

    return v_rms


def int2avg(twt, v_int):
    """
    Parameters
    ----------
    twt : 1-d ndarray

    v_int : 1-d ndarray

    Returns
    -------
    v_avg : 1-d ndarray

    Notes
    -----
    .. math:: V_{int}[i](t[i] - t[i-1]) = V_{avg}[i] t[i] - V_{avg}[i-1] t[i-1]
    """
    v_avg = np.ones((len(twt), ))
    v_avg[0] = v_int[0]
    v_avg[1:] = (v_avg[:-1] * twt[:-1] + v_int[1:] * (twt[1:] - twt[:-1])) /\
        twt[1:]

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
    v_int[0] = v_avg[0]
    v_int[1:] = (v_avg[1:]*twt[1:] - v_avg[:-1]*twt[:-1]) /\
        (twt[1:] - twt[:-1])

    return v_int


def twt2depth(twt, v_avg, stepDepth, startDepth=None, endDepth=None):
    """
    Parameters
    ----------
    twt : 1-d ndarray
    v_avg : 1-d ndarray
    stepDepth : scalar
    startDpeth (optional): scalar
    endDepth (optional): scalar

    Returns
    -------
    newDepth : 1-d ndarray
        new depth array
    new_v_avg : 1-d ndarray
        average velocity in depth domain
    """
    depth = np.ones((len(twt), ))
    depth[:] = twt[:] * v_avg[:]
    startDepth = depth[0] if startDepth is None else startDepth
    endDepth = depth[-1] if endDepth is None else endDepth
    newDepth = np.arange(startDepth, endDepth, stepDepth)
    f = interpolate.interp1d(depth, v_avg, kind='cubic')
    new_v_avg = f(newDepth)

    return (newDepth, new_v_avg)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
