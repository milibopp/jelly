"""Wrapper tests"""

from nose.tools import assert_equal
from unittest import TestCase

from ..wrapper import *


class TestParameterSetup(TestCase):
    """Test cases for ParameterSetup"""

    def test_match_line(self):
        """Match one line of a parameter file"""
        assert_equal(
            ParameterSetup._match_line('OutputDir output/'),
            ('OutputDir', 'output/'))

    def test_from_file(self):
        """Read parameter setup from file"""
        setup = ParameterSetup.from_file('test_data/stub_params.txt')
        assert_equal(setup['EnergyFile'], 'energy.txt')


class TestCompilerOptions(TestCase):
    """Test cases for CompilerOptions"""

    def test_match_line(self):
        """Match one line of the compiler options"""
        assert_equal(
            CompilerOptions._match_line('test=3'),
            ('test', '3'))
        assert_equal(
            CompilerOptions._match_line(' param =   5 # comment'),
            ('param', '5'))
        assert CompilerOptions._match_line('# only comment') is None
        assert_equal(
            CompilerOptions._match_line('flag'),
            ('flag', True))

    def test_from_file(self):
        """Read compiler options from file"""
        opts = CompilerOptions.from_file('test_data/stub_config.sh')
        assert_equal(opts['PERIODIC'], True)
        assert_equal(opts['NTYPES'], '6')

    def test_repr(self):
        """String repr of compiler options"""
        assert_equal(
            repr(CompilerOptions(a=3, b=4)),
            "CompilerOptions(" + repr(dict(a=3, b=4)) + ")")
