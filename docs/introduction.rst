Introduction
============

Pore pressure (geopressure) is of great importance in different stages of oil and gas (hydrocarbon)
exploration and development.
Predicted regional pressure data can help with:

1. well planning
2. Preventing hazards like kicks and blowouts.
3. building geomechanical model
4. anaylizing hydrocarbon distribution

Pore pressure prediction is to use geophyical and petrophysical properties (like velocity, resistivity)
measured or calculated to evaluate pore pressure underground instead of measuring pressure directly which
is expensive and can only be done after a well is drilled.
Usually pore pressure prediction is performed with `well logging <https://www.glossary.oilfield.slb.com/en/Terms/w/well_log.aspx>`_
data after exploration wells are drilled and cemented, and with seismic velocity data for regional pore pressure prediction.

:code:`pyGeoPressure` is an open source python package designed for pore pressure prediction
with both well log data and seismic velocity data.
Though lightweighted, :code:`pyGeoPressure` is able to perform whole workflow from data management to pressure prediction.

The main features of :code:`pyGeoPressure` are:

1. Overburden (or Lithostatic) Pressure Calculation (Tutorials: :doc:`OBP calculation for well <tutorial/obp_well>`, :doc:`OBP calculation for seismic <tutorial/obp_seis>`)
2. Eaton's method and Parameter Optimization (Tutorials: :doc:`Eaton for well <tutorial/eaton_well>`, :doc:`Eaton for seismic <tutorial/eaton_seis>`)
3. Bowers' method and Parameter Optimization (Tutorials: :doc:`Bowers for well <tutorial/bowers_well>`, :doc:`Bowers for seismic <tutorial/bowers_seis>`)
4. Multivariate method and Parameter Optimization (Tutorials: )

Aside from main prediction features, :code:`pyGeoPressrue` provides other functionalities to facilitate the workflow:

- Survey definition
- Data Management
- Well log data processing
- Generating figures
