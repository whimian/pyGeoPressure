# -*- coding: utf-8 -*-
"""
Test

Created on Jun. 15th 2017
"""
__author__ = "yuhao"

import unittest

from .context import pygeopressure as ppp


class WellTestSuite(unittest.TestCase):
    """Basic test cases."""
    def test_void_log(self):
        "test on boolean value of Log object"
        log = ppp.Log()
        self.assertFalse(log)

if __name__ == '__main__':
    unittest.main()
