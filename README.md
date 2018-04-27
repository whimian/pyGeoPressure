<!-- # pyGeoPressure -->
<img src="docs/img/pygeopressure-logo.png" alt="Logo" height="240">

[![Anaconda-Server Badge](https://anaconda.org/whimian/pygeopressure/badges/version.svg)](https://anaconda.org/whimian/pygeopressure)
[![GitHub release](https://img.shields.io/github/tag/whimian/pyGeoPressure.svg?label=Release)](https://github.com/whimian/pyGeoPressure/releases)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/whimian/pyGeoPressure/blob/master/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/pygeopressure/badge/?version=latest)](http://pygeopressure.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/whimian/pyGeoPressure.svg?branch=master)](https://travis-ci.org/whimian/pyGeoPressure)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2f79d873803d4ef1a3c306603fcfd767)](https://www.codacy.com/app/whimian/pyGeoPressure?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=whimian/pyGeoPressure&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/whimian/pyGeoPressure/branch/master/graph/badge.svg)](https://codecov.io/gh/whimian/pyGeoPressure)

[![Waffle.io - Columns and their card count](https://badge.waffle.io/whimian/pyGeoPressure.svg?columns=all)](https://waffle.io/whimian/pyGeoPressure)

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

[**Survey**](pygeopressure/basic/survey.py): join seismic and wells.

[**SeisCube**](pygeopressure/basic/seiSQL.py): seismic velocity stored in sqlite db file.

[**Well**](pygeopressure/basic/well.py): Well with log data stored in pandas hdf5 file.

[**Log**](pygeopressure/basic/well_log.py): log data.

## Log curve tools

- Interpolation
- Smoothing
- Upscale
