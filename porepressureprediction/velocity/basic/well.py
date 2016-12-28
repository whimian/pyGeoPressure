# -*- coding: utf-8 -*-
"""
a Well class utilizing pandas DataFrame

Created on Tue Dec 27 2016
"""
from __future__ import division, print_function
import json
import numpy as np
import pandas as pd
# from las import LASReader
from laSQL import Log

class Well(object):
    def __init__(self, json_file):
        self.json_file = json_file
        self.hdf_file = None
        self.well_name = None
        self.loc = None
        self.kelly_bushing = None
        self.water_depth = None
        self.total_depth = None
        # self.trajectory = None
        self.data_frame = None
        self.params = None
        # self.unit_dict = None
        self._parse_json()
        self._read_hdf()

    def _parse_json(self):
        try:
            with open(self.json_file) as fin:
                self.params = json.load(fin)
                self.hdf_file = self.params['hdf_file']
                self.well_name = self.params['well_name']
                self.loc = self.params['loc']
                self.kelly_bushing = self.params['KB']
                self.water_depth = self.params['WD']
                self.total_depth = self.params['TD']
        except Exception as inst:
            print(inst)

    def _read_hdf(self):
        try:
            with pd.HDFStore(self.hdf_file) as store:
                self.data_frame = store[
                    self.well_name.lower().replace('-', '_')]
        except Exception as inst:
            print(inst)

    @property
    def logs(self):
        if self.data_frame is not None:
            temp = [item.strip(')').split('(')[0] \
                for item in self.data_frame.keys()]
            temp.remove('Depth')
            return temp
        else:
            return []

    @property
    def unit_dict(self):
        temp_dict = {
            item.strip(')').split('(')[0]: item.strip(')').split('(')[-1] \
            for item in self.data_frame.keys()}
        return {key: '' if temp_dict[key] == key else temp_dict[key] \
            for key in temp_dict.keys()}

    def get_log(self, logs):
        log_list = list()
        output_list = list()
        if isinstance(logs, str):
            log_list.append(logs)
        elif isinstance(logs, list):
            log_list = logs
        for name in log_list:
            new_log = Log()
            new_log.name = name.lower()[:3] + '_' + \
                self.well_name.lower().replace('-', '_')
            new_log.units = self.unit_dict[name]
            new_log.descr = name
            new_log.depth = self.data_frame['Depth(m)'].values
            new_log.data = self.data_frame[
                '{}({})'.format(name, self.unit_dict[name])].values
            output_list.append(new_log)
        if isinstance(logs, str):
            return output_list[0]
        else:
            return output_list
