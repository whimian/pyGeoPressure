# -*- coding: utf-8 -*-
"""
class for interfacing with segy file.

Created on Feb. 7th 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

from builtins import range, open
import json
from shutil import copyfile
from itertools import product
from future.utils import native
import segyio
import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from .utils import  methdispatch
from .vawt import wiggles, img
from .indexes import InlineIndex, CrlineIndex, DepthIndex, CdpIndex
from .survey_setting import SurveySetting
from .threepoints import ThreePoints

from . import Path


class SeiSEGY(object):
    def __init__(self, segy_file, like=None):
        """
        Parameters
        ----------
        segy_file : str
            segy file path
        like : str, optional
            created segy file has the same dimesions as like.
        """
        self.segy_file = segy_file
        self.inDepth = False # True if dataset Z is in Depth
        self.property_type = None

        if like is not None:
            if Path(native(like)).exists() and not Path(native(self.segy_file)).exists():
                copyfile(src=like, dst=self.segy_file)

        if Path(native(self.segy_file)).exists():
            self._parse_segy()
        else:
            raise Exception("File does not exist!")

    @classmethod
    def from_json(cls, json_file, segy_file=None):
        """
        Initialize SeiSEGY from an json file containing information

        Parameters
        ----------
        json_file : str
            json file path
        segy_file : str
            segy file path for overriding information in json file.
        """
        with open(json_file, 'r') as fl:
            json_object = json.load(fl)
            segy = json_object["path"]
            inDepth = json_object["inDepth"]
            property_type = json_object["Property_Type"]

        if segy_file:
            segy = segy_file
        instance = cls(native(segy))
        instance.inDepth = inDepth
        instance.property_type = property_type

        return instance

    def __str__(self):
        return "SeiSEGY(inl[{},{},{}];crl[{},{},{}];z[{},{},{}])".format(
            self.startInline, self.endInline, self.stepInline,
            self.startCrline, self.endCrline, self.stepCrline,
            self.startDepth, self.endDepth, self.stepDepth)

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
            self.startDepth = segyfile.samples[0]
            self.endDepth = segyfile.samples[-1]
            self.nDepth = len(segyfile.samples)
            self.stepDepth = (self.endDepth - self.startDepth) // \
                (self.nDepth - 1)

            inline_A = self.startInline
            crline_A = self.startCrline
            index_A = 0
            x_A = segyfile.header[index_A][segyio.su.cdpx]
            y_A = segyfile.header[index_A][segyio.su.cdpy]

            inline_B = inline_A
            crline_B = self.startCrline + 2 * self.stepCrline
            index_B = 2
            x_B = segyfile.header[index_B][segyio.su.cdpx]
            y_B = segyfile.header[index_B][segyio.su.cdpy]

            inline_C = self.startInline + 2 * self.stepInline
            crline_C = crline_B
            index_C = 2 * self.nNorth + 2
            x_C = segyfile.header[index_C][segyio.su.cdpx]
            y_C = segyfile.header[index_C][segyio.su.cdpy]

            setting_dict = {
                "inline_range": [
                    self.startInline, self.endInline, self.stepInline],
                "crline_range": [
                    self.startCrline, self.endCrline, self.stepCrline],
                "z_range": [
                    self.startDepth, self.endDepth, self.stepDepth, "unknown"],
                "point_A": [inline_A, crline_A, x_A, y_A],
                "point_B": [inline_B, crline_B, x_B, y_B],
                "point_C": [inline_C, crline_C, x_C, y_C]
            }
            self.survey_setting = SurveySetting(ThreePoints(setting_dict))

    def inlines(self):
        """
        Iterator for inline numbers

        Yields
        ------
        int
            inline number
        """
        for inline in range(self.startInline, self.endInline+1, self.stepInline):
            yield inline

    def crlines(self):
        """
        Iterator for crline numbers

        Yields
        ------
        int
            cross-line number
        """
        for crline in range(self.startCrline, self.endCrline+1, self.stepCrline):
            yield crline

    def inline_crlines(self):
        """
        Iterator for both inline and crline numbers


        Yields
        ------
        tuple of int
            (inline number, crossline number)
        """
        for inline, crline in product(
                range(self.startInline, self.endInline+1, self.stepInline),
                range(self.startCrline, self.endCrline+1, self.stepCrline)):
            yield (inline, crline)

    def depths(self):
        """
        Iterator for z coordinate

        Yields
        ------
        float
            depth value
        """
        for i in range(self.nDepth):
            yield self.startDepth + i * self.stepDepth

    def inline(self, inline):
        "data of a inline section"
        with segyio.open(self.segy_file, 'r') as segyfile:
            segyfile.mmap()
            data = segyfile.iline[inline]
        return data

    def crline(self, crline):
        "data of a crossline section"
        with segyio.open(self.segy_file, 'r') as segyfile:
            segyfile.mmap()
            data = segyfile.xline[crline]
        return data

    def depth(self, depth):
        "data of a depth slice"
        depth_idx = int((depth - self.startDepth) // self.stepDepth)
        with segyio.open(self.segy_file, 'r') as segyfile:
            segyfile.mmap()
            data = segyfile.depth_slice[depth_idx]
        return data

    def cdp(self, cdp):
        "data of a cdp"
        with segyio.open(self.segy_file, 'r') as segyfile:
            segyfile.mmap()
            data = segyfile.gather[cdp]
            data = data.reshape((data.shape[-1],))
        return data

    @methdispatch
    def data(self, indexes):
        """
        Retrieve Data according to the index provided.

        Parameters
        ----------
        indexes : {InlineIndex, CrlineIndex, DepthIndex, CdpIndex}
            index of data to retrieve

        Returns
        -------
        numpy.ndarray
        """
        raise TypeError("Unsupported Type")

    @data.register(InlineIndex)
    def _(self, indexes):
        """
        data of a Inline section

        Paramaters
        ----------
        indexes : InlineIndex

        Returns
        -------
        out : 2-d ndarray
            of size nCrline * nDepth
        """
        return self.inline(indexes.value)

    @data.register(CrlineIndex)
    def _(self, indexes):
        """
        data of a Crossline section

        Paramaters
        ----------
        indexes : CrlineIndex

        Returns
        -------
        out : 2-d ndarray
            of size nInline * nDepth
        """
        return self.crline(indexes.value)

    @data.register(DepthIndex)
    def _(self, indexes):
        """
        data of a depth slice

        Paramaters
        ----------
        indexes : DepthIndex

        Returns
        -------
        out : 2-d ndarray
            of size nInline * nCrline
        """
        return self.depth(indexes.value)

    @data.register(CdpIndex)
    def _(self, indexes):
        """
        data of a cdp

        Paramaters
        ----------
        indexes : CdpIndex

        Returns
        -------
        out : 1-d ndarray
            of length nDepth
        """
        return self.cdp(indexes.value)

    def update(self, index, data):
        """
        Update data with ndarray

        Parameters
        ----------
        index : InlineIndex
        data : 2-d ndarray
            data for updating Inline
        """
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

    @methdispatch
    def plot(self, index, ax, kind='vawt', cm='seismic', ptype='seis'):
        """
        Plot seismic section according to index provided.

        Parameters
        ----------
        index : {InlineIndex, CrlineIndex, DepthIndex, CdpIndex}
            index of data to plot
        ax : matplotlib.axes._subplots.AxesSubplot
            axis to plot on
        kind : {'vawt', 'img'}
            'vawt' for variable area wiggle trace plot
            'img' for variable density plot
        cm : str
            colormap for plotting
        ptype : str, optional
            property type

        Returns
        -------
        matplotlib.image.AxesImage
         """
        raise TypeError('Unsupported index type')

    @plot.register(InlineIndex)
    def _(self, index, ax, kind='vawt', cm='seismic', ptype='seis'):
        data = self.data(index)
        handle = None
        if kind == 'vawt':
            wiggles(data.T, wiggleInterval=1, ax=ax)
        elif kind == 'img':
            handle = img(data.T,
                         extent=[
                             self.startCrline, self.endCrline,
                             self.startDepth, self.endDepth],
                         ax=ax, cm=cm, ptype=ptype)
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

        return handle

    @plot.register(CrlineIndex)
    def _(self, index, ax, kind='vawt', cm='seismic', ptype='seis'):
        data = self.data(index)
        handle = None
        if kind == 'vawt':
            wiggles(data.T, wiggleInterval=1, ax=ax)
        elif kind == 'img':
            handle = img(data.T,
                         extent=[
                             self.startInline, self.endInline,
                             self.startDepth, self.endDepth],
                         ax=ax, cm=cm, ptype=ptype)
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

        return handle

    @plot.register(DepthIndex)
    def _(self, index, ax, kind='vawt', cm='seismic', ptype='seis'):
        data = self.data(index)
        handle = None
        if kind == 'vawt':
            wiggles(data.T, wiggleInterval=1, ax=ax)
        elif kind == 'img':
            handle = img(data.T,
                         extent=[
                             self.startInline, self.endInline,
                             self.startCrline, self.endCrline,],
                         ax=ax, cm=cm, ptype=ptype)
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

        return handle

    def valid_cdp(self, cdp_num):
        "Return valid CDP numbers nearest to cdp_num"
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

    def to_gslib(self, attr, fname, cdps=None):
        """
        Output attributes to a gslib data file.
        A description of this file format could be found on
        'http://www.gslib.com/gslib_help/format.html'

        attr : str
            attribute name
        fname : str
            file name
        cdps : list of tuples
            cdps to export
        """
        try:
            if cdps is None:
                info = "Number of cells: [{},{},{}] ".format(
                        self.nEast, self.nNorth, self.nDepth) + \
                    "Cell dimensions: [{},{},{}] ".format(
                        self.stepInline, self.stepCrline, self.stepDepth) + \
                    "Origin: [{}, {}, {}]".format(
                        self.startInline, self.startCrline, self.startDepth)
                with open(fname, 'w') as fout:
                    fout.write("{}\n4\nx\ny\nz\n{}\n".format(info, attr))

                nInline = len(list(self.inlines()))
                for i, inl in enumerate(
                        tqdm(self.inlines(), total=nInline, ascii=True)):
                    data_per_inline = self.inline(inl).flatten()
                    inline_per_inline = [inl] * data_per_inline.shape[0]
                    crline_per_inline = np.array(
                        [[cl]*self.nDepth for cl in self.crlines()]).flatten()
                    depth_per_inline = np.array(
                        [d for d in self.depths()] * self.nNorth).flatten()
                    temp_frame = pd.DataFrame(
                        {'col1': inline_per_inline,
                         'col2': crline_per_inline,
                         'col3': depth_per_inline,
                         'col4': data_per_inline})
                    temp_frame.to_csv(
                        fname, mode='a', index=False, sep=str(' '),
                        header=False)
            else:
                info = "CDPs: {}".format(cdps)
                with open(fname, 'w') as fout:
                    fout.write("{}\n4\nx\ny\nz\n{}\n".format(info, attr))
                for cdp in tqdm(cdps, ascii=True):
                    data_per_cdp = self.cdp(cdp)
                    depth_per_cdp = list(self.depths())
                    n_depth = len(list(self.depths()))
                    inl, crl = cdp
                    inline_per_cdp = [inl] * n_depth
                    crline_per_cdp = [crl] * n_depth
                    temp_frame = pd.DataFrame(
                        {'col1': inline_per_cdp,
                         'col2': crline_per_cdp,
                         'col3': depth_per_cdp,
                         'col4': data_per_cdp})
                    temp_frame.to_csv(
                        fname, mode='a', index=False, sep=str(' '),
                        header=False)

        except Exception as inst:
            print(inst)
            print("Failed to export.")
