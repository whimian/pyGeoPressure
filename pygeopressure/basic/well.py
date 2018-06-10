# -*- coding: utf-8 -*-
"""
a Well class utilizing pandas DataFrame and hdf5 storage

Created on Tue Dec 27 2016
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
from .well_storage import WellStorage


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
        self.in_hdf = False
        self._parse_json()
        self._read_hdf()

    def __str__(self):
        return "Well Object: {}".format(self.well_name)

    def __repr__(self):
        return "Well Object: {}".format(self.well_name)

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
        except KeyError as inst:
            print(inst)

    def _read_hdf(self):
        try:
            storage = WellStorage(self.hdf_file)
            self.data_frame = storage.get_well_data(
                self.well_name.lower().replace('-', '_'))
            self.in_hdf = True
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

    @property
    def hydrostatic(self):
        try:
            temp_log = self.get_log('Overburden_Pressure')
            return hydrostatic_pressure(
                np.array(temp_log.depth),
                kelly_bushing=self.kelly_bushing,
                depth_w=self.water_depth)
        except KeyError:
            print("No 'Overburden_Pressure' log found.")

    @property
    def lithostatic(self):
        try:
            temp_log = self.get_log('Overburden_Pressure')
            return np.array(temp_log.data)
        except KeyError:
            print("No 'Overburden_Pressure' log found.")

    @property
    def normal_velocity(self):
        try:
            a = self.params['nct']['a']
            b = self.params['nct']['b']
            temp_log = self.get_log('Overburden_Pressure')
            return normal(x=np.array(temp_log.depth), a=a, b=b)
        except KeyError:
            print("No 'Overburden_Pressure' log found.")

    def get_log(self, logs, ref=None):
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
            new_log.depth = np.array(self.data_frame['Depth(m)'].values)
            new_log.data = np.array(self.data_frame[
                '{}({})'.format(name, self.unit_dict[name])].values)
            if ref == 'sea':
                shift = int(self.kelly_bushing // 0.1)
                shift_data = np.full_like(new_log.data, np.nan, dtype=np.double)
                shift_data[:-shift] = new_log.data[shift:]
                new_log.data = shift_data
            output_list.append(new_log)
        if isinstance(logs, str):
            return output_list[0]
        else:
            return output_list

    def add_log(self, log):
        temp_dataframe = pd.DataFrame(
            data={
                'Depth(m)':log.depth,
                '{}({})'.format(
                    log.descr.replace(' ', '_'), log.units): log.data})
        # self.data_frame = pd.merge(self.data_frame, temp_dataframe,
        #                            how='outer')
        self.data_frame = self.data_frame.join(
            temp_dataframe.set_index("Depth(m)"), on="Depth(m)")

    def drop_log(self, log_name):
        if log_name in self.logs:
            log = self.get_log(log_name)
            col = "{}({})".format(log.descr.replace(' ', '_'), log.units)
            self.data_frame = self.data_frame.drop(col, 1)
        else:
            print("no log named {}".format(log_name))

    def rename_log(self, log_name, new_log_name):
        if log_name in self.logs:
            log = self.get_log(log_name)
            old_str = "{}({})".format(log.descr.replace(' ', '_'), log.units)
            new_str = "{}({})".format(new_log_name.replace(' ', '_'), log.units)
            self.data_frame = self.data_frame.rename(index=str,
                                                     columns={old_str: new_str})

    def save_well(self):
        try:
            storage = WellStorage(self.hdf_file)
            storage.update_well(self.well_name, self.data_frame)
        except Exception as inst:
            print(inst)

    def _get_pressure(self, pres_key, ref=None, hydrodynamic=0):
        obp_log = self.get_log("Overburden_Pressure")
        hydro = hydrostatic_pressure(np.array(obp_log.depth),
                                     kelly_bushing=self.kelly_bushing,
                                     depth_w=self.water_depth)
        depth = self.params[pres_key]["depth"]
        coef = None
        try:
            coef = self.params[pres_key]["coef"]
        except KeyError:
            print("{}: Cannot find {}".format(self.well_name, pres_key))
            return Log()
        obp_depth = obp_log.depth
        pres_data = list()
        pres_depth = list()
        for dp, co in zip(depth, coef):
            if dp > hydrodynamic:
                idx = np.searchsorted(obp_depth, dp)
                pres_data.append(hydro[idx] * co)
                pres_depth.append(dp)
        log = Log()
        if ref == 'sea':
            log.depth = np.array(pres_depth) - self.kelly_bushing
        else:
            log.depth = pres_depth
        log.data = np.round(np.array(pres_data), 3)
        return log

    def get_pressure_measured(self, ref=None):
        """
        Get Measured Pressure Points
        """
        return self._get_pressure("Measured_Pressure", ref=ref)

    def get_pressure_coefficient(self):
        """
        Retrieve Pressure Coefficient
        """
        depth = self.params["Measured_Pressure"]["depth"]
        coef = self.params["Measured_Pressure"]["coef"]
        log = Log()
        log.depth = depth
        log.data = coef
        return log

    def get_pressure_normal(self):
        """
        return pressure points within normally pressured zone.
        """
        obp_log = self.get_log("Overburden_Pressure")
        hydro = hydrostatic_pressure(np.array(obp_log.depth),
                                     kelly_bushing=self.kelly_bushing,
                                     depth_w=self.water_depth)
        depth = self.params["MP"]
        obp_depth = obp_log.depth
        pres_data = list()
        for dp in depth:
            idx = np.searchsorted(obp_depth, dp)
            pres_data.append(hydro[idx])

        log = Log()
        log.depth = depth
        log.data = pres_data
        return log

    def get_emw(self, ref=None):
        """
        Get Equivalent Mud Weight
        """
        return self._get_pressure("EMW", ref=ref)

    def get_dst(self, ref=None):
        """
        Get Drillstem Test Pressure Measurements
        """
        return self._get_pressure("DST", ref=ref)

    def get_wft(self, hydrodynamic=0, ref=None):
        """
        Get Wireline Formation Test Pressure Measurements
        (Both MDT and/or RFT)

        Paramters
        ---------
        hydrodynamic : scalar
            start depth of hydrodynamic interval
        """
        return self._get_pressure("MDT", hydrodynamic=hydrodynamic, ref=ref)

    def get_loading_pressure(self, ref=None):
        """
        Get Pressure Measurements on loading curve
        """
        return self._get_pressure("loading", ref=ref)

    def get_unloading_pressure(self, ref=None):
        """
        Get Pressure Measurements on unloading curve
        """
        return self._get_pressure("unloading", ref=ref)

    def eaton(self, velocity, n=3):
        """
        Predict pore pressure using Eaton method

        Parameters
        ----------
        velocity : 1-d ndarray
            velocity data for calculation
        n : scalar
            Eaton exponent

        Returns
        -------
        Log
            a Log object containing calculated pressure.
        """
        temp_log = self.get_log("Overburden_Pressure")
        log = Log()
        log.depth = temp_log.depth
        log.data = eaton(hydrostatic=self.hydrostatic,
                         lithostatic=self.lithostatic,
                         n=n, v=velocity, vn=self.normal_velocity)
        log.name = "pressure_eaton_{}".format(
            self.well_name.lower().replace('-', '_'))
        log.descr = "Pressure_Eaton"
        log.units = temp_log.units
        log.prop_type = "PRE"
        return log

    def save_params(self):
        try:
            with open(self.json_file, "w") as fl:
                json.dump(self.params, fl, indent=4)
        except KeyError as inst:
            print(inst)
