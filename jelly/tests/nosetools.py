"""
This module monkeypatches assertions for Python 2.6 into nose.tools

"""

import nose.tools as nt


def assert_in(item, collection):
    assert item in collection, "{:r} not in {:r}".format(item, collection)

if not hasattr(nt, 'assert_in'):
    nt.assert_in = assert_in


def assert_not_in(item, collection):
    assert item not in collection, "{:r} in {:r}".format(item, collection)

if not hasattr(nt, 'assert_not_in'):
    nt.assert_not_in = assert_not_in


def assert_less_equal(first, second, msg=None):
    if not first <= second:
        if msg is None:
            raise AssertionError('"' + repr(first) + '" unexpectedly not less than or equal to "' + repr(second) + '"')
        else:
            raise AssertionError(msg)

if not hasattr(nt, 'assert_less_equal'):
    nt.assert_less_equal = assert_less_equal


def assert_greater_equal(first, second, msg=None):
    if not first >= second:
        if msg is None:
            raise AssertionError('"' + repr(first) + '" unexpectedly not greater than or equal to "' + repr(second) + '"')
        else:
            raise AssertionError(msg)

if not hasattr(nt, 'assert_greater_equal'):
    nt.assert_greater_equal = assert_greater_equal
