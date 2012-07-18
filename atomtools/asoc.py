"""Atom extensions for Social Networking.

This extension provides access information describing a social graph.

This consists of a bunch of asoc:links included in the atompub:service
document of an account and a view documents accessibly via those links.

This is work in progress and will be extended as necessary. And probably
changed completely.

You can find the documentation in doc/ames in the source distribution.
"""

from atomtools.atom import (AtomCategory, AtomCommon, AtomDate,
                            AtomEntry, AtomLink, AtomPerson, AtomText,
                            atom_ns)
from atomtools.atompub import AppFeed, AppService
from atomtools.utils import create_text_xml, from_text_xml
from atomtools.xml import define_namespace, QName, XMLObject, xml_ns

# Namespace
#
asoc_ns = define_namespace("asoc", "http://www.alipedis.com/2012/asoc")


# Messaging
#

class AsocPost(AtomCommon):
    """An entry without requirement to have a title.
    
    """
    inner_factory = {
        "author": AtomPerson.from_xml,
        "category": AtomCategory.from_xml,
        "content": AtomText.from_xml,
        "link": AtomLink.from_xml,
        "published": AtomDate.from_xml,
        "rights": AtomText.from_xml,
        "updated": AtomDate.from_xml,
    }
    standard_tag = QName(asoc_ns, "post")
    content_type = "application/asoc+xml"

    def __init__(self, authors=(), categories=(), content=None, id=None,
                 links=(), published=None, rights=None, updated=None,
                 **kwargs):
        super(AsocPost, self).__init__(**kwargs)
        self.authors = list(authors)
        self.categories = list(categories)
        self.content = content
        self.id = id
        self.links = list(links)
        self.published = published
        self.rights = rights
        self.updated = updated

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault("authors", [])
        kwargs.setdefault("categories", [])
        kwargs.setdefault("links", [])
        for sub in element:
            if sub.tag == QName(atom_ns, "author"):
                kwargs["authors"].append(cls.inner_from_xml("author", sub))
            elif sub.tag == QName(atom_ns, "category"):
                kwargs["categories"].append(cls.inner_from_xml("category",
                                                               sub))
            elif sub.tag == QName(asoc_ns, "content"):
                kwargs["content"] = cls.inner_from_xml("content", sub)
            elif sub.tag == QName(atom_ns, "id"):
                kwargs["id"] = from_text_xml(sub)
            elif sub.tag == QName(atom_ns, "link"):
                kwargs["links"].append(cls.inner_from_xml("link", sub))
            elif sub.tag == QName(atom_ns, "publised"):
                kwargs["published"] = cls.inner_from_xml("published", sub)
            elif sub.tag == QName(atom_ns, "rights"):
                kwargs["rights"] = cls.inner_from_xml("rights", sub)
            elif sub.tag == QName(atom_ns, "updated"):
                kwargs["updated"] = cls.inner_from_xml("updated", sub)
        return super(AsocPost, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AsocPost, self).prepare_xml(element)
        for author in self.authors:
            author.create_xml(element, QName(atom_ns, "author"))
        for category in self.categories:
            category.create_xml(element, QName(atom_ns, "category"))
        if self.content:
            self.content.create_xml(element, QName(asoc_ns, "content"))
        if self.id is not None:
            create_text_xml(self.id, element, QName(atom_ns, "id"))
        for link in self.links:
            link.create_xml(element, QName(atom_ns, "link"))
        if self.published:
            self.published.create_xml(element, QName(atom_ns, "published"))
        if self.rights:
            self.rights.create_xml(element, QName(atom_ns, "rights"))
        if self.updated:
            self.updated.create_xml(element, QName(atom_ns, "updated"))

    # A bunch of helpers to make life easier
    #
    def get_link(self, rel):
        """Return the href of the first link with *rel* or None."""
        for link in self.links:
            if link.rel == rel:
                return link.href
        return None

    def get_links(self, rel):
        """Return a list of the hrefs of all links with *rel*."""
        return [link.href for link in self.links if link.rel == rel]

    def get_first_link(self, rel):
        """Get the href of the first link with *rel*."""
        for link in self.links:
            if link.rel == rel:
                return link.href

    def replace_link(self, rel, href, **kwargs):
        """Replace all links with *rel* with a single new one."""
        self.remove_links(rel)
        self.links.append(AtomLink(href=href, rel=rel, **kwargs))

    def remove_links(self, rel):
        """Remove all linjks with *rel*."""
        self.links = [link for link in self.links if link.rel != rel]


class AsocFeed(AppFeed):
    """An atom:feed with asoc:posts.
    
    """
    inner_factory = {
        "post": AsocPost.from_xml,
    }

    def __init__(self, posts=(), **kwargs):
        super(AsocFeed, self).__init__(**kwargs)
        self.posts = list(posts)

    @classmethod
    def from_xml(cls, element, **kwargs):
        entries = kwargs.setdefault("entries", [])
        for sub in element:
            if sub.tag == QName(asoc_ns, "post"):
                entries.append(cls.inner_from_xml("post", sub))
        return super(AsocFeed, cls).from_xml(element, **kwargs)

# Peers
#

