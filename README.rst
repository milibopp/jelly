jelly
=====

*Abstraction layer for running numerical hydrodynamics software*

``jelly`` is supposed to abstract away the technical complexities of running
certain kinds of hydrodynamics software used in numerical computations. It
generates input files and wraps the invocation of simulation runs.

Currently it only supports the hydrodynamics software `Arepo`_. It might be
extended to similar software as well.


Code status
-----------

.. image:: https://travis-ci.org/aepsil0n/jelly.png?branch=master
    :target: https://travis-ci.org/aepsil0n/jelly


Examples
--------

There are a couple of examples in the examples/ directory in the form of simple
Python scripts. Note that you need to have ``jelly`` in your Python path to run
them.


.. _Arepo: http://www.mpa-garching.mpg.de/~volker/arepo/
