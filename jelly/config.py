"""
Pyrepo configuration.

"""

from ConfigParser import SafeConfigParser
import os


def set_config(key, value):
    """Set a configuration option."""
    _config.set('pyrepo', key, value)


def get_config(key):
    """Get a configuration option."""
    return _config.get('pyrepo', key)


# Setup the default configuration configuration
_config = SafeConfigParser()
_config.add_section('pyrepo')
set_config('arepo-path', '~/Arepo')
set_config('arepo-local', '.arepo')

# Read from external configuration files
_config.read(['pyreporc', os.path.expanduser('~/.pyreporc')])
