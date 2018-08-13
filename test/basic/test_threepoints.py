# -*- coding: utf-8 -*-
"""
Test

Created on Feb. 22nd 2018
"""
from __future__ import unicode_literals

__author__ = "yuhao"

import pytest
import pygeopressure as ppp

def test__threepoints():
    v1 = ppp.ThreePoints("test/data/v1.survey")
    v2 = ppp.ThreePoints("test/data/v2.survey")

    assert v1.startInline == v2.startInline
    assert v1.endInline == v2.endInline
    assert v1.stepInline == v2.stepInline
    assert v1.startCrline == v2.startCrline
    assert v1.endCrline == v2.endCrline
    assert v1.stepCrline == v2.stepCrline
    assert v1.startDepth == v2.startDepth
    assert v1.endDepth == v2.endDepth
    assert v1.stepDepth == v2.stepDepth
    assert v1.inline_A == v2.inline_A
    assert v1.crline_A == v2.crline_A
    assert v1.east_A == v2.east_A
    assert v1.north_A == v2.north_A
    assert v1.inline_B == v2.inline_B
    assert v1.crline_B == v2.crline_B
    assert v1.east_B == v2.east_B
    assert v1.north_B == v2.north_B
    assert v1.inline_C == v2.inline_C
    assert v1.crline_C == v2.crline_C
    assert v1.east_C == v2.east_C
    assert v1.north_C == v2.north_C
