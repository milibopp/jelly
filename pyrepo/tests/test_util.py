"""Tests of utilities"""

from nose.tools import assert_equal, raises
import numpy as np
import numpy.linalg as la

from pyrepo.util import CartesianGrid2D


def test_cartesian_grid():
    """Create Cartesian grid"""
    # Test functions
    def density(x):
        return la.norm(x)
    def velocity(x):
        return x * 2
    def internal_energy(x):
        return np.vdot(x, (1, 0, 4))
    # Create cells using grid
    cells = list(CartesianGrid2D((0, 0), (1, 1), 4, 4,
        velocity, density, internal_energy))
    # Assert properties of test cell
    test_cell = cells[0]
    assert_equal(la.norm(test_cell.position), test_cell.density)
    assert_equal(np.vdot(test_cell.position, (1, 0, 4)), test_cell.internal_energy)
    assert_equal(test_cell.position * 2, test_cell.velocity)
