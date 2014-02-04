"""Tests of utilities"""

from nose.tools import assert_equal, raises

from jelly.vector import Vector, dot
from jelly.model import InconsistentGridError
from jelly.util import *


def test_cartesian_grid_2d_iterate():
    """Concrete iterated values in a 2D Cartesian grid"""
    grid = CartesianGrid2D(
        Rectangle(Vector(0.0, 0.0), Vector(1.0, 1.0)), (2, 2))
    assert Vector(0.25, 0.75, 0.0) in grid
    assert Vector(0.75, 0.75, 0.0) in grid

def test_cartesian_grid_3d_iterate():
    """Concrete iterated values in a 3D Cartesian grid"""
    grid = CartesianGrid3D(
        Rectangle(Vector(0.0, 0.0, 0.0), Vector(1.0, 1.0, 2.0)), (2, 2, 4))

    all_vectors = [v for v in grid]

    assert_equal(len(all_vectors), 2*2*4)

    for x in (0.25, 0.75):
        for y in (0.25, 0.75):
            for z in (0.25, 0.75, 1.25, 1.75):
                assert Vector(x, y, z) in grid
