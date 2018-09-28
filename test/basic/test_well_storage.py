# -*- coding: utf-8 -*-
"""
Created on Aug. 31st 2018
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
import numpy as np
import pandas as pd
import pygeopressure as ppp
from pygeopressure.basic import Path


def test__well_storage(tmpdir, pseudo_las_file):
    temp_dir = Path(str(tmpdir))
    temp_hdf5 = temp_dir / "temp_well_storage.h5"
    storage = ppp.WellStorage(str(temp_hdf5))
    # add well
    pseudo_las_data = ppp.LasData(str(pseudo_las_file))
    df = pseudo_las_data.data_frame
    storage.add_well("test_well", df)
    assert storage.wells == ['test_well']
    # logs_into_well
    new_df = df[['Depth(m)']].copy()
    new_df.loc[:, "Some_prop(m/s)"] = 1
    storage.logs_into_well('test_well', new_df)
    assert u'Some_prop(m/s)' in storage.get_well_data('test_well').columns

    with pytest.raises(ValueError) as duplicate_log_name_error:
        storage.logs_into_well('test_well', new_df)
    assert "Duplicate logs:" in duplicate_log_name_error.exconly()

    # update well
    storage.update_well("test_well", df)
    assert u'Some_prop(m/s)' not in storage.get_well_data('test_well').columns
    # remove well
    storage.remove_well("test_well")
    assert storage.wells == []
    with pytest.raises(KeyError) as nowell_error:
        storage.remove_well("abc_well")
    assert "No well named abc_well" in nowell_error.exconly()
    # get data
    with pytest.raises(KeyError) as nowell_error:
        storage.get_well_data("abc_well")
    assert "No well named abc_well" in nowell_error.exconly()
