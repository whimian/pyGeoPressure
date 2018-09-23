# -*- coding: utf-8 -*-
"""
Routines for eaton pressure prediction

Created on Sep 20 2018
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np

from pygeopressure.pressure.utils import create_seis, create_seis_info
from pygeopressure.pressure.hydrostatic import hydrostatic_trace
from pygeopressure.basic.indexes import InlineIndex
from pygeopressure.velocity.extrapolate import normal


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

    Returns
    -------
    ndarray

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


def sigma_eaton(es_norm, v_ratio, n):
    """
    calculate effective pressure with the ratio of velocity and normal velocity

    Notes
    -----
    .. math:: {\\sigma}={\\sigma}_{n}\\left(\\frac{V}{V_{n}}\\right)^{n}

    """
    return es_norm * (v_ratio)**n


def power_eaton(v_ratio, n):
    """
    Notes
    -----
    .. math:: \\frac{\\sigma}{{\\sigma}_{n}}=
        \\left(\\frac{V}{V_{n}}\\right)^{n}

    """
    return (v_ratio)**n


def eaton_seis(output_name, obp_cube, vel_cube, a, b, n):
    # create seismic object
    eaton_cube = create_seis(output_name, vel_cube)
    # create info file
    create_seis_info(eaton_cube, output_name)

    depth = np.array(list(vel_cube.depths()))
    # depth_inline = np.tile(depth,(vel_cube.nNorth, 1))
    vn = normal(depth, a, b)
    vn_inline = np.tile(vn, (vel_cube.nNorth, 1))

    hydrostatic = hydrostatic_trace(depth)
    hydro_inline = np.tile(hydrostatic, (vel_cube.nNorth, 1))

    # actual calcualtion
    for inl in vel_cube.inlines():
        obp_data_inline = obp_cube.data(InlineIndex(inl))
        vel_data_inline = vel_cube.data(InlineIndex(inl))

        eaton_inline = obp_data_inline - \
            sigma_eaton(
                obp_data_inline-hydro_inline, vel_data_inline/vn_inline, n)

        eaton_cube.update(InlineIndex(inl), eaton_inline)

    return eaton_cube
