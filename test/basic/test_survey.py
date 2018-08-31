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

# def test__survey():
#     survey = ppp.SurveySetting(ppp.ThreePoints("test/data/v2.survey"))
#     assert tuple([int(a) for a in survey.line_2_coord(300, 800)]) == \
#         (618191, 6078903)
#     assert tuple(
#         [int(a) for a in survey.coord_2_line(
#             (618191.04009555, 6078903.52942556))]) == (300, 800)

# @pytest.fixture(autouse=True)
# def dir_F3(tmpdir):
#     return tmpdir.mkdir("F3")
    # dir_Seismics = tmpdir.mkdir("F3/Seismics")
    # dir_Wellinfo = tmpdir.mkdir("F3/Wellinfo")
    # dir_Surfaces = tmpdir.mkdir("F3/Surfaces")

# @pytest.fixture(scope='session')
# def dir_F3(tmpdir_factory):
#     # create directory
#     dir_F3 = tmpdir_factory.mktemp("F3")
#     # base = tmpdir_factory.get
#     dir_Seismics = tmpdir_factory.mktemp("F3/Seismics")
#     dir_Wellinfo = tmpdir_factory.mktemp("F3/Wellinfo")
#     dir_Surfaces = tmpdir_factory.mktemp("F3/Surfaces")
#     return dir_F3

def test__survey(tmpdir):
    # test create survey directory
    root_dir = Path(str(tmpdir))
    survey_name = "F3"
    create_survey_directory(root_dir, survey_name)
    with pytest.raises(DuplicateSurveyNameExeption):
        create_survey_directory(root_dir, survey_name)

    dir_F3 = root_dir / survey_name
    dir_Seismics = root_dir / survey_name / "Seismics"
    dir_Wellinfo = root_dir / survey_name / "Wellinfo"
    dir_Surfaces = root_dir / survey_name / "Surfaces"
    assert dir_F3.exists() is True
    assert dir_Seismics.exists() is True
    assert dir_Wellinfo.exists() is True
    assert dir_Surfaces.exists() is True

    with pytest.raises(Exception) as excinfo:
        ppp.Survey(Path(str(dir_F3)))
    assert "No survey setting file" in str(excinfo.value)
    # create survey file
    survey_file = dir_F3 / ".survey"
    survey_info = {
        "name": "F3",
        "inline_range": [200, 650, 2],
        "crline_range": [700, 1200, 2],
        "z_range": [400, 1100, 4, "T"],
        "point_A": [100, 300, 605835.516689, 6073556.38222],
        "point_B": [100, 1250, 629576.257713, 6074219.892946],
        "point_C": [750, 1250, 629122.546506, 6090463.168806]
    }
    with open(str(survey_file), 'w') as fl:
        json.dump(survey_info, fl)

    ppp.Survey(Path(str(dir_F3)))
