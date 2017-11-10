# -*- coding: utf-8 -*-
"""
Created on Nov. 10th 2017
"""
import pygeopressure as ppp


def test_traugott(depth):
    assert (ppp.traugott(depth, 1, 1) == depth + 1.70).all()
