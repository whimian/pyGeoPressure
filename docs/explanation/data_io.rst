========
Data I/O
========

Well Log
========
Well logs for a single well are stored internally as pandas DataFrame.

Both Standard LAS file and Pseudo-LAS file (TSV file without LAS header)

Seismic Velocity
================

When it comes to 3D seismic data, we directly interact with SEGY file
utlizing `segyio <https://github.com/Statoil/segyio>`_.



.. automethod:: pygeopressure.basic.seisegy.SeiSEGY.__init__

.. autoclass:: pygeopressure.basic.seisegy.SeiSEGY
    :members:
