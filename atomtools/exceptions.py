"""All our Exceptions."""

class IncompleteObjectError(ValueError):
    """The object is missing some required values.

    Normally, this happens when you try to create XML from an internal
    representation but have still some attributes left at ``None`` that
    are required in the XML.
    """
