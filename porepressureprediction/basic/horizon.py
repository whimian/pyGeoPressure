# -*- coding: utf-8 -*-
"""
class Horizon for accessing horizon

Created on Fri July 20 2017
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import json

import numpy as np
import pandas as pd

# # from scipy.interpolate import interp1d
# # from scipy.signal import butter, filtfilt

# from porepressureprediction.velocity.smoothing import smooth


class Horizon(object):
    """
    class for horizon
    """
    def __init__(self, data_file):
        # self.json_file = json_file
        self.hdf_file = None
        self.horizon_name = None
        self.data_frame = pd.read_excel(data_file)
        # self.params = None
        # self._parse_json()
        # self._read_hdf()

    def __str__(self):
        return "Horizon Object: {}".format(self.horizon_name)

    def __repr__(self):
        return "Horizon Object: {}".format(self.horizon_name)

    # def _parse_json(self):
    #     try:
    #         with open(self.json_file) as fin:
    #             self.params = json.load(fin)
    #             self.hdf_file = self.params['hdf_file']
    #             self.horizon_name = self.params['horizon_name']
    #     except Exception as inst:
    #         print(inst)

    # def _read_hdf(self):
    #     try:
    #         with pd.HDFStore(self.hdf_file) as store:
    #             self.data_frame = store[
    #                 self.horizon_name]
    #     except Exception as inst:
    #         print(inst)

    def get_cdp(self, cdp):
        inl, crl = cdp
        return self.data_frame[
            (self.data_frame.inline==inl) & \
            (self.data_frame.crline==4050)].z.values[-1]
