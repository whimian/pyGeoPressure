# -*- coding: utf-8 -*-
"""
class Log for well log data

Created on Fri Apr 18 2017
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import zip, open

__author__ = "yuhao"

import numpy as np
import matplotlib.pyplot as plt


class Log(object):
    """
    class for well log data
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

    @classmethod
    def from_scratch(cls, depth, data, name=None, units=None, descr=None,
                     prop_type=None):
        log = cls()
        log.depth = np.array(depth)
        log.data = np.array(data)
        log.name = name
        log.units = units
        log.descr = descr
        log.prop_type = prop_type

        return log

    def __init_from_file(self, file_name):
        self._read_od(file_name)
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
        return "Well_Log:{}({}[{}])".format(self.name, self.descr, self.units)

    def __bool__(self):
        return bool(bool(self.__depth) and bool(self.__data))

    def __eq__(self, other):
        return self.depth == other.depth and self.data == other.data

    @property
    def depth(self):
        "depth data of the log"
        return list(self.__depth)

    @depth.setter
    def depth(self, values):
        self.__depth = list(values)

    @property
    def data(self):
        "property data of the log"
        return list(self.__data)

    @data.setter
    def data(self, values):
        self.__data = list(values)

    @property
    def start(self):
        "start depth of available property data"
        if self.log_start is None:
            for dep, dat in zip(self.__depth, self.__data):
                if np.isfinite(dat):
                    self.log_start = dep
                    break
        return self.log_start

    @property
    def start_idx(self):
        "start index of available property data"
        if self.log_start_idx is None:
            self.__data = np.array(self.__data)
            mask = np.isfinite(self.__data)
            index = np.where(mask == True)
            self.log_start_idx = index[0][0]
        return self.log_start_idx

    @property
    def stop(self):
        "end depth of available property data"
        if self.log_stop is None:
            for dep, dat in zip(reversed(self.__depth), reversed(self.__data)):
                if np.isfinite(dat):
                    self.log_stop = dep
                    break
        return self.log_stop

    @property
    def stop_idx(self):
        "end index of available property data"
        if self.log_stop_idx is None:
            self.__data = np.array(self.__data)
            mask = np.isfinite(self.__data)
            index = np.where(mask == True)
            self.log_stop_idx = index[0][-1] + 1
            # so when used in slice, +1 will not needed.
        return self.log_stop_idx

    @property
    def top(self):
        "top depth of this log"
        return self.__depth[0]

    @property
    def bottom(self):
        "bottom depth of this log"
        return self.__depth[-1]

    def _read_od(self, file_name):
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

    def to_las(self, file_name):
        """
        Save as pseudo-las file
        """
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
        "return index of depth"
        if d > self.bottom or d < self.top:
            return None
        else:
            return int((d - self.top) // 0.1)

    def get_data(self, depth):
        "get data at certain depth"
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
        "return resampled log"
        standard_log_step = 0.1
        step = int(rate // standard_log_step) + 1
        log = Log()
        log.depth = self.depth[::step]
        log.data = self.data[::step]
        return log

    def plot(self, ax=None, color='gray', linewidth=0.5, linestyle='-',
             label=None, zorder=1):
        """
        Plot log curve

        Parameters
        ----------
        ax : matplotlib.axes._subplots.AxesSubplot
            axis object to plot on, a new axis will be created if not provided

        Returns
        -------
        matplotlib.axes._subplots.AxesSubplot
        """
        if ax is None:
            _, ax = plt.subplots()
            ax.invert_yaxis()
        if label is None:
            label = self.descr
        ax.plot(self.data, self.depth, linewidth=linewidth, color=color,
                linestyle=linestyle, label=label, zorder=zorder)
        ax.set(xlabel="{}({})".format(self.descr, self.units),
               ylabel="Depth(m)",
               title=self.name)
        return ax
