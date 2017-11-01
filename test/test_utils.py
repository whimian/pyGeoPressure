# -*- coding: utf-8 -*-
"""
Test

Created on Jun. 15th 2017
"""
__author__ = "yuhao"

import unittest
import numpy as np

from .context import pygeopressure as ppp


class UtilsTestSuite(unittest.TestCase):
    """
    Test Case for utils.py
    """
    def test_rmse(self):
        "test on rmse"
        a = np.arange(0, 10, 0.05)
        b = np.arange(0, 10, 0.05)
        self.assertEqual(ppp.nmse(a, b), 0)

if __name__ == '__main__':
    unittest.main()
