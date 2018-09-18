.. pyGeoPressure documentation master file.

.. image:: img/pygeopressure-logo.png
    :width: 40%

|

.. image:: https://badge.fury.io/py/pyGeoPressure.svg
    :target: https://badge.fury.io/py/pyGeoPressure

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

Overview
========

*A Python package for pore pressure prediction using well log data and seismic velocity data.*

Features
========

1. Hydrostatic Pressure Calculation
2. Overburden (or Lithostatic) Pressure Calculation
3. Eaton's method and Parameter Optimization (Well log)
4. Eaton's method and Parameter Optimization (Seismic Velocity)
5. Bowers' method and Parameter Optimization (Well log)
6. Bowers' method and Parameter Optimization (Seismic Velocity)
7. Multivariate method and Parameter Optimization (Well log)

Getting Started
===============

Installation
------------

:code:`pyGeoPressure` is on :code:`PyPI`:

::

    pip install pygeopressure


Example
-------

Pore Pressure Prediction using well log data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

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

.. image:: img/readme_example.svg
    :width: 40%

Contribute
----------
- Issue Tracker: https://github.com/whimian/pyGeoPressure/issues
- Source Code: https://github.com/whimian/pyGeoPressure

License
-------
The project is licensed under the MIT license, see the file `MIT <https://github.com/whimian/pyGeoPressure/blob/master/LICENSE>`_ for details.

.. toctree::
    :maxdepth: 1
    :caption: Getting Started:
    :hidden:

    install

.. toctree::
    :maxdepth: 1
    :caption: Tutorials:
    :hidden:

    tutorial/survey
    tutorial/data_types
    tutorial/data_io

.. toctree::
    :maxdepth: 1
    :caption: References:
    :hidden:

    api/modules
