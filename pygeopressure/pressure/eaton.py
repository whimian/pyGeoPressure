# -*- coding: utf-8 -*-
"""
Routines for eaton pressure prediction

Created on Sep 20 2018
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np


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
    .. math:: P = S - {\\sigma}_{n}\\left(\\frac{V}{V_{n}}\\right)^{n}

    [4]_

    .. [4] Eaton, B. A., & others. (1975). The equation for geopressure
       prediction from well logs. In Fall Meeting of the Society of Petroleum
       Engineers of AIME. Society of Petroleum Engineers.
    """
    ves = (lithostatic - hydrostatic) * (v / vn)**n
    pressure = lithostatic - ves
    return pressure
