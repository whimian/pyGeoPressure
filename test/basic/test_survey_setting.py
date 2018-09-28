# -*- coding: utf-8 -*-
"""
Test

Created on Feb. 22nd 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__author__ = "yuhao"

import pytest
import numpy as np
import pygeopressure as ppp

def test__survey_setting():
    survey = ppp.SurveySetting(ppp.ThreePoints("test/data/v2.survey"))
    assert tuple([int(a) for a in survey.line_2_coord(300, 800)]) == \
        (618191, 6078903)
    assert tuple(
        [int(a) for a in survey.coord_2_line(
            (618191.04009555, 6078903.52942556))]) == (300, 800)

    assert (
        np.array(
            survey.four_corner_on_canvas(400, 300)[0], dtype=np.float32) == \
        np.array(
            [45.88527452, 280., 274.11472548, 40.], dtype=np.float32)).all()
