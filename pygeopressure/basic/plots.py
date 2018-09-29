# -*- coding: utf-8 -*-
"""
a Well class utilizing pandas DataFrame and hdf5 storage

Created on May 27 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import zip, bytes, str

__author__ = "yuhao"

import json
from collections import OrderedDict
import random

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

import matplotlib as mpl
from pygeopressure.pressure.eaton import eaton, sigma_eaton, power_eaton
from pygeopressure.pressure.bowers import (
    virgin_curve, invert_virgin, unloading_curve)
from pygeopressure.pressure.multivariate import multivariate_virgin
from pygeopressure.velocity.extrapolate import normal
from pygeopressure.basic.well_log import Log
from pygeopressure.basic.utils import rmse, pick_sparse


class LoadingPlot(object):
    """
    Parameters
    ----------
    json_file : str
        path to parameter file
    """
    def __init__(self, ax, obp_logs, vel_logs, pres_logs, well_names):
        self.ax = ax
        self.obp_logs = obp_logs
        self.vel_logs = vel_logs
        self.pres_logs = pres_logs
        self.well_names = well_names
        self.a = None
        self.b = None
        self._calculate_data()
        self._init_axis()

    def _init_axis(self):
        # self.ax.cla()
        # self.ax.set(title="{}".format("Well"),
        #             xlabel="Effective Stress(MPa)",
        #             ylabel="Velocity(m/s)")
        # self.ax.set_xlim(xmin=0, xmax=80)
        pass

    def _calculate_data(self):
        self.vels = []
        self.ess = []
        for obp_log, vel_log, pres_log in zip(self.obp_logs, self.vel_logs, self.pres_logs):
            vel = list()
            obp = list()
            pres = list()
            depth = np.array(vel_log.depth)
            for dp in pres_log.depth:
                idx = np.searchsorted(depth, dp)
                vel.append(vel_log.data[idx])
                obp.append(obp_log.data[idx])

            vel, obp, pres = np.array(vel), np.array(obp), np.array(pres_log.data)
            es = obp - pres
            self.vels.append(vel)
            self.ess.append(es)

    def plot(self):
        # self._init_axis()
        colors = list(mpl.colors.cnames.keys())
        random.seed(2018)
        for es, vel, name in zip(self.ess, self.vels, self.well_names):
            co = random.choice(colors)
            self.ax.scatter(es, vel, color=co, marker='d', label=name)
        self.ax.legend(loc=4)
        self.ax.figure.canvas.draw()

    def fit(self):
        popt, _ = curve_fit(
            virgin_curve, np.concatenate(self.ess), np.concatenate(self.vels))
        a, b = popt
        self.a, self.b = popt
        new_es = np.arange(0, 81)
        new_vel = virgin_curve(new_es, a, b)
        self.ax.plot(new_es, new_vel, color='gray', zorder=0)
        self.ax.figure.canvas.draw()

    def error_sigma(self):
        new_es = np.arange(0, 81)
        new_vel = virgin_curve(new_es, self.a, self.b)
        error_dict = {}
        f = interp1d(new_vel, new_es, kind='cubic')
        for vel, es, wn in zip(self.vels, self.ess, self.well_names):
            predict_es = f(vel)
            error_dict[wn] = (predict_es - es) / es * 100
        return error_dict

    def check_error(self, obp_log, vel_log, pres_log):
        # for obp_log, vel_log, pres_log in zip(self.obp_logs, self.vel_logs, self.pres_logs):
        vel = list()
        obp = list()
        pres = list()
        depth = np.array(vel_log.depth)
        for dp in pres_log.depth:
            idx = np.searchsorted(depth, dp)
            vel.append(vel_log.data[idx])
            obp.append(obp_log.data[idx])

        vel, obp, pres = np.array(vel), np.array(obp), np.array(pres_log.data)
        es = obp - pres

        new_es = np.arange(0, 81)
        new_vel = virgin_curve(new_es, self.a, self.b)
        # error_dict = {}
        f = interp1d(new_vel, new_es, kind='cubic')

        predict_es = f(vel)
        return (predict_es - es) / es * 100


def plot_bowers_vrigin(ax, a, b, well, vel_log, obp_log, upper, lower,
                       pres_log='loading', mode='nc', nnc=5):
    if isinstance(upper, (bytes, str)):
        depth_upper = well.params['horizon'][upper]
    else:
        depth_upper = upper
    if isinstance(upper, (bytes, str)):
        depth_lower = well.params['horizon'][lower]
    else:
        depth_lower = lower
    if isinstance(vel_log, (bytes, str)):
        vel_log = well.get_log(vel_log)
    if isinstance(obp_log, (bytes, str)):
        obp_log = well.get_log(obp_log)
    if isinstance(pres_log, (bytes, str)):
        # pres_log = well.get_loading_pressure()
        pres_log = well.get_pressure(pres_log)

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
        ax.scatter(
            nct_es_to_fit, nct_vel_to_fit, color='blue', marker='d',
            label='NCP')
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
        ax.scatter(
            pres_es_to_fit, pres_vel_to_fit, color='purple', marker='s',
            label='measured')

    es_curve = np.arange(0, 80, 1)
    vel_curve = virgin_curve(es_curve, a, b)
    ax.plot(es_curve, vel_curve, color='black', zorder=1, label="Loading")

    ax.set(title="Loading Curve - {}".format(well.well_name),
           xlabel="Effective Stress(MPa)",
           ylabel="Velocity(m/s)")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=1500)

    ax.legend(loc=4)


def plot_bowers_unloading(ax, a, b, u, vmax, well, vel_log, obp_log,
                          pres_log='unloading'):
    """
    plot bowers unloading plot
    """
    if isinstance(vel_log, (bytes, str)):
        vel_log = well.get_log(vel_log)
    if isinstance(obp_log, (bytes, str)):
        obp_log = well.get_log(obp_log)
    if isinstance(pres_log, (bytes, str)):
        pres_log = well.get_pressure(pres_log)

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

    ax.scatter(es, vel, marker="^", color='r', label='meassured')

    sigma_max = invert_virgin(vmax, a, b)

    es_curve = np.arange(0, sigma_max+1, 1)


    vel_curve = unloading_curve(es_curve, a, b, u, vmax)

    ax.plot(es_curve, vel_curve, label='unloading')
    ax.legend(loc='lower right')


def plot_eaton_error(ax, well, vel_log, obp_log, a, b, pres_log="loading"):
    if isinstance(vel_log, (bytes, str)):
        vel_log = well.get_log(vel_log)
    if isinstance(obp_log, (bytes, str)):
        obp_log = well.get_log(obp_log)
    if isinstance(pres_log, (bytes, str)):
        # pres_log = well.get_loading_pressure()
        pres_log = well.get_pressure(pres_log)

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

    rms_err = rmse(es, sigma_eaton(es_norm, vel_ratio, n))

    n_array = np.arange(n-2, n+2, 0.01)
    err_array = []
    for ni in n_array:
        predict_sigma = sigma_eaton(es_norm, vel_ratio, ni)
        err_array.append(rmse(es, predict_sigma))

    ax.plot(n_array, err_array, color='black')
    ax.axvline(x=n, color='g')
    ax.set(title='Optimize Eaton', xlabel="n", ylabel="RMS Error")
    info_string = "n:{}\nRMS:{}".format(n, rms_err)
    ax.text(
        s="{}".format(info_string), x=0.1, y=0.1, color='b',
        transform=ax.transAxes, size=9)


def plot_multivariate(axes, well, vel_log, por_log, vsh_log, obp_log,
                      upper, lower, a0, a1, a2, a3, B):

    axes[0].plot(np.array(vel_log.data)/1000, vel_log.depth, linewidth=0.5,
                 color='gray')

    axes[0].set(xlabel='Vp (km/s)', ylabel='Depth (m)', ylim=[lower, upper])


    axes[1].plot(por_log.data, por_log.depth, linewidth=0.5, color='gray')
    axes[1].set(xlabel='$\phi$')

    axes[2].plot(vsh_log.data, vsh_log.depth, linewidth=0.5, color='gray')
    axes[2].set(xlabel='$V_{sh}$')

    depth = well.depth
    hydrostatic = well.hydrostatic
    obp = well.lithostatic
    es = obp - hydrostatic

    axes[3].plot(es**B, depth, color='gray')
    axes[3].set(xlabel='${\sigma}^{B}$')

    vel_predict = multivariate_virgin(
        es, np.array(por_log.data), np.array(vsh_log.data), a0, a1, a2, a3, B)
    axes[0].plot(vel_predict/1000, vel_log.depth)
