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

from abc import ABCMeta, abstractproperty


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
