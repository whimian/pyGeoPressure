Survey Setup
============

A geophysical survey is a data set measured and recorded with reference to a
particular area of the Earth's surface [1]_. Survey is the basic management unit for
projects in pyGeoPressure. It holds both survey geometry and references to
seismic and well data associated with the survey area.

In :code:`pyGeoPressure`, a :code:`Survey` object is initialized with a survey folder：

::

    import pygeopressure as ppp

    survey = ppp.Survey('path/to/survey/folder')

So to setup a survey is to build the survey folder.

Survey Folder Structure
-----------------------

In pyGeoPressure, all information and data are stored in a survey folder with
the following structure:

::

    +---EXAMPLE_SURVEY
    |   .survey
    |   |
    |   +---Seismics
    |   |       velocity.seis
    |   |       density.seis
    |   |       pressure.seis
    |   |
    |   +---Surfaces
    |   |       T20.hor
    |   |       T16.hor
    |   |
    |   \---Wellinfo
    |           .CUG1
    |           .CUG2
    |           well_data.h5
    |

Within the survey directory named :code:`EXAMPLE_SURVEY`, there are three
sub-folders :code:`Seismics`, :code:`Surfaces` and :code:`Wellinfo`. At the root of the
survey folder is a survey definition file :code:`.survey`. The definition file defines
the geometry of the survey, the folder structure defines its association with the data.

:code:`.survey`
---------------

First and foremost, there is a :code:`.survey` file, which stores geometry definition of the
whole geophysical survey and auxiliary information.

Geometry Definition
^^^^^^^^^^^^^^^^^^^
Survey Geometry defines:

1. Survey Area extent
2. Inline/Crossline Coordinates, along which the survey are conducted.
3. X/Y Coordinates, real world Coordinates
4. Relations between them

In pyGeoPressure, survey geometry is defined using a method I personally
dubbed "Three points" method. Given the inline/crossline number and X/Y coordinates
of three points on the survey grid, we are able to solve the linear equaions for
transformation between inline/crossline coordination and X/Y coordination.

Information in :code:`.survey` file of the example survey are

::

    {
        "name": "CUG_depth",
        "point_A": [6400, 4100, 701319, 3274887],
        "point_B": [6400, 4180, 702185, 3274387],
        "point_C": [6440, 4180, 702685, 3275253],
        "inline_range": [6400, 7000, 20],
        "crline_range": [4100, 6020, 40],
        "z_range": [0, 5000, 4, "m"]
    }

Of the three points selected, point A and point B share the same inline, and
point B and point C share the same crossline.

In addition to coordinations of three points, the extent and step of inline, crossline
,z coordinates and unit of z are also needed to fully define the extent of the
survey.

Seismics
^^^^^^^^
Within :code:`Seismics` folder, each file written in JSON with extention :code:`.seis` represents a seismic data cube.
These files contain file path to the actual SEG-Y file storing seismic data,
and the type of property (:code:`Property_Type`) and wether data is in depth scale
or not (:code:`inDepth`). So the :code:`Seismics` folder doesn't need to store
large SEG-Y files, it just holds references to them.
In-line/cross-line range and Z range are also written in these files.

Surfaces
^^^^^^^^

Surfaces like seimic horizons are stored in :code:`Surfaces` folder. Surface
files ending with :code:`.hor` are tsv files storing inline number, crossline number
and depth values defining the geometry of a 3D geologic surface.

Wellinfo
^^^^^^^^

Well information is stored in :code:`Wellinfo`. Each file with file name with
extention :code:`.well` is a well information file, it stores well position information
like coordination, kelly bushing and interpretation information like interpretated
layers, fitted coefficients. It also holds a pointer to where the log curve data is
stored. By default, well log curve data are stored in :code:`well_data.h5`, but
users can point to other storage files.

Create New Survey
-----------------
A helper function :code:`create_survey_directory` can facilitate users to build survey folder structure:

::

    import pygeopressure as ppp

    ppp.create_survey_directory(ROOTDIR, SURVEY_NAME)

It will create a survey folder named :code:`SURVEY_NAME` in :code:`ROOTDIR`
with three sub-folders for each kind of data and a :code:`.survey` file.

--------

.. [1] http://www.glossary.oilfield.slb.com/en/Terms/s/survey.aspx
