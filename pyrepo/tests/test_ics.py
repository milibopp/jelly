"""
Tests of initial conditions file output.

"""

import struct
from nose.tools import assert_equal, raises
import random
from collections import namedtuple
from operator import attrgetter
from itertools import imap

from pyrepo.ics import *
from pyrepo.model import Cell, Mesh


def test_make_f77_block():
    """Plain F77-unformatted block"""
    f77_block = make_f77_block(bytes('asdf'))
    assert_equal(
        f77_block,
        '\x04\x00\x00\x00asdf\x04\x00\x00\x00'
    )


def test_make_f77_block_padded():
    """F77-unformatted block with padding"""
    f77_block_padded = make_f77_block(bytes('asdf'), 10)
    assert_equal(
        f77_block_padded,
        '\x0a\x00\x00\x00asdf\x00\x00\x00\x00\x00\x00\x0a\x00\x00\x00'
    )


@raises(ValueError)
def test_make_f77_block_padding_too_small():
    """F77-unformatted block with too small padding"""
    f77_block_padded = make_f77_block(bytes('blah'), 2)


def test_make_header():
    """Make a header block"""
    header = make_header(
        n_part=(100, 0, 0, 0, 0, 0),
        mass_arr=(0.0,) * 6,
        time=0.0,
        redshift=0.0,
        flag_sfr=0,
        flag_feedback=0,
        n_all=(100, 0, 0, 0, 0, 0),
        flag_cooling=0,
        num_files=1,
        box_size=1.0
    )
    assert_equal(header[4:8], '\x64' + '\x00' * 3)
    assert_equal(header[8:28], '\x00' * 20)
    assert_equal(header[100:104], '\x64' + '\x00' * 3)
    assert_equal(header[128:132], '\x01' + '\x00' * 3)
    assert_equal(len(header), 264)


def test_make_default_header():
    """Make a default header block"""
    header = make_default_header((100, 0, 0, 4, 0, 0), 1.0, 0.0)
    assert_equal(header[4:8], '\x64' + '\x00' * 3)
    assert_equal(header[16:20], '\x04' + '\x00' * 3)
    assert_equal(header[100:104], '\x64' + '\x00' * 3)
    assert_equal(header[128:132], '\x01' + '\x00' * 3)
    assert_equal(len(header), 264)


def test_body_block_vector():
    """Vectorial body block"""
    data = [(0, 0, 0), (1, 0, 0), (2, -1, 0)]
    fmt = 'ddd'
    body = make_body(fmt, data)
    assert_equal(body[:4], struct.pack('i', 72))
    assert_equal(body[4:12], struct.pack('d', 0))
    assert_equal(body[52:60], struct.pack('d', 2))


def test_body_block_scalar():
    """Scalar body block"""
    data = [1, 7, 8, -4]
    fmt = 'i'
    body = make_body(fmt, data)
    assert_equal(body[:4], struct.pack('i', 16))
    assert_equal(body[8:12], struct.pack('i', 7))


def _random_mesh():
    """
    Generate a random mesh for testing purposes

    """
    def rnd_tuple(n):
        return tuple(random.uniform(0, 1) for _ in range(n))

    def rnd_cell(category='normal'):
        pos = rnd_tuple(3)
        vel = rnd_tuple(3)
        rho = random.uniform(0, 1)
        u = random.uniform(0, 1)
        return Cell(pos, vel, rho, u, category)

    cells = ListCellCollection(rnd_cell() for _ in range(10))
    return Mesh(cells)


def get_positions(mesh):
    """Obtain an iterable of the cell positions"""
    return imap(attrgetter('position'), mesh.cells)


def test_iterate_position():
    """Iterate positions in mesh"""
    mesh = _random_mesh()
    positions = get_positions(mesh)
    assert_equal(next(positions), next(mesh.cells).position)


def test_mesh_conversion():
    """Convert mesh into IC file data structure"""
    mesh = _random_mesh()
    # Implement
    icmesh_cls = namedtuple(
        'ICMesh',
        ['header', 'position', 'velocity', 'id', 'density', 'internal_energy'])

    def ICMesh(mesh):
        position = get_positions(mesh)
        return icmesh_cls(0, position, 0, 0, 0, 0)

    icmesh = ICMesh(mesh)
    # Assert
    assert 0 <= next(icmesh.position)[0] <= 10
