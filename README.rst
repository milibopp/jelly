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


Tests
-----

We use ``nosetests`` for unit testing.

To run the tests install the nose_ package and call ``nosetests`` from the base
directory.

You can also install and use tox_ to run the tests for different python versions.


.. _Arepo: http://www.mpa-garching.mpg.de/~volker/arepo/
.. _nose: https://nose.readthedocs.org/
.. _tox: https://tox.readthedocs.org/
