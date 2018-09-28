# -*- coding: utf-8 -*-
"""
Routines for Bowers' pore pressure prediction with seismic velocity
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

import numpy as np

from pygeopressure.basic.indexes import InlineIndex, CdpIndex
from pygeopressure.basic.optimizer import optimize_bowers_trace
from pygeopressure.pressure.bowers import invert_virgin
from pygeopressure.pressure.hydrostatic import hydrostatic_trace
from pygeopressure.pressure.utils import create_seis, create_seis_info


def bowers_seis(output_name, obp_cube, vel_cube, a=None, b=None,
                upper=None, lower=None, mode='simple'):
    # create seismic object
    bowers_cube = create_seis(output_name, vel_cube)
    # create info file
    create_seis_info(bowers_cube, output_name)
    # calculation
    if mode == 'optimize':
        # with optimization
        bowers_optimize(bowers_cube, obp_cube, vel_cube, upper, lower)
    else:
        # simple
        bowers_simple(bowers_cube, obp_cube, vel_cube, a, b)

    return bowers_cube


def bowers_simple(bowers_cube, obp_cube, vel_cube, a=None, b=None):
    """
    Bowers prediction with fixed a, b
    """
    for inl in vel_cube.inlines():
        obp_data_inline = obp_cube.data(InlineIndex(inl))
        vel_data_inline = vel_cube.data(InlineIndex(inl))

        bowers_inline = obp_data_inline - \
            invert_virgin(vel_data_inline, a, b)

        bowers_cube.update(InlineIndex(inl), bowers_inline)


def bowers_optimize(bowers_cube, obp_cube, vel_cube, upper_hor, lower_hor):
    """
    Bowers prediction with automatic coefficient optimization
    """
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
                a, b = optimize_bowers_trace(
                    depth_tr, vel_tr, obp_tr, hydro_tr,
                    depth_upper, depth_lower)
            except:
                raise Exception("cdp{},{}".format(inl, crl))
            bowers_data_inline[i] = invert_virgin(vel_tr, a, b)

        bowers_cube.update(InlineIndex(inl), bowers_data_inline)
