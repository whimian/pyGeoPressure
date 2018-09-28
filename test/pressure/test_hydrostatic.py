# -*- coding: utf-8 -*-
"""
Created on Nov. 9th 2017
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pygeopressure as ppp


def test_hydrostatic(depth):
    assert (ppp.hydrostatic_pressure(depth) == \
        np.array([0., 0.00980665, 0.0196133, 0.02941995, 0.0392266,
                  0.04903325, 0.0588399, 0.06864655, 0.0784532,
                  0.08825985])).all()
    assert (np.round(ppp.hydrostatic_trace(depth), 6) == \
        np.array([0., 0.009898, 0.019796, 0.029694, 0.039592, 0.04949,
                  0.059388, 0.069286, 0.079184, 0.089082])).all()
