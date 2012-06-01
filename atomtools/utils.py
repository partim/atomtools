"""Various utility functions."""

from __future__ import absolute_import
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring as to_xml_string

def create_text_xml(text, parent, tag):
    element = SubElement(parent, tag)
    if text:
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
    return text.strip()

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

def print_xml_tree(element, prefix=""):
    from sys import stderr
    stderr.write(prefix)
    stderr.write(repr(element.tag))
    for v in element.attrib.iteritems():
        stderr.write(" %r=%r" % v)
    stderr.write("\n")
    for sub in element:
        print_xml_tree(sub, "%s  " % prefix)
