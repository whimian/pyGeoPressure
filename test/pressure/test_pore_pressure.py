# -*- coding: utf-8 -*-
"""
Created on Nov. 16th 2017
"""
import pytest
import numpy as np
import pygeopressure as ppp


def test__virgin_curve():
    assert ppp.virgin_curve(36, 98, 0.5) == 2112
    assert ppp.invert_virgin(2112, 98, 0.5) == 36


def test__unloading_curve():
    assert ppp.unloading_curve(36, 98, 0.5, 1, 4000) == 2112
    assert ppp.invert_unloading(2112, 98, 0.5, 1, 4000) == 36

@pytest.fixture()
def obp():
    return np.full((3,), fill_value=100)

@pytest.fixture()
def vel():
    return np.full((3,), fill_value=2112)

def test__bowers(vel, obp):
    assert (ppp.bowers(vel, obp, 1, 1, 98, 0.5, 4000) == \
        np.full((3,), fill_value=64)).all()
    # u = np.array([1,2,3])
    # assert (ppp.bowers_varu(vel, obp, u, 0, 98, 0.5, 4000, buffer=1) == \
    #     np.array([64, 64, 64])).all()

def test__eaton():
    assert ppp.eaton(2112, 2112, 500, 1000) == 500
