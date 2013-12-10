"""Tests of models"""

from nose.tools import assert_equal, raises
import random
from collections import namedtuple

from pyrepo.util import CartesianGrid2D
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


def test_iterate_quantity():
    """Iterate positions in mesh"""
    mesh = _random_mesh()
    assert_equal(next(mesh.quantity_iterator('position')), next(mesh.cells).position)
    assert 0 <= next(mesh.quantity_iterator('position'))[0] <= 1


def make_mesh_with_nbody_cell(gridres=32):
    """
    Create amesh with an N-body cell

    :gridres: Resolution of the background gas grid

    """
    nbody_cell = Cell((0, 0, 0), (0, 0, 0), 1.0, 1.0, 'nbody')
    return Mesh(CartesianGrid2D((-2.0, -2.0), (2.0, 2.0), gridres, gridres),
        extras=[ListCellCollection([nbody_cell])])


def test_extra_objects():
    """Add additional cell collections to the mesh"""
    mesh = make_mesh_with_nbody_cell()
    cells = list(mesh.cells)
    assert_equal(sum(1 for cell in cells if cell.category == 'nbody'), 1)
