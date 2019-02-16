# -*- coding: utf-8 -*-
"""
some utilities
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import range

__author__ = "yuhao"

import sys

import numpy as np
import pandas as pd

PY_VER = sys.version_info.major

if PY_VER == 2:
    from functools import update_wrapper
    from singledispatch import singledispatch
else:
    from functools import singledispatch, update_wrapper


def rmse(measure, predict):
    """
    Relative Root-Mean-Square Error

    with RMS(y - y*) as nominator, and RMS(y) as denominator
    """
    delta = np.sqrt(np.mean((measure - predict)**2))
    denominator = np.sqrt(np.mean(measure**2))
    return delta/denominator

def nmse(measure, predict):
    """
    Normalized Root-Mean-Square Error

    with RMS(y - y*) as nominator, and MEAN(y) as denominator
    """
    delta = np.sqrt(np.mean((measure - predict)**2))
    denominator = np.mean(measure)
    return delta/denominator

def split_sequence(sequence, length):
    """
    Split a sequence into fragments with certain length
    """
    n_seq = len(sequence)
    for i in range(0, n_seq, length):
        yield sequence[i: i+length]


def methdispatch(func):
    dispatcher = singledispatch(func)
    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)
    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper


def pick_sparse(a_array, n):
    """
    Pick n equally spaced samples from array

    Parameters
    ----------
    a_array : 1-d ndarray
    n : int
        number of samples to pick
    """
    length = a_array.shape[0]
    if length < n:
        raise Exception("length of array smaller than n")
    step = length // (n - 1)
    if step == 0:
        step = 1
    new_list = []
    for i in range(0, n, step):
        new_list.append(a_array[i])
    new_array = a_array[::step]
    if length % (n - 1) != 0:
        return np.append(new_array, [a_array[-1]])
    else:
        return new_array


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
        new_df  = pd.merge(new_df, df, how='left', on = ['x', 'y', 'z'])
    with open(output_file, 'w') as out_fl:
        out_fl.write("Merged by pyGeoPressure\n")
        out_fl.write("{}\n".format(len(property_name)+3))
        out_fl.write("x\n")
        out_fl.write("y\n")
        out_fl.write("z\n")
        for prop in property_name:
            out_fl.write("{}\n".format(prop))
    new_df.to_csv(output_file, sep='\t', mode='a', header=False, index=False)
