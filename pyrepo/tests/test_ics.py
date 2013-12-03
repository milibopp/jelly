"""
Tests of initial conditions file output.

"""

import struct
from nose.tools import assert_equal, raises

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
