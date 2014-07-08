"""
Tests of initial conditions file output.

"""

import struct
from nose.tools import assert_equal, raises
from tempfile import NamedTemporaryFile
from hashlib import md5
import six
from mock import Mock

from jelly.ics import *
from jelly.model import Cell, UniformGas, make_mesh
from jelly.util import CartesianGrid2D, CircularObstacle, Box
from jelly.vector import Vector
from .test_model import make_random_mesh, make_mesh_with_nbody_cell


def mock_cell(category):
    """Helper function to create a mock cell with given category"""
    cell = Mock()
    cell.category = category
    return cell


class TestDefaultIDRangeDispatcher(object):

    def setup(self):
        self.id_range = DefaultIDRangeDispatcher()

    def test_dispatch_normal(self):
        the_range = self.id_range.dispatch(mock_cell('normal'))
        assert_equal(the_range.start, 1)

    def test_dispatch_nbody(self):
        the_range = self.id_range.dispatch(mock_cell('nbody'))
        assert_equal(the_range.start, 1)

    def test_dispatch_solid(self):
        the_range = self.id_range.dispatch(mock_cell('solid'))
        assert_equal(the_range.start, 40000000)

    def test_dispatch_solid_adjacent(self):
        the_range = self.id_range.dispatch(mock_cell('solid_adjacent'))
        assert_equal(the_range.start, 30000000)

    @raises(ValueError)
    def test_dispatch_fails(self):
        self.id_range.dispatch(mock_cell('invalid'))


def test_assign_ids():
    cells = [mock_cell('normal'), mock_cell('solid')]
    id_range = assign_ids(cells)
    assert_equal(id_range.get_id(cells[0]), 1)
    assert_equal(id_range.get_id(cells[1]), 40000000)


def test_make_f77_block():
    """Plain F77-unformatted block"""
    f77_block = make_f77_block(six.b('asdf'))
    assert_equal(
        f77_block,
        six.b('\x04\x00\x00\x00asdf\x04\x00\x00\x00')
    )


def test_make_f77_block_padded():
    """F77-unformatted block with padding"""
    f77_block_padded = make_f77_block(six.b('asdf'), 10)
    assert_equal(
        f77_block_padded,
        six.b('\x0a\x00\x00\x00asdf\x00\x00\x00\x00\x00\x00\x0a\x00\x00\x00')
    )


@raises(ValueError)
def test_make_f77_block_padding_too_small():
    """F77-unformatted block with too small padding"""
    f77_block_padded = make_f77_block(six.b('blah'), 2)


def test_make_header():
    """Make a header block"""

    data = dict(
        n_part=(100, 200, 300, 400, 500, 600),
        mass_arr=(0.0,) * 6,
        time=1000.5,
        redshift=50.1,
        flag_sfr=1,
        flag_feedback=1,
        n_all=(100, 200, 300, 400, 500, 600),
        flag_cooling=1,
        num_files=1,
        box_size=1.0,
        omega0=123.0,
        omega_lambda=412.1231,
        hubble_parameter=70.0,
        flag_stellarage=1,
        flag_metals=1,
        flag_entropy_instead_u=1,
        flag_doubleprecision=1,
        flag_lpt_ics=1,
        lpt_scalingfactor=1,
        flag_tracer_field=1,
        composition_vector_length=1,
    )

    header = make_header(**data)

    assert_equal(header[4:28], struct.pack('iiiiii', *data["n_part"]))
    assert_equal(header[28:76], struct.pack('dddddd', *data["mass_arr"]))
    assert_equal(header[76:84], struct.pack('d', data["time"]))
    assert_equal(header[84:92], struct.pack('d', data["redshift"]))
    assert_equal(header[92:96], struct.pack('i', data["flag_sfr"]))
    assert_equal(header[96:100], struct.pack('i', data["flag_feedback"]))
    assert_equal(header[100:124], struct.pack('iiiiii', *data["n_all"]))
    assert_equal(header[124:128], struct.pack('i', data["flag_cooling"]))
    assert_equal(header[128:132], struct.pack('i', data["num_files"]))
    assert_equal(header[132:140], struct.pack('d', data["box_size"]))
    assert_equal(header[140:148], struct.pack('d', data["omega0"]))
    assert_equal(header[148:156], struct.pack('d', data["omega_lambda"]))
    assert_equal(header[156:164], struct.pack('d', data["hubble_parameter"]))
    assert_equal(header[164:168], struct.pack('i', data["flag_stellarage"]))
    assert_equal(header[168:172], struct.pack('i', data["flag_metals"]))
    assert_equal(header[172:196], struct.pack('iiiiii', *(0, 0, 0, 0, 0, 0)))
    assert_equal(header[196:200], struct.pack('i', data["flag_entropy_instead_u"]))
    assert_equal(header[200:204], struct.pack('i', data["flag_doubleprecision"]))
    assert_equal(header[204:208], struct.pack('i', data["flag_lpt_ics"]))
    assert_equal(header[208:212], struct.pack('f', data["lpt_scalingfactor"]))
    assert_equal(header[212:216], struct.pack('i', data["flag_tracer_field"]))
    assert_equal(header[216:220], struct.pack('i', data["composition_vector_length"]))
    assert_equal(header[220:260], six.b('\x00') * 40)

    assert_equal(len(header), 256 + 2 * 4)  # data + length fields


