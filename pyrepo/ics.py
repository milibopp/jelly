'''
Initial conditions generator for Arepo.

## File format

This is the legacy Gadget-2 file format encoded with f77 unformatted. We
specialize it for use with Arepo, only using one type of particle and one file.

### Header

The header is a 256 bytes long zero-padded section at the beginning of the file.

The following are the relevant quantities to be set. Integers are 4 bytes,
floats are 8 bytes.

- npart -- number of particles of each type
    - set to [N, 0 ...]
- massarr -- masses of particle types
    - set to [0.0, 0.0 ...]
- time = 0.0D
- redshift = 0.0D
- flag_sfr = 0L
- flag_feedback = 0L
- npartall = npart
- flag_cooling = 0L
- num_files = 1L
- BoxSize -- size of boundary box for periodic boundary conditions

### Body

The body consists of blocks of data, representing different quantities
associated with the particles. Data types are 4-byte float and 4-byte unsigned
integer (uint).

- pos float[N][3] -- position vectors
- vel float[N][3] -- velocity vectors
- id uint[N] -- particle IDs
- masses ("rho") float[N] -- particle masses
- u float[n] -- particle internal energies
- rho float[n] -- particle densities

'''

from abc import abstractmethod, ABCMeta
from itertools import product


class VoronoiCell:
    '''A moving-mesh hydrodynamics Voronoi cell.'''
    
    def __init__(self, position, velocity, cell_id, mass, density, internal_energy):
        self.position = position
        self.velocity = velocity
        self.cell_id = cell_id
        self.mass = mass
        self.density = density
        self.internal_energy = internal_energy


class Mesh:
    
    def __init__(self, cells):
        self.cells = cells

    @classmethod
    def rectangular(cls, p1, p2, nx, ny, frho=None, fvel=None, fu=None):
        '''
        Generates a 2D rectangular Cartesian mesh spanning from point *p1* to
        *p2*. The grid is divided into *nx* and *ny* cells in each direction.
        
        It uses the functions *frho*, *fvel* and *fu* to fix the hydrodynamic
        quantities.

        >>> grid = Mesh.rectangular((0.0, 0.0), (1.0, 1.0), 2, 2)
        >>> grid.cells[0].position
        (0.25, 0.25, 0.0)

        '''
        # Unpack
        x1, y1 = p1
        x2, y2 = p2
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
        frho = frho or unity
        fvel = fvel or zerovector
        fu = fu or unity
        # Create cells
        cells = []
        id_counter = 0
        for kx, ky in product(range(nx), range(ny)):
            pos = (kx + 0.5) * dx / nx, (ky + 0.5) * dy / ny, 0.0
            vel = fvel(*pos)
            rho = frho(*pos)
            u = fu(*pos)
            cells.append(VoronoiCell(pos, vel, id_counter, rho, rho, u))
            id_counter += 1
        # Create mesh
        return cls(cells)


class InitialConditions(metaclass=ABCMeta):
    '''Abstract initial conditions.'''

    @property
    @abstractmethod
    def cells(self):
        '''Returns a list of Voronoi cells.'''
        pass
