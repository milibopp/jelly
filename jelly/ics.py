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
from .id_assign import CompoundIDRange, IDRange


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
                hubble_parameter, flag_stellarage, flag_metals,
                flag_entropy_instead_u, flag_doubleprecision, flag_lpt_ics,
                lpt_scalingfactor, flag_tracer_field, composition_vector_length):
    """
    Make a header block. This is a very thin wrapper around the Gadget-2 header
    format. The parameters correspond directly to the parameters in the
    specification found in the arepo all_vars header.

    """

    n_all_binary = [struct.pack('L', i) for i in n_all]

    n_all_binary_higher = bytearray()
    n_all_binary_lower = bytearray()
    for i in n_all_binary:
        n_all_binary_higher += bytearray(i[4:])
        n_all_binary_lower += bytearray(i[:4])

    inner = bytearray()
    inner += struct.pack('i' * 6, *n_part)
    inner += struct.pack('d' * 6, *mass_arr)
    inner += struct.pack('ddii', time, redshift, flag_sfr, flag_feedback)
    inner += n_all_binary_lower
    inner += struct.pack('iid', flag_cooling, num_files, box_size)
    inner += struct.pack('ddd', omega0, omega_lambda, hubble_parameter)
    inner += struct.pack('ii', flag_stellarage, flag_metals)
    inner += n_all_binary_higher
    inner += struct.pack(
        'iiifii', flag_entropy_instead_u, flag_doubleprecision, flag_lpt_ics,
        lpt_scalingfactor, flag_tracer_field, composition_vector_length)
    return make_f77_block(inner, 256)


def make_default_header(
        n_types, time=0.0, redshift=0.0, flag_sfr=0, flag_feedback=0,
        flag_cooling=0, box_size=1.0, omega0=1.0, omega_lambda=0.0,
        hubble_parameter=70.0, flag_stellarage=0, flag_metals=0,
        flag_entropy_instead_u=0, flag_doubleprecision=0, flag_lpt_ics=0,
        lpt_scalingfactor=1.0, flag_tracer_field=0,
        composition_vector_length=0):
    """Make a header with some reasonable default assumptions."""
    mass_arr = (0.0,) * 6
    num_files = 1
    return make_header(
        n_types, mass_arr, time, redshift, flag_sfr, flag_feedback, n_types,
        flag_cooling, num_files, box_size, omega0, omega_lambda,
        hubble_parameter, flag_stellarage, flag_metals, flag_entropy_instead_u,
        flag_doubleprecision, flag_lpt_ics, lpt_scalingfactor,
        flag_tracer_field, composition_vector_length)


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


class DefaultIDRangeDispatcher(object):
    """The default dispatcher for Arepo IC generation

    By default, normal gas cells start at 1, solid cells at 30000000, gas cells
    comoving with solids at 40000000. Each of the ID ranges can be overridden.

    """

    def __init__(self, standard_range=None, solid_range=None,
                 solid_adjacent_range=None):
        self.standard_range = standard_range or IDRange(1, 29999999)
        self.solid_adjacent_range = (
            solid_adjacent_range or IDRange(30000000, 39999999))
        self.solid_range = solid_range or IDRange(40000000, 49999999)

    def dispatch(self, cell):
        """Dispatches cell to the appropriate ID range according to category"""
        if cell.category == 'nbody' or cell.category == 'normal':
            return self.standard_range
        if cell.category == 'solid':
            return self.solid_range
        if cell.category == 'solid_adjacent':
            return self.solid_adjacent_range
        raise ValueError('cell does not have valid category ({:s})'.format(cell.category))

    @property
    def components(self):
        """Component ID ranges"""
        yield self.standard_range
        yield self.solid_range
        yield self.solid_adjacent_range


def assign_ids(cells, id_range=None):
    """Assign IDs to cells and return ID range object

    This uses the DefaultIDRangeDispatcher by default, which can be overridden.

    """
    id_range = CompoundIDRange(DefaultIDRangeDispatcher())
    for cell in cells:
        id_range.assign_id(cell)
    return id_range


def iterate_ids(cells, id_range):
    """Iterates over IDs of given cells

    It uses an ID range and expects the IDs to be assigned.

    NOTE: never use zero as a cell ID, it causes the derefinement subroutines
    to crash, since they internally set the ID of removed cells to zero

    """
    return map(id_range.get_id, cells)


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


def write_icfile(file_like, cells, id_range=None, boxsize=1.0, double=False):
    """Write an initial conditions file"""
    # Do the iteration once
    # TODO: This should be handled in a file to decrease its memory footprint
    # for large grids
    cells = sorted(cells, key=get_type_of_cell)
    if not id_range:
        id_range = assign_ids(cells)
    ntypes = count_types(cells)
    fvec = 'ddd' if double else 'fff'
    fscal = 'd' if double else 'f'
    file_like.write(make_default_header(ntypes, boxsize, flag_doubleprecision=int(double)))
    file_like.write(make_body(fvec, map_quantity(cells, 'position')))
    file_like.write(make_body(fvec, map_quantity(cells, 'velocity')))
    file_like.write(make_body('I', iterate_ids(cells, id_range)))
    file_like.write(make_body(fscal, map_quantity(cells, 'density')))
    file_like.write(make_body(fscal, map_quantity(cells[:ntypes[0]], 'internal_energy')))
    file_like.write(make_body(fscal, map_quantity(cells[:ntypes[0]], 'density')))
