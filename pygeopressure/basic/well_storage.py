# -*- coding: utf-8 -*-
"""
an interface to a hdf5 storage file

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


class WellStorage(object):
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
        well_name = well_name.lower().replace('-', '_')
        well_data_frame.to_hdf(self.hdf5_file, well_name)

    def update_well(self, well_name, well_data_frame):
        with pd.HDFStore(self.hdf5_file) as store:
            store[well_name.lower().replace('-', '_')] = well_data_frame

    def logs_into_well(self, well_name, logs_data_frame):
        well_name = well_name.lower().replace('-', '_')
        well_df = self.get_well_data(well_name)
        new_df = well_df.join(
            logs_data_frame.set_index("Depth(m)"), on="Depth(m)")
        self.remove_well(well_name)
        self.add_well(well_name, new_df)
