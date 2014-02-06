"""
Jelly configuration.

"""

try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser
import os


def set_config(key, value):
    """Set a configuration option."""
    _config.set('jelly', key, value)


def get_config(key):
    """Get a configuration option."""
    return _config.get('jelly', key)


# Setup the default configuration configuration
_config = SafeConfigParser()
_config.add_section('jelly')
set_config('arepo-path', '~/Arepo')
set_config('arepo-local', '.arepo')

# Read from external configuration files
_config.read(['jellyrc', os.path.expanduser('~/.jellyrc')])
