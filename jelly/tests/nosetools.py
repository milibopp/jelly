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
