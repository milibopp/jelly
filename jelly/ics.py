"""
Initial conditions generator for Arepo.

## File format

This is the legacy Gadget-2 file format encoded with f77 unformatted. We
specialize it for use with Arepo, only using one type of particle and one file.

### Header

The header is a 256 bytes long zero-padded section at the beginning of the
file.

The following are the relevant quantities to be set. Integers are 4 bytes,
floats are 8 bytes, flags are given as integers.

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
- Omega0 = 1.0D
- OmegaLambda = 0.0D
- HubbleParam = 70.0D
- flag_stellarage -- flags whether the file contains formation times of star particles
- flag_metals -- flags whether the file contains metallicity values for gas and star particles
- npartTotalHighWord -- High word of the total number of particles of each type
- flag_entropy_instead_u -- flags that IC-file contains entropy instead of u

Other fields not supported at the moment.


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

"""

import struct
import six
from abc import ABCMeta
from operator import attrgetter

from .model import ListCellCollection


def make_f77_block(raw_block, pad=None):
    """
    Make an F77-unformatted block out of raw binary data.

    If `pad` is set, the block is padded with zeros to the specified size in
    bytes excluding the suffixes.

    :param raw_block: raw binary data
    :param pad: zero-padded size of the block

    """
    size = len(raw_block)
    if pad:
        suffix = struct.pack('i', pad)
        if pad < size:
            raise ValueError('padding too small for data')
        padding = six.b('\x00') * (pad - size)
        return suffix + raw_block + padding + suffix
    else:
        suffix = struct.pack('i', size)
        return suffix + raw_block + suffix


def make_header(n_part, mass_arr, time, redshift, flag_sfr, flag_feedback,
                n_all, flag_cooling, num_files, box_size, omega0, omega_lambda,
                hubble_parameter, flag_stellarage, flag_metals, flag_entropy_instead_u):
    """
    Make a header block. This is a very thin wrapper around the Gadget-2 header
    format. The parameters correspond directly to the parameters in the
    specification found in the arepo all_vars header.

    """


    inner = bytearray()
    inner += struct.pack('i' * 6, *n_part)
    inner += struct.pack('d' * 6, *mass_arr)
    inner += struct.pack('ddii', time, redshift, flag_sfr, flag_feedback)
    inner += struct.pack('I' * 6, *n_all)
    inner += struct.pack('iid', flag_cooling, num_files, box_size)
    inner += struct.pack('ddd', omega0, omega_lambda, hubble_parameter)
    inner += struct.pack('ii', flag_stellarage, flag_stellarage)
    inner += struct.pack('I' * 6, *([0,] * 6))
    inner += struct.pack('i', flag_entropy_instead_u)
    return make_f77_block(inner, 256)


def make_default_header(n_types, time=0.0, redshift=0.0,
                        flag_sfr=0, flag_feedback=0, flag_cooling=0,
                        box_size=1.0, omega0 = 1.0, omega_lambda = 0.0, hubble_parameter = 70.0,
                        flag_stellarage = 0, flag_metals = 0, flag_entropy_instead_u = 0):
    """Make a header with some reasonable default assumptions."""
    mass_arr = (0.0,) * 6
    num_files = 1
    return make_header(n_types, mass_arr, time, redshift, flag_sfr,
                       flag_feedback, n_types, flag_cooling, num_files,
                       box_size, omega0, omega_lambda,
                       hubble_parameter, flag_stellarage, flag_metals, flag_entropy_instead_u)


def make_body(fmt, data):
    """
    Produces a body block. The format determines whether the data is treated as
    an iterable of actual values or as an iterable of tuple-like objects to be
    unpacked for binary formatting.

    :param fmt: format string for individual data
    :param data: iterable data
    :return: F77-unformatted binary block of the data
    :rtype: bytearray

    """
    inner = bytearray()
    if len(fmt) == 1:
        for datum in data:
            inner += struct.pack(fmt, datum)
    else:
        for datum in data:
            inner += struct.pack(fmt, *datum)
    return make_f77_block(inner)


def iterate_ids(cells):
    """
    Iterates over the computed IDs of a given mesh

    Normal gas cells start at 1, solid cells at 30000000, gas cells comoving
    with solids at 40000000.

    As a side effect this function assigns the IDs to the cells it iterates
    over.

    NOTE: never use zero as a cell ID, it causes the derefinement subroutines
    to crash, since they internally set the ID of removed cells to zero

    """
    counter = {
        'normal': 1,
        'solid': 30000000,
        'solid_adjacent': 40000000}
    for cell in cells:
        category = cell.category
        if category == 'nbody':
            category = 'normal' # Evil hack, fix this!
        yield counter[category]
        cell.ident = counter[category]
        counter[category] += 1


def get_type_of_cell(cell):
    """
    Determine the type of a cell

    """
    if cell.category in ['normal', 'solid', 'solid_adjacent']:
        return 0
    elif cell.category == 'nbody':
        return 4
    raise ValueError('cell has invalid category')


def count_types(cells):
    """
    Count the cell types in a mesh

    :mesh: The mesh to be counted

    """
    ntypes = [0] * 6
    for cell in cells:
        ntypes[get_type_of_cell(cell)] += 1
    return ntypes


def map_quantity(cells, attribute):
    """
    Map a list of cells to a list of its quantities

    The quantities are specified by the attribute name.

    """
    return map(attrgetter(attribute), cells)


def write_icfile(file_like, mesh):
    """Write an initial conditions file"""
    # Do the iteration once
    # TODO: This should be handled in a file to decrease its memory footprint
    # for large grids
    cells = sorted(mesh.cells, key=get_type_of_cell)
    ntypes = count_types(cells)
    file_like.write(make_default_header(ntypes, mesh.boxsize))
    file_like.write(make_body('fff', map_quantity(cells, 'position')))
    file_like.write(make_body('fff', map_quantity(cells, 'velocity')))
    file_like.write(make_body('I', iterate_ids(cells)))
    file_like.write(make_body('f', map_quantity(cells, 'density')))
    file_like.write(make_body('f', map_quantity(cells[:ntypes[0]], 'internal_energy')))
    file_like.write(make_body('f', map_quantity(cells[:ntypes[0]], 'density')))
