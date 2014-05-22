"""Tests of utilities"""

from unittest import TestCase
from math import pi, cos, sin, sqrt

from nose.tools import (
    assert_less_equal, assert_greater_equal, assert_in, assert_equal,
    assert_false, assert_true, raises, assert_almost_in)

from jelly.util import *


class TestBox(object):
    """Tests of Box class"""

    def test_simple(self):
        """A simple working box"""
        box = Box(Vector(0, 0), Vector(1, 1))
        assert_equal(box.position, Vector(0, 0))
        assert_equal(box.size, Vector(1, 1))

    @raises(InvalidBoxError)
    def test_negative_size(self):
        """Exception is raised for negative sizes"""
        box = Box(Vector(1, 2), Vector(-1, 1))

    @raises(InvalidBoxError)
    def test_faulty_dimensions(self):
        """Exception is raised for incompatible dimensions"""
        box = Box(Vector(1, 2, 3), Vector(1, 1))


def test_monte_carlo_grid_3d_size():
    """Check number of vectors in Monte Carlo 3D grid"""
    n = 1000
    grid = MonteCarloGrid3D(Box(Vector(2.0, -1.0, 1.0), Vector(5.0, 6.0, 3.0)), n)
    vectors = [v for v in grid]

    assert_equal(len(vectors), n)


def test_monte_carlo_grid_3d_range():
    """Check range of vectors in Monte Carlo 3D grid"""
    n = 10000
    box = Box(Vector(2.0, -1.0, 1.0), Vector(5.0, 6.0, 3.0))
    grid = MonteCarloGrid3D(box, n)
    vectors = [v for v in grid]

    for x, y, z in vectors:
        assert_greater_equal(x, box.position[0])
        assert_greater_equal(y, box.position[1])
        assert_greater_equal(z, box.position[2])
        assert_less_equal(x, box.position[0] + box.size[0])
        assert_less_equal(y, box.position[1] + box.size[1])
        assert_less_equal(z, box.position[2] + box.size[2])


def test_monte_carlo_grid_2d_size():
    """Check number of vectors in Monte Carlo 2D grid"""
    n = 1000
    grid = MonteCarloGrid2D(Box(Vector(2.0, -1.0), Vector(5.0, 6.0)), n)
    vectors = [v for v in grid]

    assert_equal(len(vectors), n)


def test_monte_carlo_grid_2d_range():
    """Check range of vectors in Monte Carlo 2D grid"""
    n = 10000
    box = Box(Vector(2.0, -1.0), Vector(5.0, 6.0))
    grid = MonteCarloGrid2D(box, n)
    vectors = [v for v in grid]

    for x, y, z in vectors:
        assert_greater_equal(x, box.position[0])
        assert_greater_equal(y, box.position[1])
        assert_greater_equal(z, 0.0)
        assert_less_equal(x, box.position[0] + box.size[0])
        assert_less_equal(y, box.position[1] + box.size[1])


def test_cartesian_grid_2d_iterate():
    """Concrete iterated values in a 2D Cartesian grid"""
    grid = CartesianGrid2D(
        Box(Vector(0.0, 0.0), Vector(1.0, 1.0)), (2, 2))
    all_vectors = [v for v in grid]

    assert_equal(len(all_vectors), 2 * 2)

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

    assert_equal(len(all_vectors), 2 * 2)

    assert Vector(0.25, 0.25, 0.0) + offset3d in grid
    assert Vector(0.75, 0.25, 0.0) + offset3d in grid
    assert Vector(0.25, 0.75, 0.0) + offset3d in grid
    assert Vector(0.75, 0.75, 0.0) + offset3d in grid


def test_cartesian_grid_3d_iterate():
    """Concrete iterated values in a 3D Cartesian grid"""
    grid = CartesianGrid3D(
        Box(Vector(0.0, 0.0, 0.0), Vector(1.0, 1.0, 2.0)), (2, 2, 4))

    all_vectors = [v for v in grid]

    assert_equal(len(all_vectors), 2 * 2 * 4)

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

    assert_equal(len(all_vectors), 2 * 2 * 3)

    for x in (2.0, 6.0):
        for y in (1.0, 3.0):
            for z in (1.0, 3.0, 5.0):
                assert Vector(x, y, z) + offset in grid


def test_polar_grid_2d_radii():
    """Radii of PolarGrid2D"""
    grid = PolarGrid2D(Vector(0.0, 0.0, 0.0), (0.1, 1.0), 0.1)
    for r in [0.1, 0.2, 1.0]:
        assert_in(Vector(0.1, 0.0, 0.0), grid)


def test_polar_grid_2d_azimuths():
    """Azimuths of PolarGrid2D"""
    grid = PolarGrid2D(Vector(0.0, 0.0, 0.0), (0.1, 1.0), 0.1)
    phi_step = 2 * pi / 31
    for phi in [k * phi_step for k in (0, 1, 2, 30)]:
        assert_in(Vector(0.5 * cos(phi), 0.5 * sin(phi), 0.0), grid)


class TestLogarithmicPolarGrid2D(object):

    def setup(self):
        self.grid = LogarithmicPolarGrid2D(
            Vector(5, 4, 0), (0.1, 10), 5, 10)

    def test_radial(self):
        for r in [0.1, sqrt(0.1), 1, sqrt(10), 10]:
            assert_almost_in(self.grid.center + Vector(r, 0, 0), self.grid)
            assert_almost_in(self.grid.center - Vector(r, 0, 0), self.grid)

    def test_azimuthal(self):
        for g in self.grid:
            print(g)
        for k in range(10):
            phi = k / 5 * pi
            assert_almost_in(self.grid.center + Vector(cos(phi), sin(phi), 0), self.grid)


class TestCircularObstacle(object):
    """
    Test of CircularObstacle class

    """

    def setup(self):
        self.circle = CircularObstacle((0.0, 0.0), 1.0)

    def test_fluids(self):
        for pos in self.circle.fluids:
            assert_greater_equal(abs(pos), 1.0)

    def test_solids(self):
        for pos in self.circle.solids:
            assert_less_equal(abs(pos), 1.0)

    def test_inside(self):
        """Inside-circle checks"""
        assert_false(self.circle.inside((2.0, 0.0)))
        assert_true(self.circle.inside((0.0, 0.0)))


class TestMultilayeredCircularObstacle(object):

    def setup(self):
        self.multi = CircularObstacle((0.0, 0.0), 1.0, n_phi=16, layers=2)

    def test_number_of_grid_points(self):
        expected_number = self.multi.n_phi * self.multi.layers
        assert_equal(len(list(self.multi.fluids)), expected_number)
        assert_equal(len(list(self.multi.solids)), expected_number)

    def test_radii(self):
        bound = 1 + 2 * pi / self.multi.n_phi
        outer_fluids = filter(lambda pos: abs(pos) > bound, self.multi.fluids)
        assert_equal(len(list(outer_fluids)), 16)
