"""Tests of models"""

from nose.tools import assert_equal, raises
import random

from pyrepo.util import CartesianGrid2D, Rectangle, MonteCarloGrid2D
from pyrepo.vector import Vector
from pyrepo.model import *


class CustomObstacle(Obstacle):
    """A custom obstacle that cuts off any cells with x < 1.5"""

    def gas_cells(self):
        return iter([])

    def solid_cells(self):
        return iter([])

    def inside(self, position):
        return position[0] < 1.5

    def check(self):
        return True


def make_random_mesh(ncells=10):
    return Mesh(
        UniformGas(),
        MonteCarloGrid2D(
            Rectangle(Vector(0, 0), Vector(1, 1)),
            ncells
        )
    )


def make_mesh_with_nbody_cell(gridres=32):
    """
    Create amesh with an N-body cell

    :gridres: Resolution of the background gas grid

    """
    nbody_cell = Cell((0, 0, 0), (0, 0, 0), 2.0, 2.0, 'nbody')
    return Mesh(
        UniformGas(),
        CartesianGrid2D(
            Rectangle(Vector(-2.0, -2.0), Vector(4.0, 4.0)),
            (gridres, gridres)),
        extras=[ListCellCollection([nbody_cell])])


def test_extra_objects():
    """Add additional cell collections to the mesh"""
    mesh = make_mesh_with_nbody_cell()
    cells = list(mesh.cells)
    assert_equal(sum(1 for cell in cells if cell.category == 'nbody'), 1)


def test_uniform_gas():
    """Uniform gas"""
    gas = UniformGas()
    x = Vector(1.0, 2.0, 3.0)
    assert_equal(gas.velocity(x), Vector(0.0, 0.0, 0.0))
    assert_equal(gas.density(x), 1.0)
    assert_equal(gas.internal_energy(x), 1.0)


def test_functional_gas():
    """Functional gas"""
    gas = FunctionalGas(
        lambda x: 2*x,
        lambda x: abs(x),
        lambda x: abs(x) * 0.5)
    cell = gas.create_cell(Vector(4.0, -3.0, 0.0))
    assert_equal(cell.velocity, Vector(8.0, -6.0, 0.0))
    assert_equal(cell.density, 5.0)
    assert_equal(cell.internal_energy, 2.5)


def test_make_gas_cell_uniform():
    gas = UniformGas(Vector(-1.0, 2.0, 3.0), 2.5, 1.3)
    cell = gas.create_cell(Vector(1.0, 2.0, 3.0))
    assert_equal(cell.position, Vector(1.0, 2.0, 3.0))
    assert_equal(cell.velocity, Vector(-1.0, 2.0, 3.0))
    assert_equal(cell.density, 2.5)
    assert_equal(cell.internal_energy, 1.3)


def test_create_gas_category():
    gas = UniformGas()
    cell = gas.create_cell(Vector(1.0, 2.0, 3.0), 'test_category')
    assert_equal(cell.category, 'test_category')


def test_approximate_gas_plain():
    grid = CartesianGrid2D(Rectangle(Vector(0, 0), Vector(1, 1)), (2, 2))
    cells = list(approximate_gas(UniformGas(), grid))
    assert_equal(cells[0].position, Vector(0.25, 0.25, 0.0))
