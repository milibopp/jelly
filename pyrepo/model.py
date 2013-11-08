'''
Abstraction model of an Arepo setup. This module contains several utilities
that abstract and thereby facilitate the construction of an initial conditions
file for Arepo.

Among these utilities one can find quantities described by a function of the
cell's coordinates, solid objects used for special boundaries etc.

'''

from __future__ import division
from abc import ABCMeta, abstractproperty, abstractmethod


class VoronoiCell(object):
    '''
    A moving-mesh hydrodynamics Voronoi cell. This is the fundamental
    component of the grid, once it is established. In principle, this can also
    function as a more general particle.

    >>> cell = VoronoiCell((0, 1, -2), (-3, 7, 4), 6.2, 3.1)
    >>> cell.position
    (0, 1, -2)
    >>> cell.velocity
    (-3, 7, 4)
    >>> cell.density
    6.2
    >>> cell.internal_energy
    3.1

    '''

    def __init__(self, position, velocity, density, internal_energy):
        self.position = position
        self.velocity = velocity
        self.density = density
        self.internal_energy = internal_energy


class InconsistentGridError(Exception):
    '''Raised when a grid is found to be inconsistent.'''
    pass


class CellCollection(object):
    '''
    A collection of cells.

    '''

    __metaclass__ = ABCMeta

    @abstractproperty
    def cells(self):
        '''
        Returns a collection or an iterable containing the cells.

        '''
        pass

    @abstractmethod
    def check(self):
        '''
        Do a self-consistency check. Should raise an exception upon
        encountering anomalies.

        '''
        pass

    @abstractproperty
    def limits(self):
        '''
        The limits of this collection. This should be two tuples describing the
        minimum and maximum coordinates on each axis.

        '''
        pass


class ListCellCollection(CellCollection):
    '''
    This implements the cell collection using a simple list internally.

    >>> cell = VoronoiCell((0, 1, 2), (3, 4, 5), 1.0, 2.0)
    >>> collection = ListCellCollection([cell])
    >>> assert collection.cells[0] is cell

    '''

    def __init__(self, cells=None):
        self.__cells = list(cells) if cells else list()

    @property
    def cells(self):
        '''The list of cells in the collection.'''
        return self.__cells

    def check(self):
        '''
        Do a self-consistency check. Should raise an exception upon
        encountering anomalies.

        >>> cells = [VoronoiCell((0, 9, 2), (3, 4, 5), 1.1, 2.0),
        ...          VoronoiCell((0, 1, 2), (-3, 7, 5), 1.3, 1.7)]
        >>> collection = ListCellCollection(cells)
        >>> collection.check()

        For instance, identical positions are not allowed:

        >>> cells = [VoronoiCell((0, 1, 2), (3, 4, 5), 1.1, 2.0),
        ...          VoronoiCell((0, 1, 2), (-3, 7, 5), 1.3, 1.7)]
        >>> collection = ListCellCollection(cells)
        >>> collection.check()
        Traceback (most recent call last):
            ...
        InconsistentGridError: multiple cell position (0.0, 1.0, 2.0)

        '''
        positions = set()
        for cell in self.__cells:
            pos = tuple(float(x) for x in cell.position[:3])
            if pos in positions:
                raise InconsistentGridError('multiple cell position {}'.format(pos))
            positions.add(pos)

    @property
    def limits(self):
        pass


class Mesh(object):
    '''
    The mesh is the top-level object containing the information required to
    describe an initial conditions file (or a snapshot).

    '''

    def __init__(self, gas, boxsize=1.0):
        self.gas = gas
        self.boxsize = boxsize
