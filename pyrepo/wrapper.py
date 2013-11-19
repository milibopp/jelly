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

import re


class ParameterSetup(dict):
    """
    An abstraction of the Arepo parameter file. It may be provided procedurally
    from some object model or directly as a standard text file.

    The typical format of Arepo parameter files is the following: there are a
    number of key-value pairs separated by white space, line by line. There may
    be empty lines, comments are denoted by "%".

    This class is simply a dict with some additional methods.

    """

    __regex_comment = r'^\s*%.*$'
    __regex_value = r'^\s*(?P<option>\w+)\s*(?P<value>.*?)\s*(%.*)?$'

    @staticmethod
    def _match_line(line):
        """
        Matches a line.

        >>> ParameterSetup._match_line('OutputDir output/')
        ('OutputDir', 'output/')

        """
        match = re.match(ParameterSetup.__regex_comment, line)
        if match:
            return
        match = re.match(ParameterSetup.__regex_value, line)
        if match:
            return match.group('option'), match.group('value')

    @classmethod
    def from_file(cls, file_name):
        """
        Loads the parameter setup from a file.

        >>> setup = ParameterSetup.from_file('test_data/stub_params.txt')
        >>> setup['EnergyFile']
        'energy.txt'

        """
        parameters = cls()
        with open(file_name) as param_file:
            for line in param_file:
                match = cls._match_line(line)
                if match:
                    key, value = match
                    parameters[key] = value
        return parameters


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
