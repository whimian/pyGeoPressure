---
title: 'PyGeoPressure: Geopressure Prediction in Python'
tags:
  - Python
  - geophysics
  - geomechanics
  - pore pressure
  - well planning
authors:
  - name: Hao Yu
    orcid: 0000-0002-4109-6358
    affiliation: 1
affiliations:
  - name: Institute of Geophysics and Geomatics, China University of Geosciences
    index: 1
date: 29 September 2018
bibliography: paper.bib
---

# Summary

Geopressure (or pore pressure) prediction is of central importance in both the exploration and development of hydrocarbon reservoirs. Pore fluid pressure affects the physical properties of reservoir rocks, hence predicted pressure is a key input when building the geomechanical model of a reservoir. Overpressure also influences the distribution of hydrocarbon, and sometimes can even work as an effective seal. Predrill pore pressure data in depth can help prevent geo-hazards like kicks, blowouts and drilling fluid infiltrating the formation whiling drilling in overpressured formations.

``pyGeoPressure`` provides a set of open-source tools to perform geopressure prediction workflow which involves data preprocessing, parameter optimization, and pressure prediction. Pore pressure can be predicted using well log data or seismic velocity data. Both of these two kinds of predictions are implemented in ``pyGeoPressure``. In addition to standard methods of Eaton’s[@eaton1975] and Bowers’[@bowers1994], a new multivariate prediction model[@sayers2003] is also implemented in ``pyGeoPressure`` which incorporates petrophysical properties like porosity and shale volume other than sonic velocity. Another set of functionalities that ``pyGeoPressure`` provides are generating graphs. It can generate slices and sections of predicted pressure cube and well log predicted pressure profiles.

``pyGeoPressure`` is designed with flexibility and portability in mind. ``pyGeoPressure`` provides a flexible survey management system based on a clear folder structure, in which adding new well or seismic data cube can simply be achieved by adding a json file with required information. The basic numerical type used in computation under the hood is NumPy array, so it can work together with scientific computation tools within python ecosystem. ``pyGeoPressure`` provides a simple, easily accessed open-source solution to geopressure prediction and a framework upon which researchers and engineers can quickly test and implement new prediction ideas.

# References
