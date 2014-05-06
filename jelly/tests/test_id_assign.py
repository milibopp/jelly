"""
Tests for ID assignment

"""

from nose.tools import assert_equal, raises, assert_is, assert_is

from jelly.id_assign import *


class TestIDRange(object):

    def setup(self):
        self.id_range = IDRange(3, 14)

    def test_init(self):
        assert_equal(self.id_range.start, 3)
        assert_equal(self.id_range.end, 14)

    def test_assign_id(self):
        objs = [object() for _ in range(10)]
        for obj in objs:
            self.id_range.assign_id(obj)
        for k, obj in enumerate(objs):
            assert_equal(self.id_range.get_id(obj), k + 3)

    @raises(RangeExhaustedError)
    def test_assign_id_range_exhausted(self):
        objs = [object() for _ in range(20)]
        for obj in objs:
            self.id_range.assign_id(obj)

    @raises(ValueError)
    def test_assign_id_duplicate(self):
        blah = object()
        for _ in [0, 0]:
            self.id_range.assign_id(blah)

    def test_get_id(self):
        foo = object()
        self.id_range.assign_id(foo)
        assert_equal(self.id_range.get_id(foo), 3)

    def test_get_id_does_not_exist(self):
        foo = object()
        bar = object()
        self.id_range.assign_id(foo)
        assert_is(self.id_range.get_id(bar), None)

    def test_get_object(self):
        foo = object()
        self.id_range.assign_id(foo)
        assert_is(self.id_range.get_object(3), foo)

    def test_get_object_does_not_exist(self):
        assert_is(self.id_range.get_object(3), None)


class MockDispatcher(object):

    def __init__(self):
        self.witha = IDRange(0, 9)
        self.others = IDRange(10, 19)

    def dispatch(self, obj):
        return self.witha if obj[0] in 'Aa' else self.others

    @property
    def components(self):
        yield self.witha
        yield self.others


class TestCompoundIDRange(object):

    def setup(self):
        self.compound = CompoundIDRange(MockDispatcher())

    def test_assign_id_witha(self):
        witha = ['a', 'b', 'c']
        self.compound.assign_id(witha)
        assert_is(self.compound.get_object(0), witha)
        assert_equal(self.compound.get_id(witha), 0)

    def test_assign_id_other(self):
        other = ['d', 'e', 'f']
        self.compound.assign_id(other)
        assert_is(self.compound.get_object(10), other)
        assert_equal(self.compound.get_id(other), 10)
