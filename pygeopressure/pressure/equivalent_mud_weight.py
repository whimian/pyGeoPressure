# -*- coding: utf-8 -*-
"""
Function to calculate Equivalent Mud Weight in MPa from mud density in kg/L

Created on Sat Oct 19 2019
"""
import numpy as np


def bfill(arr):
        mask = np.isnan(arr)
        idx = np.where(~mask, np.arange(mask.shape[1]), mask.shape[1] - 1)
        idx = np.minimum.accumulate(idx[:, ::-1], axis=1)[:, ::-1]
        out = arr[np.arange(idx.shape[0])[:,None], idx]
        return out


def emw(depth_mud, den_mud, kelly_bushing, depth_w, rho_f=1.01, rho_w=1.):
    """
    den_mud : 1-d array
        in kg/L
    """
    rho_f *= 1000  # kg/m3
    rho_w *= 1000  # kg/m3
    acceleration = 9.80665  # m/s2

    depth_mud = np.array(depth_mud)
    den_mud = np.array(den_mud) * 1000

    depth = np.arange(0, depth_mud[-1]+0.1, 0.1)

    density = np.full_like(depth, np.nan)

    for d, dm in zip(depth_mud, den_mud):
        density[np.searchsorted(depth, d)] = dm

    density = bfill(density.reshape(1, -1))
    density = density.reshape(density.shape[1])

    # sea level to sea bottom
    mask = depth < (kelly_bushing + depth_w)
    density[mask] = rho_w
    # kelly bushing to sea level
    mask = depth < kelly_bushing
    density[mask] = 0

    delta_depth = np.full_like(depth, np.nan)
    delta_depth[1:] = depth[1:] - depth[:-1]
    delta_depth[0] = 0
    emw = delta_depth * density * acceleration / 1000000  # mPa
    emw = np.cumsum(emw)

    emw_select = []
    for d in depth_mud:
        emw_select.append(emw[np.searchsorted(depth, d)])

    return np.array(emw_select)
