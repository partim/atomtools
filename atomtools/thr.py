"""Atom Threading Extensions

The document you are looking for is RFC 4685.
"""

from atomtools.atom import AtomCommon, AtomLink, AtomText
from atomtools.xml import define_namespace, QName, XMLObject

# Namespaces
#
thr_ns = define_namespace("thr", "http://purl.org/syndication/thread/1.0")

class ThrInReplyTo(AtomCommon):
    """3.  The 'in-reply-to' Extension Element.

    """
    def __init__(self, ref=None, href=None, source=None, type=None, **kwargs):
        super(ThrInReplyTo, self).__init__(**kwargs)
        self.ref = ref
        self.href = href
        self.source = source
        self.type = type

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(ThrInReplyTo, cls).from_xml(element,
                ref=element.attrib.get("ref"),
                href=element.attrib.get("href"),
                source=element.attrib.get("source"),
                type=element.attrib.get("type"),
                **kwargs)

    def create_xml(self, parent, tag=QName(thr_ns, "in-reply-to")):
        return super(ThrInReplyTo, self).create_xml(parent, tag)

    def prepare_xml(self, element):
        super(ThrInReplyTo, self).prepare_xml(element)
        if self.ref is not None:
            element.attrib["ref"] = self.ref
        if self.href is not None:
            element.attrib["href"] = self.href
        if self.source is not None:
            element.attrib["source"] = self.source
        if self.type is not None:
            element.attrib["type"] = self.type


class ThrLink(AtomLink):
    """4.  The 'replies' Link Relation

    """
    def __init__(self, count=None, updated=None, **kwargs):
        super(ThrLink, self).__init__(**kwargs)
        self.count = count
        self.updated = updated

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(ThrLink, cls).from_xml(element,
                count=element.attrib.get(QName(thr_ns, "count")),
                updated=element.attrib.get(QName(thr_ns, "updated")),
                **kwargs)

    def prepare_xml(self, element):
        super(ThrLink, self).prepare_xml(element)
        if self.count is not None:
            element.attrib[QName(thr_ns, "count")] = self.count
        if self.updated is not None:
            element.attrib[QName(thr_ns, "updated")] = self.updated


class ThrMixin(XMLObject):
    """5.  The 'total' Extension Element

    """
    inner_factor = {
        "total": AtomText.from_xml,
        "link": ThrLink.from_xml,
        "in-reply-to": ThrInReplyTo.from_xml
    }

    def __init__(self, total=None, in_reply_tos=(), **kwargs):
        super(ThrMixin, self).__init__(**kwargs)
        self.total = total
        self.in_reply_tos = list(in_reply_tos)

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault("in_reply_tos", [])
        for sub in element:
            if sub.tag == QName(thr_ns, "total"):
                kwargs["total"] = cls.inner_from_xml("total", sub)
            if sub.tag == QName(thr_ns, "in-reply-to"):
                kwargs["in_reply_tos"].append(
                        cls.inner_from_xml("in_reply_to", sub))
        return super(ThrMixin, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(ThrMixin, self).prepare_xml(element)
        if self.total:
            self.total.create_xml(element, QName(thr_ns, "total"))
        for item in self.in_reply_tos:
            item.create_xml(element)
