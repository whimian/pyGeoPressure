************
Installation
************

|

Denpendencies
=============

:code:`pyGeoPressure` supports both Python 2.7 and Python 3.6 and some of mainly
dependent packages are:

- NumPy
- SciPy
- matplotlib
- Jupyter
- segyio

Installing Python
=================
The recommended way to intall Python is to
use conda package manager from Anaconda Inc. You may download and install
Miniconda from https://conda.io/miniconda which contains both Python and
conda package manager.

Installing pyGeoPressure
========================

:code:`pyGeoPressure` is recommended to be installed in a seperate python environment
which can be easily created with :code:`conda`. So first create a new environment with
:code:`conda`. The new environment should have :code:`pip` installed.

.. code:: bash

    conda update conda
    conda create -n ENV python=3.6 pip

or

.. code:: bash

    conda update conda
    conda create -n ENV python=2.7 pip

if using Python 2.7.

Install from :code:`pyPI`
-------------------------
:code:`pyGeoPressure` is on :code:`PyPI`, so run the following command to install
:code:`pyGeoPressure` from :code:`pypi`.

.. code:: bash

    pip install pygeopressure

Install from :code:`github repo`
--------------------------------

Install latest develop branch from github:

.. code:: bash

    pip install -e git://github.com/whimian/pyGeoPressure.git@develop

Alternatively, if you don't have :code:`git` installed, you can download the repo
from `Github <https://github.com/whimian/pyGeoPressure/archive/develop.zip>`_,
unzip, :code:`cd` to that directory and run:

.. code:: bash

    pip install pyGeoPressure

For Developers
==============

Clone the github repo:

.. code:: bash

    git clone https://github.com/whimian/pyGeoPressure.git

Setup the development environment with :code:`conda`:

.. code:: bash

    conda env create --file test/test_env_2.yml

or

.. code:: bash

    conda env create --file test/test_env_3.yml

The testing framework used is :code:`pytest`. To run all tests, just run the
following code at project directory:

.. code:: bash

    pytest --cov
