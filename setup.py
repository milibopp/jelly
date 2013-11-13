#!/usr/bin/env python
"""Setup script for pyrepo."""

from distutils.core import setup


if __name__ == '__main__':
    setup(
        name='pyrepo',
        version='0.0',
        description='Convenient Python wrapper for the hydrodynamics software Arepo',
        author='Eduard Bopp',
        author_email='eduard.bopp@aepsil0n.de',
        packages=['pyrepo'],
    )
