Data Types
==========

Three basic Data types in :code:`pyGeoPressure` are :code:`Well` for well,
:code:`Log` for well log and :code:`SeiSEGY` for seismic data.

Well
----

.. autoclass:: pygeopressure.basic.well.Well
    :noindex:

Initializer:
^^^^^^^^^^^^

.. automethod:: pygeopressure.basic.well.Well.__init__
    :noindex:

Properties
^^^^^^^^^^

.. automethod:: pygeopressure.basic.well.Well.depth
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.logs
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.unit_dict
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.hydrostatic
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.lithostatic
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.hydro_log
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.normal_velocity
    :noindex:

log curve data manipulation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: pygeopressure.basic.well.Well.get_log
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.add_log
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.drop_log
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.rename_log
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.update_log
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.to_las
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.save_well_logs
    :noindex:

Get Meassured pyGeoPressure
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: pygeopressure.basic.well.Well.get_pressure
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.get_pressure_normal
    :noindex:


Pressure Prediction
^^^^^^^^^^^^^^^^^^^

.. automethod:: pygeopressure.basic.well.Well.eaton
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.bowers
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.multivariate
    :noindex:

Other
^^^^^

.. automethod:: pygeopressure.basic.well.Well.plot_horizons
    :noindex:

.. automethod:: pygeopressure.basic.well.Well.save_params
    :noindex:

--------------------------------------------

Log
---

.. autoclass:: pygeopressure.basic.well_log.Log
    :noindex:

Initializer:
^^^^^^^^^^^^

.. automethod:: pygeopressure.basic.well_log.Log.__init__
    :noindex:

Alternative initializer:

.. automethod:: pygeopressure.basic.well_log.Log.from_scratch
    :noindex:

Data interfaces:
^^^^^^^^^^^^^^^^

.. automethod:: pygeopressure.basic.well_log.Log.depth
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.data
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.start
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.stop
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.start_idx
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.stop_idx
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.top
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.bottom
    :noindex:

Plot:
^^^^^

.. automethod:: pygeopressure.basic.well_log.Log.plot
    :noindex:

Others:
^^^^^^^

.. automethod:: pygeopressure.basic.well_log.Log.to_las
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.get_data
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.get_depth_idx
    :noindex:

.. automethod:: pygeopressure.basic.well_log.Log.get_resampled
    :noindex:

--------------------------------------------

SeiSEGY
-------

.. autoclass:: pygeopressure.basic.seisegy.SeiSEGY
    :noindex:

Initializers:
^^^^^^^^^^^^^

The default initializer takes a segy file path:

.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.__init__
    :noindex:

The alternative initilizer :code:`from_json` takes a info file in json.

.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.from_json
    :noindex:

Iterators:
^^^^^^^^^^

.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.inlines
    :noindex:

.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.crlines
    :noindex:

.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.inline_crlines
    :noindex:

.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.depths
    :noindex:

Data interface:
^^^^^^^^^^^^^^^

.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.data
    :noindex:

Plots Data Sections:
^^^^^^^^^^^^^^^^^^^^

.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.plot
    :noindex:

Others:
^^^^^^^

.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.valid_cdp
    :noindex:

.. note::

    Internally, :code:`pyGeoPressrue` interacts with SEGY file
    utlizing `segyio <https://github.com/Statoil/segyio>`_.
