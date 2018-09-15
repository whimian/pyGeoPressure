# -*- coding: utf-8 -*-
"""
Created on Nov. 15th 2017
"""
import pytest
import pygeopressure


@pytest.fixture()
def real_well():
    return pygeopressure.Well(json_file='test/data/FW1.json')


def test__well_properties(real_well):
    assert real_well.logs == [
        'Velocity', 'Shale_Volume', 'Overburden_Pressure']
    assert real_well.unit_dict == {
        'Depth': 'm',
        'Overburden_Pressure': 'MegaPascal',
        'Shale_Volume': 'Fraction',
        'Velocity': 'Meter/Second'}

@pytest.fixture()
def measured_log():
    temp_log = pygeopressure.Log()
    temp_log.depth = [4118.5]
    temp_log.data = [60.605]
    return temp_log

def test__well_get_pressure(real_well, measured_log):
    assert real_well.get_pressure_measured(ref='sea') == measured_log
    assert real_well.get_dst(ref='sea') == measured_log
    assert real_well.get_wft(ref='sea') == measured_log
    assert real_well.get_emw(ref='sea') == measured_log
    assert real_well.get_loading_pressure(ref='sea') == measured_log
    assert real_well.get_unloading_pressure(ref='sea') == measured_log
