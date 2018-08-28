# -*- coding: utf-8 -*-
"""
Created on Aug. 27th 2018
"""
import pytest
import pygeopressure as ppp


def test__InlineIndex():
    assert ppp.InlineIndex(1).value == 1


def test__CrlineIndex():
    assert ppp.CrlineIndex(1).value == 1


def test__DepthIndex():
    assert ppp.DepthIndex(1.1).value == 1.1


def test_CdpIndex():
    assert ppp.CdpIndex((1, 2)).value == (1, 2)

    with pytest.raises(TypeError) as excinfo:
        ppp.CdpIndex(1)
    assert "Expected tuple, got <type 'int'>" in str(excinfo.value)
