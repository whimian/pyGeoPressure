.. Pore Pressure Prediction documentation master file, created by
   sphinx-quickstart on Thu Oct 26 10:58:51 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pore Pressure Prediction
====================================================

.. image:: https://badge.fury.io/gh/whimian%2FPorePressurePrediction.svg
    :target: https://badge.fury.io/gh/whimian%2FPorePressurePrediction
    :alt: Github
.. image:: https://travis-ci.org/whimian/PorePressurePrediction.svg?branch=master
    :target: https://travis-ci.org/whimian/PorePressurePrediction
    :alt: Travis-CI
.. image:: https://api.codacy.com/project/badge/Grade/c6f8b9c3fb7945469c110bd155bfe649
    :target: https://www.codacy.com/app/whimian/PorePressurePrediction?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=whimian/PorePressurePrediction&amp;utm_campaign=Badge_Grade
    :alt: Codacy
.. image:: https://readthedocs.org/projects/porepressureprediction/badge/?version=latest
    :target: http://porepressureprediction.readthedocs.io/en/latest/?badge=latest
    :alt: ReadtheDocs

.. toctree::
    :hidden:
    :maxdepth: 2
    :caption: Contents:
    abc

Tools for pore pressure prediction using well log data and seismic velocity data.

Seismic velocity data are stored using sqlite, and well log data are stored in pandas hdf5 file.

Features
--------

1. Hydrostatic Pressure Calculation
2. Overburden (or Lithostatic) Pressure Calculation
3. Eaton's method
4. Bowers' method

Data I/O
--------

**Well log**:

- las file

- pseudo-las file without proper header

**Seismic Velocity**:

- Opendtect ascii file

- SEG-Y file (require [segpy](https://github.com/sixty-north/segpy))


