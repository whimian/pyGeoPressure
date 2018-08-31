# -*- coding: utf-8 -*-
"""
Class for defining a seismic survey

Created on Fri Dec 11 20:24:38 2015
"""
from __future__ import absolute_import, division, print_function

from builtins import str

__author__ = "yuhao"

import json
from itertools import product
from . import Path

import numpy as np

# from .seiSQL import SeisCube
from .seiSEGY import SeiSEGY
from .well import Well
from .survey_setting import SurveySetting
from .threepoints import ThreePoints


class Survey(SurveySetting):
    """
    Survey object for combining seismic data and well log data.

    Parameters
    ----------
    survey_dir : Path
        survey directory.

    Attributes
    ----------
    seis_json : str
        associated seismic data information file.
    well_json : str
        associated well data information file.
    wells : dict
        dictionary holding all Well objects.
    seisCube : SeisCube
        SeisCube object holding seismic data.
    inl_crl : dict
        well position in reference to seismic survey setting (inl/crl)

    Methods
    -------
    add_well(well)
        add a well to survey
    get_seis(well_name, attr, radius=0)
        get seismic data in the vicinity of a given well
    """
    def __init__(self, survey_dir):
        self.survey_dir = survey_dir
        self.setting_json = None
        self._check_dir()
        super(Survey, self).__init__(ThreePoints(self.setting_json))
        self.wells = dict()
        self.seismics = dict()
        self.seisCube = None
        self.inl_crl = dict()
        self._add_seis_wells()
        # self._add_seismic()  # you have to call it explicitly

    def _check_dir(self):
        survey_file = Path(self.survey_dir, '.survey')
        if survey_file.exists():
            self.setting_json = str(survey_file)
        else:
            raise Exception("No survey setting file in folder!")

    def add_seismic(self):
        seis_dir = self.survey_dir / "Seismics"
        for seis_name in get_data_files(seis_dir):
            with open(str(self.survey_dir.absolute() / \
                    "Seismics" / ".{}".format(seis_name)), 'r') as fl:
                temp_json = json.load(fl)
            temp = SeiSEGY(temp_json['path'])
            self.seismics[seis_name] = temp

    def _add_seis_wells(self):
        # self.seisCube = SeisCube(self.seis_json)
        well_dir = self.survey_dir / "Wellinfo"
        for well_name in get_data_files(well_dir):
            temp = Well(str(self.survey_dir.absolute() / \
                "Wellinfo" / ".{}".format(well_name)))
            self.wells[temp.well_name] = temp
        # for jsf in self.well_json:
        #     temp = Well(jsf)
        #     self.wells[temp.well_name] = temp
        for well in self.wells.values():
            loc = self._tie(well)
            self.inl_crl[well.well_name] = loc

    def _tie(self, well):
        return self.coord_2_line(well.loc)

    def add_well(self, well):
        loc = self._tie(well)
        self.wells[well.well_name] = well
        self.inl_crl[well.well_name] = loc

    def get_seis(self, well_name, attr, radius=0):
        """
        Get seismic trace data nearest to the well location.
        """
        radius = int(radius)
        if well_name in self.inl_crl.keys():
            loc = self.inl_crl[well_name]
            if radius == 0:
                data = self.seisCube.get_cdp(loc, attr)
                return [loc], [data]
            else:
                inlines, crlines = self._get_traces(radius, loc)
                loc = list()
                data = list()
                for inl, crl in product(inlines, crlines):
                    loc.append((inl, crl))
                    data.append(self.seisCube.get_cdp((inl, crl), attr))
                return loc, data
        else:
            print("Well not found!")
            return []

    def _get_traces(self, radius, cdp):
        inline, crline = cdp
        start_inline = self.seisCube.startInline
        end_inline = self.seisCube.endInline
        step_inline = self.seisCube.stepInline
        start_crline = self.seisCube.startCrline
        end_crline = self.seisCube.endCrline
        step_crline = self.seisCube.stepCrline

        inl_min = inline - radius * step_inline
        if inl_min < start_inline:
            inl_min = start_inline
        inl_max = inline + radius * step_inline
        if inl_max > end_inline:
            inl_max = end_inline
        crl_min = crline - radius * step_crline
        if crl_min < start_crline:
            crl_min = start_crline
        crl_max = crline + radius * step_crline
        if crl_max > end_crline:
            crl_max = end_crline
        inlines = np.arange(inl_min, inl_max+1, step_inline)
        crlines = np.arange(crl_min, crl_max+1, step_crline)
        return (inlines, crlines)

    def sparse_mesh(self, depth, log_name):
        depth_range = range(
            self.seisCube.startDepth, (self.seisCube.endDepth + 1),
            self.seisCube.stepDepth)
        if depth > self.seisCube.endDepth:
            print("input depth larger than maximum depth")
            # depth = self.seisCube.endDepth
        elif depth < self.seisCube.startDepth:
            print("input depth smaller than minimum depth")
            # depth = self.seisCube.startDepth
        elif depth not in depth_range:
            print("return values on nearest depth")
        else:
            pass
        depth = min(depth_range, key=lambda x: abs(x-depth))
        mesh = np.array([np.nan] * self.seisCube.nNorth * self.seisCube.nEast)
        mesh.shape = (self.seisCube.nNorth, self.seisCube.nEast)
        for we in self.wells.values():
            log_depth = we.get_log("depth")
            log_data = we.get_log(log_name)
            log_index = range(len(log_depth))
            d = log_data[min(log_index, key=lambda x: abs(log_depth[x]-depth))]
            # print("d = ", d)
            w_inline = self.inl_crl[we.name][0]
            w_crline = self.inl_crl[we.name][1]
            a = (w_crline - self.seisCube.startCrline) // \
                self.seisCube.stepCrline
            b = (w_inline - self.seisCube.startInline) // \
                self.seisCube.stepInline
            mesh[a, b] = d
        return mesh

    def get_sparse_list(self, depth, log_name):
        depth_range = range(self.seisCube.startDepth,
                            (self.seisCube.endDepth + 1),
                            self.seisCube.stepDepth)
        if depth > self.seisCube.endDepth:
            print("input depth larger than maximum depth")
            # depth = self.seisCube.endDepth
        elif depth < self.seisCube.startDepth:
            print("input depth smaller than minimum depth")
            # depth = self.seisCube.startDepth
        elif depth not in depth_range:
            print("return values on nearest depth")
        else:
            pass
        depth = min(depth_range, key=lambda x: abs(x-depth))
        sparse_list = list()
        for we in self.wells.values():
            log_depth = we.get_log("depth")
            log_data = we.get_log(log_name)
            log_index = range(len(log_depth))
            d = log_data[min(log_index, key=lambda x: abs(log_depth[x]-depth))]
            # print("d = ", d)
            w_inline = self.inl_crl[we.name][0]
            w_crline = self.inl_crl[we.name][1]
            # a = (w_crline - self.seisCube.startCrline) // \
            #     self.seisCube.stepCrline
            # b = (w_inline - self.seisCube.startInline) // \
            #     self.seisCube.stepInline
            sparse_list.append([w_inline, w_crline, d])

        return sparse_list

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
def create_survey_directory(root_dir, survey_name):
    """
    Create survey folder structure

    Parameters
    ----------
    root_dir : Path
        Root directory for storing surveys
    survey_nam : str
    """
    survey_root = root_dir / survey_name
    try:
        survey_root.mkdir()
        dir_to_create = [root_dir / survey_name / 'Seismics',
                         root_dir / survey_name / 'Wellinfo',
                         root_dir / survey_name / 'Surfaces']
        for directory in dir_to_create:
            directory.mkdir()
        # new folder structure does not require folder dot file
        #     file_path = directory / ".{}".format(str(directory.name).lower())
        #     file_path.touch()
        return survey_root
    except OSError:
        raise DuplicateSurveyNameExeption()


class DuplicateSurveyNameExeption(Exception):
    def __init__(self):
        self.message = ""
        super(DuplicateSurveyNameExeption, self).__init__(self.message)


def get_data_files(dir_path):
    """
    get all dot file with given path

    dir_path: Path
    """
    fnames = list()
    # dir_path = Path(dir_path)
    if dir_path.exists():
        if list(dir_path.glob('.*')):
            for item in list(dir_path.glob('.*')):
                fnames.append(item.name[1:])
    return fnames
