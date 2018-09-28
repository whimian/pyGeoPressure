# -*- coding: utf-8 -*-
"""
Created on Nov. 9th 2017
"""
import pytest
import numpy as np
import pygeopressure

@pytest.fixture()
def real_well_log():
    return pygeopressure.Log("test/data/seudo_las.las")


def test__log_range(real_well_log):
    assert real_well_log.start == 374.6
    assert real_well_log.stop == 998.9
    assert real_well_log.top == 0
    assert real_well_log.bottom == 1000
    assert real_well_log.start_idx == 3746
    assert real_well_log.stop_idx == 9990


def test__log_data(real_well_log):
    assert real_well_log.name == "vel_unk"
    assert real_well_log.prop_type == "VEL"
    assert real_well_log.depth[6762] == 676.2
    assert real_well_log.data[6762] == 2000.262329
    assert real_well_log.get_depth_idx(676.2) == 6762
    assert real_well_log.get_data([676.2])[0] == 2000.262329


def test__log_object(real_well_log):
    assert real_well_log == real_well_log
    assert str(real_well_log) == "Well_Log:vel_unk(Velocity[Meter/second])"


# def test__log_plot(real_well_log):
#     ax = real_well_log.plot()
#     line = ax.get_lines()[0]
#     x_plot, _ = line.get_xydata().T
#     np.testing.assert_array_equal(x_plot, real_well_log.data)


def test_log_smooth(real_well_log):
    smooth_log = pygeopressure.smooth_log(real_well_log)
    assert float("{:.3f}".format(smooth_log.data[6762])) == 1993.915


@pytest.fixture
def void_well_log():
    return pygeopressure.Log()


def test__log_void(void_well_log):
    assert not void_well_log
    assert void_well_log.name == "unk"
    assert void_well_log.prop_type is None
