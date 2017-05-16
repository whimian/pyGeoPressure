# -*- coding: utf-8 -*-
"""
some utilities
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np


def rmse(measure, predict):
    """
    Relative Root-Mean-Square Error

    with RMS(y - y*) as nominator, and RMS(y) as denominator
    """
    delta = np.sqrt(np.mean((measure - predict)**2))
    denominator = np.sqrt(np.mean(measure**2))
    return delta/denominator
