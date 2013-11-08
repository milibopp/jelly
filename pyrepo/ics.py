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

import struct

from .model import ListCellCollection


class ICWriter(object):

    def __init__(self, output_buffer):
        self.output_buffer = output_buffer

    def write(self, mesh):
        '''Writes the given mesh to a file.'''
        # Total number of particles
        cells = list(mesh.gas.cells)
        N = len(cells)
        # Compile the header
        header_parts = [
            ('I' * 6, [N] + [0] * 5),   # Npart
            ('d' * 6, [0.0] * 6),       # Massarr
            ('ddii', [0.0, 0.0, 0, 0]), # Time, Redshift, FlagSfr, FlagFeedback
            ('i' * 6, [N] + [0] * 5),   # Nall
            ('ii', [0, 1]),             # FlagCooling, NumFiles
            ('d', [mesh.boxsize])]      # BoxSize
        header = bytearray()
        for fmt, data in header_parts:
            header += struct.pack(fmt, *data)
        header = header + bytes('\x00') * (256 - len(header))
        # Compile the body
        chunks = [header]
        block_specs = [
            ('fff', lambda c, i: c.position),
            ('fff', lambda c, i: c.velocity),
            ('I', lambda c, i: [i]),
            ('f', lambda c, i: [c.density]),
            ('f', lambda c, i: [c.internal_energy]),
            ('f', lambda c, i: [c.density]),
        ]
        for fmt, getter in block_specs:
            body = bytearray()
            gas_i = 0
            for cell in cells:
                body += struct.pack(fmt, *getter(cell, gas_i))
                gas_i += 1
            chunks.append(body)
        # Write everything to file
        for chunk in chunks:
            size = len(chunk)
            self.output_buffer.write(struct.pack('i', size))
            self.output_buffer.write(chunk)
            self.output_buffer.write(struct.pack('i', size))
