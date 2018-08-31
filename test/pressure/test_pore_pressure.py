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


def test__multivariate_virgin():
    assert (
        ppp.multivariate_virgin(
            20, 0.3, 0.6, 1000, 1000, 1000, 1000, 1) == 20100)


def test__invert_multivariate_virgin():
    assert (
        ppp.invert_multivariate_virgin(
            20100, 0.3, 0.6, 1000, 1000, 1000, 1000, 1) == 20)


def test__multivariate_unloading():
    assert (
        ppp.multivariate_unloading(
            20, 0.3, 0.6, 1000, 1000, 1000, 1000, 1, 1, 4000) == \
        ppp.multivariate_virgin(20, 0.3, 0.6, 1000, 1000, 1000, 1000, 1))


def test__invert_multivariate_unloading():
    assert (
        ppp.invert_multivariate_unloading(
            20100, 0.3, 0.6, 1000, 1000, 1000, 1000, 1, 1, 4000) == 20)


def test__pressure_multivariate():
    assert (
        ppp.pressure_multivariate(
            np.array([40]*10), np.array([2112]*10),
            np.array([0.3]*10), np.array([0.6]*10),
            1000, 1000, 1000, 1000, 1, 1, 4000, 4)[0] == 37.988)


def test__pressure_multivariate_varu():
    pres = ppp.pressure_multivariate_varu(
        np.array([40]*10), np.array([2112]*10),
        np.array([0.3]*10), np.array([0.6]*10),
        1000, 1000, 1000, 1000, 1, 1.5, 4000, 4, buf=1, end_idx=7, end_buffer=1)
    assert pres[0] == 37.988
    assert float("{:.4f}".format(pres[7])) == 38.5549
    assert pres[-1] == 37.988
