#!/usr/bin/env python
"""Setup script for jelly."""

from setuptools import setup


if __name__ == '__main__':
    setup(
        name='jelly',
        version='0.1.0',
        description='Abstraction layer for running numerical hydrodynamics software',
        author='Eduard Bopp',
        author_email='eduard.bopp@aepsil0n.de',
        packages=['jelly'],
        install_requires=['six'],
    )
