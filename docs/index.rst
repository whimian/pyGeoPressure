.. Pore Pressure Prediction documentation master file, created by
   sphinx-quickstart on Thu Oct 26 10:58:51 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========================
Pore Pressure Prediction
========================

.. image:: https://img.shields.io/github/tag/whimian/pyGeoPressure.svg?label=Release
    :target: https://github.com/whimian/pyGeoPressure/releases
    :alt: Releases

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg
    :target: https://github.com/whimian/pyGeoPressure/blob/master/LICENSE
    :alt: License

.. image:: https://travis-ci.org/whimian/pyGeoPressure.svg?branch=master
    :target: https://travis-ci.org/whimian/pyGeoPressure
    :alt: Travis-CI

.. image:: https://api.codacy.com/project/badge/Grade/2f79d873803d4ef1a3c306603fcfd767
    :target: https://www.codacy.com/app/whimian/pyGeoPressure?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=whimian/pyGeoPressure&amp;utm_campaign=Badge_Grade
    :alt: Codacy

.. image:: https://readthedocs.org/projects/pygeopressure/badge/?version=latest
    :target: http://pygeopressure.readthedocs.io/en/latest/?badge=latest
    :alt: ReadtheDocs

.. image:: https://codecov.io/gh/whimian/pyGeoPressure/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/whimian/pyGeoPressure
    :alt: Codecov

.. toctree::
    :maxdepth: 1
    :caption: Getting Started:
    :hidden:

    api/api

|
*Tools for pore pressure prediction using well log data and seismic velocity data.*


Features
========

1. Hydrostatic Pressure Calculation
2. Overburden (or Lithostatic) Pressure Calculation
3. Eaton's method
4. Bowers' method

Data I/O
========

**Well log**:

- las file

- pseudo-las file without proper header

**Seismic Velocity**:

- Opendtect ascii file

- SEG-Y file (require `segpy <https://github.com/sixty-north/segpy>`_)

Getting Started
===============

* :doc:`api/api`
