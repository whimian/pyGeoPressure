# -*- coding: utf-8 -*-
"""
Routines to calculate pore pressure
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np
from scipy.optimize import curve_fit

from pygeopressure.pressure.utils import create_seis, create_seis_info
from pygeopressure.basic.indexes import InlineIndex, CdpIndex
from pygeopressure.basic.utils import pick_sparse
from pygeopressure.pressure.hydrostatic import hydrostatic_trace


def bowers(v, obp, u, start_idx, a, b, vmax, end_idx=None):
    """
    Compute pressure using Bowers equation.

    Parameters
    ----------
    v : 1-d ndarray
        velocity array whose unit is m/s.
    obp : 1-d ndarray
        Overburden pressure whose unit is Pa.
    v0 : float, optional
        the velocity of unconsolidated regolith whose unit is m/s.
    a : float, optional
        coefficient a
    b : float, optional
        coefficient b

    Notes
    -----
    .. math:: P = S - \\left[\\frac{(V-V_{0})}{a}\\right]^{\\frac{1}{b}}

    [3]_

    .. [3] Bowers, G. L. (1994). Pore pressure estimation from velocity data:
       accounting from overpressure mechanisms besides undercompaction:
       Proceedings of the IADC/SPE drilling conference, Dallas, 1994,
       (IADC/SPE), 1994, pp 515–530. In International Journal of Rock
       Mechanics and Mining Sciences & Geomechanics Abstracts (Vol. 31,
       p. 276). Pergamon.
    """
    sigma_max = ((vmax-1524)/a)**(1/b)
    ves = ((v - 1524) / a)**(1.0 / b)
    ves_fe = sigma_max*(((v-1524)/a)**(1/b)/sigma_max)**u
    ves[start_idx: end_idx] = ves_fe[start_idx: end_idx]
    return obp - ves


def bowers_varu(v, obp, u, start_idx, a, b, vmax, buf=20, end_idx=None, end_buffer=10):
    """
    Bowers Method with buffer zone above unloading zone

    Parameters
    ----------
    v : 1-d ndarray
        velocity array whose unit is m/s.
    obp : 1-d ndarray
        Overburden pressure whose unit is Pa.
    u : float
        coefficient u
    start_idx : int
        index of start of fluid expansion
    a : float, optional
        coefficient a
    b : float, optional
        coefficient b
    vmax : float
    buf : int, optional
        len of buffer interval, buf should be smaller than start_idx
    end_idx : int
        end of fluid expasion
    end_buffer : int
        len of end buffer interval
    """
    u_array = np.ones(v.shape)
    u_array[start_idx: end_idx] = u
    # start buffer
    u_buffer = np.linspace(1, u, buf)
    u_array[start_idx-buf+1: start_idx + 1] = u_buffer
    # end buffer
    if end_idx is not None:
        u_array[end_idx: end_idx + end_buffer] = np.linspace(u, 1, end_buffer)
    sigma_max = ((vmax-1524)/a)**(1/b)
    ves = sigma_max*(((v-1524)/a)**(1/b)/sigma_max)**u_array
    return obp - ves


def virgin_curve(sigma, a, b):
    "Virgin curve in Bowers' method."
    v0 = 1524
    return v0 + a * sigma**b


def invert_virgin(v, a, b):
    "invert of virgin curve."
    v0 = 1524
    return ((v-v0)/a)**(1/b)


def unloading_curve(sigma, a, b, u, v_max):
    "Unloading curve in Bowers's method."
    sigma_max = ((v_max-1524)/a)**(1/b)
    independent = sigma_max*(sigma/sigma_max)**(1/u)
    return virgin_curve(independent, a, b)


def invert_unloading(v, a, b, u, v_max):
    "invert of Unloading curve in Bowers's method."
    sigma_max = invert_virgin(v_max, a, b)
    sigma_vc = invert_virgin(v, a, b)
    return sigma_max * (sigma_vc/sigma_max)**u


def power_bowers(sigma_vc_ratio, u):
    return sigma_vc_ratio**u


def bowers_seis(output_name, obp_cube, vel_cube, a=None, b=None,
                upper=None, lower=None, mode='simple'):
    # create seismic object
    bowers_cube = create_seis(output_name, vel_cube)
    # create info file
    create_seis_info(bowers_cube, output_name)
    if mode == 'optimize':
        # with optimization
        bowers_optimize(bowers_cube, obp_cube, vel_cube, upper, lower)
    else:
        # simple
        bowers_simple(bowers_cube, obp_cube, vel_cube, a, b)

    return bowers_cube


def bowers_simple(bowers_cube, obp_cube, vel_cube, a=None, b=None):
    # actual calcualtion
    for inl in vel_cube.inlines():
        obp_data_inline = obp_cube.data(InlineIndex(inl))
        vel_data_inline = vel_cube.data(InlineIndex(inl))

        bowers_inline = obp_data_inline - \
            invert_virgin(vel_data_inline, a, b)

        bowers_cube.update(InlineIndex(inl), bowers_inline)

def bowers_optimize(bowers_cube, obp_cube, vel_cube, upper_hor, lower_hor):

    depth_tr = np.array(list(vel_cube.depths()))
    hydro_tr = hydrostatic_trace(depth_tr)

    for inl in vel_cube.inlines():
        bowers_data_inline = np.zeros((vel_cube.nNorth, vel_cube.nDepth))
        for i, crl in enumerate(vel_cube.crlines()):
            vel_tr = vel_cube.data(CdpIndex((inl, crl)))
            obp_tr = obp_cube.data(CdpIndex((inl, crl)))
            depth_upper = upper_hor.get_cdp((inl, crl))
            if lower_hor == "bottom":
                depth_lower = depth_tr[-1]
            else:
                depth_lower = lower_hor.get_cdp((inl, crl))
            try:
                a, b = optimize_bowers_seismic(
                    depth_tr, vel_tr, obp_tr, hydro_tr, depth_upper, depth_lower)
            except:
                raise Exception("cdp{},{}".format(inl, crl))
            bowers_data_inline[i] = invert_virgin(vel_tr, a, b)

        bowers_cube.update(InlineIndex(inl), bowers_data_inline)


def optimize_bowers_seismic(depth_tr, vel_tr, obp_tr, hydro_tr, depth_upper, depth_lower):

    es_data = np.array(obp_tr) - np.array(hydro_tr)
    depth = np.array(depth_tr)

    mask = depth < depth_lower
    mask *= depth > depth_upper
    mask *= depth <= depth_tr[-1]

    vel_interval = np.array(vel_tr)[mask]
    es_interval = es_data[mask]

    vel_to_fit = pick_sparse(vel_interval, 3)
    es_to_fit = pick_sparse(es_interval, 3)

    popt, _ = curve_fit(virgin_curve, es_to_fit, vel_to_fit)
    a, b = popt

    return a, b
