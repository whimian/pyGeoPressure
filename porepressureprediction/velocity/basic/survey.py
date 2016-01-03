# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 20:24:38 2015

@author: yuhao
"""
from __future__ import division, print_function
import numpy as np


class Survey(object):
    """a survey is a combination of seismic and well logs
    """
    def __init__(self, cube):
        self.wells = list()
        self.seisCube = cube
        self.wells_loc = dict()

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
        return (inline, crline)

    def add_well(self, well):
        loc = self._tie(well)
        self.wells.append(well)
        self.wells_loc[well.name] = loc

    def get_seis(self, well_name, attr):
        if well_name in self.wells_loc.keys():
            loc = self.wells_loc[well_name]
            data = self.seisCube.get_cdp(loc, attr)
            return data
        else:
            print("Well not found! return None")
            return None

    def sparse_mesh(self, depth, log_name):
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
        mesh = np.array([np.nan] * self.seisCube.nNorth * self.seisCube.nEast)
        mesh.shape = (self.seisCube.nNorth, self.seisCube.nEast)
        for we in self.wells:
            log_depth = we.get_log("depth")
            log_data = we.get_log(log_name)
            log_index = range(len(log_depth))
            d = log_data[min(log_index, key=lambda x: abs(log_depth[x]-depth))]
            # print("d = ", d)
            w_inline = self.wells_loc[we.name][0]
            w_crline = self.wells_loc[we.name][1]
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
        for we in self.wells:
            log_depth = we.get_log("depth")
            log_data = we.get_log(log_name)
            log_index = range(len(log_depth))
            d = log_data[min(log_index, key=lambda x: abs(log_depth[x]-depth))]
            # print("d = ", d)
            w_inline = self.wells_loc[we.name][0]
            w_crline = self.wells_loc[we.name][1]
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

if __name__ == "__main__":
    from seiSQL import SeisCube
    from laSQL import Well
    chx = Well(js="../testFile/TWT1.json", db="../testFile/TWT1.db")

    cube = SeisCube("../velocity_2.db", "../survey.json")

    sur = Survey(cube)
    sur.add_well(chx)
    print(sur.wells_loc)
    tdk = sur.get_seis(chx.name)
    print(type(tdk), tdk[:10], sep=',')
    me = sur.sparse_mesh(1600, 'ac')
    print("shape:", me.shape)
    for m in me:
        for n in m:
            if not np.isnan(n):
                print(n)
