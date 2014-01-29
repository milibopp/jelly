'''Small script to generate a rectangular grid with jelly.'''

import sys

from jelly.ics import write_icfile
from jelly.model import Mesh
from jelly.util import CartesianGrid2D


def main():
    # Parse command line arguments
    try:
        fname = sys.argv[1]
    except:
        fname = 'test.dat'
    # Generate ICs
    mesh = Mesh(CartesianGrid2D((0.0, 0.0), (2.0, 2.0), 16, 16), boxsize=2.0)
    with open(fname, 'wb') as icfile:
        write_icfile(icfile, mesh)


if __name__ == '__main__':
    main()
