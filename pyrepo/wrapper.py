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


class TextFileParameterSetup(object):
    r"""
    A simple text file implementation of the parameter abstraction. This is
    pretty similar to the standard behaviour of Arepo.

    It is initialized with some file path:

    >>> params = TextFileParameterSetup('test_data/stub_params.txt')
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


class CompilerOptions(object):
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

    """

    @abstractproperty
    def all_options(self):
        """All options as a dictionary."""
        pass

    @abstractmethod
    def get_option(self, option):
        """Get the value of a particular option."""
        pass


class FileCompilerOptions(object):
    """
    A compiler options implementation based on an actual config file.

    >>> opt = FileCompilerOptions('test_data/stub_config.sh')
    >>> opt.get_option('NTYPES')
    '6'
    >>> opt.get_option('PERIODIC')
    True
    >>> opt.all_options
    {'PERIODIC': True, 'NTYPES': '6'}

    """

    __regex_comment = r'^\s*#.*$'
    __regex_value = r'^\s*(?P<option>\w+)\s*=\s*(?P<value>.*?)\s*(#.*)?$'
    __regex_flag = r'^\s*(?P<option>\w+)\s*(#.*)?$'

    @staticmethod
    def _match_line(line):
        """
        Matches a line.

        >>> FileCompilerOptions._match_line('test=3')
        ('test', '3')
        >>> FileCompilerOptions._match_line(' param =   5 # comment')
        ('param', '5')
        >>> FileCompilerOptions._match_line('# only comment') is None
        True
        >>> FileCompilerOptions._match_line('flag')
        ('flag', True)

        """
        match = re.match(FileCompilerOptions.__regex_comment, line)
        if match:
            return
        match = re.match(FileCompilerOptions.__regex_value, line)
        if match:
            return match.group('option'), match.group('value')
        match = re.match(FileCompilerOptions.__regex_flag, line)
        if match:
            return match.group('option'), True

    def __init__(self, file_name):
        self.file_name = file_name
        self.__options = {}
        self.parse_file()

    def parse_file(self):
        """
        Parses the file. Typically this is not necessary to do manually,
        since it is called in the constructor. However, it might be useful if a
        given file changes during runtime.

        """
        with open(self.file_name) as cfg_file:
            for line in cfg_file:
                match = self._match_line(line)
                if match:
                    option, value = match
                    self.__options[option] = value

    @property
    def all_options(self):
        return self.__options

    def get_option(self, option):
        """Get the value of an option."""
        return self.__options[option]
