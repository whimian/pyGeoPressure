# -*- coding: utf-8 -*-
"""
Created on Aug. 28th 2018
"""
import os
import pytest
import pygeopressure as ppp


def test__Horizon(tmpdir):
    p = tmpdir.mkdir("sub").join("horizon.txt")
    p.write("inline\tcrline\tz\n1\t1\t200\n1\t2\t300\n")

    hor = ppp.Horizon(str(p))
    hor.horizon_name = "hor_A"
    assert hor.get_cdp((1, 1)) == 200
    assert str(hor) == "Horizon Object: hor_A"
    assert repr(hor) == "Horizon Object: hor_A"
