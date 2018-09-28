Adding Seismic Cube and Surface
===============================

Add Seismic Cube
----------------

Seismic cube is added by creating a new :code:`.seis` file in :code:`Seismics` folder.

The content of `velocity.seis` file in our example survey are:

::

    {
        "path": "velocity.sgy",
        "inline_range": [200, 650, 2],
        "z_range": [400, 1100, 4],
        "crline_range": [700, 1200, 2],
        "inDepth": true,
        "Property_Type": "Velocity"
    }

*Note that if path is relative, pygeopressure will look for segy file in
the Seismics folder.*

Add Horizon
-----------

Horizons can added by placing the horizon data file with extention :code:`.hor` in :code:`Surfaces` folder.

Horizon files are tsv(Tab Seperated Value) files with three columns each stores inline, crossline and Z value.

It header should be:

::

    inline  crline  z
