"""Tests of utilities"""

from nose.tools import assert_equal, assert_true, assert_false, raises
from unittest import TestCase

from jelly.vector import Vector, dot
from jelly.model import InconsistentGridError
from jelly.util import *


def test_cartesian_grid_2d_iterate():
    """Concrete iterated values in a 2D Cartesian grid"""
    grid = CartesianGrid2D(
        Box(Vector(0.0, 0.0), Vector(1.0, 1.0)), (2, 2))
    all_vectors = [v for v in grid]

    assert_equal(len(all_vectors), 2*2)

    assert Vector(0.25, 0.25, 0.0) in grid
    assert Vector(0.75, 0.25, 0.0) in grid
    assert Vector(0.25, 0.75, 0.0) in grid
    assert Vector(0.75, 0.75, 0.0) in grid

def test_cartesian_grid_2d_iterate_with_offset():
    """Concrete iterated values in a 2D Cartesian grid with an offset"""
    offset2d = Vector(2.0, -1.5)
    offset3d = Vector(2.0, -1.5, 0.0)
    grid = CartesianGrid2D(
        Box(offset2d, Vector(1.0, 1.0)), (2, 2))
    all_vectors = [v for v in grid]

    assert_equal(len(all_vectors), 2*2)

    assert Vector(0.25, 0.25, 0.0) + offset3d in grid
    assert Vector(0.75, 0.25, 0.0) + offset3d in grid
    assert Vector(0.25, 0.75, 0.0) + offset3d in grid
    assert Vector(0.75, 0.75, 0.0) + offset3d in grid

def test_cartesian_grid_3d_iterate():
    """Concrete iterated values in a 3D Cartesian grid"""
    grid = CartesianGrid3D(
        Box(Vector(0.0, 0.0, 0.0), Vector(1.0, 1.0, 2.0)), (2, 2, 4))

    all_vectors = [v for v in grid]

    assert_equal(len(all_vectors), 2*2*4)

    for x in (0.25, 0.75):
        for y in (0.25, 0.75):
            for z in (0.25, 0.75, 1.25, 1.75):
                assert Vector(x, y, z) in grid

def test_cartesian_grid_3d_iterate_with_offset():
    """Concrete iterated values in a 3D Cartesian grid with an offset"""
    offset = Vector(1.0, 2.0, -3.0)

    grid = CartesianGrid3D(
        Box(offset, Vector(8.0, 4.0, 6.0)), (2, 2, 3))

    all_vectors = [v for v in grid]

    assert_equal(len(all_vectors), 2*2*3)

    for x in (2.0, 6.0):
        for y in (1.0, 3.0):
            for z in (1.0, 3.0, 5.0):
                assert Vector(x, y, z) + offset in grid


class TestCircularObstacle(TestCase):
    """
    Test of CircularObstacle class

    """

    def test_inside(self):
        """Inside-circle checks"""
        circle = CircularObstacle((0.0, 0.0), 1.0)
        assert_false(circle.inside((2.0, 0.0)))
        assert_true(circle.inside((0.0, 0.0)))
