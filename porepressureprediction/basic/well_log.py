# -*- coding: utf-8 -*-
"""
class Log for well log data

Created on Fri Apr 18 2017
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt

from porepressureprediction.velocity.smoothing import smooth


class Log(object):
    """
    class for well log
    """
    def __init__(self, file_name=None):
        self.name = ""
        self.units = ""
        self.descr = ""
        self.data = list()
        self.depth = list()
        self.log_start = None
        self.log_stop = None
        self.depth_start = None
        self.depth_stop = None
        self.log_start_idx = None
        self.log_stop_idx = None
        if file_name is not None:
            self.read_od(file_name)

    def __len__(self):
        return len(self.data)

    def _info(self):
        return "Log Name: {}\n".format(self.name) +\
               "Attribute Name: {}\n".format(self.descr) +\
               "Log Units: {}\n".format(self.units) +\
               "Depth range: {} - {} - {}\n".format(
                   self.depth[0], self.depth[-1], 0.1)

    def __str__(self):
        return self._info()

    def __repr__(self):
        return self._info()

    @property
    def start(self):
        if self.log_start is None:
            for dep, dat in zip(self.depth, self.data):
                if dat is not np.nan:
                    self.log_start = dep
                    break
        return self.log_start

    @property
    def start_idx(self):
        if self.log_start_idx is None:
            self.data = np.array(self.data)
            mask = np.isfinite(self.data)
            index = np.where(mask == True)
            self.log_start_idx = index[0][0]
            return self.log_start_idx
        else:
            return self.log_start_idx


    @property
    def stop(self):
        if self.log_stop is None:
            for dep, dat in zip(reversed(self.depth), reversed(self.data)):
                if dat is not np.nan:
                    self.log_stop = dep
                    break
        return self.log_stop

    @property
    def stop_idx(self):
        if self.log_stop_idx is None:
            self.data = np.array(self.data)
            mask = np.isfinite(self.data)
            index = np.where(mask == True)
            self.log_stop_idx = index[0][-1] + 1
            # so when used in slice, +1 will not needed.
            return self.log_stop_idx
        else:
            return self.log_stop_idx

    @property
    def top(self):
        return self.depth[0]

    @property
    def bottom(self):
        return self.depth[-1]

    def read_od(self, file_name):
        try:
            with open(file_name, "r") as fin:
                info_list = fin.readline().split('\t')
                temp_list = info_list[-1].split('(')
                self.descr = temp_list[0]
                self.units = temp_list[1][:-2]
                for line in fin:
                    tempList = line.split()
                    self.depth.append(round(float(tempList[0]), 1))
                    if tempList[1] == "1e30":
                        self.data.append(np.nan)
                    else:
                        self.data.append(float(tempList[1]))
        except Exception as inst:
            print('{}: '.format(self.name))
            print(inst.args)

    def write_od(self, file_name):
        try:
            with open(file_name, 'w') as fout:
                split_list = self.descr.split(' ')
                description = '_'.join(split_list)
                fout.write("Depth(m)\t" + description + "(" + self.units + ")\n")
                for d, v in zip(self.depth, self.data):
                    d = str(d)
                    v = str(v) if np.isfinite(v) else "1e30"
                    fout.write("\t".join([d, v]) + "\n")
        except Exception as inst:
            print(inst.args)

    def get_depth_idx(self, d):
        if d > self.bottom or d < self.top:
            return None
        else:
            return int((d - self.top) // 0.1)

    def get_data(self, depth):
        depth_idx = list()
        for de in depth:
            depth_idx.append(self.get_depth_idx(de))
        log_depth = np.array(self.depth)
        log_data = np.array(self.data)
        mask = log_depth < 0
        for idx in depth_idx:
            if idx is not None:
                mask[idx] = True
        return log_data[mask]

def rolling_window(a, window):
    a = np.array(a)
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolled = np.lib.stride_tricks.as_strided(
        a, shape=shape, strides=strides)
    return rolled


def despike(curve, curve_sm, max_clip):
    spikes = np.where(curve - curve_sm > max_clip)[0]
    spukes = np.where(curve_sm - curve > max_clip)[0]
    out = np.copy(curve)
    out[spikes] = curve_sm[spikes] + max_clip
    out[spukes] = curve_sm[spukes] - max_clip
    return out


def smooth_log(log, window=1500):
    """
    Parameter
    ---------
    log : Log object
        log to smooth
    window : scalar
        window size of the median filter

    Return
    ------
    smoothed log : Log object
        smoothed log
    """
    data = np.array(log.data)
    depth = np.array(log.depth)
    mask = np.isfinite(data)
    func = interp1d(depth[mask], data[mask])
    interp_data = func(depth[log.start_idx: log.stop_idx])
    new_data = np.array(data)
    new_data[log.start_idx: log.stop_idx] = interp_data
    smoothed = smooth(new_data[log.start_idx: log.stop_idx], window_len=window//2, window='flat')
    # using half the window length in order to be consistent with opendtect
    smooth_data = np.array(data)
    smooth_data[log.start_idx: log.stop_idx] = smoothed
    log_smooth = Log()
    log_smooth.name = log.name + "_sm"
    log_smooth.units = log.units
    log_smooth.descr = log.descr
    log_smooth.depth = log.depth
    log_smooth.data = smooth_data
    return log_smooth


def downscale_log(log, freq=20):
    """
    downscale a well log with a lowpass butterworth filter
    """
    depth = np.array(log.depth)
    data = np.array(log.data)
    mask = np.isfinite(data)
    func = interp1d(depth[mask], data[mask])
    interp_data = func(depth[log.start_idx: log.stop_idx])
    nyq = 10000 / 2
    dw = freq / nyq
    b, a = butter(4, dw, btype='low', analog=False)
    filtered = filtfilt(b, a, interp_data, method='gust')
    downscale_data = np.array(data)
    downscale_data[log.start_idx: log.stop_idx] = filtered
    log_downscale = Log()
    log_downscale.name = log.name + "_downscale_" + str(freq)
    log_downscale.units = log.units
    log_downscale.descr = log.descr
    log_downscale.depth = log.depth
    log_downscale.data = downscale_data
    return log_downscale

def truncate_log(log, top, bottom):
    """
    Remove unreliable values in the top and bottom section of well log

    Parameters
    ----------
    log : Log object
    top, bottom : scalar
        depth value

    Returns
    -------
    trunc_log : Log object
    """
    depth = np.array(log.depth)
    data = np.array(log.data)
    if top != 0:
        mask = depth < top
        data[mask] = np.nan
    if bottom != 0:
        mask = depth > bottom
        data[mask] = np.nan
    trunc_log = Log()
    trunc_log.name = log.name + '_trunc'
    trunc_log.units = log.units
    trunc_log.descr = log.descr
    trunc_log.depth = depth
    trunc_log.data = data
    return trunc_log


def shale(log, vsh_log, thresh=0.35):
    """
    Discern shale intervals

    log : Log
        log to discern
    vsh_log : Log
        shale volume log
    thresh : scalar
        percentage threshold, 0 < thresh < 1
    """
    shale_mask = np.isfinite(vsh_log.depth)
    shale_mask[vsh_log.start_idx: vsh_log.stop_idx] = True
    mask_thresh = np.array(vsh_log.data) < thresh
    mask = shale_mask * mask_thresh
    data = np.array(log.data)
    data[mask] = np.nan
    log_sh = Log()
    log_sh.name = log.name + "_sh"
    log_sh.units = log.units
    log_sh.descr = log.descr
    log_sh.depth = log.depth
    log_sh.data = data
    return log_sh


def interpolate_log(log):
    "log curve interpolation"
    depth = np.array(log.depth)
    data = np.array(log.data)
    # interpolation function
    mask_finite = np.isfinite(data)
    func = interpolate.interp1d(depth[mask_finite], data[mask_finite])
    mask = np.isnan(depth)
    mask[log.start_idx: log.stop_idx] = True
    mask_nan = np.isnan(data)
    mask = mask * mask_nan
    data[mask] = func(depth[mask])
    interp_log = Log()
    interp_log.name = log.name + '_interp'
    interp_log.units = log.units
    interp_log.descr = log.descr
    interp_log.depth = depth
    interp_log.data = data
    return interp_log
