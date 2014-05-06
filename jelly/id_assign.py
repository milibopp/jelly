"""
ID assignment module

"""


class RangeExhaustedError(Exception):
    pass


class IDRange(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self._state = start
        self._map = {}

    def assign_id(self, obj):
        """Assign an ID to an object

        This function uses the next available ID and advances the range's
        internal state used for ID assignment.

        If an object is a duplicate or no further IDs are available, an
        appropriate exception will be raised.

        """
        if self._state > self.end:
            raise RangeExhaustedError('ID range is exhausted')
        if obj in self._map.itervalues():
            raise ValueError('duplicate object')
        self._map[self._state] = obj
        self._state += 1

    def get_id(self, obj):
        """Get the ID of an object"""
        for key, value in self._map.iteritems():
            if value is obj:
                return key
        raise ValueError('object not found')

    def get_object(self, object_id):
        """Get the object associated with a given ID"""
        return self._map[object_id]
