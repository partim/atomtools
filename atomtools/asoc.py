"""Atom extensions for Social Networking.

This extension provides access information describing a social graph.

This consists of a bunch of asoc:links included in the atompub:service
document of an account and a view documents accessibly via those links.

This is work in progress and will be extended as necessary. And probably
changed completely.
"""

from atomtools.atom import AtomCommon
from atomtools.atompub import AppService
from atomtools.utils import create_text_xml
from atomtools.xml import define_namespace, QName, XMLObject, xml_ns

# Namespace
#
asoc_ns = define_namespace("asoc", "http://www.alipedis.com/2012/asoc")


class AsocLink(XMLObject):
    """The "asoc:link" Element

    Links to the various social networking documents.
    """
    standard_tag = QName(asoc_ns, "link")

    def __init__(self, href=None, rel=None, base=None, **kwargs):
        super(AsocLink, self).__init__(**kwargs)
        self.href = href
        self.rel = rel
        self.base = base

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(AsocLink, cls).from_xml(element,
                href=element.attrib.get("href"),
                rel=element.attrib.get("rel"),
                base=element.attrib.get(QName(xml_ns, "base")),
                **kwargs)

    def prepare_xml(self, element):
        super(AsocLink, self).prepare_xml(element)
        if self.href is not None:
            element.attrib["href"] = self.href
        if self.rel is not None:
            element.attrib["rel"] = self.rel
        if self.base is not None:
            element.attrib[QName(xml_ns, "base")] = self.base


class AsocPeer(XMLObject):
    """The "asoc:peer" Element.

    """
    standard_tag = QName(asoc_ns, "peer")

    def __init__(self, uri=None, name=None, **kwargs):
        super(AsocPeer, self).__init__(**kwargs)
        self.uri = uri
        self.name = name

    @classmethod
    def from_xml(cls, element, **kwargs):
        for sub in element:
            if sub.tag == QName(asoc_ns, "uri"):
                kwargs["uri"] = sub.text
            elif sub.tag == QName(asoc_ns, "name"):
                kwargs["name"] = sub.text
        return super(AsocPeer, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AsocPeer, self).prepare_xml(element)
        if self.uri:
            create_text_xml(self.uri, element, QName(asoc_ns, "uri"))
        if self.name:
            create_text_xml(self.name, element, QName(asoc_ns, "name"))


class AsocPeerGroup(XMLObject):
    """The "asoc:peergroup" Element.

    """
    standard_tag = QName(asoc_ns, "peergroup")
    inner_factory = {
        "peer": AsocPeer.from_xml,
    }

    def __init__(self, name=None, peers=(), **kwargs):
        super(AsocPeerGroup, self).__init__(**kwargs)
        self.name = name
        self.peers = list(peers)

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault("peers", [])
        for sub in element:
            if sub.tag == QName(asoc_ns, "name"):
                kwargs["name"] = sub.text
            elif sub.tag == QName(asoc_ns, "peer"):
                kwargs["peers"].append(cls.inner_from_xml("peer", sub))
        return super(AsocPeerGroup, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AsocPeerGroup, self).prepare_xml(element)
        if self.name:
            create_text_xml(self.name, element, QName(asoc_ns, "name"))
        for item in sel.peers:
            item.create_xml(element)


class AsocPeers(XMLObject):
    """The "asoc:peers" Element and Document

    """
    inner_factory = {
        "peergroup": AsocPeerGroup.from_xml,
    }
    standard_tag = QName(asoc_ns, "peers")
    content_type = "application/asoc+xml;type=peers"

    def __init__(self, peergroups=(), **kwargs):
        super(AsocPeers, self).__init__(**kwargs)
        self.peergroups = list(peergroups)

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault("peergroups", [])
        for sub in element:
            if sub.tag == QName(asoc_ns, "peergroup"):
                kwargs["peergroup"].append(cls.inner_from_xml("peergroup",
                                                              sub))
        return super(AsocPeers, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AsocPeers, self).prepare_xml(element)
        for item in self.peergroups:
            item.create_xml(element)


class AsocCertificate(XMLObject):
    """The "asoc:certificate" Element.

    """
    standard_tag = QName(asoc_ns, "certificate")

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
    content_type = "application/asoc+xml;type=certificates"

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
        'link': AsocLink.from_xml,
    }

    def __init__(self, links=(), **kwargs):
        super(AsocService, self).__init__(**kwargs)
        self.links = list(links)

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault('links', [])
        for sub in element:
            if sub.tag == QName(asoc_ns, "link"):
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

