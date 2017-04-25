# Pore Pressure Prediction

Tools for pore pressure prediction using well log data and seismic velocity data.

Seismic velocity data are stored using sqlite, and well log data are stored in pandas hdf5 file.

# Features

1. Hydrostatic Pressure Calculation
2. Overburden (or Lithostatic) Pressure Calculation
3. Eaton's method
4. Bowers' method

# Data I/O

**Well log**: las file

**Seismic Velocity**: Opendtect ascii file

# Basic Classes

[**Survey**](porepressureprediction/basic/survey.py): join seismic and wells.

[**SeisCube**](porepressureprediction/basic/seiSQL.py): seismic velocity stored in sqlite db file.

[**Well**](porepressureprediction/basic/well.py): Well with log data stored in pandas hdf5 file.

[**Log**](porepressureprediction/basic/well_log.py): log data.