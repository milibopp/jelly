"""Tests of utilities"""

from nose.tools import assert_equal, raises

from pyrepo.vector import Vector, dot
from pyrepo.model import InconsistentGridError
from pyrepo.util import *


def test_cartesian_grid_2d_iterate():
    """Concrete iterated values in Cartesian grid"""
    grid = CartesianGrid2D(
        Rectangle(Vector(0.0, 0.0), Vector(1.0, 1.0)), (2, 2))
    assert Vector(0.25, 0.75, 0.0) in grid
    assert Vector(0.75, 0.75, 0.0) in grid
