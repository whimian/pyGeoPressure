# -*- coding: utf-8 -*-
"""
class Log for well log data

Created on Fri Apr 18 2017
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit

from pygeopressure.velocity.smoothing import smooth
from pygeopressure.velocity.extrapolate import normal_dt


class Log(object):
    """
    class for well log

    Attributes
    ----------
    name : str
        log name
    units : str
        units of log
    descr : str
        description of log
    prop_type : str {'VEL', 'DEN', 'VSH', 'PRE'}
        property type of log
    depth : list
    data : list
    top : float
        minimum depth of log
    bottom : float
        maximum depth of log
    start : float
        start depth of log data
    stop : float
        end depth of log data
    start_idx : int
        index of start of log data
    stop_idx : int
        index of end of log data
    """
    def __init__(self, file_name=None, log_name="unk"):
        """
        Parameters
        ----------
        file_name : str
            pseudo las file path
        log_name : str
            log name to create
        """
        self.name = log_name
        self.units = ""
        self.descr = ""
        self.prop_type = None
        self.__data = []
        self.__depth = []
        self.log_start = None
        self.log_stop = None
        self.depth_start = None
        self.depth_stop = None
        self.log_start_idx = None
        self.log_stop_idx = None
        if file_name is not None:
            self.__init_from_file(file_name)

    def __init_from_file(self, file_name):
        self.read_od(file_name)
        try:
            shorthand = self.descr[:3].lower()
            self.name = shorthand + "_unk"
            prop_dict = {
                'vel': 'VEL',
                'den': 'DEN',
                'sha': 'VSH',
                'ove': 'PRE',
                'pre': 'PRE'
            }
            try:
                self.prop_type = prop_dict[shorthand]
            except KeyError:
                pass
        except IndexError:
            self.name = "unk_unk"

    def __len__(self):
        return len(self.__data)

    def __str__(self):
        if not self.__depth:
            start, end = (0, 0)
        elif len(self.__depth) == 1:
            start, end = [self.__depth[0]] * 2
        else:
            start = self.__depth[0]
            end = self.__depth[-1]
        return "Log Name: {}\n".format(self.name) +\
               "Attribute Name: {}\n".format(self.descr) +\
               "Log Units: {}\n".format(self.units) +\
               "Depth range: {} - {} - {}\n".format(
                   start, end, 0.1)

    def __repr__(self):
        return "<Well_log:_{}>".format(self.name)

    def __bool__(self):
        return bool(bool(self.__depth) and bool(self.__data))

    def __eq__(self, other):
        return self.depth == other.depth and self.data == other.data

    @property
    def depth(self):
        return list(self.__depth)

    @depth.setter
    def depth(self, values):
        self.__depth = list(values)

    @property
    def data(self):
        return list(self.__data)

    @data.setter
    def data(self, values):
        self.__data = list(values)

    @property
    def start(self):
        if self.log_start is None:
            for dep, dat in zip(self.__depth, self.__data):
                if np.isfinite(dat):
                    self.log_start = dep
                    break
        return self.log_start

    @property
    def start_idx(self):
        if self.log_start_idx is None:
            self.__data = np.array(self.__data)
            mask = np.isfinite(self.__data)
            index = np.where(mask == True)
            self.log_start_idx = index[0][0]
        return self.log_start_idx

    @property
    def stop(self):
        if self.log_stop is None:
            for dep, dat in zip(reversed(self.__depth), reversed(self.__data)):
                if np.isfinite(dat):
                    self.log_stop = dep
                    break
        return self.log_stop

    @property
    def stop_idx(self):
        if self.log_stop_idx is None:
            self.__data = np.array(self.__data)
            mask = np.isfinite(self.__data)
            index = np.where(mask == True)
            self.log_stop_idx = index[0][-1] + 1
            # so when used in slice, +1 will not needed.
        return self.log_stop_idx

    @property
    def top(self):
        return self.__depth[0]

    @property
    def bottom(self):
        return self.__depth[-1]

    def read_od(self, file_name):
        try:
            with open(file_name, "r") as fin:
                info_list = fin.readline().split('\t')
                temp_list = info_list[-1].split('(')
                self.descr = temp_list[0]
                self.units = temp_list[1][:-2]
                for line in fin:
                    tempList = line.split()
                    self.__depth.append(round(float(tempList[0]), 1))
                    if tempList[1] == "1e30":
                        self.__data.append(np.nan)
                    else:
                        self.__data.append(float(tempList[1]))
        except Exception as inst:
            print('{}: '.format(self.name))
            print(inst.args)

    def write_od(self, file_name):
        try:
            with open(file_name, 'w') as fout:
                split_list = self.descr.split(' ')
                description = '_'.join(split_list)
                fout.write("Depth(m)\t" + description + "(" + self.units + ")\n")
                for d, v in zip(self.__depth, self.__data):
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
        log_depth = np.array(self.__depth)
        log_data = np.array(self.__data)
        mask = log_depth < 0
        for idx in depth_idx:
            if idx is not None:
                mask[idx] = True
        return log_data[mask]

    def get_resampled(self, rate):
        standard_log_step = 0.1
        step = int(rate // standard_log_step) + 1
        log = Log()
        log.depth = self.depth[::step]
        log.data = self.data[::step]
        return log

    def plot(self, ax=None):
        """
        Plot log curve

        Parameters
        ----------
        ax : matplotlib.axes._subplots.AxesSubplot
            axis object to plot on, a new axis will be created if not provided

        Returns
        -------
        ax : matplotlib.axes._subplots.AxesSubplot
            axis object on which the curve has been plotted
        """
        if ax is None:
            _, ax = plt.subplots()
            ax.invert_yaxis()
        ax.plot(self.data, self.depth)
        ax.set(xlabel="{}({})".format(self.descr, self.units),
               ylabel="Depth(m)",
               title=self.name)
        return ax

    def fit_normal(self, interval=None):
        if interval is None:
            interval = (self.start, self.stop)
        if self.prop_type == 'VEL':
            start_idx = self.get_depth_idx(interval[0])
            stop_idx = self.get_depth_idx(interval[1]) + 1
            depth = np.array(self.depth[start_idx: stop_idx + 1])
            vel = np.array(self.data[start_idx: stop_idx + 1])
            dt = vel**(-1)
            dt_log = np.log(dt)
            mask = np.isfinite(dt_log)
            dt_log_finite = dt_log[mask]
            depth_finite = depth[mask]

            popt, _ = curve_fit(normal_dt, depth_finite, dt_log_finite)
            a, b = popt

            new_dt_log = normal_dt(np.array(self.depth), a, b)
            new_dt = np.exp(new_dt_log)
            new_vel = new_dt**(-1)

            normal_vel_log = Log()
            normal_vel_log.depth = self.depth
            normal_vel_log.data = new_vel
            normal_vel_log.name = "nct" + self.name[3:]
            normal_vel_log.descr = "Normal Velocity"
            normal_vel_log.units = 'm/s'
            normal_vel_log.prop_type = 'VEL'
            return (a, b), normal_vel_log
        elif self.prop_type == 'DEN':
            pass
        else:
            print("function applied only to VEL or DEN")


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
    Parameters
    ----------
    log : Log object
        log to smooth
    window : scalar
        window size of the median filter

    Returns
    -------
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


def upscale_log(log, freq=20):
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
    """
    Log curve interpolation
    """
    depth = np.array(log.depth)
    data = np.array(log.data)
    mask = np.isfinite(data)
    func = interp1d(depth[mask], data[mask])
    interp_data = func(depth[log.start_idx: log.stop_idx])
    data[log.start_idx: log.stop_idx] = interp_data

    interp_log = Log()
    interp_log.name = log.name + '_interp'
    interp_log.units = log.units
    interp_log.descr = log.descr
    interp_log.depth = depth
    interp_log.data = data
    return interp_log


def local_average(log, rad=10):
    """upscale data using local averaging

    Parameters
    ----------
    data : Log()
        log data to be upscaled
    rad : int
        local radius, data within this radius will be represented by a single value

    Returns
    -------
    new_log : Log()
        upscaled log data
    """
    data = np.array(log.data)
    mask = np.isfinite(data)
    index = np.where(mask)
    start = index[0][0]
    end = index[0][-1]+1
    interval = data[start: end]
    index_toadd = []
    data_toadd = []

    step = rad*2+1
    n = len(interval)
    for i in range(0, n, step):
        seg = interval[i: i+step]
        new_mask = np.isfinite(seg)
        if len(seg[new_mask]) > rad+1:
            data_toadd.append(np.mean(seg[new_mask]))
            index_toadd.append(start+i+rad)
    data_toadd, index_toadd = np.array(data_toadd), np.array(index_toadd)
    new_data = np.full_like(data, np.nan)
    new_data[index_toadd] = data_toadd
    new_log = Log()
    new_log.depth = log.depth
    new_log.data = new_data
    return new_log


def write_peudo_las(file_name, logs):
    """
    Write multiple logs to a pseudo las file.
    """
    try:
        with open(file_name, 'w') as fout:
            description = ["Depth(m)"]
            for log in logs:
                split_list = log.descr.split(' ')
                description.append('_'.join(split_list)+"(" + log.units + ")")
            first_line = '\t'.join(description)
            fout.write(first_line + "\n")
            data = [logs[0].depth] + [log.data for log in logs]
            data = np.stack(data)
            for ds in np.nditer(data, flags=['external_loop'], order='F'):
                line = [str(v) if np.isfinite(v) else "1e30" for v in ds]
                fout.write("\t".join(line) + "\n")
            return True
    except Exception as inst:
        print(inst.args)
