"""
jelly example script - simple constant gas

This is a trivial example for setting up initial conditions with jelly using a
constant gas distribution and approximating this with a rectangular grid.

"""

import sys

from jelly.ics import write_icfile
from jelly.model import Mesh, UniformGas
from jelly.util import CartesianGrid2D, Rectangle
from jelly.vector import Vector


# Describe a uniform gas distribution
gas = UniformGas(
        velocity=Vector(0.0, 0.0, 0.0),
        density=2.0,
        internal_energy=1.0)

# Setup a grid to approximate the continuous gas
grid = CartesianGrid2D(
        Rectangle(Vector(0.0, 0.0), Vector(2.0, 2.0)),
        (16, 16))

# Combine everything into a mesh
mesh = Mesh(gas, grid, boxsize=2.0)

# Write the mesh to a file
with open('simple_mesh.dat', 'wb') as icfile:
    write_icfile(icfile, mesh)
