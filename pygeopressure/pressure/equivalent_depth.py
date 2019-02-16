# -*- coding: utf-8 -*-
"""
Equivalent Depth Method

Created on Dec 12 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

import numpy as np


def invert_NCT(vel, a, b):
    """
    Invert Normal Compaction Trend for velocity
    """
    h = (np.log(vel)+a) / b
    return h


def normal_sigma(depth, obp, hydro):
    """
    Interpolater of depth and normal effective stress
    """
    n_sigma = obp - hydro
    func = interp1d(depth, n_sigma)
    return func


def euqivalent_depth(depth, velocity, obp, hydrostatic, a, b):
    """
    equivalent depth method
    """
    h = invert_NCT(velocity, a, b)
    conversion = normal_sigma(
        depth, obp, hydrostatic)
    n_sigma = conversion(h)
    pres = obp - n_sigma
