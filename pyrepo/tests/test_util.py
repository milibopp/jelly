"""Tests of utilities"""

from nose.tools import assert_equal, raises

from pyrepo.vector import Vector, dot
from pyrepo.util import *


def test_cartesian_grid():
    """Create Cartesian grid"""
    # Test functions
    def density(x):
        return abs(x)
    def velocity(x):
        return x * 2
    def internal_energy(x):
        return dot(x, Vector(4, 0, 1))
    # Create cells using grid
    cells = list(CartesianGrid2D(
        Rectangle(Vector(0.0, 0.0), Vector(1.0, 1.0)), (4, 4),
        velocity, density, internal_energy))
    # Assert properties of test cell
    test_cell = cells[0]
    assert_equal(abs(test_cell.position), test_cell.density)
    assert_equal(dot(test_cell.position, Vector(4, 0, 1)), test_cell.internal_energy)
    assert_equal(test_cell.position * 2, test_cell.velocity)


def test_cartesian_grid_2d_iterate():
    """Concrete iterated values in Cartesian grid"""
    grid = CartesianGrid2D(
        Rectangle(Vector(0.0, 0.0), Vector(1.0, 1.0)), (2, 2))
    positions = map(lambda c: c.position, grid)
    assert Vector(0.25, 0.75, 0.0) in positions
    assert Vector(0.75, 0.75, 0.0) in positions
