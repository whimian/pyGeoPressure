.. pyGeoPressure documentation master file.

.. image:: img/pygeopressure-logo.png
    :width: 40%

|

Overview
========

:code:`pyGeoPressure` is an open source Python package for pore pressure prediction using well log data and seismic velocity data.

Features
========

1. Overburden (or Lithostatic) Pressure Calculation
2. Eaton's method and Parameter Optimization
3. Bowers' method and Parameter Optimization
4. Multivariate method and Parameter Optimization

Contribute
==========

- Source Code: https://github.com/whimian/pyGeoPressure
- Issue Tracker: https://github.com/whimian/pyGeoPressure/issues

License
=======
The project is licensed under the MIT license, see the file '`MIT <https://github.com/whimian/pyGeoPressure/blob/master/LICENSE>`_' for details.

Documentation Structure
=======================

- **Getting Started** (*thorough introduction and installation instructions*)

- :doc:`Tutorials <tutorial_overview>` (*walkthrough of main features using example survey*)

- **How-to** (*topic guides*)

- **References** (*inner workings*)

Contents
========

.. toctree::
    :maxdepth: 1
    :caption: Getting Started:

    introduction
    install

.. toctree::
    :maxdepth: 1
    :caption: Tutorials:

    tutorial_overview
    tutorial/obp_well
    tutorial/eaton_well
    tutorial/bowers_well
    tutorial/multivariate
    tutorial/obp_seis
    tutorial/eaton_seis
    tutorial/bowers_seis

.. toctree::
    :maxdepth: 1
    :caption: How-to:

    howtos/survey
    howtos/import_well_log_data
    howtos/manage_well_storage

.. toctree::
    :maxdepth: 1
    :caption: References:

    explanation/data_types
    explanation/data_io
    api/modules
