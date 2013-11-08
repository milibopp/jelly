'''
Concrete implementations of the abstraction model.

'''

from itertools import product

from .model import CellCollection, VoronoiCell


class CartesianGrid2D(CellCollection):
    '''
    A 2D rectangular Cartesian grid spanning from point *p1* to *p2*. The grid
    is divided into *nx* and *ny* cells in each direction.

    It uses the functions *frho*, *fvel* and *fu* to fix the hydrodynamic
    quantities.

    Example:

    >>> grid = CartesianGrid2D((0.0, 0.0), (2.0, 3.0), 16, 24)

    '''

    def __init__(self, p1, p2, nx, ny, frho=None, fvel=None, fu=None):
        self.__p1 = p1
        self.__p2 = p2
        self.__nx = nx
        self.__ny = ny
        self.__frho = frho
        self.__fvel = fvel
        self.__fu = fu

    @property
    def cells(self):
        '''
        Iterates over the cartesian grid.

        >>> grid = CartesianGrid2D((0.0, 0.0), (1.0, 1.0), 2, 2)
        >>> cells = list(grid.cells)
        >>> cells[0].position
        (0.0, 0.0, 0.0)
        >>> cells[3].position
        (0.5, 0.5, 0.0)

        '''
        # Unpack
        x1, y1 = self.__p1
        x2, y2 = self.__p2
        # Order
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        # Deltas
        dx = x2 - x1
        dy = y2 - y1
        # Default functions
        def unity(x, y, z):
            return 1.0
        def zerovector(x, y, z):
            return 0.0, 0.0, 0.0
        frho = self.__frho or unity
        fvel = self.__fvel or zerovector
        fu = self.__fu or unity
        # Yield cells
        for kx, ky in product(range(self.__nx), range(self.__ny)):
            pos = kx * dx / self.__nx, ky * dy / self.__ny, 0.0
            vel = fvel(*pos)
            rho = frho(*pos)
            u = fu(*pos)
            yield VoronoiCell(pos, vel, rho, u)

    def check(self):
        '''
        Do some self-consistency checks.

        '''
        assert self.__n1 > 0
        assert self.__n2 > 0
        assert len(self.__p1) == 2
        assert len(self.__p2) == 2
        for p1, p2 in zip(self.__p1, self.__p2):
            assert p1 < p2

    @property
    def limits(self):
        '''
        The limits of the grid. This is equivalent to the corresponding
        parameter supplied to the constructor.

        >>> grid = CartesianGrid2D((0.0, -1.0), (1.0, 2.0), 16, 16)
        >>> grid.limits
        ((0.0, -1.0), (1.0, 2.0))

        '''
        return self.__p1, self.__p2
