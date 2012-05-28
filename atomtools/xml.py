"""Basic XML handling."""

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

        The implementation here in the base class simply creates the
        instance with all the collected arguments.
        """
        return cls(**kwargs)

    def create_xml(self, parent, tag):
        """Create an XML element for this object.

        Creates an new XML element tree element instance as the last
        child of *parent* and *tag*. It then calls :meth:`prepare_xml`
        to set up the element. The argument *parent* may be ``None`` in
        which case the new element will not have a parent.

        Returns the newly created elment.

        The tag name is included in the arguments to allow using a class
        for different actual XML element types. If your class will always
        create an element with the same tag, you can overide the method
        dropping the tag argument.
        """
        element = Element(tag)
        self.prepare_xml(element)
        if parent is not None:
            parent.append(element)
        return element

    def prepare_xml(self, element):
        """Prepare this object's XML element.

        The *element* is the actual element for this object, not its parent.

        When you implement your version of this method, don't forget to
        call the parent implementation(s) via the super construct.
        """
        pass
