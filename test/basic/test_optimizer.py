# -*- coding: utf-8 -*-
"""
Created on Sep 16 2018
"""
from __future__ import unicode_literals

import pytest
import pygeopressure

from pygeopressure.basic.optimizer import (
    optimize_bowers_virgin, optimize_eaton, optimize_nct)

from builtins import str

@pytest.fixture()
def real_well():
    return pygeopressure.Well(json_file='test/data/FW1.json')


def test__optimize_bowers_virgin(real_well):
    a, b, err = optimize_bowers_virgin(
        real_well, 'Velocity', 'Overburden_Pressure', 'T12', 'T20',
        pres_log='loading', mode='both')
    assert float("{:.4f}".format(a)) == 121.3322
    assert float("{:.4f}".format(b)) == 0.8358
    assert float("{:.4f}".format(err)) == 0.1688


def test__optimize_eaton(real_well):
    a = real_well.params['nct']['a']
    b = real_well.params['nct']['b']
    n = optimize_eaton(real_well, "Velocity", "Overburden_Pressure",
                       a, b, pres_log="loading")
    assert float("{:.4f}".format(n)) == 3.9799


def test__optimize_nct(real_well):
    vel_log = real_well.get_log("Velocity")
    a, b = optimize_nct(vel_log, 1200, 2000)
    assert float("{:.4f}".format(a)) == -7.7037
    assert float("{:.7f}".format(b)) == 0.0001281
