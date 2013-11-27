"""
Tests of initial conditions file output.

"""

import struct
from nose.tools import assert_equal, raises

from pyrepo.ics import *


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
