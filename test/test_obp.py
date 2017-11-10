# -*- coding: utf-8 -*-
"""
Created on Nov. 10th 2017
"""
import pytest
import numpy as np
import pygeopressure as ppp

@pytest.fixture(scope="session", autouse=True)
def depth():
    return np.arange(10)

def test_traugott(depth):
    assert (ppp.traugott(depth, 1, 1) == depth + 1.70).all()
