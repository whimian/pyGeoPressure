# -*- coding: utf-8 -*-
"""
Test

Created on Aug. 30th 2018
"""

__author__ = "yuhao"

from pygeopressure.basic import Path
import json
import pytest
import pygeopressure as ppp
from pygeopressure.basic.survey import (
    create_survey_directory, DuplicateSurveyNameExeption)


@pytest.fixture()
def data_root(tmpdir):
    # create directory
    data_root = Path(str(tmpdir.mkdir("data_root")))
    survey_name = "F3"
    create_survey_directory(data_root, survey_name)
    return data_root


def test__survey(data_root):
    # test create survey directory
    survey_name = "F3"
    with pytest.raises(DuplicateSurveyNameExeption):
        create_survey_directory(data_root, survey_name)

    dir_F3 = data_root / survey_name
    dir_Seismics = data_root / survey_name / "Seismics"
    dir_Wellinfo = data_root / survey_name / "Wellinfo"
    dir_Surfaces = data_root / survey_name / "Surfaces"
    assert dir_F3.exists() is True
    assert dir_Seismics.exists() is True
    assert dir_Wellinfo.exists() is True
    assert dir_Surfaces.exists() is True

    with pytest.raises(Exception) as excinfo:
        ppp.Survey(dir_F3)
    assert "No survey setting file" in str(excinfo.value)
    # create survey file
    survey_file = dir_F3 / ".survey"
    survey_info = {
        "name": "F3",
        "inline_range": [200, 640, 20],
        "crline_range": [700, 1200, 20],
        "z_range": [400, 1100, 20, "T"],
        "point_A": [100, 300, 605835.516689, 6073556.38222],
        "point_B": [100, 1250, 629576.257713, 6074219.892946],
        "point_C": [750, 1250, 629122.546506, 6090463.168806]
    }
    with open(str(survey_file), 'w') as fl:
        json.dump(survey_info, fl)
    # create seismic definition
    seis_file = dir_Seismics / "poststack.seis"
    seis_info = {
        "path": "test/data/f3_sparse.sgy",
        "inline_range": [200, 640, 20],
        "z_range": [400, 1100, 20],
        "crline_range": [700, 1200, 20]
    }
    with open(str(seis_file), 'w') as fl:
        json.dump(seis_info, fl)
    survey = ppp.Survey(Path(str(dir_F3)))
    # survey.add_seismic()
    assert list(survey.seismics.keys()) == ['poststack']
