"""Elements of the Atom Publication Protocol.

The document you are looking for is RFC 5023.
"""

from __future__ import absolute_import
from xml.etree.ElementTree import QName

from atomtools.atom import (atom_ns, AtomCommon, AtomCategory, AtomText,
                            AtomSource, AtomEntry, AtomFeed)
from atomtools.xml import define_namespace, XMLObject

app_ns = define_namespace("app", "http://www.w3.org/2007/app")


class AppCategories(AtomCommon):
    """7.  Category Documents
    
    """
    inner_factory = {
        "category": AtomCategory.from_xml,
    }

    def __init__(self, fixed=False, scheme=None, href=None, categories=(),
                 **kwargs):
        super(AppCategories, self).__init__(**kwargs)
        self.fixed = fixed
        self.scheme = scheme
        self.href = href
        self.categories = list(categories)

    @classmethod
    def from_xml(cls, element, **kwargs):
        href = element.attrib.get("href")
        if href is not None:
            kwargs["fixed"] = False
            kwargs["scheme"] = None
            kwargs["categories"] = ()
        else:
            kwargs["fixed"] = element.attrib.get("fixed", "").lower() == "yes"
            kwargs["scheme"] = element.attrib.get("scheme")
            kwargs.setdefault(category, [])
            for sub in element:
                if sub.tag == QName(atom_ns, "category"):
                    kwargs["category"].append(cls.inner_from_xml("category",
                                                                 sub))
        return super(AppCategories, cls).from_xml(element, **kwargs)

    def create_xml(self, parent, tag=QName(app_ns, "categories")):
        return super(AppCategories, self).create_xml(parent, tag)

    def create_root_xml(self, tag=QName(app_ns, "categories"),
                        element_class=None):
        return super(AppCategories, self).create_root_xml(tag, element_class)

    def prepare_xml(self, element):
        super(AppCategories, self).prepare_xml(element)
        if self.href is not None:
            element.attrib["href"] = self.href
        else:
            if self.fixed:
                element.attrib["fixed"] = "yes"
            if self.schema is not None:
                element.attrib["schema"] = self.schema
            for item in self.categories:
                item.create_xml(element, QName(atom_ns, "category"))


class AppAccept(AtomCommon):
    """8.3.4  The "app:accept" Element

    """
    def __init__(self, media_range=None, **kwargs):
        super(AtomAccept, self).__init__(**kwargs)
        self.media_range = media_range

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(AppAccept, cls).from_xml(element,
                media_range=element.text, **kwargs)

    def prepare_xml(self, element):
        super(AppAccept, self).prepare_xml(element)
        if self.media_range is not None:
            element.text = self.media_range


