# -*- coding: utf-8 -*-
"""
class Horizon for accessing horizon

Created on Fri July 20 2017
"""
from __future__ import division, print_function, absolute_import

__author__ = "yuhao"

import pandas as pd


class Horizon(object):
    """
    Horizon using excel file as input

    Parameters
    ----------
    data_file : str
        path to excel data file
    """
    def __init__(self, data_file):
        self.hdf_file = None
        self.horizon_name = None
        # self.data_frame = pd.read_excel(data_file)
        self.data_frame = pd.read_csv(data_file, sep='\t')

    def __str__(self):
        return "Horizon Object: {}".format(self.horizon_name)

    def __repr__(self):
        return "Horizon Object: {}".format(self.horizon_name)

    def get_cdp(self, cdp):
        """
        Get value for a CDP point on the horizon.

        Parameters
        ----------
        cdp : tuple of int (inline, crossline)
        """
        inl, crl = cdp
        return self.data_frame[
            (self.data_frame.inline == inl) & \
            (self.data_frame.crline == crl)].z.values[-1]