def test_make_header_large_n_all():
    """Make a header block with more than 2**32 n_all"""

    data = dict(
        n_part=(100, 200, 300, 400, 500, 600),
        mass_arr=(0.0,) * 6,
        time=1000.5,
        redshift=50.1,
        flag_sfr=1,
        flag_feedback=1,
        n_all=(
            2 ** 32 + 100, 2 ** 33 + 200, 2 ** 34 + 300, 2 ** 35 + 400,
            2 ** 36 + 500, 2 ** 37 + 600),
        flag_cooling=1,
        num_files=1,
        box_size=1.0,
        omega0=123.0,
        omega_lambda=412.1231,
        hubble_parameter=70.0,
        flag_stellarage=1,
        flag_metals=1,
        flag_entropy_instead_u=1,
        flag_doubleprecision=1,
        flag_lpt_ics=1,
        lpt_scalingfactor=1,
        flag_tracer_field=1,
        composition_vector_length=1,
    )

    header = make_header(**data)

    assert_equal(header[100:124], struct.pack('iiiiii', 100, 200, 300, 400, 500, 600))
    assert_equal(header[172:196], struct.pack(
        'iiiiii', 2 ** 0, 2 ** 1, 2 ** 2, 2 ** 3, 2 ** 4, 2 ** 5))

    assert_equal(len(header), 264)


def test_make_default_header():
    """Make a default header block"""
    header = make_default_header((100, 0, 0, 4, 0, 0), 1.0, 0.0)
    assert_equal(header[4:8], six.b('\x64') + six.b('\x00') * 3)
    assert_equal(header[16:20], six.b('\x04') + six.b('\x00') * 3)
    assert_equal(header[100:104], six.b('\x64') + six.b('\x00') * 3)
    assert_equal(header[128:132], six.b('\x01') + six.b('\x00') * 3)
    assert_equal(len(header), 264)


def test_body_block_vector():
    """Vectorial body block"""
    data = [Vector(0, 0, 0), Vector(1, 0, 0), Vector(2, -1, 0)]
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


def test_iterate_ids_simple():
    """Generate IDs for plain mesh"""
    cells = make_random_mesh()
    id_range = assign_ids(cells)
    id_iter = iterate_ids(cells, id_range)
    assert_equal(list(id_iter), list(range(1, 11)))


def _mesh_with_obstacle():
    """Generate a mesh with obstacles for testing"""
    grid = CartesianGrid2D(Box(Vector(0, 0), Vector(2, 2)), (10, 10))
    circle = CircularObstacle((1, 1), 0.2, n_phi=12)
    return make_mesh(UniformGas(), grid, [circle]), circle


def test_iterate_ids_obstacle():
    """Generate IDs for mesh with obstacle"""
    # Fixture
    cells, obstacle = _mesh_with_obstacle()
    id_range = assign_ids(cells)
    ids = list(iterate_ids(cells, id_range))
    # All cells inside mesh have IDs >= 30000000
    for id_, cell in zip(ids, cells):
        if obstacle.inside(cell.position):
            assert id_ >= 30000000, "pos: {}, id: {}".format(cell.position, id_)
    # Total numbers of cells with certain ID ranges
    assert_equal(len(list(filter(lambda id_: 40000000 > id_ >= 30000000, ids))), 12)
    assert_equal(len(list(filter(lambda id_: id_ >= 40000000, ids))), 12)
    assert_equal(len(list(filter(lambda id_: id_ < 30000000, ids))), 88)


class TestGetType(object):

    def test_zeros(self):
        for category in ['normal', 'solid', 'solid_adjacent']:
            cell = Cell(None, None, None, None, category)
            assert_equal(get_type_of_cell(cell), 0)

    def test_nbody(self):
        cell = Cell(None, None, None, None, 'nbody')
        assert_equal(get_type_of_cell(cell), 4)

    @raises(ValueError)
    def test_invalid(self):
        cell = Cell(None, None, None, None, 'invalid_category')
        _ = get_type_of_cell(cell)


def test_count_types():
    """Count the cell types in a mesh"""
    cells = make_mesh_with_nbody_cell(10)
    ntypes = count_types(cells)
    assert_equal(count_types(cells), [100, 0, 0, 0, 1, 0])
    assert_equal(sum(ntypes), len(list(cells)))


def _hash_write(cells, ids=None):
    """
    Hash the file output of a initial conditions write

    This is used to compare the MD5 hash of the output file to some fixed value
    determined at some point. This test is suboptimal, since the structure of
    the file may vary under changes of the implementation, though it is still a
    valid file.

    In case the internal structure has to be changed, the fixed MD5 hash
    expected by the test has to be changed accordingly.

    """
    # Write initial conditions to a temporary file
    with NamedTemporaryFile() as tmpfile:
        fname = tmpfile.name
    with open(fname, 'wb') as tmpfile:
        write_icfile(tmpfile, cells, ids)
    # Create MD5 hash and check it
    with open(fname, 'rb') as tmpfile:
        output_hash = md5(tmpfile.read()).hexdigest()
    return output_hash


def test_write_ics_md5():
    """Write initial conditions (md5 test)"""
    cells, _ = _mesh_with_obstacle()
    output_hash = _hash_write(cells)
    assert_equal(output_hash, '717cc22e0890deb67af19c7b445086c8')


def test_write_ics_md5_manual_ids():
    """Write initial conditions (md5 test)"""
    cells, _ = _mesh_with_obstacle()
    output_hash = _hash_write(cells, assign_ids(cells))
    assert_equal(output_hash, '717cc22e0890deb67af19c7b445086c8')


def test_iterate_ids_with_nbody():
    """Iterate over IDs of mesh N-body particle"""
    cells = make_mesh_with_nbody_cell(10)
    ids = list(iterate_ids(cells, assign_ids(cells)))
    assert_equal(len(ids), 101)
    assert_equal(ids, list(range(1, 102)))


def test_write_ics_with_nbody_md5():
    """Write initial conditions with N-body particle (md5 test)"""
    cells = make_mesh_with_nbody_cell(10)
    output_hash = _hash_write(cells)
    assert_equal(output_hash, 'fb1abeec313777c7f57154561c7750a2')
