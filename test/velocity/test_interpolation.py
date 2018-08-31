# -*- coding: utf-8 -*-
"""
Created on Aug. 31st 2018
"""
import pytest
import numpy as np
import pygeopressure as ppp


def test__interp_DW():
    a = np.array([[2, 2, 2], [2, np.nan, 2], [2, 2, 2]])
    ppp.interp_DW(a)
    assert (a == np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]])).all()


def test__spline_1d():
    twt = np.array([1000, 2000, 3000, 4000])
    vel = np.array([1500, 1800, 2200, 2100])
    assert (np.array(ppp.spline_1d(twt, vel, 500)[-1]) == \
        np.array([1500.0, 1600.0, 1800.0, 2025.0, 2200.0, 2250.0])).all()
