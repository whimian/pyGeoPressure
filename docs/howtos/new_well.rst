Add Well
========

Adding a new well is acheived by add a :code:`.well` file to :code:`Wellinfo` folder in
survey directory(see :doc:`survey`).

A minimal :code:`.well` should contain the following information:
1. "well_name"
2. "loc" - X/Y coordination of the well
3. "KB" - kelly bushing elevation
4. "WD" - water depth
5. "TD" - total depth of the wellbore
6. "hdf_file" - storage file path, if only the file name is provided, pyGeoPressure will assume it is in the :code:`Wellinfo` folder.

::

    {
        "well_name": "CUG1",
        "loc": [
            707838,
            3274780
        ],
        "KB": 23,
        "WD": 85,
        "TD": 5000,
        "hdf_file": "well_data.h5"
    }

More information can be stored in well information file. Please check out the :code:`CUG1.well` in the example surey.