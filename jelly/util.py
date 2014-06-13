# coding=utf-8
"""
Concrete implementations of the abstraction model.

"""

from __future__ import division

from itertools import product
from math import pi, sin, cos
from collections import namedtuple
from random import uniform

from .model import CellCollection, Obstacle, InconsistentGridError
from .vector import Vector


class InvalidBoxError(Exception):
    """Raised when an invalid box is created"""
    pass


class Box(object):
    """
    An axis-parallel box

    The bottom-left corner is at *position* and spans *size*. *position* and
    *size* must have the same dimensions.

    """

    def __init__(self, position, size):
        if len(size) != len(position):
            raise InvalidBoxError("box position and size must have same dimension")
        for x in size:
            if x < 0:
                raise InvalidBoxError("box size must have positive values")
        self.position = position
        self.size = size


class MonteCarloGrid2D(object):
    """
    A completely random 2d grid.

    Its grid points are sampled uniformly within a box. The number of grid
    points can be specified.

    TODO: needs testing

    """

    def __init__(self, box, number):
        self.box = box
        self.number = number

    def __iter__(self):
        for _ in range(self.number):
            x, y = (uniform(p, dp) for p, dp in zip(
                self.box.position, self.box.position + self.box.size))
            yield Vector(x, y, 0.0)


class MonteCarloGrid3D(object):
    """
    A completely random 3d grid.

    Its grid points are sampled uniformly within a box. The number of grid
    points can be specified.

    TODO: needs testing

    """

    def __init__(self, box, number):
        self.box = box
        self.number = number

    def __iter__(self):
        for _ in range(self.number):
            x, y, z = (uniform(p, dp) for p, dp in zip(
                self.box.position, self.box.position + self.box.size))
            yield Vector(x, y, z)


class CartesianGrid2D(object):
    """
    A 2D rectangular Cartesian grid spanning a rectangular *box*. The grid
    resolution is given as a 2-tuple of the coordinate resolutions in x and y
    direction.

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

    """

    def __init__(self, box, resolution):
        self.cube = box
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
    """
    A 2D grid resembling polar coordinates

    Within radial *boundaries* around the *center* radii are sampled with equal
    spacing given by *resolution*. For each annulus, the azimuthal direction is
    sampled with the same equal spacing to achieve a homogenous distribution of
    grid points.

    """

    def __init__(self, center, boundaries, resolution):
        self.center = center
        self.boundaries = boundaries
        self.resolution = resolution

    def __iter__(self):
        a, b = self.boundaries
        r_step = self.resolution
        n_r = int((b - a) / self.resolution)
        for r in [a + r_step * n for n in range(n_r)]:
            n_phi = int(2 * pi * r / self.resolution)
            phi_step = 2 * pi / n_phi
            for phi in [phi_step * n for n in range(n_phi)]:
                yield self.center + Vector(r * cos(phi), r * sin(phi), 0.0)


class LogarithmicPolarGrid2D(object):
    """
    A 2D grid with a logarithmic resolution in radial direction

    The radial dimension is resolved within *boundaries*. There are *n_radius*
    radial steps. The azimuthal dimension is resolved by *n_phi* cells for each
    radius and spans from 0 to 2π.

    """

    def __init__(self, center, boundaries, n_radius, n_phi):
        self.center = center
        self.boundaries = boundaries
        self.n_radius = n_radius
        self.n_phi = n_phi

    def __iter__(self):
        a, b = self.boundaries
        for n in range(self.n_radius):
            r = a * (b / a) ** (n / (self.n_radius - 1))
            for k in range(self.n_phi):
                phi = 2 * k * pi / self.n_phi
                yield self.center + Vector(r * cos(phi), r * sin(phi), 0.0)


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

    def __init__(self, center, radius, n_phi=100, inverted=False, layers=1):
        self.center = center
        self.radius = radius
        self.n_phi = n_phi
        self.inverted = inverted
        self.layers = layers

    @property
    def __angle_segment(self):
        """
        The angular size of the tesselated segments making up the circle.

        """
        return 2 * pi / self.n_phi

    def __circle_position(self, k, inner, layer):
        """
        Calculate position of a cell on the circle using its running index and
        whether it is the inner or outer circle.

        """
        r = self.radius * (1 + (layer - 0.5) * self.__angle_segment * (-1 if inner else 1))
        phi = (k + 0.5) * self.__angle_segment
        return Vector(
            r * sin(phi) + self.center[0],
            r * cos(phi) + self.center[1],
            0.0)

    @property
    def fluids(self):
        """Generator of gas cells surrounding obstacle"""
        for j in range(1, self.layers + 1):
            for k in range(self.n_phi):
                yield self.__circle_position(k, self.inverted, j)

    @property
    def solids(self):
        """Generator of solid obstacle cells"""
        for j in range(1, self.layers + 1):
            for k in range(self.n_phi):
                yield self.__circle_position(k, not self.inverted, j)

    def inside(self, position):
        """
        Checks whether a given position is inside the circle's domain.

        """
        dist = sum((self.center[i] - position[i]) ** 2.0 for i in [0, 1]) ** 0.5
        extra_space = (self.layers + 0.5) * self.__angle_segment
        r_max = self.radius * (1 + extra_space * (-1 if self.inverted else 1))
        return (dist > r_max) if self.inverted else (dist < r_max)
