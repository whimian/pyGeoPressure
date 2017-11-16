# -*- coding: utf-8 -*-
"""
Test

Created on Jun. 15th 2017
"""
__author__ = "yuhao"

import pytest
import numpy as np
import pygeopressure as ppp

@pytest.fixture()
def array_for_test():
    return np.arange(0, 10, 0.05)

def test__rmse(array_for_test):
    assert ppp.rmse(array_for_test, array_for_test) == 0


def test__nmse(array_for_test):
    assert ppp.nmse(array_for_test, array_for_test) == 0


def test__split_sequence():
    sequence = [1] * 9
    length = 2
    output = [[1, 1]] * 4 + [[1]]
    assert list(ppp.basic.utils.split_sequence(sequence, length)) ==\
        output
