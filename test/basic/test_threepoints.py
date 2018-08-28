# -*- coding: utf-8 -*-
"""
Test

Created on Feb. 22nd 2018
"""
from __future__ import unicode_literals

__author__ = "yuhao"

import json
import pytest
import pygeopressure as ppp
from pygeopressure.basic.threepoints import (
    Invalid_threepoints_Exception,
    Not_threepoints_v1_Exception,
    Not_threepoints_v2_Exception)


def test__threepoints():
    # init with file
    v1 = ppp.ThreePoints("test/data/v1.survey")
    v2 = ppp.ThreePoints("test/data/v2.survey")
    # init with dict
    with open("test/data/v1.survey", 'r') as fl:
        dict_survey = json.load(fl)
    _ = ppp.ThreePoints(dict_survey)
    # test wrong version
    dict_survey.pop('inline')
    with pytest.raises(Invalid_threepoints_Exception) as excinfo:
        _ = ppp.ThreePoints(dict_survey)
    assert "Not valid three points file" in str(excinfo.value)
    # test None json file
    with pytest.raises(Exception) as excinfo:
        _ = ppp.ThreePoints()
    assert "json_file is None" in str(excinfo.value)
    # test properties
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
