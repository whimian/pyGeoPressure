# -*- coding: utf-8 -*-
"""
class for survey index definition

created on Jun 10th 2017
"""
__author__ = "yuhao"


class SurveyIndex(object):
    def __init__(self, value):
        self.value = int(value)

class InlineIndex(SurveyIndex):
    pass

class CrlineIndex(SurveyIndex):
    pass

class DepthIndex(SurveyIndex):
    def __init__(self, value):
        self.value = value

class CdpIndex(SurveyIndex):
    def __init__(self, cdp):
        try:
            self.inline, self.crline = [int(_) for _ in cdp]
            self.value = (self.inline, self.crline)
        except TypeError as inst:
            print(inst)
