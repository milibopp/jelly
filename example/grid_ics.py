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
    grid = Mesh2D.rectangular((-1.0, -1.0), (1.0, 1.0), 32, 32)
    ICWriter(fname).write(grid)


if __name__ == '__main__':
    main()
