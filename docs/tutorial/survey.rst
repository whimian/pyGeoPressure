Survey
======

A Survey is a data set measured and recorded with reference to a particular
area of the Earth's surface [1]_. Survey is the basic management unit for
projects in pyGeoPressure. It holds survey geometry and references to
seismic and well data associated with the survey area.

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


::

    import pygeopressure as ppp

    survey = ppp.Survey('path/to/file')

.. [1] http://www.glossary.oilfield.slb.com/en/Terms/s/survey.aspx