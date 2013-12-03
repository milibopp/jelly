"""Tests of models"""

from nose.tools import assert_equal, raises
import random
from collections import namedtuple

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


def test_iterate_position():
    """Iterate positions in mesh"""
    mesh = _random_mesh()
    assert_equal(next(mesh.positions), next(mesh.cells).position)
    assert 0 <= next(mesh.positions)[0] <= 10
