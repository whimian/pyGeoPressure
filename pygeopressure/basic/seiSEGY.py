# -*- coding: utf-8 -*-
"""
class for interfacing with segy file.

Created on Feb. 7th 2018
"""
from __future__ import division, print_function

__author__ = "yuhao"

import sqlite3
import os
import json
from shutil import copyfile
from itertools import product

import numpy as np

from . import Path

import segyio

from .utils import split_sequence, methdispatch
from .vawt import wiggles, img
from .indexes import InlineIndex, CrlineIndex, DepthIndex, CdpIndex
from .well_log import Log


class SeiSEGY(object):
    def __init__(self, segy_file, like=None):
        self.segy_file = segy_file

        if like is not None:
            if Path(like).exists() and not Path(self.segy_file).exists():
                copyfile(src=like, dst=self.segy_file)

        if self.segy_file is not None:
            self._parse_segy()

    def _info(self):
        return "A seismic Data Cube\n" +\
               'In-line range: {} - {} - {}\n'.format(
                   self.startInline, self.endInline, self.stepInline) +\
               'Cross-line range: {} - {} - {}\n'.format(
                   self.startCrline, self.endCrline, self.stepCrline) +\
               'Z range: {} - {} - {}\n'.format(
                   self.startDepth, self.endDepth, self.stepDepth)

    def __str__(self):
        return self._info()

    def __repr__(self):
        return self._info()

    def _parse_segy(self):
        with segyio.open(self.segy_file, 'r') as segyfile:
            segyfile.mmap()
            self.startInline = segyfile.ilines[0]
            self.endInline = segyfile.ilines[-1]
            self.nEast = len(segyfile.ilines)
            self.stepInline = (self.endInline - self.startInline) // \
                (self.nEast - 1)
            self.startCrline = segyfile.xlines[0]
            self.endCrline = segyfile.xlines[-1]
            self.nNorth = len(segyfile.xlines)
            self.stepCrline = (self.endCrline - self.startCrline) // \
                (self.nNorth - 1)
            # self.startDepth = segyfile.bin[segyio.BinField.SamplesOriginal]
            # # in miliseconds
            # self.stepDepth = segyfile.bin[segyio.BinField.Interval] // 1000
            # self.nDepth = segyfile.bin[segyio.BinField.Samples]
            # self.endDepth = self.startDepth + self.stepDepth * (self.nDepth - 1)
            self.startDepth = segyfile.samples[0]
            self.endDepth = segyfile.samples[-1]
            self.nDepth = len(segyfile.samples)
            self.stepDepth = (self.endDepth - self.startDepth) // \
                (self.nDepth - 1)

    # @property
    # def attributes(self):
    #     try:
    #         with sqlite3.connect(self.db_file) as conn:
    #             cur = conn.cursor()
    #             cur.execute("""SELECT name FROM sqlite_master
    #                         WHERE type='table' ORDER BY name""")
    #             temp = cur.fetchall()
    #         attributelist = [item[0] for item in temp]
    #         return attributelist
    #     except Exception as inst:
    #         print(inst.args[0])
    #         return []

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

    def depths(self):
        """
        Iterator for z coordinate
        """
        for i in range(self.nDepth):
            yield self.startDepth + i * self.stepDepth

    def inline(self, inline):
        with segyio.open(self.segy_file, 'r') as segyfile:
            segyfile.mmap()
            data = segyfile.iline[inline]
        return data

    def crline(self, crline):
        with segyio.open(self.segy_file, 'r') as segyfile:
            segyfile.mmap()
            data = segyfile.xline[crline]
        return data

    def depth(self, depth):
        with segyio.open(self.segy_file, 'r') as segyfile:
            segyfile.mmap()
            data = segyfile.depth_slice[depth]
        return data

    def cdp(self, cdp):
        with segyio.open(self.segy_file, 'r') as segyfile:
            segyfile.mmap()
            data = segyfile.gather[cdp]
        return data

    @methdispatch
    def data(self, indexes):
        raise TypeError("Unsupported Type")

    @data.register(InlineIndex)
    def _(self, indexes):
        return self.inline(indexes.value)

    @data.register(CrlineIndex)
    def _(self, indexes):
        return self.crline(indexes.value)

    @data.register(DepthIndex)
    def _(self, indexes):
        return self.depth(indexes.value)

    @data.register(CdpIndex)
    def _(self, indexes):
        return self.cdp(indexes.value)

    def update(self, index, data):
        try:
            if not isinstance(index, InlineIndex):
                raise TypeError("has to be InlineIndex")
            if data.shape != (self.nNorth, self.nDepth):
                raise ValueError
            with segyio.open(self.segy_file, 'r+') as segyfile:
                segyfile.mmap()
                segyfile.iline[index.value] = data
        except Exception as er:
            print(er.message)

    # def set_inline(self, inline, attr, data):
    #     """update attribute within an inline

    #        Parameters
    #        ----------
    #        inline : int
    #        attr : str
    #        data : list of float
    #     """
    #     val = [(d[0],) for d in data]
    #     with sqlite3.connect(self.db_file) as conn:
    #         cur = conn.cursor()
    #         cur.executemany("""UPDATE {table}
    #                        SET attribute = ?
    #                        WHERE inline={inl}
    #                        """.format(table=attr, inl=inline), val)

    # def set_crline(self, crline, attr, data):
    #     val = [(d[0],) for d in data]
    #     with sqlite3.connect(self.db_file) as conn:
    #         cur = conn.cursor()
    #         cur.executemany("""UPDATE {table}
    #                        SET attribute = ?
    #                        WHERE crline={crl}
    #                        """.format(table=attr, crl=crline), val)

    # def set_depth(self, depth, attr, data):
    #     val = [(d[0],) for d in data]
    #     with sqlite3.connect(self.db_file) as conn:
    #         cur = conn.cursor()
    #         cur.executemany("""UPDATE {table}
    #                        SET attribute = ?
    #                        WHERE twt={d}""".format(table=attr, d=depth), val)

    # def set_cdp(self, CDP, attr, data):
    #     il = CDP[0]
    #     cl = CDP[1]
    #     val = [(d[0],) for d in data]
    #     with sqlite3.connect(self.db_file) as conn:
    #         cur = conn.cursor()
    #         cur.executemany("""UPDATE {table}
    #                        SET attribute = ?
    #                        WHERE inlne={inl} AND crline={crl}
    #                        """.format(table=attr, inl=il, crl=cl), val)

    # def write_to_db(self, data, attr):
    #     at = [(da,) for da in data]
    #     with sqlite3.connect(self.db_file) as conn:
    #         cur = conn.cursor()
    #         cur.execute(
    #             "CREATE TABLE IF NOT EXISTS {} ( ".format(attr) +\
    #             "id INTEGER PRIMARY KEY, " +\
    #             "attribute REAL) ")
    #         cur.executemany(
    #             "INSERT INTO {} ({}) ".format(attr, 'attribute') +\
    #             "VALUES (?)", at)

    # def add_attr(self, attr):
    #     "Add an empty attribute to a SeisCube object"
    #     try:
    #         if attr in self.attributes:
    #             raise Exception("Attribute already exists, use another name")
    #         with sqlite3.connect(self.db_file) as conn:
    #             cur = conn.cursor()
    #             cur.execute("""CREATE TABLE {}(
    #                 id INTEGER PRIMARY KEY,
    #                 attribute REAL
    #             )""".format(attr))
    #     except Exception as inst:
    #         print(inst)

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
    # def export_od(self, attr, fname):
    #     try:
    #         with open(fname, 'w') as fout:
    #             fout.write("{}\t{}\t{}\n".format(
    #                 self.stepInline, self.stepCrline, self.stepDepth))
    #             for inl in self.inlines():
    #                 data = self.get_inline(inl, attr)
    #                 for crl, dlist in zip(self.crlines(), data):
    #                     dlist = np.nan_to_num(dlist)
    #                     data_string = '\t'.join([str(d) for d in dlist])
    #                     tempList = [str(inl), str(crl), data_string]
    #                     tempStr = '\t'.join(tempList) + '\n'
    #                     fout.write(tempStr)

    #     except Exception as inst:
    #         print(inst)
    #         print("failed to export")

    # def export_gslib(self, attr, fname, title="seismic data"):
    #     """
    #     Output attributes to a gslib data file.
    #     A description of this file format could be found on
    #     'http://www.gslib.com/gslib_help/format.html'
    #     """
    #     try:
    #         with open(fname, 'w') as fout:
    #             fout.write(title+'\n')
    #             fout.write("4\nx\ny\nz\n")
    #             fout.write(attr+'\n')
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
    #                         # if len(temp) == 0:
    #                         if not temp:
    #                             continue
    #                         else:
    #                             x, y = self.line_2_coord(inl, crl)
    #                             for i in range(self.nDepth):
    #                                 tempList = [str(x), str(y), str(self.startDepth+self.stepDepth*i), str(temp[i][0])]
    #                                 fout.write('\t'.join(tempList) + '\n')
    #     except Exception as inst:
    #         print(inst)
    #         print("Failed to export.")

    # def inline_to_indexes(self, inline):
    #     """
    #     Iterator on sample idexes of a given inline
    #     """
    #     n_samples_per_inline = self.nNorth * self.nDepth
    #     shift = ((inline - self.startInline) // self.stepInline) * \
    #         n_samples_per_inline
    #     # for i in range(n_samples_per_inline):
    #     #     yield i + shift + 1

    #     return [i + shift + 1 for i in range(n_samples_per_inline)]

    # def crline_to_indexes(self, crline):
    #     """
    #     Iterator on sample indexes of a given crline
    #     """
    #     n_samples_per_inline = self.nNorth * self.nDepth
    #     deviation = (crline - self.startCrline) // self.stepCrline * self.nDepth
    #     for nil in range(self.nEast):
    #         for sam in range(self.nDepth):
    #             yield sam + deviation + nil*n_samples_per_inline + 1

    # def depth_to_indexes(self, depth):
    #     """
    #     Iterator on sample indexes of a given depth
    #     """
    #     diff = (depth - self.startDepth) // self.stepDepth
    #     n_cdp = self.nNorth * self.nEast
    #     n_depth = self.nDepth
    #     for ncdp in range(n_cdp):
    #         yield diff + ncdp * n_depth + 1

    # def cdp_to_indexes(self, cdp):
    #     """
    #     Iterator on sample indexes of a given cdp
    #     """
    #     inline, crline = cdp
    #     diff = ((inline - self.startInline) // self.stepInline) * \
    #         self.nNorth * self.nDepth + \
    #         ((crline - self.startCrline) // self.stepCrline) * self.nDepth
    #     num = self.nDepth
    #     for item in range(num):
    #         yield item + diff + 1

    # def plot_inline(self, inline, attr, ax, kind='vawt'):
    #     data = self.get_inline(inline, attr)
    #     if kind == 'vawt':
    #         wiggles(data.T, wiggleInterval=1, ax=ax)
    #     else:
    #         pass

    # def plot_crline(self, crline, attr, ax, kind='vawt'):
    #     data = self.get_crline(crline, attr)
    #     if kind == 'vawt':
    #         wiggles(data.T, wiggleInterval=1, ax=ax)
    #     else:
    #         pass

    # def plot_slice(self, depth, attr, ax, kind='vawt'):
    #     data = self.get_depth(depth, attr)
    #     if kind == 'vawt':
    #         wiggles(data.T, wiggleInterval=1, ax=ax)
    #     else:
    #         pass

    # @methdispatch
    # def plot(self, index, attr, ax, kind='vawt', cm='seismic', ptype='seis'):
    #     raise TypeError('Unsupported index type')

    # @plot.register(InlineIndex)
    # def _(self, index, attr, ax, kind='vawt', cm='seismic', ptype='seis'):
    #     data = self.get_data(index, attr)
    #     if kind == 'vawt':
    #         wiggles(data.T, wiggleInterval=1, ax=ax)
    #     elif kind == 'img':
    #         img(data.T,
    #             extent=[
    #                 self.startCrline, self.endCrline,
    #                 self.startDepth, self.endDepth],
    #             ax=ax, cm=cm, ptype=ptype)
    #         ax.invert_yaxis()
    #     else:
    #         pass
    #     ax.get_figure().suptitle('In-line Section: {}'.format(index.value))
    #     from matplotlib.offsetbox import AnchoredText
    #     z_text = AnchoredText(
    #         r"$\downarrow$Z",
    #         loc=2, prop=dict(size=10), frameon=False,
    #         bbox_to_anchor=(0., 0.),
    #         bbox_transform=ax.transAxes)
    #     ax.add_artist(z_text)
    #     inline_text = AnchoredText(
    #         r"Cross-line $\rightarrow$ ",
    #         loc=1, prop=dict(size=10), frameon=False,
    #         bbox_to_anchor=(1., 0.),
    #         bbox_transform=ax.transAxes)
    #     ax.add_artist(inline_text)

    # @plot.register(CrlineIndex)
    # def _(self, index, attr, ax, kind='vawt', cm='seismic', ptype='seis'):
    #     data = self.get_data(index, attr)
    #     if kind == 'vawt':
    #         wiggles(data.T, wiggleInterval=1, ax=ax)
    #     elif kind == 'img':
    #         img(data.T,
    #             extent=[
    #                 self.startInline, self.endInline,
    #                 self.startDepth, self.endDepth],
    #             ax=ax, cm=cm, ptype=ptype)
    #         ax.invert_yaxis()
    #     else:
    #         pass
    #     ax.get_figure().suptitle('Cross-line Section: {}'.format(index.value))
    #     from matplotlib.offsetbox import AnchoredText
    #     z_text = AnchoredText(
    #         r"$\downarrow$Z",
    #         loc=2, prop=dict(size=10), frameon=False,
    #         bbox_to_anchor=(0., 0.),
    #         bbox_transform=ax.transAxes)
    #     ax.add_artist(z_text)
    #     inline_text = AnchoredText(
    #         r"In-line $\rightarrow$ ",
    #         loc=1, prop=dict(size=10), frameon=False,
    #         bbox_to_anchor=(1., 0.),
    #         bbox_transform=ax.transAxes)
    #     ax.add_artist(inline_text)

    # @plot.register(DepthIndex)
    # def _(self, index, attr, ax, kind='vawt', cm='seismic', ptype='seis'):
    #     data = self.get_data(index, attr)
    #     if kind == 'vawt':
    #         wiggles(data.T, wiggleInterval=1, ax=ax)
    #     elif kind == 'img':
    #         img(data.T,
    #             extent=[
    #                 self.startInline, self.endInline,
    #                 self.startCrline, self.endCrline,],
    #             ax=ax, cm=cm, ptype=ptype)
    #         ax.invert_yaxis()
    #     else:
    #         pass
    #     ax.get_figure().suptitle("Z slice: {}".format(index.value))
    #     from matplotlib.offsetbox import AnchoredText
    #     z_text = AnchoredText(
    #         r"$\downarrow$Cross-line",
    #         loc=2, prop=dict(size=10), frameon=False,
    #         bbox_to_anchor=(0., 0.),
    #         bbox_transform=ax.transAxes)
    #     ax.add_artist(z_text)
    #     inline_text = AnchoredText(
    #         r"In-line $\rightarrow$ ",
    #         loc=1, prop=dict(size=10), frameon=False,
    #         bbox_to_anchor=(1., 0.),
    #         bbox_transform=ax.transAxes)
    #     ax.add_artist(inline_text)

    # def retrieve_data(self, sample_idx, attr):
    #     data = []
    #     with sqlite3.connect(self.db_file) as conn:
    #         cur = conn.cursor()
    #         # due to limitation of sqlite IN clause
    #         for sample_transact in split_sequence(sample_idx, 999):
    #             cur.execute(
    #                 "SELECT {} ".format('attribute') +\
    #                 "FROM {table} ".format(table=attr) +\
    #                 "WHERE id " +\
    #                 "IN ({})".format(', '.join('?'*len(sample_transact))),
    #                 sample_transact)
    #             data_transact = cur.fetchall()
    #             data_transact = [d[0] for d in data_transact]
    #             data += data_transact
    #     return data

    # @methdispatch
    # def get_data(self, indexes, attr):
    #     raise TypeError("Unsupported Type")

    # @get_data.register(InlineIndex)
    # def _(self, indexes, attr):
    #     return self.get_inline(indexes.value, attr)

    # @get_data.register(CrlineIndex)
    # def _(self, indexes, attr):
    #     return self.get_crline(indexes.value, attr)

    # @get_data.register(DepthIndex)
    # def _(self, indexes, attr):
    #     return self.get_depth(indexes.value, attr)

    # @get_data.register(CdpIndex)
    # def _(self, indexes, attr):
    #     return self.get_cdp(indexes.value, attr)

    # def get_pseudo_log(self, cdp, attr):
    #     pseudo_log = Log()
    #     pseudo_log.depth = list(self.depth())
    #     pseudo_log.data = self.get_data(CdpIndex(cdp), attr)
    #     pseudo_log.name = "{}_inline_{}_crline_{}".format(attr, cdp[0], cdp[1])
    #     return pseudo_log

    def valid_cdp(self, cdp_num):
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

