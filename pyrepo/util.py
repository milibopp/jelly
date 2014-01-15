"""
Concrete implementations of the abstraction model.

"""

from __future__ import division

from itertools import product
from math import pi, sin, cos
from collections import namedtuple

from .model import CellCollection, Cell, Obstacle
from .vector import Vector


Rectangle = namedtuple('Rectangle', ['position', 'size'])


class CartesianGrid2D(CellCollection):
    """
    A 2D rectangular Cartesian grid spanning from point *p1* to *p2*. The grid
    is divided into *nx* and *ny* cells in each direction.

    It uses the functions *frho*, *fvel* and *fu* to fix the hydrodynamic
    quantities.

    Example:

    >>> grid = CartesianGrid2D((0.0, 0.0), (2.0, 3.0), 16, 24)

    """

    def __init__(self, box, nx, ny, fvel=None, frho=None, fu=None):
        self.box = box
        self.__nx = nx
        self.__ny = ny
        self.__fvel = fvel
        self.__frho = frho
        self.__fu = fu

    def __iter__(self):
        """
        Iterates over the cartesian grid.

        >>> grid = CartesianGrid2D((0.0, 0.0), (1.0, 1.0), 2, 2)
        >>> positions = map(lambda c: c.position, grid)
        >>> assert (0.25, 0.75, 0.0) in positions
        >>> assert (0.75, 0.75, 0.0) in positions

        """
        # Unpack
        x1, y1 = self.box.position
        x2, y2 = self.box.position + self.box.size
        # Order
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        # Deltas
        dx = x2 - x1
        dy = y2 - y1
        # Default functions
        unity = lambda x: 1.0
        zerovector = lambda x: Vector(0.0, 0.0, 0.0)
        frho = self.__frho or unity
        fvel = self.__fvel or zerovector
        fu = self.__fu or unity
        # Yield cells
        for kx, ky in product(range(self.__nx), range(self.__ny)):
            pos = Vector((kx + 0.5) * dx / self.__nx, (ky + 0.5) * dy / self.__ny, 0.0)
            vel = fvel(pos)
            rho = frho(pos)
            u = fu(pos)
            yield Cell(pos, vel, rho, u)

    def check(self):
        """
        Do some self-consistency checks.

        """
        assert self.__n1 > 0
        assert self.__n2 > 0
        assert len(self.__p1) == 2
        assert len(self.__p2) == 2
        for p1, p2 in zip(self.__p1, self.__p2):
            assert p1 < p2


class CircularObstacle(Obstacle):
    """
    A two-dimensional circular obstacle described by a center and radius.
    Additionally, a `density_function` describing the density of the fluid
    adjacent to the obstacle may be supplied. Similarly
    `internal_energy_function` and `velocity_function` control their respective
    quantities in the surrounding fluid. The resolution of the circle is
    controlled via the parameter `n_phi`.

    """

    def __init__(self, center, radius, velocity_function=None,
                 density_function=None, internal_energy_function=None,
                 n_phi=100):
        self.center = center
        self.radius = radius
        self.density_function = density_function or (lambda x: 1.0)
        self.internal_energy_function = internal_energy_function or (lambda x: 1.0)
        self.velocity_function = velocity_function or (lambda x: (0.0, 0.0, 0.0))
        self.n_phi = n_phi

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
        return r * sin(phi) + self.center[0], r * cos(phi) + self.center[1], 0.0

    def __iter__(self):
        """Iterates over all cells making up the obstacle."""
        # TODO: test this properly
        for k in range(self.n_phi):
            x = self.__circle_position(k, False)
            v = self.velocity_function(x)
            rho = self.density_function(x)
            u = self.internal_energy_function(x)
            yield Cell(x, v, rho, u, category='solid_adjacent')
            yield Cell(self.__circle_position(k, True), (0.0, 0.0, 0.0), 1.0,
                       1.0, category='solid')

    def inside(self, position):
        """
        Checks whether a given position is inside the circle's domain.

        >>> circle = CircularObstacle((0.0, 0.0), 1.0)
        >>> circle.inside((2.0, 0.0))
        False
        >>> circle.inside((0.0, 0.0))
        True

        """
        dist = sum((self.center[i] - position[i]) ** 2.0 for i in [0, 1]) ** 0.5
        r_max = self.radius * (1 + 1.5 * self.__angle_segment)
        return dist < r_max

    def check(self):
        """Some sanity checks."""
        assert self.radius > 0
        assert type(n_phi) is int
        assert n_phi > 0
