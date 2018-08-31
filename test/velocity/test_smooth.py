# -*- coding: utf-8 -*-
"""
Created on Aug. 31st 2018
"""
import pytest
import numpy as np
import pygeopressure as ppp


def test__smooth():
    with pytest.raises(ValueError) as dimension_error:
        ppp.smooth(np.array([[1]*20, [3]*20]))
    assert "smooth only accepts 1" in str(dimension_error.value)

    with pytest.raises(ValueError) as window_error:
        ppp.smooth(np.array([1, 2]))
    assert "Input vector needs to be bigger" in str(window_error.value)

    with pytest.raises(ValueError) as method_error:
        ppp.smooth(np.array([1]*20), window='random')
    assert "Window is on of 'flat', 'hanning'" in str(method_error.value)

    assert (ppp.smooth(np.array([1, 2]), window_len=2) == np.array([1, 2])).all()


def test__smooth_2d():
    assert ppp.smooth_2d(np.array([[1, 1, 1], [1, 2, 1], [1, 1, 1]]))[1][1] ==\
        1


def test__smooth_trace():
    assert ppp.smooth_trace(np.array([1, 1, 1, 2, 1, 1]), window=8)[3] == 1
