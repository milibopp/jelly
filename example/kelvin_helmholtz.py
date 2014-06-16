"""
jelly example script - Kelvin-Helmholtz instability

This illustrates the generation of input data for a very common hydrodynamical
test problem, the Kelvin-Helmholtz instability.

"""

from __future__ import division
from math import pi, exp, sin, sqrt
from jelly.ics import write_icfile
from jelly.model import make_mesh, FunctionalGas
from jelly.util import CartesianGrid2D, Box
from jelly.vector import Vector


def gauss(x, mu, omega):
    """Gauss function (non-normalized)"""
    return exp(-((x - mu) / (2 * omega)) ** 2)


def kh_velocity(x):
    vy0, omega = 0.1, 0.05 / sqrt(2)
    bulk = Vector(1, 0, 0) * (-0.5 if 0.25 < x[1] < 0.75 else 0.5)
    excite = Vector(0, 1, 0) * (
        vy0 * sin(4 * pi * x[0]) *
        (gauss(x[1], 0.25, omega) + gauss(x[1], 0.75, omega))
    )
    return bulk + excite


def kh_density(x):
    return 2 if 0.25 < x[1] < 0.75 else 1


def kh_internal_energy(x):
    return 2.5 / (kh_density(x) * (5/3 - 1))


if __name__ == "__main__":
    # Describe the initial conditions using a couple of functions
    gas = FunctionalGas(
        density=kh_density, velocity=kh_velocity,
        internal_energy=kh_internal_energy)

    # Create a grid, on which the gas is to be approximated
    grid = CartesianGrid2D(Box(Vector(0, 0), Vector(1, 1)), (128, 128))

    # Now generate the mesh...
    mesh = make_mesh(gas, grid)

    # ...and write it to a file
    with open("kh_instab.dat", "wb") as icfile:
        write_icfile(icfile, mesh, double=True)
