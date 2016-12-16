# -*- coding: utf-8 -*-
"""
A straightforward 2D kriging program

Created on Fri Nov 11 2016
"""
def hydrostatic_pressure(depth):
    """
    Parameters
    ----------
    depth : scalar or 1-d ndarray
        unit: meter

    Returns
    -------
    pressure : scalar or 1-d ndarray
        unit: mPa
    """
    den_w = 1.174  # g/c3
    den_w *= 1000  # kg/m3
    acceleration = 9.80665  # m/s2
    return depth * acceleration * den_w / 10**6  # mPa
