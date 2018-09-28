# -*- coding: utf-8 -*-
"""
Routines for eaton seismic pressure prediction

Created on Sep 24 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

import numpy as np
from pygeopressure.basic.indexes import InlineIndex
from pygeopressure.basic.optimizer import optimize_nct_trace
from pygeopressure.velocity.extrapolate import normal
from pygeopressure.pressure.hydrostatic import hydrostatic_trace
from pygeopressure.pressure.utils import create_seis, create_seis_info
from pygeopressure.pressure.eaton import sigma_eaton


def eaton_seis(output_name, obp_cube, vel_cube, n,
               a=None, b=None, upper=None, lower=None):
    # create seismic object
    eaton_cube = create_seis(output_name, vel_cube)
    # create info file
    create_seis_info(eaton_cube, output_name)

    depth = np.array(list(vel_cube.depths()))

    hydrostatic = hydrostatic_trace(depth)
    hydro_inline = np.tile(hydrostatic, (vel_cube.nNorth, 1))

    # actual calcualtion
    for inl in vel_cube.inlines():
        obp_data_inline = obp_cube.data(InlineIndex(inl))
        vel_data_inline = vel_cube.data(InlineIndex(inl))
        vn_inline = np.zeros((vel_cube.nNorth, vel_cube.nDepth))
        for i, crl in enumerate(vel_cube.crlines()):
            cdp = (inl, crl)
            start_depth = upper.get_cdp(cdp)
            end_depth = lower.get_cdp(cdp)

            a, b = optimize_nct_trace(
                depth, vel_data_inline[i], start_depth, end_depth)

            vn_inline[i] = normal(depth, a, b)
        eaton_inline = obp_data_inline - \
            sigma_eaton(
                obp_data_inline-hydro_inline, vel_data_inline/vn_inline, n)

        eaton_cube.update(InlineIndex(inl), eaton_inline)

    return eaton_cube
