# -*- coding: utf-8 -*-
"""
class for storing seismic data utilizing sqlite database.
"""
from __future__ import division, print_function

__author__ = "yuhao"

import sqlite3
import os
import json
from itertools import product

import numpy as np

from .utils import split_sequence, methdispatch
from .vawt import wiggles, img
from .indexes import InlineIndex, CrlineIndex, DepthIndex, CdpIndex
from .well_log import Log


class SeisCube(object):
    def __init__(self, json_file):
        self.db_file = None
        self.json_file = json_file
        if self.json_file is not None:
            self._readJSON()

    def _info(self):
        return "A seismic Data Cube\n" +\
               'In-line range: {} - {} - {}\n'.format(
                   self.startInline, self.endInline, self.stepInline) +\
               'Cross-line range: {} - {} - {}\n'.format(
                   self.startCrline, self.endCrline, self.stepCrline) +\
               'Z range: {} - {} - {}\n'.format(
                   self.startDepth, self.endDepth, self.stepDepth) +\
               "Inl/Crl bin size (m/line): {}/{}\n".format(
                   self.inline_bin, self.crline_bin) +\
               "SQL file location : {}\n".format(
                   os.path.abspath(self.db_file)) +\
               "Stored attributes: {}".format(self.attributes)

    def __str__(self):
        return self._info()

    def __repr__(self):
        return self._info()

    def _readJSON(self):
        with open(self.json_file, 'r') as fin:
            json_setting = json.load(fin)
            self.db_file = json_setting['db_file']
            self.startInline = json_setting['inline'][0]
            self.endInline = json_setting['inline'][1]
            self.stepInline = json_setting['inline'][2]
            self.startCrline = json_setting['crline'][0]
            self.endCrline = json_setting['crline'][1]
            self.stepCrline = json_setting['crline'][2]
            self.startDepth = json_setting['depth'][0]
            self.endDepth = json_setting['depth'][1]
            self.stepDepth = json_setting['depth'][2]
            self.inline_A = json_setting['Coordinate'][0][0]
            self.crline_A = json_setting['Coordinate'][0][1]
            self.east_A = json_setting['Coordinate'][0][2]
            self.north_A = json_setting['Coordinate'][0][3]
            self.inline_B = json_setting['Coordinate'][1][0]
            self.crline_B = json_setting['Coordinate'][1][1]
            self.east_B = json_setting['Coordinate'][1][2]
            self.north_B = json_setting['Coordinate'][1][3]
            self.inline_C = json_setting['Coordinate'][2][0]
            self.crline_C = json_setting['Coordinate'][2][1]
            self.east_C = json_setting['Coordinate'][2][2]
            self.north_C = json_setting['Coordinate'][2][3]
        self.nEast = (self.endInline - self.startInline) // \
            self.stepInline + 1
        self.nNorth = (self.endCrline - self.startCrline) // \
            self.stepCrline + 1
        self.nDepth = int((self.endDepth - self.startDepth) // self.stepDepth + 1)
        self._coordinate_conversion()

    def _coordinate_conversion(self):
        self.gamma_x = (self.east_B - self.east_A) / \
            (self.crline_B - self.crline_A)
        self.beta_x = (self.east_C - self.east_B) / \
            (self.inline_C - self.inline_B)
        self.alpha_x = self.east_A - \
            self.beta_x * self.inline_A - \
            self.gamma_x * self.crline_A
        self.gamma_y = (self.north_B - self.north_A) / \
            (self.crline_B - self.crline_A)
        self.beta_y = (self.north_C - self.north_B) / \
            (self.inline_C - self.inline_B)
        self.alpha_y = self.north_A - \
            self.beta_y * self.inline_A - \
            self.gamma_y * self.crline_A
        dist_ab = np.sqrt((self.north_B - self.north_A) *\
                          (self.north_B - self.north_A) + \
                          (self.east_B - self.east_A) * \
                          (self.east_B - self.east_A))
        dist_bc = np.sqrt((self.north_C - self.north_B) *\
                          (self.north_C - self.north_B) + \
                          (self.east_C - self.east_B) * \
                          (self.east_C - self.east_B))
        self.crline_bin = np.round(dist_ab / (self.crline_B - self.crline_A),
                                   decimals=2)
        self.inline_bin = np.round(dist_bc / (self.inline_C - self.inline_B),
                                   decimals=2)

    @property
    def attributes(self):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cur = conn.cursor()
                cur.execute("""SELECT name FROM sqlite_master
                            WHERE type='table' ORDER BY name""")
                temp = cur.fetchall()
            attributelist = [item[0] for item in temp]
            return attributelist
        except Exception as inst:
            print(inst.args[0])
            return []

    def inlines(self):
        """
        Iterator for inline numbers
        """
        for inline in range(self.startInline, self.endInline+1, self.stepInline):
            yield inline

    def crlines(self):
        """
        Iterator for crline numbers
        """
        for crline in range(self.startCrline, self.endCrline+1, self.stepCrline):
            yield crline

    def inline_crlines(self):
        """
        Iterator for both inline and crline numbers
        """
        for inline, crline in product(
                range(self.startInline, self.endInline+1, self.stepInline),
                range(self.startCrline, self.endCrline+1, self.stepCrline)):
            yield (inline, crline)

    def depth(self):
        """
        Iterator for z coordinate
        """
        for i in range(self.nDepth):
            yield self.startDepth + i * self.stepDepth

    def coord_2_line(self, coordinate):
        x = coordinate[0]
        y = coordinate[1]
        d = np.matrix([[x - self.alpha_x],
                       [y - self.alpha_y]])
        G = np.matrix([[self.beta_x, self.gamma_x],
                       [self.beta_y, self.gamma_y]])
        m = G.I * d
        # m = m.astype(int)

        inline, crline = m[0][0], m[1][0]
        param_in = (inline - self.startInline) // self.stepInline + \
            ((inline - self.startInline) % self.stepInline) // \
            (self.stepInline / 2)
        inline = self.startInline + self.stepInline * param_in
        param_cr = (crline - self.startCrline) // self.stepCrline + \
            ((inline - self.startCrline) % self.stepCrline) // \
            (self.stepCrline)
        crline = self.startCrline + self.stepCrline * param_cr
        return (inline, crline)

    def line_2_coord(self, inline, crline):
        x = self.alpha_x + self.beta_x * inline + self.gamma_x * crline
        y = self.alpha_y + self.beta_y * inline + self.gamma_y * crline
        return (x, y)

    def get_inline(self, inline, attr):
        "Retrieve data by inline number"
        try:
            if inline < self.startInline or inline > self.endInline:
                raise Exception("Inline number out of range.")

            samples = list(self.inline_to_indexes(inline))
            data = self.retrieve_data(samples, attr)
            return np.array(data, dtype=np.float).reshape((self.nNorth, self.nDepth))
        except Exception as inst:
            print(inst)
            return []

    def get_crline(self, crline, attr):
        try:
            if crline < self.startCrline or crline > self.endCrline:
                raise Exception("Crossline number out of range.")
            samples = list(self.crline_to_indexes(crline))
            data = self.retrieve_data(samples, attr)
            return np.array(data).reshape((self.nEast, self.nDepth))
        except Exception as inst:
            print(inst)
            return []

    def get_depth(self, depth, attr):
        try:
            if depth < self.startDepth or depth > self.endDepth:
                raise Exception("Depth out of range.")
            samples = list(self.depth_to_indexes(depth))
            data = self.retrieve_data(samples, attr)
            return np.array(data).reshape((self.nEast, self.nNorth))
        except Exception as inst:
            print(inst)
            return []

    def get_cdp(self, CDP, attr):
        try:
            il = CDP[0]
            cl = CDP[1]
            if il < self.startInline or il > self.endInline:
                raise Exception("Inline out of range.")
            if cl < self.startCrline or cl > self.endCrline:
                raise Exception("Crossline out of range.")
            samples = list(self.cdp_to_indexes(CDP))
            data = self.retrieve_data(samples, attr)
            return np.array(data, dtype=np.float)
        except Exception as inst:
            print(inst)
            return []

    def set_inline(self, inline, attr, data):
        """update attribute within an inline

           Parameters
           ----------
           inline : int
           attr : str
           data : list of float
        """
        val = [(d[0],) for d in data]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.executemany("""UPDATE {table}
                           SET attribute = ?
                           WHERE inline={inl}
                           """.format(table=attr, inl=inline), val)

    def set_crline(self, crline, attr, data):
        val = [(d[0],) for d in data]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.executemany("""UPDATE {table}
                           SET attribute = ?
                           WHERE crline={crl}
                           """.format(table=attr, crl=crline), val)

    def set_depth(self, depth, attr, data):
        val = [(d[0],) for d in data]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.executemany("""UPDATE {table}
                           SET attribute = ?
                           WHERE twt={d}""".format(table=attr, d=depth), val)

    def set_cdp(self, CDP, attr, data):
        il = CDP[0]
        cl = CDP[1]
        val = [(d[0],) for d in data]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.executemany("""UPDATE {table}
                           SET attribute = ?
                           WHERE inlne={inl} AND crline={crl}
                           """.format(table=attr, inl=il, crl=cl), val)

    def write_to_db(self, data, attr):
        at = [(da,) for da in data]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS {} ( ".format(attr) +\
                "id INTEGER PRIMARY KEY, " +\
                "attribute REAL) ")
            cur.executemany(
                "INSERT INTO {} ({}) ".format(attr, 'attribute') +\
                "VALUES (?)", at)

    def add_attr(self, attr):
        "Add an empty attribute to a SeisCube object"
        try:
            if attr in self.attributes:
                raise Exception("Attribute already exists, use another name")
            with sqlite3.connect(self.db_file) as conn:
                cur = conn.cursor()
                cur.execute("""CREATE TABLE {}(
                    id INTEGER PRIMARY KEY,
                    attribute REAL
                )""".format(attr))
        except Exception as inst:
            print(inst)

    # def export_od(self, attr, fname):
    #     try:
    #         with open(fname, 'w') as fout:
    #             fout.write("{}\t{}\t{}\n".format(
    #                                         self.stepInline, self.stepCrline,
    #                                         self.stepDepth))
    #             with sqlite3.connect(self.db_file) as conn:
    #                 cur = conn.cursor()
    #                 for inl in range(self.startInline, self.endInline+1,
    #                                  self.stepInline):
    #                     for crl in range(self.startCrline, self.endCrline+1,
    #                                      self.stepCrline):
    #                         cur.execute(
    #                             "SELECT attribute \
    #                              FROM position \
    #                              JOIN {table} \
    #                              ON position.id = {table}.id \
    #                              WHERE inline = {inline} \
    #                              AND crline = {crline}".format(table=attr,
    #                                                            inline=inl,
    #                                                            crline=crl))
    #                         temp = cur.fetchall()
    #                         if len(temp) == 0:
    #                             continue
    #                         else:
    #                             tempStr = list()
    #                             for i in range(len(temp)):
    #                                 tempStr.append(str(temp[i][0]))
    #                             data = '\t'.join(tempStr) + '\n'
    #                             string = str(inl) + '\t' + str(crl) + '\t'
    #                             fout.write(string + data)
    #     except Exception as inst:
    #         print(inst)
    #         print("failed to export")
    def export_od(self, attr, fname):
        try:
            with open(fname, 'w') as fout:
                fout.write("{}\t{}\t{}\n".format(
                                            self.stepInline, self.stepCrline,
                                            self.stepDepth))
                for inl in self.inlines():
                    data = self.get_inline(inl, attr)
                    for crl, dlist in zip(self.crlines(), data):
                        dlist = np.nan_to_num(dlist)
                        data_string = '\t'.join([str(d) for d in dlist])
                        tempList = [str(inl), str(crl), data_string]
                        tempStr = '\t'.join(tempList) + '\n'
                        fout.write(tempStr)

        except Exception as inst:
            print(inst)
            print("failed to export")

    def export_gslib(self, attr, fname, title="seismic data"):
        """
        Output attributes to a gslib data file.
        A description of this file format could be found on
        'http://www.gslib.com/gslib_help/format.html'
        """
        try:
            with open(fname, 'w') as fout:
                fout.write(title+'\n')
                fout.write("4\nx\ny\nz\n")
                fout.write(attr+'\n')
                with sqlite3.connect(self.db_file) as conn:
                    cur = conn.cursor()
                    for inl in range(self.startInline, self.endInline+1,
                                     self.stepInline):
                        for crl in range(self.startCrline, self.endCrline+1,
                                         self.stepCrline):
                            cur.execute(
                                "SELECT attribute \
                                 FROM position \
                                 JOIN {table} \
                                 ON position.id = {table}.id \
                                 WHERE inline = {inline} \
                                 AND crline = {crline}".format(table=attr,
                                                               inline=inl,
                                                               crline=crl))
                            temp = cur.fetchall()
                            if len(temp) == 0:
                                continue
                            else:
                                x, y = self.line_2_coord(inl, crl)
                                for i in range(self.nDepth):
                                    tempList = [str(x), str(y), str(self.startDepth+self.stepDepth*i), str(temp[i][0])]
                                    fout.write('\t'.join(tempList) + '\n')
        except Exception as inst:
            print(inst)
            print("Failed to export.")

    def inline_to_indexes(self, inline):
        """
        Iterator on sample idexes of a given inline
        """
        n_samples_per_inline = self.nNorth * self.nDepth
        shift = ((inline - self.startInline) // self.stepInline) * \
            n_samples_per_inline
        for i in range(n_samples_per_inline):
            yield i + shift + 1

    def crline_to_indexes(self, crline):
        """
        Iterator on sample indexes of a given crline
        """
        n_samples_per_inline = self.nNorth * self.nDepth
        deviation = (crline - self.startCrline) // self.stepCrline * self.nDepth
        for nil in range(self.nEast):
            for sam in range(self.nDepth):
                yield sam + deviation + nil*n_samples_per_inline + 1

    def depth_to_indexes(self, depth):
        """
        Iterator on sample indexes of a given depth
        """
        diff = (depth - self.startDepth) // self.stepDepth
        n_cdp = self.nNorth * self.nEast
        n_depth = self.nDepth
        for ncdp in range(n_cdp):
            yield diff + ncdp * n_depth + 1

    def cdp_to_indexes(self, cdp):
        """
        Iterator on sample indexes of a given cdp
        """
        inline, crline = cdp
        diff = ((inline - self.startInline) // self.stepInline) * \
            self.nNorth * self.nDepth + \
            ((crline - self.startCrline) // self.stepCrline) * self.nDepth
        num = self.nDepth
        for item in range(num):
            yield item + diff + 1

    def plot_inline(self, inline, attr, ax, kind='vawt'):
        data = self.get_inline(inline, attr)
        if kind == 'vawt':
            wiggles(data.T, wiggleInterval=1, ax=ax)
        else:
            pass

    def plot_crline(self, crline, attr, ax, kind='vawt'):
        data = self.get_crline(crline, attr)
        if kind == 'vawt':
            wiggles(data.T, wiggleInterval=1, ax=ax)
        else:
            pass

    def plot_slice(self, depth, attr, ax, kind='vawt'):
        data = self.get_depth(depth, attr)
        if kind == 'vawt':
            wiggles(data.T, wiggleInterval=1, ax=ax)
        else:
            pass

    @methdispatch
    def plot(self, index, attr, ax, kind='vawt', cm='seismic'):
        raise TypeError('Unsupported index type')

    @plot.register(InlineIndex)
    def _(self, index, attr, ax, kind='vawt', cm='seismic'):
        data = self.get_data(index, attr)
        if kind == 'vawt':
            wiggles(data.T, wiggleInterval=1, ax=ax)
        elif kind == 'img':
            img(data.T,
                extent=[
                    self.startCrline, self.endCrline,
                    self.startDepth, self.endDepth],
                ax=ax, cm=cm)
            ax.invert_yaxis()
        else:
            pass
        ax.get_figure().suptitle('In-line Section: {}'.format(index.value))
        from matplotlib.offsetbox import AnchoredText
        z_text = AnchoredText(
            r"$\downarrow$Z",
            loc=2, prop=dict(size=10), frameon=False,
            bbox_to_anchor=(0., 0.),
            bbox_transform=ax.transAxes)
        ax.add_artist(z_text)
        inline_text = AnchoredText(
            r"Cross-line $\rightarrow$ ",
            loc=1, prop=dict(size=10), frameon=False,
            bbox_to_anchor=(1., 0.),
            bbox_transform=ax.transAxes)
        ax.add_artist(inline_text)

    @plot.register(CrlineIndex)
    def _(self, index, attr, ax, kind='vawt', cm='seismic'):
        data = self.get_data(index, attr)
        if kind == 'vawt':
            wiggles(data.T, wiggleInterval=1, ax=ax)
        elif kind == 'img':
            img(data.T,
                extent=[
                    self.startInline, self.endInline,
                    self.startDepth, self.endDepth],
                ax=ax, cm=cm)
            ax.invert_yaxis()
        else:
            pass
        ax.get_figure().suptitle('Cross-line Section: {}'.format(index.value))
        from matplotlib.offsetbox import AnchoredText
        z_text = AnchoredText(
            r"$\downarrow$Z",
            loc=2, prop=dict(size=10), frameon=False,
            bbox_to_anchor=(0., 0.),
            bbox_transform=ax.transAxes)
        ax.add_artist(z_text)
        inline_text = AnchoredText(
            r"In-line $\rightarrow$ ",
            loc=1, prop=dict(size=10), frameon=False,
            bbox_to_anchor=(1., 0.),
            bbox_transform=ax.transAxes)
        ax.add_artist(inline_text)

    @plot.register(DepthIndex)
    def _(self, index, attr, ax, kind='vawt', cm='seismic'):
        data = self.get_data(index, attr)
        if kind == 'vawt':
            wiggles(data.T, wiggleInterval=1, ax=ax)
        elif kind == 'img':
            img(data.T,
                extent=[
                    self.startInline, self.endInline,
                    self.startCrline, self.endCrline,],
                ax=ax, cm=cm)
            ax.invert_yaxis()
        else:
            pass
        ax.get_figure().suptitle("Z slice: {}".format(index.value))
        from matplotlib.offsetbox import AnchoredText
        z_text = AnchoredText(
            r"$\downarrow$Cross-line",
            loc=2, prop=dict(size=10), frameon=False,
            bbox_to_anchor=(0., 0.),
            bbox_transform=ax.transAxes)
        ax.add_artist(z_text)
        inline_text = AnchoredText(
            r"In-line $\rightarrow$ ",
            loc=1, prop=dict(size=10), frameon=False,
            bbox_to_anchor=(1., 0.),
            bbox_transform=ax.transAxes)
        ax.add_artist(inline_text)

    def retrieve_data(self, sample_idx, attr):
        data = []
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            for sample_transact in split_sequence(sample_idx, 990):
                cur.execute(
                    "SELECT {} ".format('attribute') +\
                    "FROM {table} ".format(table=attr) +\
                    "WHERE id " +\
                    "IN ({})".format(', '.join('?'*len(sample_transact))), sample_transact)
                data_transact = cur.fetchall()
                data_transact = [d[0] for d in data_transact]
                data += data_transact
        return data

    @methdispatch
    def get_data(self, indexes, attr):
        raise TypeError("Unsupported Type")

    @get_data.register(InlineIndex)
    def _(self, indexes, attr):
        return self.get_inline(indexes.value, attr)

    @get_data.register(CrlineIndex)
    def _(self, indexes, attr):
        return self.get_crline(indexes.value, attr)

    @get_data.register(DepthIndex)
    def _(self, indexes, attr):
        return self.get_depth(indexes.value, attr)

    @get_data.register(CdpIndex)
    def _(self, indexes, attr):
        return self.get_cdp(indexes.value, attr)

    def get_pseudo_log(self, cdp, attr):
        pseudo_log = Log()
        pseudo_log.depth = list(self.depth())
        pseudo_log.data = self.get_data(CdpIndex(cdp), attr)
        pseudo_log.name = "{}_inline_{}_crline_{}".format(attr, cdp[0], cdp[1])
        return pseudo_log

    def valid_cdp(self, cdp_num: tuple):
        inl_num, crl_num = cdp_num
        n_inline = (inl_num - self.startInline) // self.stepInline
        in_plus_one = round(((inl_num - self.startInline) % self.stepInline) / \
                            self.stepInline)
        inline = self.startInline + (n_inline + in_plus_one) * self.stepInline

        n_crline = (crl_num - self.startCrline) // self.stepCrline
        cr_plus_one = round(((crl_num - self.startCrline) % self.stepCrline) / \
                            self.stepCrline)
        crline = self.startCrline + (n_crline + cr_plus_one) * self.stepCrline
        return (inline, crline)
