# -*- coding: utf-8 -*-
"""
conversion of gslib files
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import range
from future.utils import native

__author__ = "yuhao"


import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from .seisegy import SeiSEGY, InlineIndex

from . import Path


def gslib_to_od(gslib_file, od_file):
    """
    Convert gslib file to opendtect file
    """
    with open(gslib_file, 'r') as fl:
        info = fl.readline().strip('\n')
        header_len = int(fl.readline().strip('\n'))
        column_name = [fl.readline().strip('\n') for i in range(header_len)]
    df = pd.read_csv(
        gslib_file, sep=str(' '), header=None, names=column_name,
        index_col=False, skiprows=header_len+2)
    df.groupby(['X', 'Y'])[column_name[-1]].apply(list).to_csv(
        od_file, sep='\t')


def merge_gslib(gslib_files, output_file):
    df_list = []
    property_name = []
    for gslib_f in gslib_files:
        with open(gslib_f, 'r') as fl:
            info = fl.readline().strip('\n')
            header_len = int(fl.readline().strip('\n'))
            column_name = [fl.readline().strip('\n') for i in range(header_len)]
            property_name.append(column_name[-1])

        df_list.append(pd.read_csv(
            gslib_f, sep=str(' '), header=None, names=column_name,
            index_col=False, skiprows=header_len+2))
    new_df = df_list[0]
    for df in df_list[1:]:
        new_df = pd.merge(new_df, df, how='left', on = ['x', 'y', 'z'])
    with open(output_file, 'w') as out_fl:
        out_fl.write("Merged by pyGeoPressure\n")
        out_fl.write("{}\n".format(len(property_name)+3))
        out_fl.write("x\n")
        out_fl.write("y\n")
        out_fl.write("z\n")
        for prop in property_name:
            out_fl.write("{}\n".format(prop))
    new_df.to_csv(output_file, sep=' ', mode='a', header=False, index=False)


class Gslib(object):
    def __init__(self):
        self.info = None
        self.header_len = None
        self.column_names = None

    def from_gslib(self, gslib_file, na=None):
        with open(gslib_file, 'r') as fl:
            self.info = fl.readline().strip('\n')
            self.header_len = int(fl.readline().strip('\n'))
            self.column_names = [fl.readline().strip('\n') \
                for i in range(self.header_len)]
            self.dataframe = pd.read_csv(
                gslib_file, sep=str(r"\s+|\t+|\s+\t+|\t+\s+"), header=None,
                names=self.column_names, index_col=False,
                skiprows=self.header_len+2, na_values=na, engine='python')
            # df.groupby(['X', 'Y'])[column_names[-1]].apply(list).to_csv(
            #     od_file, sep='\t')

    def to_grid(self, filename, shape=None):
        with open(filename, 'w') as out_fl:
            out_fl.write("{}\n".format(self.info))
            out_fl.write("1\n")
            out_fl.write("{}\n".format(self.column_names[-1]))
        pd.DataFrame(
            {self.column_names[-1]: self.dataframe[self.column_names[-1]].\
                values.reshape(shape).flatten(order="F")}).to_csv(
                    filename, sep=' ', mode='a', header=False, index=False)

    def to_od(self, od_file, shape, startInline, stepInline, startCrline, stepCrline):
        inlines, crlines, _ = np.meshgrid(
            np.arange(startInline, startInline+shape[0]*stepInline, stepInline),
            np.arange(startCrline, startCrline+shape[1]*stepCrline, stepCrline),
            np.arange(0, shape[2]), indexing='ij')
        for i, cn in enumerate(tqdm(self.column_names, ascii=True)):
            # attr = self.dataframe[self.column_names[0]].values
            attr = self.dataframe[cn].values
            pd.DataFrame({
                'x' : inlines.flatten(),
                'y': crlines.flatten(),
                'attr': attr.reshape(shape, order="F").flatten()
            }).groupby(['x', 'y'])['attr'].apply(list).to_csv(od_file+"_{}.txt".format(i), sep='\t')
            # pd.DataFrame({
            #     'x' : inlines.flatten(),
            #     'y': crlines.flatten(),
            #     'attr': attr.reshape(shape, order="F").flatten()
            # }).groupby(['x', 'y'])['attr'].apply(list).to_csv(od_file, sep='\t')


    def to_segy(self, output_folder, like, shape):
        Path(native(output_folder)).mkdir(parents=True, exist_ok=True)
        for i, cn in enumerate(tqdm(self.column_names, ascii=True)):
            attr = self.dataframe[cn].values.reshape(shape, order="F")
            segy = SeiSEGY(output_folder+"/{}.sgy".format(cn), like=like)
            for inl, attr_slice in zip(list(segy.inlines()), attr):
                segy.update(InlineIndex(inl), attr_slice)

        # self.dataframe[self.column_names[0]].values.reshape(shape).flatten(order="C")
        # self.dataframe.groupby(['x', 'y'])[self.column_names[-1]].\
        #     apply(list).to_csv(od_file, sep='\t')
# .to_csv(od_file, sep='\t')

class Grid(Gslib):
    def __init__(self):
        pass

    def to_od(self):
        pass

    def to_segy(self):
        pass


class PointSet(Gslib):
    def __init__(self):
        pass
