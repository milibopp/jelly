'''Small script to generate a rectangular grid with pyrepo.'''

import sys

from pyrepo.ics import ICWriter
from pyrepo.model import Mesh
from pyrepo.util import CartesianGrid2D


def main():
    # Parse command line arguments
    try:
        fname = sys.argv[1]
    except:
        fname = 'test.dat'
    # Generate ICs
    mesh = Mesh(CartesianGrid2D((0.0, 0.0), (2.0, 2.0), 16, 16), boxsize=2.0)
    ICWriter(open(fname, 'wb')).write(mesh)


if __name__ == '__main__':
    main()
