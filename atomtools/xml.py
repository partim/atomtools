"""Basic XML handling."""

from __future__ import absolute_import
from xml.etree.ElementTree import (Element, ElementTree, register_namespace,
                                   SubElement)
from xml.etree.ElementTree import parse as xml_parse

# Imports carried over. You are encouraged to import these names from here
#
from xml.etree.ElementTree import QName
from xml.etree.ElementTree import ParseError

def define_namespace(prefix, url):
    register_namespace(prefix, url)
    return url

# Namespaces
#
xml_ns = define_namespace("xml", "http://www.w3.org/XML/1998/namespace")


class XMLObject(object):
    """Base class for XML handling classes.

    In order to get multiple inhertiance right, you will have to base all
    your XML handling classes directly or indirectly on this class and
    stick to the method signatures given here if your class could ever be
    the parent class somewhere in the tree.

    All methods use keyword arguments only if they have variable arguments
    passed along to their parents. For instance, in the constructor
    define all the arguments you wish to swallow and add ``**kwargs`` at
    the end. Then call the ``super.__init__(**kwargs)`` somewhere.
    """

    @classmethod
    def from_xml(cls, element, **kwargs):
        """Create an instance from an XML element.

        The argument *element* will be a XML element tree's element
        instance (or something compatible). Your implementation can assume
        that the entire subtree of *element* is available.

        The purpose of this method is to create a full set of keyword
        arguments for creating the instance. You basically call the
        super's implementation adding all the keyword arguments that your
        constructor handles. By bubbeling up the inheritance tree, we thus
        create all the arguments for creating a complete instance.

        Your implementation should be generous. If stuff is missing or has
        the wrong type, go ahead anyhow. In this case, create an instance
        that will not result in valid XML later. The method :meth:`validate`
        can be used to check if the the incoming XML was broken. If you
        want, you can note the errors so that :meth:`validate` can give
        specific information.

        The implementation here in the base class simply creates the
        instance with all the collected arguments.
        """
        return cls(**kwargs)

    @classmethod
    def parse_from_xml(cls, source, tag=None, parser=None):
        """Create an instance from an XML file object."""
        tag = tag or cls.standard_tag
        tree = xml_parse(source, parser)
        element = tree.getroot()
        if element.tag != tag:
            raise ParseError("expected '%s' element, got '%s'"
                                % (tag, element.tag))
        return cls.from_xml(element)

    def validate(self, secure=True):
        """Validate whether the object would result in proper XML.

        The function returns a :class:`ValidationResult` object. Truth
        check this object to see if all is well. Otherwise you'll find
        a list of all the errors found as a pair of the XPath
        to the broken elements and a description. 

        The method should always check if the XML would be valid. If the
        attribute *secure* is ``True`` (the default), it should also
        check whether the result should be considered safe, whatever that
        means.
        """
        return ValidationResult()

    @classmethod
    def inner_from_xml(cls, name, sub):
        """Create an instance of an inner object identified by *name*.

        This method provides a way to change the class for inner objects
        in derived classes. This is useful to provide a class the provides
        certain extensions.

        In order to use the facility, add a class attribute
        *inner_factory* to your class. This should be a dictionary
        mapping names to factory functions that create an instance from an
        element tree element. Mostly, this will be the :meth:`from_xml`
        methods.

        The method will resolve the factory function in the same way Python
        resolves methods and will then call it with ``*args`` and
        ``**kwargs``, returning the result. If no function for *name* can
        be found, it will raise :exc:`KeyError`.
        """
        for type in cls.__mro__:
            try:
                factory = type.__dict__["inner_factory"][name]
            except KeyError: 
                continue
            return factory(sub)
        raise KeyError, name

    def create_xml(self, parent, tag=None):
        """Create an XML element for this object.

        Creates an new XML element tree element instance as the last
        child of *parent* and *tag*. It then calls :meth:`prepare_xml`
        to set up the element. The argument *parent* mus not be ``None``.

        If *tag* is ``None`` (or missing), tries to get the flag from
        ``self.standard_tag``.

        Returns the newly created elment.
        """
        try:
            tag = tag or self.standard_tag
        except AttributeError:
            raise ValueError, 'need "tag" or self.standard_tag'
        element = SubElement(parent, tag)
        self.prepare_xml(element)
        return element

    def create_root_xml(self, tag=None, element_class=None):
        """Create a root XML element for this object.

        Same as :meth:`create_xml` except that it creates an element
        without a parent as an instance of *element_class*.
        """
        element_class = element_class or Element
        try:
            tag = tag or self.standard_tag
        except AttributeError:
            raise ValueError, 'need "tag" or self.standard_tag'
        element = element_class(tag)
        self.prepare_xml(element)
        return element

    def encode(self):
        """Encode the object into a byte string."""
        class dummy:
            pass
        data = []
        file = dummy()
        file.write = data.append
        ElementTree(self.create_root_xml()).write(file, "utf-8", True, "xml")
        return "".join(data)
        element = self.create_root_xml()
        return tostring(element)

    def prepare_xml(self, element):
        """Prepare this object's XML element.

        The *element* is the actual element for this object, not its parent.

        When you implement your version of this method, don't forget to
        call the parent implementation(s) via the super construct.

        Note that this is the place to check if the instance has enough
        status to create valid XML. If it doesn't, you should raise a
        :exc:`.atomtools.exceptions.IncompleteObjectError`.
        """
        pass


class ValidationResult(list):
    """Result of a validation run.
    
    This is essentially a list of pairs, each representing an error: The
    first item is the XPath to the faulty element, the second a textual
    description of the error.
    """
    def add(self, path, text):
        self.append((path, text))

    def update(self, result, prefix):
        """Update from *result*, adding *prefix* to the XPath."""
        self.extend(("%s%s" % (prefix, path), text) for path, text in result)

    def __unicode__(self):
        return "".join("%s: %s\n" % item for item in self)

