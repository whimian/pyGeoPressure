# -*- coding: utf-8 -*-
"""
well log processing tools

Created on Sep 19 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

from builtins import range, open
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt

from pygeopressure.velocity.smoothing import smooth

from pygeopressure.pressure.obp import traugott_trend
from pygeopressure.basic.well_log import Log
from pygeopressure.velocity.lowpass_filter import butter_lowpass_filter


def extrapolate_log_traugott(den_log, a, b, kb=0, wd=0):
    """
    Extrapolate density log using Traugott equation
    """
    density_trend = traugott_trend(
        np.array(den_log.depth), a, b, kb=kb, wd=wd)

    extra_log = Log()
    extra_log.name = den_log.name + "_ex"
    extra_log.units = den_log.units
    extra_log.descr = "Density_extra"
    extra_log.depth = np.array(den_log.depth)

    new_data = np.full_like(density_trend, np.nan)
    new_data[:den_log.start_idx] = density_trend[:den_log.start_idx]

    old_data = np.array(den_log.data)
    new_data[den_log.start_idx:] = old_data[den_log.start_idx:]

    extra_log.data = new_data

    return extra_log


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


# def upscale_log(log, freq=20):
#     """
#     downscale a well log with a lowpass butterworth filter
#     """
#     depth = np.array(log.depth)
#     data = np.array(log.data)
#     mask = np.isfinite(data)
#     func = interp1d(depth[mask], data[mask])
#     interp_data = func(depth[log.start_idx: log.stop_idx])

#     sample_rate = 1 / 0.002
#     filtered = butter_lowpass_filter(
#         interp_data, freq, sample_rate/2)

#     downscale_data = np.array(data)
#     downscale_data[log.start_idx: log.stop_idx] = filtered
#     log_downscale = Log()
#     log_downscale.name = log.name + "_downscale_" + str(freq)
#     log_downscale.units = log.units
#     log_downscale.descr = log.descr
#     log_downscale.depth = log.depth
#     log_downscale.data = downscale_data

#     return log_downscale

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
