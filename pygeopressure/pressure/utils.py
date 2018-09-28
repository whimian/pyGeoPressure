# -*- coding: utf-8 -*-
"""
some utilities regarding pressure calculation
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import str, open

__author__ = "yuhao"

import json
from collections import OrderedDict
from pygeopressure.basic.seisegy import SeiSEGY
from . import Path


def create_seis(name, like):
    """
    Parameters
    ----------
    name : str
    like : SeiSEGY
    """
    # create output segy file
    input_path = Path(like.segy_file)
    output_path = input_path.parent / "{}.sgy".format(name)
    return SeiSEGY(str(output_path), like=str(like.segy_file))


def create_seis_info(segy_object, name):
    """
    Parameters
    ----------
    segy_object : SeiSEGY
    name : str
    """
    file_path = Path(segy_object.segy_file).absolute()
    parent_folder = file_path.parent
    dict_info = OrderedDict([
        ("path", str(file_path)),
        ("inDepth", segy_object.inDepth),
        ("Property_Type", segy_object.property_type),
        ("inline_range", [segy_object.startInline,
                          segy_object.endInline,
                          segy_object.stepInline]),
        ("crline_range", [segy_object.startCrline,
                          segy_object.endCrline,
                          segy_object.stepCrline]),
        ("z_range", [segy_object.startDepth,
                     segy_object.endDepth,
                     segy_object.stepDepth])])
    with open(str(parent_folder / "{}.seis".format(name)), 'w') as fl:
        json.dump(dict_info, fl, indent=4)