class AppCollection(AtomCommon):
    """8.3.3.  The "app:collection" Element

    """
    inner_factory = {
        "title": AtomText.from_xml,
        "accept": AppAccept.from_xml,
        "categories": AppCategories.from_xml,
    }

    def __init__(self, href=None, title=None, accept=(), categories=(),
                 **kwargs):
        super(AppCollection, self).__init__(**kwargs)
        self.href = href
        self.title = title
        self.accept = accept
        self.categories = categories

    @classmethod
    def from_xml(cls, element, **kwargs):
        accept = kwargs.setdefault("accept", [])
        categories = kwargs.setdefault("categories", [])
        for sub in element:
            if sub.tag == QName(atom_ns, "title"):
                kwargs["title"] = cls.inner_from_xml("title", sub)
            elif sub.tag == QName(app_ns, "accept"):
                accept.append(cls.inner_from_xml("accept", sub))
            elif sub.tag == QName(app_ns, "categories"):
                categories.append(cls.inner_from_xml("categories", sub))
        return super(AppCollection, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        if self.href is None:
            raise IncompleteObjectError, "href is required"
        if not self.title:
            raise IncompleteObjectError, "title is required"
        super(AppCollection, self).prepare_xml(element)
        element.attrib["href"] = self.href
        self.title.create_xml(element, QName(atom_ns, "title"))
        for item in self.accept:
            item.create_xml(element, QName(app_ns, "accept"))
        for item in self.categories:
            item.create_xml(element, QName(app_ns, "categories"))


class AppWorkspace(AtomCommon):
    """8.3.2.  The "app:workspace" Element

    """
    inner_factory = {
        "title": AtomText.from_xml,
        "collection": AppCollection.from_xml
    }

    def __init__(self, title=None, **kwargs):
        super(AppWorkspace, self).__init__(**kwargs)
        self.title = title

    @classmethod
    def from_xml(cls, element, **kwargs):
        collections = kwargs.setdefault("collections", [])
        for sub in element:
            if sub.tag == QName(atom_ns, "title"):
                kwargs["title"] = cls.inner_from_xml("title", sub)
            elif sub.tag == QName(app_ns, "collection"):
                collections.append(cls.inner_from_xml("collection", sub))
        return super(AppWorkspace, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        if not self.title:
            raise IncompleteObjectError, "title is required"
        super(AppWorkspace, self).prepare_xml(element)
        for item in self.collections:
            item.create_xml(element, QName(app_ns, "collection"))


class AppService(AtomCommon):
    """8.3.1  The "app:service" Element

    """
    inner_factory = {
        "workspace": AppWorkspace.from_xml,
    }

    def __init__(self, workspaces, **kwargs):
        super(AppService, self).__init__(**kwargs)
        self.workspaces = workspaces

    @classmethod
    def from_xml(cls, element, **kwargs):
        workspaces = kwargs.setdefault("workspaces", [])
        for sub in element:
            if sub.tag == QName(app_ns, "workspace"):
                workspaces.append(cls.inner_from_xml("workspace", sub))
        return super(AppService, cls).from_xml(element, **kwargs)

    def create_xml(self, parent, tag=QName(app_ns, "service")):
        return super(AppService, self).create_xml(parent, tag)

    def create_root_xml(tag=QName(app_ns, "service"), element_class=None):
        return super(AppService, self).create_root_xml(tag, element_class)

    def prepare_xml(self, element):
        if not self.workspaces:
            raise IncompleteObjectError, "workspaces is required"
        super(AppService, self).prepare_xml(element)
        for item in self.workspaces:
            item.create_xml(element, QName(app_ns, "workspace"))


# 8.3.5.  Usage in Atom Feed Documents

class AppSource(AtomSource):
    inner_factory = {
        "collection": AppCollection.from_xml,
    }

    def __init__(self, collection=None, **kwargs):
        super(AppSource, self).__init__(**kwargs)
        self.collection = collection

    @classmethod
    def from_xml(cls, element, **kwargs):
        collection = element.find(QName(app_ns, "collection"))
        if collection:
            collection = cls.inner_from_xml("collection", collection)
        return super(AppSource, cls).from_xml(element, collection=collection,
                                              **kwargs)

    def prepare_xml(self, element):
        super(AppSource, element).prepare_xml(self, element)
        if self.collection:
            self.collection.prepare_xml(element, QName(app_ns, "collection"))


class AppEntry(AtomEntry):
    inner_factory = {
        "source": AppSource.from_xml,
    }


class AppFeed(AtomFeed):
    inner_factory = {
        "entry": AppEntry.from_xml,
        "collection": AppCollection.from_xml,
    }

    def __init__(self, collection=None, **kwargs):
        super(AppFeed, self).__init__(**kwargs)
        self.collection = collection

    @classmethod
    def from_xml(cls, element, **kwargs):
        collection = element.find(QName(app_ns, "collection"))
        if collection:
            collection = cls.inner_from_xml("collection", collection)
        return super(AppFeed, cls).from_xml(element, collection=collection,
                                            **kwargs)

    def prepare_xml(self, element):
        super(AppFeed, element).prepare_xml(self, element)
        if self.collection:
            self.collection.prepare_xml(element, QName(app_ns, "collection"))

