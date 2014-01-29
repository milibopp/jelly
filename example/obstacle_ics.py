"""
This script generates a 2D Cartesian grid with a circular obstacle in the
center and exports this as initial conditions.

"""

from jelly.ics import write_icfile
from jelly.model import Mesh
from jelly.util import CartesianGrid2D, CircularObstacle


if __name__ == '__main__':
    # Generate the initial conditions
    rho = lambda x, y, z: 1.0
    v = lambda x, y, z: (0.0, 0.0, 0.0)
    u = lambda x, y, z: 1.0
    grid = CartesianGrid2D((0, 0), (2, 2), 100, 100, v, rho, u)
    circle = CircularObstacle((1, 1), 0.1, v, rho, u, 100)
    mesh = Mesh(grid, [circle])
    # Write to file
    with open('test.dat', 'wb') as icfile:
        write_icfile(icfile, mesh)
