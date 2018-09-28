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
