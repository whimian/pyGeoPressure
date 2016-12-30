# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 20:24:38 2015

@author: yuhao
"""
from __future__ import division, print_function
from itertools import product
import json
import numpy as np
from seiSQL import SeisCube
from well import Well


class Survey(object):
    """
    Survey object for combining seismic data and well log data.
    """
    def __init__(self, json_file):
        self.json_file = json_file
        self.seis_json = None
        self.well_json = None
        self.wells = dict()
        self.seisCube = None
        self.inl_crl = dict()
        self._parse_json()
        self._add_seis_wells()

    def _parse_json(self):
        try:
            with open(self.json_file) as fin:
                params = json.load(fin)
                self.seis_json = params['seis']
                self.well_json = params['wells']
        except Exception as inst:
            print(inst)

    def _add_seis_wells(self):
        self.seisCube = SeisCube(self.seis_json)
        for jsf in self.well_json:
            temp = Well(jsf)
            self.wells[temp.well_name] = temp
        for well in self.wells.values():
            loc = self._tie(well)
            self.inl_crl[well.well_name] = loc

    def _tie(self, well):
        w_east = well.loc[0]
        w_north = well.loc[1]
        gamma_x = (self.seisCube.east_B - self.seisCube.east_A) / \
            (self.seisCube.crline_B - self.seisCube.crline_A)
        beta_x = (self.seisCube.east_C - self.seisCube.east_B) / \
            (self.seisCube.inline_C - self.seisCube.inline_B)
        alpha_x = self.seisCube.east_A - \
            beta_x * self.seisCube.inline_A - \
            gamma_x * self.seisCube.crline_A
        gamma_y = (self.seisCube.north_B - self.seisCube.north_A) / \
            (self.seisCube.crline_B - self.seisCube.crline_A)
        beta_y = (self.seisCube.north_C - self.seisCube.north_B) / \
            (self.seisCube.inline_C - self.seisCube.inline_B)
        alpha_y = self.seisCube.north_A - \
            beta_y * self.seisCube.inline_A - \
            gamma_y * self.seisCube.crline_A

        d = np.matrix([[w_east - alpha_x], [w_north - alpha_y]])
        G = np.matrix([[beta_x, gamma_x], [beta_y, gamma_y]])
        m = G.I * d

        m = m.astype(int)
        # w_inline, w_xline = m[0][0], m[1][0]

        inline, crline = int(m[0][0]), int(m[1][0])
        param_in = (inline - self.seisCube.startInline) // \
            self.seisCube.stepInline + \
            ((inline - self.seisCube.startInline) %
             self.seisCube.stepInline) // \
            (self.seisCube.stepInline / 2)
        inline = self.seisCube.startInline + \
            self.seisCube.stepInline * param_in
        param_cr = (crline - self.seisCube.startCrline) // \
            self.seisCube.stepCrline + \
            ((inline - self.seisCube.startCrline) %
             self.seisCube.stepCrline) // \
            (self.seisCube.stepCrline)
        crline = self.seisCube.startCrline + \
            self.seisCube.stepCrline * param_cr
        return (int(inline), int(crline))

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
            a = (w_crline - self.seisCube.startCrline) // \
                self.seisCube.stepCrline
            b = (w_inline - self.seisCube.startInline) // \
                self.seisCube.stepInline
            sparse_list.append([w_inline, w_crline, d])

        return sparse_list


# region Store
    # def _cal_setting(self):
    #     self.nNorth = (self.endCrline - self.startCrline) // \
    #         self.stepCrline + 1
    #     self.nEast = (self.endInline - self.startInline) // \
    #         self.stepInline + 1
    #     self.stepEast = np.sqrt((self.north_C - self.north_B)**2 +
    #                             (self.east_C - east_B)**2) / \
    #         ((self.inline_C - self.inline_B) //
    #             self.stepInline)
    #     self.stepNorth = np.sqrt((self.north_B - self.north_A)**2 +
    #                              (self.east_B - east_A)**2) / \
    #         ((self.crline_B - self.crline_A) //
    #             self.stepCrline)
    #     # point D helps make ABCD a rectangle
    #     inline_D = self.inline_C
    #     crline_D = self.crline_A
    #     east_D = east_A + east_C - east_B
    #     north_D = north_A + north_C - north_B

    #     angleNorth = self._angle(east_A, north_A, east_B, north_B)
    #     angleEast = self._angle(east_A, north_A, east_D, north_D)

    # def _angle(self, x1, y1, x2, y2):
    #     angle = 0
    #     x = x2 - x1
    #     y = y2 - y1
    #     arctanAngle = np.arctan(y / x)
    #     if x > 0 and y > 0:
    #         angle = arctanAngle
    #     elif x > 0 and y < 0:
    #         angle = 2 * np.pi + arctanAngle
    #     elif x < 0 and y > 0:
    #         angle = np.pi + arctanAngle
    #     elif x < 0 and y < 0:
    #         angle = np.pi + arctanAngle
    #     return angle
# endregion
