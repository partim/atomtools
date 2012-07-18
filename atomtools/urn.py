"""Tools for URNs."""

import uuid

def urn_uuid4():
    """Generate a random UUID URN."""
    return "urn:uuid:%s" % uuid.uuid4()
