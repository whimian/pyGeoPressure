<!-- # pyGeoPressure -->
<img src="docs/img/pygeopressure-logo.png" alt="Logo" height="240">

[![PyPI version](https://badge.fury.io/py/pyGeoPressure.svg)](https://badge.fury.io/py/pyGeoPressure)
[![GitHub release](https://img.shields.io/github/tag/whimian/pyGeoPressure.svg?label=Release)](https://github.com/whimian/pyGeoPressure/releases)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/whimian/pyGeoPressure/blob/master/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/pygeopressure/badge/?version=latest)](http://pygeopressure.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/whimian/pyGeoPressure.svg?branch=master)](https://travis-ci.org/whimian/pyGeoPressure)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2f79d873803d4ef1a3c306603fcfd767)](https://www.codacy.com/app/whimian/pyGeoPressure?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=whimian/pyGeoPressure&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/whimian/pyGeoPressure/branch/master/graph/badge.svg)](https://codecov.io/gh/whimian/pyGeoPressure)
[![Waffle.io - Columns and their card count](https://badge.waffle.io/whimian/pyGeoPressure.svg?columns=all)](https://waffle.io/whimian/pyGeoPressure)

A Python package for pore pressure prediction using well log data and seismic velocity data.

# Features

1. Hydrostatic Pressure Calculation
2. Overburden (or Lithostatic) Pressure Calculation
3. Eaton's method and Parameter Optimization (Well log)
4. Eaton's method and Parameter Optimization (Seismic Velocity)
5. Bowers' method and Parameter Optimization (Well log)
6. Bowers' method and Parameter Optimization (Seismic Velocity)
7. Multivariate method and Parameter Optimization (Well log)

# Getting Started

## Installation

`pyGeoPressure` is on `PyPI`:

```bash
pip install pygeopressure
```

## Example

### Pore Pressure Prediction using well log data

```python
import pygeopressure as ppp

survey = ppp.Survey("CUG")

well = survey.wells['CUG1']

a, b = ppp.optimize_nct(well.get_log("Velocity"),
                        well.params['horizon']["T16"],
                        well.params['horizon']["T20"])
n = ppp.optimize_eaton(well, "Velocity", "Overburden_Pressure", a, b)

pres_eaton_log = well.eaton(np.array(well.get_log("Velocity").data), n)

fig, ax = plt.subplots()
ax.invert_yaxis()

pres_eaton_log.plot(ax, color='blue')
well.get_log("Overburden_Pressure").plot(ax, 'g')
ax.plot(well.hydrostatic, well.depth, 'g', linestyle='--')
well.plot_horizons(ax)
```

<img src="docs/img/readme_example.svg" alt="Logo" height="600">

# Documentation

Read the documentaion for detailed explanations, tutorials and references:
https://pygeopressure.readthedocs.io/en/latest/

# Contribute

- Issue Tracker: https://github.com/whimian/pyGeoPressure/issues
- Source Code: https://github.com/whimian/pyGeoPressure

# License

The project is licensed under the MIT license, see the file [LICENSE](<https://github.com/whimian/pyGeoPressure/blob/master/LICENSE>) for details.
