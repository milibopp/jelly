"""
Abstraction model of an Arepo setup. This module contains several utilities
that abstract and thereby facilitate the construction of an initial conditions
file for Arepo.

Among these utilities one can find quantities described by a function of the
cell's coordinates, solid objects used for special boundaries etc.

"""

from __future__ import division
from abc import ABCMeta, abstractproperty, abstractmethod
from itertools import chain

from .vector import Vector


class Cell(object):
    """
    A moving-mesh hydrodynamics Voronoi cell. This is the fundamental
    component of the grid, once it is established.

    In principle, this can also function as a more general particle. This is
    what the `category` attribute is intended to cover. For instance, while the
    default category is 'normal', cells making up solid obstacles are
    categorized as 'solid'.

    """

    def __init__(self, position, velocity, density, internal_energy,
                 category='normal', ident=None):
        self.position = position
        self.velocity = velocity
        self.density = density
        self.internal_energy = internal_energy
        self.category = category
        self.ident = ident


class Gas(object):
    """
    Description of a background gas in terms of several functions

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def velocity(self, position):
        """Velocity of the gas"""
        pass

    @abstractmethod
    def density(self, position):
        """Density of the gas"""
        pass

    @abstractmethod
    def internal_energy(self, position):
        """Internal energy of the gas"""
        pass

    def create_cell(self, position, category='normal'):
        """Create a gas cell at a given position"""
        return Cell(
            position,
            self.velocity(position),
            self.density(position),
            self.internal_energy(position),
            category)


class UniformGas(Gas):
    """
    A uniform background gas

    This gas has zero velocity and a constant density and internal energy of
    one.

    """

    def __init__(
            self, velocity=Vector(0.0, 0.0, 0.0), density=1.0,
            internal_energy=1.0):
        self.__velocity = velocity
        self.__density = density
        self.__internal_energy = internal_energy

    def velocity(self, position):
        return self.__velocity

    def density(self, position):
        return self.__density

    def internal_energy(self, position):
        return self.__internal_energy


class FunctionalGas(Gas):
    """
    A background gas described by functions

    It requires the velocity as a vector field and two scalar fields, the
    density and internal energy

    """

    def __init__(self, velocity, density, internal_energy):
        self.__velocity = velocity
        self.__density = density
        self.__internal_energy = internal_energy

    def velocity(self, position):
        return self.__velocity(position)

    def density(self, position):
        return self.__density(position)

    def internal_energy(self, position):
        return self.__internal_energy(position)


def approximate_gas(gas, grid, obstacles=None):
    """Approximate a continuous gas using a discrete grid"""
    for grid_point in grid:
        valid = True
        if obstacles:
            valid = not any(
                obstacle.inside(grid_point) for obstacle in obstacles)
        if valid:
            yield gas.create_cell(grid_point)


class InconsistentGridError(Exception):
    """Raised when a grid is found to be inconsistent."""
    pass


class CellCollection(object):
    """
    Abstract base class for collections of cells. These should also
    implement the iterator protocol to iterate over the cells.

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def check(self):
        pass


class ListCellCollection(list, CellCollection):
    """
    This implements the CellCollection as a simple list.

    """

    def check(self):
        """
        Do a self-consistency check. Should raise an exception upon
        encountering anomalies.

        """
        positions = set()
        for cell in self:
            pos = tuple(float(x) for x in cell.position[:3])
            if pos in positions:
                raise InconsistentGridError('multiple cell position {0}'.format(pos))
            positions.add(pos)


class Obstacle(object):
    """
    This represents a solid obstacle within the simulation domain acting as an
    arbitrarily shaped reflective boundary condition.

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def inside(self, position):
        """
        Determines whether a certain position is inside the obstacle's domain,
        i.e. either within its solid or within the area designated for the
        adjacent fluid cells.

        """
        pass


def make_obstacle_cells(obstacle, background_gas):
    """Generate cells for an obstacle

    The return value is a tuple (fluids, solids) containing a list of the fluid
    and solid cells generated. The solid cells are filled with a default
    UniformGas, while the fluid cells require a background gas to be
    approximated.

    """
    uniform = UniformGas()
    fluids = list(map(
        lambda x: background_gas.create_cell(x, 'solid_adjacent'), obstacle.fluids))
    solids = list(map(
        lambda x: uniform.create_cell(x, 'solid'), obstacle.solids))
    return fluids, solids


def make_mesh(gas, grid, obstacles=None, extras=None):
    """Create a whole mesh

    This is a convenience function that takes care of the entire mesh
    generation process, such as discretising the gas distribution onto a grid.
    It also generates obstacles and consider extra particles.

    """
    return (
        list(approximate_gas(gas, grid, obstacles))
        + list(chain(*[
            chain(*make_obstacle_cells(obstacle, gas))
            for obstacle in (obstacles or [])
        ]))
        + list(chain(*(extras or [])))
    )
