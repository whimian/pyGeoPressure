# -*- coding: utf-8 -*-
"""
an interface for interacting with Las file

Created on Thu May 10 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

from builtins import open
from future.utils import native
import numpy as np
import pandas as pd

from pygeopressure.pressure.hydrostatic import hydrostatic_pressure
from pygeopressure.pressure.eaton import eaton
from pygeopressure.velocity.extrapolate import normal
from pygeopressure.basic.well_log import Log
from pygeopressure.basic.las_reader import LASReader

from . import Path


class LasData(object):
    """
    Class for reading LAS and pseudo-LAS file data

    null_values could be set to more values in order to deal with messy files
    """
    def __init__(self, las_file):
        self.las_file = las_file
        self.null_values = [-999.25, 1.0e30]
        self._file_type = None
        self._data_frame = None
        self._logs = None
        self._units = None
        self.depth_unit = "m"

    @property
    def file_type(self):
        if self._file_type is None:
            with open(self.las_file, "r") as fl:
                first_line = fl.readline()
                if first_line[0] == '~':
                    self._file_type = "las"
                else:
                    self._file_type = "pseudo-las"
                return self._file_type
        else:
            return self._file_type

    @property
    def data_frame(self):
        if self._data_frame is None:
            if self.file_type is "las":
                self.read_las()
            else:
                self.read_pseudo_las()
        return self._data_frame

    def read_pseudo_las(self):
        df = pd.read_csv(self.las_file, sep='\t')
        for value in self.null_values:
            df = df.replace(value, np.nan)  # replace 1e30 with np.nan
        df = df.round({df.columns[0]: 1})  # round depth to 1 decimal
        if 'Depth(M)' in df.columns.values.tolist():
            df.rename(columns={'Depth(M)': 'Depth(m)'}, inplace=True)
        self._data_frame = df
        # data.to_hdf(self.hdf5_file, well_name)

    def read_las(self):
        if Path(native(self.las_file)).exists():
            las = LASReader(native(str(Path(self.las_file))), null_subs=np.nan)
            # well_name = las.well.items['WELL'].data
            df = pd.DataFrame(
                las.data2d,
                columns=["{}({})".format(
                    las.curves.items[name].descr.replace(' ', '_'),
                    las.curves.items[name].units) \
                    for name in las.curves.names])
            if 'Depth(M)' in df.columns.values.tolist():
                df.rename(columns={'Depth(M)': 'Depth(m)'}, inplace=True)
            self._data_frame = df

    def find_logs(self):
        self._logs = []
        self._units = []
        for name in self.data_frame.columns.values:
            str_list = name.split("(")
            if str_list[0] != "Depth":
                self._logs.append(str_list[0])
                self._units.append(str_list[1][:-1])
            else:
                self.depth_unit = str_list[1][:-1]

    @property
    def logs(self):
        if self._logs is None:
            self.find_logs()
        return self._logs

    @property
    def units(self):
        if self._units is None:
            self.find_logs()
        return self._units
