# Pore Pressure Prediction

[![GitHub version](https://badge.fury.io/gh/whimian%2FPorePressurePrediction.svg)](https://badge.fury.io/gh/whimian%2FPorePressurePrediction)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/whimian/PorePressurePrediction/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/whimian/PorePressurePrediction.svg?branch=master)](https://travis-ci.org/whimian/PorePressurePrediction)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c6f8b9c3fb7945469c110bd155bfe649)](https://www.codacy.com/app/whimian/PorePressurePrediction?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=whimian/PorePressurePrediction&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/porepressureprediction/badge/?version=latest)](http://porepressureprediction.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/whimian/PorePressurePrediction/branch/master/graph/badge.svg)](https://codecov.io/gh/whimian/PorePressurePrediction)

Tools for pore pressure prediction using well log data and seismic velocity data.

Seismic velocity data are stored using sqlite, and well log data are stored in pandas hdf5 file.

# Features

1. Hydrostatic Pressure Calculation
2. Overburden (or Lithostatic) Pressure Calculation
3. Eaton's method
4. Bowers' method

# Data I/O

**Well log**:

- las file

- pseudo-las file without proper header

**Seismic Velocity**:

- Opendtect ascii file

- SEG-Y file (require [segpy](https://github.com/sixty-north/segpy))

# Basic Classes

[**Survey**](porepressureprediction/basic/survey.py): join seismic and wells.

[**SeisCube**](porepressureprediction/basic/seiSQL.py): seismic velocity stored in sqlite db file.

[**Well**](porepressureprediction/basic/well.py): Well with log data stored in pandas hdf5 file.

[**Log**](porepressureprediction/basic/well_log.py): log data.

## Log curve tools

- Interpolation
- Smoothing
- Upscale
