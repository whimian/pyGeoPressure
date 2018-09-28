# -*- coding: utf-8 -*-
"""
Created on Aug. 23rd 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
import numpy as np
import pygeopressure as ppp


@pytest.fixture()
def twt():
    return np.array([1000, 2000, 3000, 4000])


@pytest.fixture()
def vel():
    return np.array([1500, 1800, 2200, 2100])


def test__rms_int(twt, vel):
    assert (vel == ppp.rms2int(twt, ppp.int2rms(twt, vel))).all()


def test__avg_int(twt, vel):
    assert (vel == ppp.avg2int(twt, ppp.int2avg(twt, vel))).all()


def test_time2depth(twt, vel):
    _, new_vel = ppp.twt2depth(twt, vel, vel, stepDepth=500)
    assert new_vel[0] == vel[0]
