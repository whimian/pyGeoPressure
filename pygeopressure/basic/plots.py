# -*- coding: utf-8 -*-
"""
a Well class utilizing pandas DataFrame and hdf5 storage

Created on May 27 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import str

__author__ = "yuhao"

import json
from collections import OrderedDict
import random

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

import matplotlib as mpl
from ..pressure.hydrostatic import hydrostatic_pressure
from ..pressure.eaton import eaton
from ..velocity.extrapolate import normal
from ..pressure.bowers import virgin_curve
from .well_log import Log
# from .well_storage import WellStorage
from pygeopressure.basic.utils import rmse, pick_sparse
from pygeopressure.pressure.eaton import sigma_eaton, ratio_eaton


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
            label='NCP')

    es_curve = np.arange(0, 80, 1)
    vel_curve = virgin_curve(es_curve, a, b)
    ax.plot(es_curve, vel_curve, color='black', zorder=1, label="Loading")

    ax.set(title="Loading Curve - {}".format(well.well_name),
           xlabel="Effective Stress(MPa)",
           ylabel="Velocity(m/s)")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=1500)

    ax.legend(loc=4)

# # Plot LOADING points -----------------------------
    # vel_loading = list()
    # obp_loading = list()
    # pres_log_loading = well.get_loading_pressure()
    # for dp in pres_log_loading.depth:
    #     index = np.searchsorted(depth, dp)
    #     vel_loading.append(vel_log.data[index])
    #     obp_loading.append(obp_log.data[index])
    # vel_loading, obp_loading, pres_loading = np.array(vel_loading), np.array(obp_loading), np.array(pres_log_loading.data)
    # es_loading = obp_loading - pres_loading
    # handles.append(ax_virgin.scatter(es_loading, vel_loading, marker='o', color = 'red', label='Loading'))
    # # get UNLOADING points ----------------------------------------------------------------------------------
    # vel_unloading = list()
    # obp_unloading = list()
    # pres_log_unloading = well.get_unloading_pressure()
    # print(len(pres_log_unloading.data), len(pres_log_unloading.depth))
    # for dp in pres_log_unloading.depth:
    #     index = np.searchsorted(depth, dp)
    #     vel_unloading.append(vel_log.data[index])
    #     obp_unloading.append(obp_log.data[index])
    # vel_unloading, obp_unloading, pres_unloading = np.array(vel_unloading), np.array(obp_unloading), np.array(pres_log_unloading.data)
    # es_unloading = obp_unloading - pres_unloading
    # handles.append(ax_virgin.scatter(es_unloading, vel_unloading, color='darkgreen', marker='*', label='Unloading', zorder=10))
    #plot a empty scatter for legend
    # handles_wells.append(ax_virgin.scatter([], [], color=co2))

    # sc_normal = ax_virgin.scatter([], [], marker='o', color='grey')
    # sc_unloading = ax_virgin.scatter([], [], marker='*', color='grey')
    # sc_loading = ax_virgin.scatter([], [], marker='d', color='grey')


def plot_eaton_error(ax, well, vel_log, obp_log, a, b, pres_log="loading"):
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

    popt, _ = curve_fit(ratio_eaton, vel_ratio, es_ratio)
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