class AsocPeer(XMLObject):
    """The "asoc:peer" Element.

    """
    inner_factory = {
        "category": AtomCategory.from_xml,
        "link": AtomLink.from_xml,
    }
    standard_tag = QName(asoc_ns, "peer")
    content_type = "application/asoc+xml"

    def __init__(self, id=None, uri=None, name=None, categories=(), links=(),
                 **kwargs):
        super(AsocPeer, self).__init__(**kwargs)
        self.id = id
        self.uri = uri
        self.name = name
        self.categories = list(categories)
        self.links = list(links)

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault("categories", [])
        kwargs.setdefault("links", [])
        for sub in element:
            if sub.tag == QName(atom_ns, "id"):
                kwargs["id"] = from_text_xml(sub)
            elif sub.tag == QName(asoc_ns, "uri"):
                kwargs["uri"] = from_text_xml(sub)
            elif sub.tag == QName(asoc_ns, "name"):
                kwargs["name"] = from_text_xml(sub)
            elif sub.tag == QName(atom_ns, "category"):
                kwargs["categories"].append(cls.inner_from_xml("category",
                                                               sub))
            elif sub.tag == QName(atom_ns, "link"):
                kwargs["links"].append(cls.inner_from_xml("link", sub))
        return super(AsocPeer, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AsocPeer, self).prepare_xml(element)
        if self.id:
            create_text_xml(self.id, element, QName(atom_ns, "id"))
        if self.uri:
            create_text_xml(self.uri, element, QName(asoc_ns, "uri"))
        if self.name:
            create_text_xml(self.name, element, QName(asoc_ns, "name"))
        for item in self.categories:
            item.create_xml(element)
        for item in self.links:
            item.create_xml(element)


class AsocPeers(XMLObject):
    """The "asoc:peers" Element and Document

    """
    inner_factory = {
        "peer": AsocPeer.from_xml,
    }
    standard_tag = QName(asoc_ns, "peers")
    content_type = "application/asoc+xml"

    def __init__(self, peers=(), **kwargs):
        super(AsocPeers, self).__init__(**kwargs)
        self.peers = list(peers)

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault("peers", [])
        for sub in element:
            if sub.tag == QName(asoc_ns, "peer"):
                kwargs["peer"].append(cls.inner_from_xml("peer", sub))
        return super(AsocPeers, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AsocPeers, self).prepare_xml(element)
        for item in self.peers:
            item.create_xml(element)


class AsocCertificate(XMLObject):
    """The "asoc:certificate" Element.

    """
    standard_tag = QName(asoc_ns, "certificate")
    content_type = "application/asoc+xml"

    def __init__(self, href=None, name=None, certificate=None, **kwargs):
        super(AsocCertificate, self).__init__(**kwargs)
        self.href = href
        self.name = name
        self.certificate = certificate

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(AsocCertificate, cls).from_xml(element,
                href=element.attrib.get("href"),
                name=element.attrib.get("name"),
                certificate=element.text,
                **kwargs)

    def prepare_xml(self, element):
        super(AsocCertificate, self).prepare_xml(element)
        if self.href is not None:
            element.attrib["href"] = self.href
        if self.name is not None:
            element.attrib["name"] = self.name
        if self.certificate:
            element.text = self.certificate


class AsocCertificates(XMLObject):
    """The "asoc:certificates" Element

    Contains a list of asoc:certifcate elements. Can be its own document.
    """
    inner_factory = {
        "certificate": AsocCertificate.from_xml,
    }
    standard_tag = QName(asoc_ns, "certificates")
    content_type = "application/asoc+xml"

    def __init__(self, certificates=(), **kwargs):
        super(AsocCertificates, self).__init__(**kwargs)
        self.certificates = list(certificates)

    @classmethod
    def from_xml(self, element, **kwargs):
        kwargs.setdefault("certificates", list())
        for sub in element:
            if sub.tag == QName(asoc_ns, "certificate"):
                kwargs["certificates"].append(
                        cls.inner_from_xml("certificate", sub))
        return super(AsocCertificates, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AsocCertificates, self).prepare_xml(element)
        for cert in self.certificates:
            cert.create_xml(element)


class AsocService(AppService):
    """An app:service element with asoc extensions.

    """
    inner_factory = {
        'link': AtomLink.from_xml,
    }

    def __init__(self, links=(), **kwargs):
        super(AsocService, self).__init__(**kwargs)
        self.links = list(links)

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault('links', [])
        for sub in element:
            if sub.tag == QName(atom_ns, "link"):
                kwargs["links"].append(cls.inner_from_xml("link", sub))
        return super(AsocService, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AsocService, self).prepare_xml(element)
        for link in self.links:
            link.create_xml(element)

    def get_link(self, rel):
        """Return the href of the first link with *rel* or None."""
        for link in self.links:
            if link.rel == rel:
                return link.href
        return None

    def get_links(self, rel):
        """Return a list of the hrefs of all links with *rel*."""
        return [link.href for link in self.links if link.rel == rel]

    def get_first_link(self, rel):
        """Get the href of the first link with *rel*."""
        for link in self.links:
            if link.rel == rel:
                return link.href

    def replace_link(self, rel, href, **kwargs):
        """Replace all links with *rel* with a single new one."""
        self.remove_links(rel)
        self.links.append(AtomLink(href=href, rel=rel, **kwargs))

    def remove_links(self, rel):
        """Remove all linjks with *rel*."""
        self.links = [link for link in self.links if link.rel != rel]

