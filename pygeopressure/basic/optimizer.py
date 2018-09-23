# -*- coding: utf-8 -*-
"""
optimizer for different models

Created on Sep 16 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import str

__author__ = "yuhao"

import json
from collections import OrderedDict

import numpy as np
from scipy.optimize import curve_fit

from pygeopressure.pressure.bowers import (
    virgin_curve, invert_virgin, power_bowers)
from pygeopressure.velocity.extrapolate import normal, normal_dt
from pygeopressure.pressure.obp import traugott
from pygeopressure.basic.well import Well
from pygeopressure.basic.well_log import Log
from pygeopressure.basic.utils import rmse, pick_sparse
from pygeopressure.pressure.eaton import power_eaton
from sklearn import linear_model


def optimize_bowers_virgin(well, vel_log, obp_log, upper, lower,
                           pres_log='loading', mode='nc', nnc=5):
    """
    Optimizer for Bowers loading curve

    Parameters
    ----------
    well : Well
    vel_log : Log or str
        Log object or well log name stored in well
    obp_log : Log or str
        Log object or well log name stored in well
    upper : float or str
        upper bound of nct, depth value or horizon name
    lower : float or str
        lower bound of nct, depth value or horizon name
    pres_log : Log or str
        Log object storing measured pressure value or Pressure name
        stored in well
    mode : {'nc', 'pres', 'both'}
        which pressure to use for optimization,
        - 'nc' : points on NCT
        - 'pres' : points in pres_log
        - 'both' : both of them
    nnc : int
        number of points to pick on NCT

    Returns
    -------
    a, b : tuple of floats
        optimized bowers loading curve coefficients
    rms_err : float
        root mean square error of pressure
    """
    if isinstance(upper, str):
        depth_upper = well.params['horizon'][upper]
    else:
        depth_upper = upper
    if isinstance(upper, str):
        depth_lower = well.params['horizon'][lower]
    else:
        depth_lower = lower
    if isinstance(vel_log, str):
        vel_log = well.get_log(vel_log)
    if isinstance(obp_log, str):
        obp_log = well.get_log(obp_log)
    if isinstance(pres_log, str):
        pres_log = well.get_loading_pressure()

    depth = np.array(obp_log.depth)

    nct_vel_to_fit = []
    nct_es_to_fit = []
    pres_vel_to_fit = []
    pres_es_to_fit = []
    if mode == 'nct' or mode == 'both':
        nct_es_data = np.array(obp_log.data) - np.array(well.hydrostatic)
        nct_mask = depth < depth_lower
        nct_mask *= depth > depth_upper
        nct_mask *= depth < vel_log.stop

        nct_vel_interval = np.array(vel_log.data)[nct_mask]
        nct_es_interval = nct_es_data[nct_mask]

        nct_vel_to_fit = np.array(pick_sparse(nct_vel_interval, nnc))
        nct_es_to_fit = np.array(pick_sparse(nct_es_interval, nnc))
    if mode == 'pres' or mode == 'both':
        vel = list()
        obp = list()
        pres = list()
        for dp in pres_log.depth:
            idx = np.searchsorted(depth, dp)
            vel.append(vel_log.data[idx])
            obp.append(obp_log.data[idx])
        vel, obp, pres = np.array(vel), np.array(obp), np.array(pres_log.data)
        es = obp - pres

        pres_vel_to_fit = vel
        pres_es_to_fit = es
    vel_to_fit = np.append(nct_vel_to_fit, pres_vel_to_fit)
    es_to_fit = np.append(nct_es_to_fit, pres_es_to_fit)

    popt, _ = curve_fit(virgin_curve, es_to_fit, vel_to_fit)
    a, b = popt

    es_predicted = invert_virgin(vel_to_fit, a, b)
    rms_err = rmse(es_to_fit, es_predicted)

    return a, b, rms_err


def optimize_bowers_unloading(well, vel_log, obp_log, a, b,
                              vmax, pres_log='unloading'):
    """
    Optimize for Bowers Unloading curve parameter U

    Parameters
    ----------
    well : Well
    vel_log : Log or str
        Log object or well log name stored in well
    obp_log : Log or str
        Log object or well log name stored in well
    vmax : float
        vmax in bowers unloading curve
    pres_log : Log or str
        Log object storing measured pressure value or Pressure name
        stored in well

    Returns
    -------
    u : float
        unloading curve cofficient U
    error : float
        Relative RMS error
    """
    if isinstance(vel_log, str):
        vel_log = well.get_log(vel_log)
    if isinstance(obp_log, str):
        obp_log = well.get_log(obp_log)
    if isinstance(pres_log, str):
        pres_log = well._get_pressure(pres_log)

    depth = np.array(obp_log.depth)

    vel = list()
    obp = list()
    pres = list()
    for dp in pres_log.depth:
        idx = np.searchsorted(depth, dp)
        vel.append(vel_log.data[idx])
        obp.append(obp_log.data[idx])
    vel, obp, pres = np.array(vel), np.array(obp), np.array(pres_log.data)
    es = obp - pres

    sigma_max = invert_virgin(vmax, a, b)

    sigma_vc = invert_virgin(vel, a, b)

    popt, _ = curve_fit(power_bowers, sigma_vc/sigma_max, es/sigma_max)

    u, = popt

    return u


def optimize_eaton(well, vel_log, obp_log, a, b, pres_log="loading"):
    """
    Optimizer for Eaton model

    Parameters
    ----------
    well : Well
    vel_log : Log or str
        Log object or well log name stored in well
    obp_log : Log or str
        Log object or well log name stored in well
    a, b : float
        coefficients of NCT
    pres_log : Log or str
        Log object storing measured pressure value or Pressure name
        stored in well

    Returns
    -------
    n : float
        optimized eaton exponential
    min_eer : float
        minimum error abtained by optimized n
    rms_err : array
        array of rms error of different n around minmum
    """
    if isinstance(vel_log, str):
        vel_log = well.get_log(vel_log)
    if isinstance(obp_log, str):
        obp_log = well.get_log(obp_log)
    if isinstance(pres_log, str):
        pres_log = well.get_loading_pressure()

    depth = np.array(obp_log.depth)

    hydrostatic = np.array(well.hydrostatic)
    es_normal = np.array(obp_log.data) - hydrostatic
    v_normal = normal(depth, a, b)

    vel = list()
    vel_norm = list()
    es_norm = list()
    obp = list()
    pres = list()
    for dp in pres_log.depth:
        idx = np.searchsorted(depth, dp)
        vel.append(vel_log.data[idx])
        vel_norm.append(v_normal[idx])
        es_norm.append(es_normal[idx])
        obp.append(obp_log.data[idx])
    vel, vel_norm = np.array(vel), np.array(vel_norm)
    vel_ratio = vel / vel_norm

    obp, pres = np.array(obp), np.array(pres_log.data)
    es = obp - pres
    es_norm = np.array(es_norm)
    es_ratio = es / es_norm

    popt, _ = curve_fit(power_eaton, vel_ratio, es_ratio)
    n, = popt

    return n


def optimize_multivaraite(well, obp_log, vel_log, por_log, vsh_log, B,
                          upper, lower):
    if isinstance(vel_log, str):
        vel_log = well.get_log(vel_log)
    if isinstance(por_log, str):
        por_log = well.get_log(por_log)
    if isinstance(vsh_log, str):
        vsh_log = well.get_log(vsh_log)
    if isinstance(obp_log, str):
        obp_log = well.get_log(obp_log)
    # --------------------------------------------
    obp_data = np.array(obp_log.data)
    por_data = np.array(por_log.data)
    vp_data = np.array(vel_log.data)
    vsh_data = np.array(vsh_log.data)

    depth = well.depth
    hydrostatic = well.hydrostatic

    es = obp_data - hydrostatic

    B = well.params['bowers']['B'] if B is None else B  # 0.88
    es_data = es**B

    mask = np.isfinite(vp_data)
    mask *= np.isfinite(por_data)
    mask *= np.isfinite(vsh_data)
    mask *= depth < lower #3500
    mask *= depth > upper #1500

    por_data = por_data[mask]
    vsh_data = vsh_data[mask]
    es_data = es_data[mask]
    vp_data = vp_data[mask]
    depth = depth[mask]

    por_data = por_data.reshape((por_data.shape[0], 1))
    vsh_data = vsh_data.reshape((vsh_data.shape[0], 1))
    es_data = es_data.reshape((es_data.shape[0], 1))
    vp_data = vp_data.reshape((vp_data.shape[0], 1))

    #_____________________REGRESSION______________________
    data = np.hstack((por_data, vsh_data, es_data))
    # global REG
    reg = linear_model.LinearRegression()
    reg.fit(data, vp_data)

    r2 = reg.score(data, vp_data)

    a0 = reg.intercept_[0]
    a1 = -reg.coef_[0][0]
    a2 = -reg.coef_[0][1]
    a3 = reg.coef_[0][2]

    return a0, a1, a2, a3


def optimize_nct(vel_log, fit_start, fit_stop):
    """
    Fit velocity NCT

    Parameters
    ----------
    vel_log : Log
        Velocity log
    fit_start, fit_stop : float
        start and end depth for fitting

    Returns
    -------
    a, b : float
        NCT coefficients
    """
    fit_start = fit_start
    fit_stop = fit_stop

    if fit_start is None or fit_start < vel_log.top:
        fit_start = vel_log.top
    if fit_stop is None or fit_stop > vel_log.bottom:
        fit_stop = vel_log.bottom

    start_idx = vel_log.get_depth_idx(fit_start)
    stop_idx = vel_log.get_depth_idx(fit_stop) + 1
    depth = np.array(vel_log.depth[start_idx: stop_idx + 1])
    vel = np.array(vel_log.data[start_idx: stop_idx + 1])
    dt = vel**(-1)
    dt_log = np.log(dt)
    mask = np.isfinite(dt_log)
    dt_log_finite = dt_log[mask]
    depth_finite = depth[mask]

    popt, _ = curve_fit(normal_dt, depth_finite, dt_log_finite)
    a, b = popt

    return a, b


def optimize_traugott(den_log, fit_start, fit_stop, kb=0, wd=0):
    """
    Fit density variation against depth with Traugott equation

    Parameters
    ----------
    den_log : Log
        Density log
    fit_start, fit_stop : float
        start and end depth for fitting
    kb : float
        kelly bushing height in meters
    wd : float
        water depth in meters

    Returns
    -------
    a, b : float
        Traugott equation coefficients
    """
    start_idx = den_log.get_depth_idx(fit_start)
    stop_idx = den_log.get_depth_idx(fit_stop) + 1
    depth = np.array(den_log.depth[start_idx: stop_idx + 1])
    den = np.array(den_log.data[start_idx: stop_idx + 1])

    mask = np.isfinite(den)
    den_finite = den[mask]
    depth_finite = depth[mask]

    depth_finite_shift = depth_finite - kb - wd

    popt, _ = curve_fit(traugott, depth_finite, den_finite)
    a, b = popt

    return a, b
