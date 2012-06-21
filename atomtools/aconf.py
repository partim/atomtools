"""Accout Configuration

This lives within the atomtools since it is anchored in the app:service
documents.
"""

from atomtools.atom import AtomCommon
from atomtools.atompub import AppService
from atomtools.xml import define_namespace, QName, XMLObject, xml_ns


# Namespace
#
aconf_ns = define_namespace("aconf", "http://www.alipedis.com/2012/aconf")

class AconfLink(XMLObject):
    """The "aconf:link" Element

    Links to the various configuration services. This has only a subset of
    xhtml:link or atom:link, mostly because the rel attribute defines
    the expectations.
    """
    standard_tag = QName(aconf_ns, "link")

    def __init__(self, href=None, rel=None, base=None, **kwargs):
        super(AconfLink, self).__init__(**kwargs)
        self.href = href
        self.rel = rel
        self.base = base

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(AconfLink, cls).from_xml(element,
                href=element.attrib.get("href"),
                rel=element.attrib.get("rel"),
                base=element.attrib.get(QName(xml_ns, "base")),
                **kwargs)

    def prepare_xml(self, element):
        super(AconfLink, self).prepare_xml(element)
        if self.href is not None:
            element.attrib["href"] = self.href
        if self.rel is not None:
            element.attrib["rel"] = self.rel
        if self.base is not None:
            element.attrib[QName(xml_ns, "base")] = self.base


class AconfCertificate(XMLObject):
    """The "aconf:certificate" Element.

    """
    standard_tag = QName(aconf_ns, "certificate")

    def __init__(self, href=None, name=None, certificate=None, **kwargs):
        super(AconfCertificate, self).__init__(**kwargs)
        self.href = href
        self.name = name
        self.certificate = certificate

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(AconfCertificate, cls).from_xml(element,
                href=element.attrib.get("href"),
                name=element.attrib.get("name"),
                certificate=element.text,
                **kwargs)

    def prepare_xml(self, element):
        super(AconfCertificate, self).prepare_xml(element)
        if self.href is not None:
            element.attrib["href"] = self.href
        if self.name is not None:
            element.attrib["name"] = self.name
        if self.certificate:
            element.text = self.certificate


class AconfCertificates(XMLObject):
    """The "aconf:certificates" Element

    Contains a list of aconf:certifcate elements. Can be its own document.
    """
    inner_factory = {
        "certificate": AconfCertificate.from_xml,
    }
    standard_tag = QName(aconf_ns, "certificates")
    content_type = "application/x-aconf+xml;type=certificates"

    def __init__(self, certificates=(), **kwargs):
        super(AconfCertificates, self).__init__(**kwargs)
        self.certificates = list(certificates)

    @classmethod
    def from_xml(self, element, **kwargs):
        kwargs.setdefault("certificates", list())
        for sub in element:
            if sub.tag == QName(aconf_ns, "certificate"):
                kwargs["certificates"].append(
                        cls.inner_from_xml("certificate", sub))
        return super(AconfCertificates, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AconfCertificates, self).prepare_xml(element)
        for cert in self.certificates:
            cert.create_xml(element)


class AconfService(AppService):
    """An app:service element with aconf extensions.

    """
    inner_factory = {
        'link': AconfLink,
    }

    def __init__(self, links=(), **kwargs):
        super(AconfService, self).__init__(**kwargs)
        self.links = list(links)

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault('links', [])
        for sub in element:
            if sub.tag == QName(aconf_ns, "link"):
                kwargs["links"].append(cls.inner_from_xml("link", sub))
        return super(AconfService, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AconfService, self).prepare_xml(element)
        for link in self.links:
            link.create_xml(element)


