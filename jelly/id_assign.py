"""
ID assignment module

"""

import six


class RangeExhaustedError(Exception):
    pass


class IDRange(object):
    """Range of IDs for assignment

    A simple range of IDs that can be consumed by objects to which IDs from the
    range are assigned. Once exhausted, no further IDs can be assigned. Both
    objects and IDs are guaranteed to be uniquely associated with each other.

    """

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
        if obj in six.itervalues(self._map):
            raise ValueError('duplicate object')
        self._map[self._state] = obj
        self._state += 1

    def get_id(self, obj):
        """Get the ID of an object"""
        for key, value in six.iteritems(self._map):
            if value is obj:
                return key

    def get_object(self, object_id):
        """Get the object associated with a given ID"""
        return self._map.get(object_id, None)


class CompoundIDRange(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def assign_id(self, obj):
        self.dispatcher.dispatch(obj).assign_id(obj)

    def get_id(self, obj):
        for comp in self.dispatcher.components:
            the_id = comp.get_id(obj)
            if the_id is not None:
                return the_id

    def get_object(self, object_id):
        for comp in self.dispatcher.components:
            obj = comp.get_object(object_id)
            if obj is not None:
                return obj
