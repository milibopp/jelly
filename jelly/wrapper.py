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
import os.path
import shutil
import subprocess
import multiprocessing

from .config import get_config
from .ics import write_icfile


__all__ = ['ArepoRun', 'ArepoInstallation', 'ParameterSetup', 'CompilerOptions']


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

        """
        parameters = cls()
        with open(file_name) as param_file:
            for line in param_file:
                match = cls._match_line(line)
                if match:
                    key, value = match
                    parameters[key] = value
        return parameters

    def write(self, file_name):
        """Writes the parameters to a file."""
        with open(file_name, 'w') as param_file:
            for key, value in self.iteritems():
                param_file.write('{} {}\n'.format(key, value))


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

        """
        options = cls()
        with open(file_name) as cfg_file:
            for line in cfg_file:
                match = CompilerOptions._match_line(line)
                if match:
                    key, value = match
                    options[key] = value
        return options

    def write(self, file_name):
        """Writes the options to a file."""
        with open(file_name, 'w') as cfg_file:
            for key, value in self.iteritems():
                if value is True:
                    cfg_file.write('{}\n'.format(key))
                else:
                    cfg_file.write('{}={}\n'.format(key, value))

    def __repr__(self):
        """
        String representation of compiler configuration

        """
        return '{0}({1})'.format(self.__class__.__name__, dict.__repr__(self))


class ArepoInstallation(object):
    """
    An abstraction of the Arepo installation used. By default, a subfolder
    `.arepo` is used in the current working directory. (This may be modified
    using the configuration option `arepo-local`.) If this does not exist, it
    is constructed by making a copy of the global Arepo installation folder.
    (By default, `arepo-path=~/Arepo`)

    Optionally, one can provide an argument to the constructor to specify a
    custom Arepo folder to use.

    """

    def __init__(self, directory=None):
        self.directory = directory or get_config('arepo-local')
        if not self.__check_dir():
            self.__create_dir()

    def get_file(self, file_name):
        """Get the path to a particular file in the Arepo directory."""
        return os.path.join(self.directory, file_name)

    @property
    def config(self):
        """The Config.sh file includes Arepo's compiler options."""
        return self.get_file('Config.sh')

    @property
    def systype(self):
        """The Makefile.systype file defines the type of system."""
        return self.get_file('Makefile.systype')

    def __check_dir(self):
        """Checks if the local Arepo directory exists."""
        return os.path.isdir(self.directory)

    def __create_dir(self):
        """Creates the local Arepo directory as a copy of the global one."""
        src = os.path.expanduser(get_config('arepo-path'))
        dest = self.directory
        ignore_pattern = shutil.ignore_patterns(
            '.*', 'data', 'jobscripts', 'tools', 'parameterfiles',
            '*.txt', 'Doxyfile', 'Template-*', 'indent-*.sh')
        shutil.copytree(src, dest, ignore=ignore_pattern)


class ArepoRun(object):
    """
    An Arepo run. This class is used to handle preparational steps to be taken
    before the simulation can be run and thereby interaction with the Arepo
    working directory. Eventually it runs the simulation as a subprocess.

    """

    def __init__(self, arepo, compiler_options, systype='Ubuntu',
                 proc_count=None):
        self.arepo = arepo
        self.compiler_options = compiler_options
        self.systype = systype
        self.__proc_count = proc_count

    @property
    def proc_count(self):
        """
        The number of processes used for the compiling and running the
        simulation. This defaults (value None) to the number of CPUs available
        but it may also be set manually.

        """
        if self.__proc_count:
            return self.__proc_count
        try:
            return multiprocessing.cpu_count()
        except:
            return 1

    @proc_count.setter
    def proc_count(self, value):
        assert isinstance(value, int)
        self.__proc_count = value

    def compile(self):
        """Compiles the Arepo software using its makefile."""
        # Write compiler options
        self.compiler_options.write(self.arepo.config)
        # Set SYSTYPE variable
        with open(self.arepo.systype, 'w') as msystype:
            msystype.write('SYSTYPE="{}"'.format(self.systype))
        # Compile
        retcode = subprocess.call(['make', '-j{:d}'.format(self.proc_count)],
                                  cwd=self.arepo.directory)
        if retcode != 0:
            raise RuntimeError(
                'Arepo compilation failed (exit code: {})'.format(retcode))

    def run(self, parameters):
        """
        Run the simulation with given parameter setup and initial conditions.

        The initial conditions are automatically saved as the file specified in
        the parameter `InitCondFile`.

        """
        # Write parameter file
        pfile = 'jelly-params.txt'
        parameters.write(pfile)
        # Run the simulation
        subprocess.call([
            'mpirun', '-np', str(self.proc_count), '.arepo/Arepo', pfile])
