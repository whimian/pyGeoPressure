============
Installation
============

|
Denpendencies
=============
- Python 3.6
- NumPy 1.8 (or greater)
- SciPy 0.13 (or greater)
- matplotlib 1.3 (or greater)

*Optional:*

* IPython
* Jupyter Notebook

Installing Python
=================
The recommended way to intall Python and the dependencies of this package is
using conda package manager from Anaconda Inc. You may download and install
Miniconda from https://conda.io/miniconda which contains both Python and
conda package manager.

Installing pyGeoPressure
========================
First, download the source code or clone from our Github repository.

pyGeoPressure is recommended to be installed in a seperate python environment
which can be easily created with conda. For example, with requirements.yml file
the following command will create an environment named pygeopressure_env with
all of our denpendencies installed.

.. code:: bash

    conda update conda
    conda env create --file environments.yml

Then, run the following command to install pyGeoPressure.

.. code:: bash

    python setup.py install
