"""
This module monkeypatches assertions for Python 2.6 into nose.tools

"""

import nose.tools as nt


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
    nt.assert_in = assert_in
