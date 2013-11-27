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


class BinaryBlock(object):
    """A binary block of an initial conditions file."""

    __metaclass__ = ABCMeta


class ICWriter(object):

    def __init__(self, file_name):
        self.file_name = file_name

    def __attribute_block(self, cells, fmt, getter):
        """Builds a block based on simple attributes of the cells."""
        block = bytearray()
        for cell in cells:
            block += struct.pack(fmt, *getter(cell))
        return block

    def write(self, mesh):
        """Writes the given mesh to a file."""
        # Total number of particles
        cells = list(mesh.cells)
        gas = filter(lambda cell: cell.category == 'normal', cells)
        solid = filter(lambda cell: cell.category == 'solid', cells)
        solid_adjacent = filter(lambda cell: cell.category == 'solid_adjacent', cells)
        N = len(cells)
        solid_min = 30000000
        solidn_min = 40000000
        # Compile the header
        header_parts = [
            ('I' * 6, [N] + [0] * 5),    # Npart
            ('d' * 6, [0.0] * 6),        # Massarr
            ('ddii', [0.0, 0.0, 0, 0]),  # Time, Redshift, FlagSfr,
                                         # FlagFeedback
            ('i' * 6, [N] + [0] * 5),    # Nall
            ('ii', [0, 1]),              # FlagCooling, NumFiles
            ('d', [mesh.boxsize])]       # BoxSize
        header = bytearray()
        for fmt, data in header_parts:
            header += struct.pack(fmt, *data)
        header = header + bytes('\x00') * (256 - len(header))
        # Compile the body
        chunks = [header]
        # Position & velocity
        chunks.append(self.__attribute_block(
            cells, 'fff', lambda c: c.position))
        chunks.append(self.__attribute_block(
            cells, 'fff', lambda c: c.velocity))
        # Special treatment to generate IDs
        id_block = bytearray()
        for i, cell in enumerate(gas):
            id_block += struct.pack('I', i)
        for i, cell in enumerate(solid):
            id_block += struct.pack('I', i + solid_min)
        for i, cell in enumerate(solid_adjacent):
            id_block += struct.pack('I', i + solidn_min)
        chunks.append(id_block)
        # Density & internal energy
        chunks.append(self.__attribute_block(
            cells, 'f', lambda c: [c.density]))
        chunks.append(self.__attribute_block(
            cells, 'f', lambda c: [c.internal_energy]))
        chunks.append(self.__attribute_block(
            cells, 'f', lambda c: [c.density]))
        # Write everything to file
        with open(self.file_name, 'wb') as icfile:
            for chunk in chunks:
                size = len(chunk)
                icfile.write(struct.pack('i', size))
                icfile.write(chunk)
                icfile.write(struct.pack('i', size))


class ICFileHeader(object):
    """The header of an IC file. This is a helper object of the IC writer."""
    pass


def write_icfile(file_name, mesh):
    """Writes an initial conditions file."""
    # Generate header and body of the file
    header = ICFileHeader(mesh)
    body = ICFileBody(mesh)
    # Write to file
    with open(file_name, 'wb') as icfile:
        for block in [header.binary, body.position, body.velocity, body.ids,
                      body.density, body.internal_energy, body.density]:
            size = len(block)
            icfile.write(struct.pack('i', size))
            icfile.write(block)
            icfile.write(struct.pack('i', size))
