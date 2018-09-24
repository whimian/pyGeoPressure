# -*- coding: utf-8 -*-
"""
a Well class utilizing pandas DataFrame and hdf5 storage

Created on Tue Dec 27 2016
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import str

__author__ = "yuhao"

import json
from collections import OrderedDict

import numpy as np
import pandas as pd

from ..pressure.hydrostatic import hydrostatic_pressure
from ..pressure.eaton import eaton
from pygeopressure.pressure.bowers import bowers_varu
from pygeopressure.pressure.multivariate import pressure_multivariate
from ..velocity.extrapolate import normal
from .well_log import Log
from .well_storage import WellStorage


class Well(object):
    """
    A class representing a well with information and log curve data.
    """
    def __init__(self, json_file, hdf_path=None):
        """
        Parameters
        ----------
        json_file : str
            path to parameter file
        hdf_path : str, optional
            path to hdf5 file used to override the one written in json_file
        """
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
        if hdf_path:
            self.hdf_file = hdf_path
        self._read_hdf()

    def __str__(self):
        return "Well-{}".format(self.well_name)

    def _parse_json(self):
        try:
            with open(self.json_file) as fin:
                self.params = json.load(fin, object_pairs_hook=OrderedDict)
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
    def depth(self):
        """
        depth values of the well

        Returns
        -------
        numpy.ndarray
        """
        if self.data_frame is not None:
            return np.around(self.data_frame['Depth(m)'].values, decimals=1)
        else:
            raise Exception("No dataframe found.")

    @property
    def logs(self):
        """
        logs stored in this well

        Returns
        -------
        list
        """
        if self.data_frame is not None:
            temp = [item.strip(')').split('(')[0] \
                for item in self.data_frame.keys()]
            temp.remove('Depth')
            return temp
        else:
            return []

    @property
    def unit_dict(self):
        """
        properties and their units
        """
        temp_dict = {
            item.strip(')').split('(')[0]: item.strip(')').split('(')[-1] \
            for item in self.data_frame.keys()}
        return {key: '' if temp_dict[key] == key else temp_dict[key] \
            for key in temp_dict.keys()}

    @property
    def hydrostatic(self):
        """
        Hydrostatic Pressure

        Returns
        -------
        numpy.ndarray
        """
        try:
            # temp_log = self.get_log('Overburden_Pressure')
            return hydrostatic_pressure(
                self.depth,
                kelly_bushing=self.kelly_bushing,
                depth_w=self.water_depth)
        except Exception as ex:
            print(ex.message)
            # print("No 'Overburden_Pressure' log found.")

    def hydro_log(self):
        """
        Returns
        -------
        Log
            Hydrostatic Pressure
        """
        hydro_log = Log()
        hydro_log.depth = np.array(self.depth)
        hydro_log.data = self.hydrostatic
        hydro_log.name = '{}_hydro'.format(self.well_name)
        hydro_log.descr = "Hydrostatic_Pressure"
        hydro_log.units = "MPa"

        return hydro_log

    @property
    def lithostatic(self):
        """
        Overburden Pressure (Lithostatic)

        Returns
        -------
        numpy.ndarray
        """
        try:
            temp_log = self.get_log('Overburden_Pressure')
            return np.array(temp_log.data)
        except KeyError:
            print("No 'Overburden_Pressure' log found.")

    @property
    def normal_velocity(self):
        """
        Normal Velocity calculated using NCT stored in well

        Returns
        -------
        numpy.ndarray
        """
        try:
            a = self.params['nct']['a']
            b = self.params['nct']['b']
            # temp_log = self.get_log('Overburden_Pressure')
            return normal(x=self.depth, a=a, b=b)
        except KeyError:
            print("No 'Overburden_Pressure' log found.")

    def get_log(self, logs, ref=None):
        """
        Retreive one or several logs in well

        Parameters
        ----------
        logs : str or list str
            names of logs to be retrieved
        ref : {'sea', 'kb'}
            depth reference, 'sea' references to sea level, 'kb' references
            to Kelly Bushing

        Returns
        -------
        Log
            one or a list of Log objects
        """
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

    def add_log(self, log, name=None, unit=None):
        """
        Add new Log to current well

        Parameters
        ----------
        log : Log
            log to be added
        name : str, optional
            name for the newly added log, None, use log.name
        unit : str, optional
            unit for the newly added log, None, use log.unit
        """
        log_name = log.descr.replace(' ', '_')
        log_unit = log.units
        if name is not None:
            log_name = name
        if unit is not None:
            log_unit = unit
        if log_name not in self.logs:
            temp_dataframe = pd.DataFrame(
                data={
                    'Depth(m)':log.depth,
                    '{}({})'.format(
                        log_name, log_unit): log.data})
            self.data_frame = self.data_frame.join(
                temp_dataframe.set_index("Depth(m)"), on="Depth(m)")
        else:
            raise Warning("{} already exists in well {}".format(
                log_name, self.well_name))

    def drop_log(self, log_name):
        """
        delete a Log in current Well

        Parameters
        ----------
        log_name : str
            name of the log to be deleted
        """
        if log_name in self.logs:
            log = self.get_log(log_name)
            col = "{}({})".format(log.descr.replace(' ', '_'), log.units)
            self.data_frame = self.data_frame.drop(col, 1)
        else:
            print("no log named {}".format(log_name))

    def rename_log(self, log_name, new_log_name):
        """
        Parameters
        ----------
        log_name : str
            log name to be replaced
        new_log_name : str
        """
        if log_name in self.logs:
            log = self.get_log(log_name)
            old_str = "{}({})".format(log.descr.replace(' ', '_'), log.units)
            new_str = "{}({})".format(new_log_name.replace(' ', '_'), log.units)
            self.data_frame = self.data_frame.rename(index=str,
                                                     columns={old_str: new_str})

    def update_log(self, log_name, log):
        """
        Update well log already in current well with a new Log

        Parameters
        ----------
        log_name : str
            name of the log to be replaced in current well
        log : Log
            Log to replace
        """
        old_log = self.get_log(log_name)
        if old_log.depth == log.depth:
            self.data_frame["{}({})".format(
                old_log.descr.replace(' ', '_'), old_log.units)] = log.data
        else:
            raise Warning("Mismatch")

    def export(self, file_path, logs_to_export=None, full_las=False,
               null_value=1e30):
        """
        Export logs to LAS or pseudo-LAS file

        Parameters
        ----------
        file_path : str
            output file path
        logs_to_export : list of str
            Log names to be exported, None export all logs
        full_las : bool
            True, export LAS header; False export only data hence psuedo-LAS
        null_value : scalar
            Null Value representation in output file.
        """
        if logs_to_export is None:
            logs_to_export = self.logs
        keys_to_export = ["Depth(m)"]
        for log_name in logs_to_export:
            log = self.get_log(log_name)
            keys_to_export.append(
                "{}({})".format(log.descr.replace(' ', '_'), log.units))
        self.data_frame.to_csv(
            file_path, sep='\t', na_rep="{}".format(null_value),
            columns=keys_to_export, index=False)

    def save_well(self):
        """
        Save current well logs to file
        """
        try:
            storage = WellStorage(self.hdf_file)
            storage.update_well(self.well_name, self.data_frame)
        except Exception as inst:
            print(inst)
    # Presure -----------------------------------------------------------------
    def _get_pressure(self, pres_key, ref=None, hydrodynamic=0):
        pres_to_get = None
        try:
            pres_to_get = self.params[pres_key]
        except KeyError:
            print("{}: Cannot find {}".format(self.well_name, pres_key))
            return Log()
        hydro = hydrostatic_pressure(self.depth,
                                     kelly_bushing=self.kelly_bushing,
                                     depth_w=self.water_depth)
        depth = pres_to_get["depth"]
        coef = pres_to_get["coef"]
        pres = pres_to_get["data"]
        if not coef:
            coef = pres
            hydro = np.ones(hydro.shape)
        obp_depth = self.depth # obp_log.depth
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
        Get Measured Pressure

        Parameters
        ----------
        ref : {'sea', 'kb'}
            depth reference, 'sea' references to sea level, 'kb' references
            to Kelly Bushing

        Returns
        -------
        Log
            Log object containing Measured Pressure
        """
        return self._get_pressure("Measured_Pressure", ref=ref)

    def get_pressure_coefficient(self):
        """
        Retrieve Pressure Coefficient

        Returns
        -------
        Log
            Log object containing Measured Pressure Coefficients
        """
        depth = self.params["Measured_Pressure"]["depth"]
        coef = self.params["Measured_Pressure"]["coef"]
        pres = self.params["Measured_Pressure"]["data"]
        if depth and not coef and pres:
            hydro = hydrostatic_pressure(self.depth,
                                         kelly_bushing=self.kelly_bushing,
                                         depth_w=self.water_depth)
            coef_data = list()
            for dp, pr in zip(depth, pres):
                idx = np.searchsorted(self.depth, dp)
                coef_data.append(pr / hydro[idx])
            log = Log()
            log.depth = depth
            log.data = coef_data
            return log
        else:
            log = Log()
            log.depth = depth
            log.data = coef
        return log

    def get_pressure_normal(self):
        """
        return pressure points within normally pressured zone.

        Returns
        -------
        Log
            Log object containing normally pressured measurements
        """
        # obp_log = self.get_log("Overburden_Pressure")
        hydro = hydrostatic_pressure(self.depth,
                                     kelly_bushing=self.kelly_bushing,
                                     depth_w=self.water_depth)
        depth = self.params["MP"]
        obp_depth = self.depth
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

        Parameters
        ----------
        ref : {'sea', 'kb'}
            depth reference, 'sea' references to sea level, 'kb' references
            to Kelly Bushing

        Returns
        -------
        Log
            Log object containing Equivalent Mud Weight
        """
        return self._get_pressure("EMW", ref=ref)

    def get_dst(self, ref=None):
        """
        Get Drill-Stem Test Pressure Measurements

        Parameters
        ----------
        ref : {'sea', 'kb'}
            depth reference, 'sea' references to sea level, 'kb' references
            to Kelly Bushing

        Returns
        -------
        Log
            Log object containing Drill-Stem Test Pressure
        """
        return self._get_pressure("DST", ref=ref)

    def get_wft(self, hydrodynamic=0, ref=None):
        """
        Get Wireline Formation Test Pressure Measurements
        (Both MDT and/or RFT)

        Parameters
        ----------
        hydrodynamic : scalar
            start depth of hydrodynamic interval
        ref : {'sea', 'kb'}
            depth reference, 'sea' references to sea level, 'kb' references
            to Kelly Bushing

        Returns
        -------
        Log
            Log object containing Wireline Formation Test Pressure
        """
        return self._get_pressure("MDT", hydrodynamic=hydrodynamic, ref=ref)

    def get_loading_pressure(self, ref=None):
        """
        Get Pressure Measurements on loading curve

        Parameters
        ----------
        ref : {'sea', 'kb'}
            depth reference, 'sea' references to sea level, 'kb' references
            to Kelly Bushing

        Returns
        -------
        Log
            Log object containing Pressure on Loading Curve
        """
        return self._get_pressure("loading", ref=ref)

    def get_unloading_pressure(self, ref=None):
        """
        Get Pressure Measurements on unloading curve

        Parameters
        ----------
        ref : {'sea', 'kb'}
            depth reference, 'sea' references to sea level, 'kb' references
            to Kelly Bushing

        Returns
        -------
        Log
            Log object containing Pressure on Unloading Curve
        """
        return self._get_pressure("unloading", ref=ref)

    def eaton(self, vel_log, obp_log=None, n=None, a=None, b=None):
        """
        Predict pore pressure using Eaton method

        Parameters
        ----------
        vel_log : Log
            velocity log
        obp_log : Log
            overburden pressure log
        n : scalar
            Eaton exponent

        Returns
        -------
        Log
            a Log object containing calculated pressure.
        """
        if isinstance(vel_log, str):
            vel_log.get_log(vel_log)
        velocity = np.array(vel_log.data)

        if obp_log is None:
            obp = self.lithostatic
        else:
            if isinstance(obp_log, str):
                obp_log.get_log(obp_log)
            obp = np.array(obp_log.data)

        try:
            n = self.params['n'] if n is None else n
        except KeyError:
            n = 3

        if a is None or b is None:
            a = self.params['nct']['a']
            b = self.params['nct']['b']

        # log = Log()
        # log.depth = self.depth

        pres_eaton = eaton(hydrostatic=self.hydrostatic,
                         lithostatic=obp,
                         n=n, v=velocity, vn=self.normal_velocity)
        # log.name = "pressure_eaton_{}".format(
        #     self.well_name.lower().replace('-', '_'))
        # log.descr = "Pressure_Eaton"
        # log.units = "MPa"
        # log.prop_type = "PRE"

        log = Log.from_scratch(
            self.depth, pres_eaton,
            "pressure_eaton_{}".format(self.well_name.lower().replace('-', '_')),
            descr = "Pressure_Eaton",
            units = "MPa",
            prop_type = "PRE")

        return log

    def bowers(self, vel_log, obp_log=None, a=None, b=None, u=1, vmax=4600,
               start_depth=None, buf=20, end_depth=None, end_buffer=10):
        """
        Predict pore pressure using Eaton method

        Parameters
        ----------
        vel_log : Log
            velocity log
        obp_log : Log
            overburden pressure log
        a, b, u : float
            bowers model coefficients

        Returns
        -------
        Log
            a Log object containing calculated pressure.
        """
        if isinstance(vel_log, str):
            vel_log.get_log(vel_log)
        velocity = np.array(vel_log.data)

        if obp_log is None:
            obp = self.lithostatic
        else:
            if isinstance(obp_log, str):
                obp_log.get_log(obp_log)
            obp = np.array(obp_log.data)

        try:
            a = self.params['bowers']['A'] if a is None else a
            b = self.params['bowers']['B'] if b is None else b
            if not start_depth:
                start_depth = self.params['bowers']["start_depth"]
            if not end_depth:
                end_depth = self.params['bowers']["end_depth"]
            vmax = self.params['bowers']["vmax"] if vmax is None else vmax
            u = self.params['bowers']["U"] if u is None else u
        except KeyError as e:
            raise KeyError("Missing parameter: {}".format(e.args[0]))

        log = Log()
        log.depth = self.depth

        log.data = bowers_varu(
            velocity, obp, u, start_idx=vel_log.get_depth_idx(start_depth),
            a=a, b=b, vmax=vmax, buf=buf,
            end_idx=vel_log.get_depth_idx(end_depth), end_buffer=end_buffer)

        log.name = "pressure_bowers_{}".format(
            self.well_name.lower().replace('-', '_'))
        log.descr = "Pressure_Bowers"
        log.units = "MPa"
        log.prop_type = "PRE"
        return log

    def multivariate(self, vel_log, por_log, vsh_log, obp_log=None,
                     a0=None, a1=None, a2=None, a3=None, b=None):
        if isinstance(vel_log, str):
            vel_log.get_log(vel_log)
        vel = np.array(vel_log.data)
        if isinstance(por_log, str):
            por_log.get_log(por_log)
        phi = np.array(por_log.data)
        if isinstance(vsh_log, str):
            vsh_log.get_log(vsh_log)
        vsh = np.array(vsh_log.data)
        if isinstance(vsh_log, str):
            vsh_log.get_log(vsh_log)
        vsh = np.array(vsh_log.data)

        if obp_log is None:
            obp = self.lithostatic
        else:
            if isinstance(obp_log, str):
                obp_log.get_log(obp_log)
            obp = np.array(obp_log.data)

        try:
            a0 = self.params['multivariate']['a0'] if a0 is None else a0
            a1 = self.params['multivariate']['a1'] if a1 is None else a1
            a2 = self.params['multivariate']['a2'] if a2 is None else a2
            a3 = self.params['multivariate']['a3'] if a3 is None else a3
            b = self.params['multivariate']['B'] if b is None else b
        except KeyError as e:
            raise KeyError("Missing parameter: {}".format(e.args[0]))

        log = Log()
        log.depth = self.depth

        log.data = pressure_multivariate(
            obp, vel, phi, vsh, a0, a1, a2, a3,
            b, 1, 4600, start_idx=3000, end_idx=None)

        log.name = "pressure_mutlivariate_{}".format(
            self.well_name.lower().replace('-', '_'))
        log.descr = "Pressure_Multivariate"
        log.units = "MPa"
        log.prop_type = "PRE"
        return log

    def plot_horizons(self, ax, color_dict=None):
        horizon_dict = None
        try:
            color_dict = self.params['color_dict']
        except:
            pass
        try:
            horizon_dict = self.params['horizon']
        except KeyError:
            print("no horizons")
        for key in horizon_dict.keys():
            try:
                color = color_dict[key]
            except KeyError:
                color = 'black'
            except TypeError:
                color = 'black'
            ax.axhline(y=horizon_dict[key],
                       color=color, linewidth=0.5, zorder=0)

            import matplotlib.transforms as transforms
            trans = transforms.blended_transform_factory(
                ax.transAxes, ax.transData)
            ax.text(
                s=key, x=0.8, y=horizon_dict[key],
                color=color, transform=trans, size=9)
        ax.figure.canvas.draw()

    def save_params(self):
        """
        Save edited parameters to file
        """
        try:
            with open(self.json_file, "w") as fl:
                json.dump(self.params, fl, indent=4)
        except KeyError as inst:
            print(inst)
