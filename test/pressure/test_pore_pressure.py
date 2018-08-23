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
    return np.full((10,), fill_value=100, dtype=np.float32)


@pytest.fixture()
def vel():
    return np.full((10,), fill_value=2112, dtype=np.float32)


def test__bowers(vel, obp):
    assert (ppp.bowers(vel, obp, 1, 1, 98, 0.5, 4000) == \
        np.full((10,), fill_value=64, dtype=np.float32)).all()

def test__bowers_varu(vel, obp):
    assert (np.array(
        ppp.bowers_varu(vel, obp, 3, 3, 98, 0.5, 4000,
                        buf=2, end_idx=6, end_buffer=2), dtype=np.float32) == \
        np.array([64]*3 + [99.88549805]*4 + [64]*3, dtype=np.float32)).all()


def test__eaton():
    assert ppp.eaton(2112, 2112, 500, 1000) == 500
