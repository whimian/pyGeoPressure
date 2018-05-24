# -*- coding: utf-8 -*-
"""
an interface to a hdf5 storage

Created on Thu May 10 2018
"""
from __future__ import absolute_import, division, print_function

__author__ = "yuhao"

import json

import numpy as np
import pandas as pd

from ..pressure.hydrostatic import hydrostatic_pressure
from ..pressure.pore_pressure import eaton
from ..velocity.extrapolate import normal
from .well_log import Log
from pygeopressure.basic.las_reader import LASReader
from . import Path


class Well_Storage(object):
    """
    interface to hdf5 file storing well logs

    this class is designed to accept only LasData.data_frame as input data
    """
    def __init__(self, hdf5_file=None):
        self.hdf5_file = hdf5_file

    @property
    def wells(self):
        well_names = None
        with pd.HDFStore(self.hdf5_file) as store:
            well_names = [key[1:] for key in store.keys()]
        return well_names

    # def read_pseudo_las(self, las_file, well_name):
    #     data = pd.read_csv(las_file, sep='\t')
    #     data = data.replace(1.0e30, np.nan)  # replace 1e30 with np.nan
    #     data = data.round({'Depth(m)': 1})  # round depth to 1 decimal
    #     data.to_hdf(self.hdf5_file, well_name)

    # def read_las(self, las_file):
    #     if Path(las_file).exists():
    #         las = LASReader(str(Path(las_file)), null_subs=np.nan)
    #         well_name = las.well.items['WELL'].data
    #         import pandas as pd
    #         df = pd.DataFrame(las.data2d, columns=[c for c in las.curves.names])
    #         if len(las.curves.names) > 0:
    #             df = df.set_index(las.curves.names[0])
    #         return df

    def get_well_data(self, well_name):
        try:
            with pd.HDFStore(self.hdf5_file) as store:
                return store[well_name]
        except KeyError:
            print("No well named {}".format(well_name))

    def remove_well(self, well_name):
        try:
            with pd.HDFStore(self.hdf5_file) as store:
                return store.remove(well_name)
        except KeyError:
            print("No well named {}".format(well_name))

    def add_well(self, well_name, well_data_frame):
        well_data_frame.to_hdf(self.hdf5_file, well_name)
