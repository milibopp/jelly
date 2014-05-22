"""
This module monkeypatches assertions for Python 2.6 into nose.tools

"""

import nose.tools as nt


def assert_is(x, y):
    assert x is y, "{:?} and {:?} are not identical".format(x, y)

if not hasattr(nt, 'assert_is'):
    nt.assert_is = assert_is


def assert_in(item, collection):
    assert item in collection, "{:r} not in {:r}".format(item, collection)

if not hasattr(nt, 'assert_in'):
    nt.assert_in = assert_in


def assert_almost_in(item, collection):
    for stuff in collection:
        try:
            nt.assert_almost_equal(item, stuff)
            return
        except:
            pass
    raise AssertionError('no item in {} almost equal to {}'.format(collection, item))

nt.assert_almost_in = assert_almost_in


def assert_not_in(item, collection):
    assert item not in collection, "{:r} in {:r}".format(item, collection)

if not hasattr(nt, 'assert_not_in'):
    nt.assert_not_in = assert_not_in


def assert_less_equal(first, second, msg=None):
    if not first <= second:
        if msg is None:
            raise AssertionError(
                '"{:s}" unexpectedly not less than or equal to "{:s}"'
                .format(repr(first), repr(second)))
        else:
            raise AssertionError(msg)

if not hasattr(nt, 'assert_less_equal'):
    nt.assert_less_equal = assert_less_equal


def assert_greater_equal(first, second, msg=None):
    if not first >= second:
        if msg is None:
            raise AssertionError(
                '"{:s}" unexpectedly not greater than or equal to "{:s}"'
                .format(repr(first), repr(second)))
        else:
            raise AssertionError(msg)


if not hasattr(nt, 'assert_greater_equal'):
    nt.assert_greater_equal = assert_greater_equal
