"""
The `wrapper` module provides a simple wrapper around an Arepo simulation run.
It deals with the following steps necessary to run Arepo:

- Configuration of compiler flags
- Compilation
- Generation of initial conditions
- Parameter files
- Run the compiled executable with the parameter file

Some of these steps are automated to various degrees to ease the burden of
running Arepo.

"""

from abc import ABCMeta, abstractproperty, abstractmethod
import re


class ParameterSetup(object):
    """
    An abstraction of the Arepo parameter file. It may be provided procedurally
    from some object model or directly as a standard text file.

    """

    __metaclass__ = ABCMeta

    @abstractproperty
    def content(self):
        """The content of the parameter file as a string."""
        pass


class FileParameterSetup(object):
    r"""
    A simple text file implementation of the parameter abstraction. This is
    pretty similar to the standard behaviour of Arepo.

    It is initialized with some file path:

    >>> params = FileParameterSetup('test_data/stub_params.txt')
    >>> params.file_name
    'test_data/stub_params.txt'
    >>> params.content.split('\n')[0]
    '% Sample Arepo parameter file'

    """

    def __init__(self, file_name):
        self.file_name = file_name

    @property
    def content(self):
        """The content of the parameter file."""
        with open(self.file_name) as textfile:
            text = ''.join(line for line in textfile)
        return text


class CompilerOptions(dict):
    """
    An abstraction of the compiler options supplied to Arepo.

    The configuration of Arepo compiler options typically takes place in a
    simple bash script that defines a bunch of environment variables.

    These variables can have a value such as `NTYPES=6` but most are simple
    flags, that are either set or commented out. This class maps these options
    to behave somewhat like a dictionary mapping flags to boolean True/False
    values and the other options to strings.

    It is possible to use other values, such as integers or floats for the
    options as long as Python can automatically convert them to strings.

    This is a rather trivial subclass of a dictionary with some additional
    methods.

    """

    __regex_comment = r'^\s*#.*$'
    __regex_value = r'^\s*(?P<option>\w+)\s*=\s*(?P<value>.*?)\s*(#.*)?$'
    __regex_flag = r'^\s*(?P<option>\w+)\s*(#.*)?$'

    @staticmethod
    def _match_line(line):
        """
        Matches a line.

        >>> CompilerOptions._match_line('test=3')
        ('test', '3')
        >>> CompilerOptions._match_line(' param =   5 # comment')
        ('param', '5')
        >>> CompilerOptions._match_line('# only comment') is None
        True
        >>> CompilerOptions._match_line('flag')
        ('flag', True)

        """
        match = re.match(CompilerOptions.__regex_comment, line)
        if match:
            return
        match = re.match(CompilerOptions.__regex_value, line)
        if match:
            return match.group('option'), match.group('value')
        match = re.match(CompilerOptions.__regex_flag, line)
        if match:
            return match.group('option'), True

    @classmethod
    def from_file(cls, file_name):
        """
        Alternative constructor loading the compiler options from a standard
        Arepo config file.

        >>> CompilerOptions.from_file('test_data/stub_config.sh')
        CompilerOptions({'PERIODIC': True, 'NTYPES': '6'})
        
        """
        options = cls()
        with open(file_name) as cfg_file:
            for line in cfg_file:
                match = CompilerOptions._match_line(line)
                if match:
                    key, value = match
                    options[key] = value
        return options

    def __repr__(self):
        """

        >>> CompilerOptions(a=3, b=4)
        CompilerOptions({'a': 3, 'b': 4})

        """
        return '{}({})'.format(self.__class__.__name__, dict.__repr__(self))
