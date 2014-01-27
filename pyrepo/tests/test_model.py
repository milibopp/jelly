"""Tests of models"""

from nose.tools import assert_equal, raises
import random

from pyrepo.util import CartesianGrid2D, Rectangle
from pyrepo.vector import Vector
from pyrepo.model import *


def _random_mesh():
    """
    Generate a random mesh for testing purposes

    """
    def rnd_tuple(n):
        return tuple(random.uniform(0, 1) for _ in range(n))

    def rnd_cell(category='normal'):
        pos = rnd_tuple(3)
        vel = rnd_tuple(3)
        rho = random.uniform(0, 1)
        u = random.uniform(0, 1)
        return Cell(pos, vel, rho, u, category)

    cells = ListCellCollection(rnd_cell() for _ in range(10))
    return Mesh(cells)


def make_mesh_with_nbody_cell(gridres=32):
    """
    Create amesh with an N-body cell

    :gridres: Resolution of the background gas grid

    """
    nbody_cell = Cell((0, 0, 0), (0, 0, 0), 2.0, 2.0, 'nbody')
    return Mesh(
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


def test_make_gas_cell_uniform():
    gas = UniformGas(Vector(-1.0, 2.0, 3.0), 2.5, 1.3)
    cell = gas.create_cell(Vector(1.0, 2.0, 3.0))
    assert_equal(cell.position, Vector(1.0, 2.0, 3.0))
    assert_equal(cell.velocity, Vector(-1.0, 2.0, 3.0))
    assert_equal(cell.density, 2.5)
    assert_equal(cell.internal_energy, 1.3)
