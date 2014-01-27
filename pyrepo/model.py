"""
Abstraction model of an Arepo setup. This module contains several utilities
that abstract and thereby facilitate the construction of an initial conditions
file for Arepo.

Among these utilities one can find quantities described by a function of the
cell's coordinates, solid objects used for special boundaries etc.

"""

from __future__ import division
from abc import ABCMeta, abstractproperty, abstractmethod

from .vector import Vector


class Cell(object):
    """
    A moving-mesh hydrodynamics Voronoi cell. This is the fundamental
    component of the grid, once it is established.

    In principle, this can also function as a more general particle. This is
    what the `category` attribute is intended to cover. For instance, while the
    default category is 'normal', cells making up solid obstacles are
    categorized as 'solid'.

    Usage:

    >>> cell = Cell((0, 1, -2), (-3, 7, 4), 6.2, 3.1)
    >>> cell.position
    (0, 1, -2)
    >>> cell.velocity
    (-3, 7, 4)
    >>> cell.density
    6.2
    >>> cell.internal_energy
    3.1
    >>> cell.category
    'normal'

    """

    def __init__(self, position, velocity, density, internal_energy,
                 category='normal'):
        self.position = position
        self.velocity = velocity
        self.density = density
        self.internal_energy = internal_energy
        self.category = category


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

    def create_cell(self, position):
        """Create a gas cell at a given position"""
        return Cell(
            position,
            self.velocity(position),
            self.density(position),
            self.internal_energy(position),
            'normal')


class UniformGas(Gas):
    """
    A uniform background gas

    This gas has zero velocity and a constant density and internal energy of
    one.

    """

    def __init__(self,
            velocity=Vector(0.0, 0.0, 0.0),
            density=1.0,
            internal_energy=1.0
            ):
        self.__velocity = velocity
        self.__density = density
        self.__internal_energy = internal_energy

    def velocity(self, position):
        return self.__velocity

    def density(self, position):
        return self.__density

    def internal_energy(self, position):
        return self.__internal_energy


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

        >>> cells = [Cell((0, 9, 2), (3, 4, 5), 1.1, 2.0),
        ...          Cell((0, 1, 2), (-3, 7, 5), 1.3, 1.7)]
        >>> collection = ListCellCollection(cells)
        >>> collection.check()

        For instance, identical positions are not allowed:

        >>> cells = [Cell((0, 1, 2), (3, 4, 5), 1.1, 2.0),
        ...          Cell((0, 1, 2), (-3, 7, 5), 1.3, 1.7)]
        >>> collection = ListCellCollection(cells)
        >>> collection.check()
        Traceback (most recent call last):
            ...
        InconsistentGridError: multiple cell position (0.0, 1.0, 2.0)

        """
        positions = set()
        for cell in self:
            pos = tuple(float(x) for x in cell.position[:3])
            if pos in positions:
                raise InconsistentGridError('multiple cell position {}'.format(pos))
            positions.add(pos)


class Obstacle(CellCollection):
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


class Mesh(object):
    """
    The mesh is the top-level object containing the information required to
    describe an initial conditions file (or a snapshot).

    """

    def __init__(self, gas, obstacles=None, extras=None, boxsize=1.0):
        self.gas = gas
        self.obstacles = obstacles or list()
        self.extras = extras or list()
        self.boxsize = boxsize

    def __outside_obstacles(self, cell):
        """
        Tests, whether a given cell does intersect with any obstacle.

        """
        for obstacle in self.obstacles:
            if obstacle.inside(cell.position):
                return False
        return True

    @property
    def cells(self):
        """
        All cells of this mesh. This basically wraps up all gas (dynamically
        excluding everything inside some obstacle) and the cells making up
        obstacles.

        """
        for cell in self.gas:
            if self.__outside_obstacles(cell):
                yield cell
        for obstacle in self.obstacles:
            for cell in obstacle:
                yield cell
        for extra in self.extras:
            for cell in extra:
                yield cell
