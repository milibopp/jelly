"""
Concrete implementations of the abstraction model.

"""

from __future__ import division

from itertools import product
from math import pi, sin, cos
from collections import namedtuple
from random import uniform
import numpy as np

from .model import CellCollection, Cell, Obstacle, InconsistentGridError, UniformGas
from .vector import Vector

'''
An axis-parallel n-Cube, with the 'bottom-right' cornar at *position* and *size*.

*Position* and *size* should have the same dimensions.
'''
nCube = namedtuple('nCube', ['position', 'size'])

class MonteCarloGrid2D(object):
    """
    A completely random grid

    Its grid points are sampled uniformly within a box. The number of grid
    points can be specified.

    """

    def __init__(self, box, number):
        self.box = box
        self.number = number

    def __iter__(self):
        for _ in range(self.number):
            x, y = (uniform(x, dx)
                for x, dx in zip(self.box.position, self.box.size))
            yield Vector(x, y, 0.0)


class CartesianGrid2D(object):
    """
    A 2D rectangular Cartesian grid spanning a rectangular *box*. The grid
    resolution is given as a 2-tuple of the coordinate resolutions in x and y
    direction.

    Hydrodynamic quantities are given as a function of the position vector.

    The returned vector has three dimensions.

    """

    def __init__(self, box, resolution):
        self.box = box
        self.resolution = resolution

    def __iter__(self):
        """Iterate over the cartesian grid"""
        nx, ny = self.resolution
        dx, dy = self.box.size
        offset_x, offset_y = self.box.position

        for kx, ky in product(range(nx), range(ny)):
            yield Vector((kx + 0.5) * dx / nx + offset_x, (ky + 0.5) * dy / ny + offset_y, 0.0)


class CartesianGrid3D(object):
    """
    A 3D rectangular Cartesian grid spanning a *cube*. The grid
    resolution is given as a 3-tuple of the coordinate resolutions in x, y and
    z direction.

    Hydrodynamic quantities are given as a function of the position vector.

    """

    def __init__(self, cube, resolution):
        self.cube = cube
        self.resolution = resolution

    def __iter__(self):
        """Iterate over the cartesian grid"""
        nx, ny, nz = self.resolution
        dx, dy, dz = self.cube.size
        for kx, ky, kz in product(range(nx), range(ny), range(nz)):
            yield self.cube.position +\
                Vector((kx + 0.5) * dx / nx,
                       (ky + 0.5) * dy / ny,
                       (kz + 0.5) * dz / nz)


class PolarGrid2D(object):

    def __init__(self, center, boundaries, resolution):
        self.center = center
        self.boundaries = boundaries
        self.resolution = resolution

    def __iter__(self):
        a, b = self.boundaries
        for r in np.arange(a, b, self.resolution):
            for phi in np.linspace(0.0, 2*pi, (2*pi*r/self.resolution), endpoint=False):
                yield self.center + Vector(r*cos(phi), r*sin(phi), 0.0)


class CircularObstacle(Obstacle):
    """
    A two-dimensional circular obstacle described by a center and radius.
    Additionally, a `density_function` describing the density of the fluid
    adjacent to the obstacle may be supplied. Similarly
    `internal_energy_function` and `velocity_function` control their respective
    quantities in the surrounding fluid. The resolution of the circle is
    controlled via the parameter `n_phi`.

    The `inverted` flag controls whether the circle is to be constructed
    inside-out, i.e. the solid cells are outside, the fluid cells inside. It
    defaults to False.

    """

    def __init__(self, center, radius, n_phi=100, inverted=False):
        self.center = center
        self.radius = radius
        self.n_phi = n_phi
        self.inverted = inverted

    @property
    def __angle_segment(self):
        """
        The angular size of the tesselated segments making up the circle.

        """
        return 2 * pi / self.n_phi

    def __circle_position(self, k, inner):
        """
        Calculate position of a cell on the circle using its running index and
        whether it is the inner or outer circle.

        """
        r = self.radius * (1 + 0.5 * self.__angle_segment * (-1 if inner else 1))
        phi = (k + 0.5) * self.__angle_segment
        return Vector(
            r * sin(phi) + self.center[0],
            r * cos(phi) + self.center[1],
            0.0)

    def gas_cells(self, gas):
        """Generator of gas cells surrounding obstacle"""
        for k in range(self.n_phi):
            x = self.__circle_position(k, self.inverted)
            yield gas.create_cell(x, 'solid_adjacent')

    def solid_cells(self):
        """Generator of solid obstacle cells"""
        nongas = UniformGas()
        for k in range(self.n_phi):
            yield nongas.create_cell(
                self.__circle_position(k, not self.inverted),
                category='solid')

    def inside(self, position):
        """
        Checks whether a given position is inside the circle's domain.

        """
        dist = sum((self.center[i] - position[i]) ** 2.0 for i in [0, 1]) ** 0.5
        extra_space = 1.5 * self.__angle_segment
        r_max = self.radius * (1 + extra_space * (-1 if self.inverted else 1))
        return (dist > r_max) if self.inverted else (dist < r_max)
