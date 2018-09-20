# -*- coding: utf-8 -*-
"""
well log processing tools

Created on Sep 19 2018
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit

from pygeopressure.velocity.smoothing import smooth
from pygeopressure.velocity.extrapolate import normal_dt
from pygeopressure.pressure.obp import traugott_trend
from pygeopressure.basic.well_log import Log


def extrapolate_log_traugott(den_log, a, b, kb=0, wd=0):
    """
    Extrapolate density log using Traugott equation
    """
    density_trend = traugott_trend(
        np.array(den_log.depth), a, b, kb=kb, wd=wd)

    extra_log = Log()
    extra_log.name = den_log.name + "_ex"
    extra_log.units = den_log.units
    extra_log.descr = "Density_extra"
    extra_log.depth = np.array(den_log.depth)

    new_data = np.full_like(density_trend, np.nan)
    new_data[:den_log.start_idx] = density_trend[:den_log.start_idx]

    old_data = np.array(den_log.data)
    new_data[den_log.start_idx:] = old_data[den_log.start_idx:]

    extra_log.data = new_data

    return extra_log
