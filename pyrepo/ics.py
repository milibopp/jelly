"""
Initial conditions generator for Arepo.

## File format

This is the legacy Gadget-2 file format encoded with f77 unformatted. We
specialize it for use with Arepo, only using one type of particle and one file.

### Header

The header is a 256 bytes long zero-padded section at the beginning of the
file.

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

"""

import struct
from abc import ABCMeta

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
        padding = '\x00' * (pad - size)
        return suffix + raw_block + padding + suffix
    else:
        suffix = struct.pack('i', size)
        return suffix + raw_block + suffix


def make_header(n_part, mass_arr, time, redshift, flag_sfr, flag_feedback,
                n_all, flag_cooling, num_files, box_size):
    """
    Make a header block. This is a very thin wrapper around the Gadget-2 header
    format. The parameters correspond directly to the parameters in the
    specification found in the Gadget-2 manual.

    """
    inner = bytearray()
    inner += struct.pack('I' * 6, *n_part)
    inner += struct.pack('d' * 6, *mass_arr)
    inner += struct.pack('ddii', time, redshift, flag_sfr, flag_feedback)
    inner += struct.pack('i' * 6, *n_all)
    inner += struct.pack('iid', flag_cooling, num_files, box_size)
    return make_f77_block(inner, 256)


def make_default_header(n_types, box_size=1.0, time=0.0, redshift=0.0,
                        flag_sfr=0, flag_feedback=0, flag_cooling=0):
    """Make a header with some reasonable default assumptions."""
    mass_arr = (0.0,) * 6
    num_files = 1
    return make_header(n_types, mass_arr, time, redshift, flag_sfr,
                       flag_feedback, n_types, flag_cooling, num_files,
                       box_size)


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


def iterate_ids(mesh):
    """Iterates over the computed IDs of a given mesh"""
    counter = {
        'normal': 0,
        'solid': 30000000,
        'solid_adjacent': 40000000}
    for category in mesh.quantity_iterator('category'):
        yield counter[category]
        counter[category] += 1


def count_types(mesh):
    """
    Count the cell types in a mesh

    :mesh: The mesh to be counted

    """
    ntypes = [0] * 6
    for cell in mesh.cells:
        if cell.category in ['normal', 'solid', 'solid_adjacent']:
            ntypes[0] += 1
        elif cell.category == 'nbody':
            ntypes[4] += 1
    return ntypes


def write_icfile(file_like, mesh):
    """Write an initial conditions file"""
    ntypes = [len(list(mesh.cells))] + [0] * 5
    file_like.write(make_default_header(ntypes, mesh.boxsize))
    file_like.write(make_body('fff', mesh.quantity_iterator('position')))
    file_like.write(make_body('fff', mesh.quantity_iterator('velocity')))
    file_like.write(make_body('I', iterate_ids(mesh)))
    file_like.write(make_body('f', mesh.quantity_iterator('density')))
    file_like.write(make_body('f', mesh.quantity_iterator('internal_energy')))
    file_like.write(make_body('f', mesh.quantity_iterator('density')))
