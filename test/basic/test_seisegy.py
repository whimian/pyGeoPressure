# -*- coding: utf-8 -*-
"""
Test

Created on Aug. 30th 2018
"""

__author__ = "yuhao"

import pytest
import pygeopressure as ppp


def test__seisegy():
    seis_cube = ppp.SeiSEGY("test/data/f3_sparse.sgy")
    # test generators
    assert list(seis_cube.inlines()) == list(range(200, 641, 20))
    assert list(seis_cube.crlines())[-1] == 1200
    assert list(seis_cube.inline_crlines())[-1] == (640, 1200)
    assert list(seis_cube.depths())[-1] == 1100
    # test retrieve data
    first_test_cdp_data = seis_cube.data(ppp.CdpIndex((200, 700)))
    assert (seis_cube.data(ppp.InlineIndex(200))[0] == \
        first_test_cdp_data).all()
    assert (seis_cube.data(ppp.CrlineIndex(700))[0] == \
        first_test_cdp_data).all()
    assert seis_cube.data(ppp.DepthIndex(1100))[0][0] == \
        first_test_cdp_data[-1]
    assert seis_cube.valid_cdp((199, 400)) == (200, 400)
    assert str(seis_cube) == ("SeiSEGY(inl[200,640,20];crl[700,1200,20];"
                              "z[400.0,1100.0,20.0])")
