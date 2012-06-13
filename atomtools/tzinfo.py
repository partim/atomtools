"""tzinfo implementations for use with Internet timestamps.

This is "borrowed" partly from the Python documentation and partly from
the smart Django people.
"""
from datetime import tzinfo, timedelta

# Python's doc say: "A tzinfo subclass must have an __init__() method that can
# be called with no arguments". FixedOffset and LocalTimezone don't honor this
# requirement. Defining __getinitargs__ is sufficient to fix copy/deepcopy as
# well as pickling/unpickling.

class TzInfoFixedOffset(tzinfo):
    "Fixed offset in minutes east from UTC."
    def __init__(self, offset):
        if isinstance(offset, timedelta):
            self.__offset = offset
            offset = self.__offset.seconds // 60
        else:
            self.__offset = timedelta(minutes=offset)

        sign = '-' if offset < 0 else '+'
        self.__name = u"%s%02d:%02d" % (sign, abs(offset) / 60., abs(offset) % 60)

    def __repr__(self):
        return self.__name

    def __getinitargs__(self):
        return self.__offset,

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return timedelta(0)


ZERO = timedelta(0)

class TzInfoUTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "Z"

    def dst(self, dt):
        return ZERO

