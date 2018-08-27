# -*- coding: utf-8 -*-
"""
Created on Aug. 23rd 2018
"""
import pytest
import numpy as np
import pygeopressure as ppp


@pytest.fixture()
def twt():
    return np.array([1000, 2000, 3000, 4000])


@pytest.fixture()
def vel():
    return np.array([1500, 1800, 2200, 2100])


def test__normal():
    assert ppp.normal(1, 1, 1) == 1


def test__normal_dt():
    assert ppp.normal_dt(1, 1, 1) == 0


def test__slotnick():
    ppp.set_v0(1524)
    assert ppp.slotnick(1, 1) == 1525
