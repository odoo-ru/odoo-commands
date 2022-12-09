from collections import Mapping

SKIPPED_ELEMENT_TYPES = None

find_in_path = None
def find_in_path(arg):
    return arg

# ConstantMapping = None
class ConstantMapping(Mapping):
    """
    An immutable mapping returning the provided value for every single key.

    Useful for default value to methods
    """
    __slots__ = ['_value']
    def __init__(self, val):
        self._value = val

    def __len__(self):
        """
        defaultdict updates its length for each individually requested key, is
        that really useful?
        """
        return 0

    def __iter__(self):
        """
        same as len, defaultdict udpates its iterable keyset with each key
        requested, is there a point for this?
        """
        return iter([])

    def __getitem__(self, item):
        return self._value
