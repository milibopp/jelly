"""Vector arithmetics"""


class Vector(object):

    def __init__(self, *args):
        self.__values = tuple(args)

    @property
    def values(self):
        return self.__values

    def __repr__(self):
        return 'Vector{}'.format(self.__values)

    def __len__(self):
        return len(self.__values)

    def __eq__(self, other):
        return self.values == other.values

    def __add__(self, other):
        return Vector(*(a + b for a, b in zip(self.values, other.values)))

    def __sub__(self, other):
        return Vector(*(a - b for a, b in zip(self.values, other.values)))

    def __mul__(self, scalar):
        return Vector(*(x * scalar for x in self.values))

    def __div__(self, scalar):
        return Vector(*(x / scalar for x in self.values))

    def __abs__(self):
        return sum(x ** 2 for x in self.values) ** 0.5
