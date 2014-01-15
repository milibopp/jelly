"""Tests of vector class"""

from nose.tools import assert_equal

from pyrepo.vector import *


def test_init():
    """Initialize vector"""
    v = Vector(3, 1, 2)
    assert_equal(v.values, (3, 1, 2))


def test_repr():
    """String representation of vector"""
    assert_equal(repr(Vector(1, 2)), 'Vector(1, 2)')


def test_len():
    """Length of vector"""
    assert_equal(len(Vector(2, 5, 6)), 3)


def test_equality():
    """Equality of vectors"""
    assert_equal(Vector(2, 1), Vector(2, 1))


def test_add():
    """Add two vectors"""
    assert_equal(Vector(2, 1) + Vector(3, -2), Vector(5, -1))


def test_sub():
    """Subtract two vectors"""
    assert_equal(Vector(3, 2) - Vector(-1, 2), Vector(4, 0))


def test_mul():
    """Multiply vector by scalar"""
    assert_equal(Vector(3, 1) * 2, Vector(6, 2))


def test_div():
    """Divide vector by scalar"""
    assert_equal(Vector(4.0, 1.0) / 2.0, Vector(2.0, 0.5))


def test_abs():
    """Absolute value of vector"""
    assert_equal(abs(Vector(3.0, 4.0)), 5.0)


def test_dot():
    """Dot product of two vectors"""
    assert_equal(dot(Vector(3.0, 2.0), Vector(2.0, -1.0)), 4.0)
