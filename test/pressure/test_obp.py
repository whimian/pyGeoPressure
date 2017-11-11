# -*- coding: utf-8 -*-
"""
Created on Nov. 10th 2017
"""
import pytest
import numpy as np
import pygeopressure as ppp

@pytest.fixture(scope='module')
def rho():
    return np.full(10, 1.1)

def test_traugott(depth):
    assert (ppp.traugott(depth, 1, 1) == depth + 1.70).all()

def test_gardner(depth):
    assert (ppp.gardner(depth, 1, 1) == depth).all()

def test_overburden_pressure(depth, rho):
    assert (np.round(ppp.overburden_pressure(depth, rho, kelly_bushing=1, depth_w=1), 6) == \
            np.array([0., 0.009905, 0.020692, 0.031479, 0.042267, 0.053054,
                      0.063841, 0.074629, 0.085416, 0.096203])).all()

def test_obp_trace(rho):
    assert (np.round(ppp.obp_trace(rho, 1), 5) == \
        np.array([0.01078, 0.02156, 0.03234, 0.04312, 0.0539, 0.06468,
                  0.07546, 0.08624, 0.09702, 0.1078])).all()
