# -*- coding: utf-8 -*-
"""
Created on Aug. 28th 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import pytest
import pygeopressure as ppp


def test__LasData(pseudo_las_file):
    pseudo_las_data = ppp.LasData(str(pseudo_las_file))
    _ = pseudo_las_data.data_frame
    assert pseudo_las_data.file_type == "pseudo-las"
    assert pseudo_las_data.logs == ['Velocity', 'Shale_Volume', 'Overburden_Pressure']
    assert pseudo_las_data.units == ['Meter/Second', 'Fraction', 'MegaPascal']
