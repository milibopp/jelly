"""Vector arithmetics"""


class DimensionalityError(Exception):
    """Exception for incompatible dimensionalities

    An exception raised, when the operation needs object of the same
    dimensionality, but it is different.

    """
    pass


class Vector(object):

    def __init__(self, *args):
        self.__values = tuple(args)

    @property
    def values(self):
        return self.__values

    def _assert_same_dimensionality(self, other):
        if len(self) != len(other):
            raise DimensionalityError("Vectors don't have the same size")

    def __repr__(self):
        return 'Vector{0}'.format(self.__values)

    def __getitem__(self, key):
        return self.__values[key]

    def __len__(self):
        return len(self.__values)

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.values == other.values
        return False

    def __ne__(self, other):
        result = self.__eq__(other)
        return not result

    def __lt__(self, other):
        raise NotImplementedError("Vectors have no order")

    def __le__(self, other):
        raise NotImplementedError("Vectors have no order")

    def __gt__(self, other):
        raise NotImplementedError("Vectors have no order")

    def __ge__(self, other):
        raise NotImplementedError("Vectors have no order")

    def __hash__(self):
        return hash(self.__values)

    def __add__(self, other):
        self._assert_same_dimensionality(other)
        return Vector(*(a + b for a, b in zip(self.values, other.values)))

    def __sub__(self, other):
        self._assert_same_dimensionality(other)
        return Vector(*(a - b for a, b in zip(self.values, other.values)))

    def __mul__(self, scalar):
        return Vector(*(x * scalar for x in self.values))

    def __rmul__(self, scalar):
        return Vector(*(x * scalar for x in self.values))

    def __div__(self, scalar):
        return Vector(*(x / scalar for x in self.values))

    __truediv__ = __div__

    def __abs__(self):
        return sum(x ** 2 for x in self.values) ** 0.5

    def unit(self):
        return self / abs(self)


def dot(v1, v2):
    """Dot product of two vectors"""
    v1._assert_same_dimensionality(v2)
    return sum(a * b for a, b in zip(v1.values, v2.values))


def cross(a, b):
    """Cross product of two 3-vectors"""
    assert len(a) == len(b) == 3
    return Vector(
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0])
