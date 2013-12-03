"""
Tests of the mesh class.

"""

from pyrepo.model import *


def make_some_cells():
    """Helper function to generate cells."""
    return ListCellCollection(Cell((i * 0.1, 0), (0, 0), 1, 1) for i in range(40))


class CustomObstacle(Obstacle):
    """A custom obstacle that cuts off any cells with x < 1.5"""

    def __iter__(self):
        return iter([])

    def inside(self, position):
        return position[0] < 1.5

    def check(self):
        return True


def test_plain_mesh():
    """Test mesh with plain gas."""
    cells = make_some_cells()
    mesh = Mesh(cells)
    assert set(mesh.cells) == set(cells)


def test_mesh_with_obstacle():
    """Test mesh with an obstacle."""
    cells = make_some_cells()
    obstacle = CustomObstacle()
    mesh = Mesh(cells, [obstacle])
    assert set(mesh.cells) < set(cells)
    for cell in mesh.cells:
        assert cell.position[0] >= 1.5
