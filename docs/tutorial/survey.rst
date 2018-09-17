Survey Setup
============

A geophysical survey is a data set measured and recorded with reference to a
particular area of the Earth's surface [1]_. Survey is the basic management unit for
projects in pyGeoPressure. It holds both survey geometry and references to
seismic and well data associated with the survey area.

Create Survey
-------------
A new survey can be created with a survey folder：

::

    import pygeopressure as ppp

    survey = ppp.Survey('path/to/survey/folder')

Survey Folder Structure
-----------------------

In pyGeoPressure, all information and data are stored in a survey folder with
the following structure:

::

    +---EXAMPLE_SURVEY
    |   .survey
    |   |
    |   +---Seismics
    |   |       .SEIS_1
    |   |       .SEIS_2
    |   |       .SEIS_3
    |   |
    |   +---Surfaces
    |   |       .HORIZON_1
    |   |       .HORIZON_2
    |   |       .HORIZON_3
    |   |       .HORIZON_4
    |   |
    |   \---Wellinfo
    |           .WELL-1
    |           .WELL-2
    |           .WELL-3
    |           .WELL-4
    |           well_data.h5
    |

Within the survey directory named :code:`EXAMPLE_SURVEY`, there are three
sub-folders :code:`Seismics`, :code:`Surfaces` and :code:`Wellinfo`.
Their names are self-explanatory.

Seismics
^^^^^^^^
Within :code:`Seismics` folder, each file written in JSON represents a seismic data cube.
In-line/cross-line range and Z range are stored in each file.
The file also contains file path to the actual SEG-Y file storing seismic data.
So the :code:`Seismics` folder doesn't need to store large SEG-Y files, it just holds references to them.

::

    {
        "path": "D:\\poststack_f3.sgy",
        "inline_range": [200, 650, 2],
        "z_range": [400, 1100, 4],
        "crline_range": [700, 1200, 2]
    }

Surfaces
^^^^^^^^

Surfaces like seimic horizons are stored in :code:`Surfaces`. Surface files are
just tsv files storing inline number, crossline number and depth values of 3D geologic surfaces.

Wellinfo
^^^^^^^^

Well log data is stored in :code:`Wellinfo`. Each file with file name staring with '.' plus well name is a
well information file, it stores well name, kelly bushing, water depth and other information.
Actual well logging data are stored in :code:`well_data.h5`.

:code:`.survey`
---------------

Most importantly, there is a :code:`.survey` file, which stores geometry definition of the
whole geophysical survey and auxiliary information.

Geometry Definition
-------------------
Survey Geometry defines:

1. Survey Area extent
2. Inline/Crossline Coordinates, along which the survey are conducted.
3. X/Y Coordinates, real world Coordinates
4. Relations between them

In pyGeoPressure, survey geometry is defined using a method I personally dubbed
"Three points" method. The information needed are the extent and step of
Inline/Crline coordinates



.. [1] http://www.glossary.oilfield.slb.com/en/Terms/s/survey.aspx
