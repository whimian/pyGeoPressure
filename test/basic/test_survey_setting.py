# -*- coding: utf-8 -*-
"""
Test

Created on Feb. 22nd 2018
"""
from __future__ import unicode_literals

__author__ = "yuhao"

import pytest
import pygeopressure as ppp

def test__survey_setting():
    survey = ppp.SurveySetting(ppp.ThreePoints("test/data/v2.survey"))
