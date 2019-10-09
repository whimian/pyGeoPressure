# -*- coding: utf-8 -*-
"""
Routines for Eberhart-Phillips pressure prediction

Created on Mar 25 2019
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

import numpy as np
from scipy.interpolate import interp1d


def eberhart_phillips(sigma, phi, vsh, a_0, a_1, a_2, a_3, B):
    """
    calculate effective pressure with the ratio of velocity and normal velocity

    Notes
    -----
    .. math:: V=a_{0}+a_{1} \\phi+a_{2} \\sqrt{C}+a_{3}\\left(\\sigma-e^{b \\sigma}\\right)

    [5]_

    .. [5] Eberhart‐Phillips D, Han D, Zoback M (1989) Empirical relationships
           among seismic velocity, effective pressure, porosity, and clay
           content in sandstone. GEOPHYSICS 54:82–89. doi: 10.1190/1.1442580
    """
    return a_0 + a_1 * phi + a_2*np.sqrt(vsh)+a_3*(sigma - np.exp(B*sigma))


def eberhart_phillips_univariate(sigma, a_0, a_1, B):
    """
    calculate effective pressure with the ratio of velocity and normal velocity

    Notes
    -----
    .. math:: V=a_{0}+a_{1} \\left(\\sigma-e^{b \\sigma}\\right)

    [5]_

    .. [5] Eberhart‐Phillips D, Han D, Zoback M (1989) Empirical relationships
           among seismic velocity, effective pressure, porosity, and clay
           content in sandstone. GEOPHYSICS 54:82–89. doi: 10.1190/1.1442580
    """
    return a_0 + a_1*(sigma - np.exp(B*sigma))


class Han_lookup(object):
    def __init__(self, B):
        y = np.arange(1000)
        x = y - np.exp(B*y)
        self.func = interp1d(x, y)#, kind='cubic')

    def __call__(self, value):
        return self.func(value)
