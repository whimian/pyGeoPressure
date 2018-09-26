Manage Well Storage File
========================

In :code:`pyGeoPressure`, well log data is stored in :code:`hdf5` files (I call it storage file).
Different wells may share the same storage file.
When working with well log data, :code:`Well` class will handle storage file automatically.
But there are times when the storage file may get too large, and you want to clean it up.
Or you would want take only part of the well log data stored in an old storage file to create a
new storage file for other projects.
In the following part, we will show you how to manage well storage file directly.

