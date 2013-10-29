'''Small script to generate a rectangular grid with pyrepo.'''

import sys

from pyrepo.ics import Mesh2D, ICWriter


def main():
    # Parse command line arguments
    try:
        fname = sys.argv[1]
    except:
        fname = 'test.dat'
    # Generate ICs
    grid = Mesh2D.rectangular((0.0, 0.0), (2.0, 2.0), 16, 16)
    ICWriter(open(fname, 'wb')).write(grid)


if __name__ == '__main__':
    main()
