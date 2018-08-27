# -*- coding: utf-8 -*-
"""
Created on Aug. 27th 2018
"""
import pytest
import numpy as np
import pygeopressure as ppp


def test__normal():
    assert ppp.normal(1, 1, 1) == 1


def test__normal_dt():
    assert ppp.normal_dt(1, 1, 1) == 0


def test__slotnick():
    ppp.set_v0(1524)
    assert ppp.slotnick(1, 1) == 1525
