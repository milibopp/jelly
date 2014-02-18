"""
jelly example script - background gas with obstacle

This script demonstrates the use of a circular obstacle within the initial
conditions.

"""

from jelly.ics import write_icfile
from jelly.model import Mesh, UniformGas
from jelly.util import CartesianGrid2D, Box, CircularObstacle
from jelly.vector import Vector


# Setup gas and grid
gas = UniformGas()
grid = CartesianGrid2D(
        Box(Vector(0.0, 0.0), Vector(1.0, 1.0)),
        (32, 32))

# Setup a circular obstacle
circle = CircularObstacle(
        center=Vector(0.5, 0.5),
        radius=0.1,
        n_phi=100)

# Combine everything into a mesh
mesh = Mesh(gas, grid, [circle])

# Write the mesh to a file
with open('obstacle.dat', 'wb') as icfile:
    write_icfile(icfile, mesh)
