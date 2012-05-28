"""Various utility functions."""

def create_text_xml(text, parent, tag):
    element = SubElement(parent, tag)
    element.text = unicode(text)
    return element

def flatten_xml_content(element):
    """Returns a flat version of the content of *element*."""
    if len(element) > 0:
        # XXX Not sure if this is smart
        text = [element.text]
        text.extend((to_xml_string(e) for e in element))
        text = ''.join(text)
    else:
        text = element.text

def from_text_xml(element):
    """Return only the initial text.

    If there is child elements, ignore them.
    """
    return element.text

def wrap_xml_tree(element, tag):
    """Wrap content of element in a *tag* element if it isn't already."""
    if len(element) == 1 and element[0].tag == tag:
        return element[0]
    else:
        res = element.makeelement(tag)
        res.text = element.text
        res.extend(e for e in element)
        return res

