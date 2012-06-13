"""Elements of the Atom Syndication Format.

The document you are looking for is RFC 4287.
"""
from __future__ import absolute_import
import base64
from datetime import datetime, tzinfo
import re
from xml.etree.ElementTree import QName

from atomtools.exceptions import ValidationError
from atomtools.utils import (create_text_xml, flatten_xml_content,
                             from_text_xml, wrap_xml_tree)
from atomtools.tzinfo import TzInfoFixedOffset, TzInfoUTC
from atomtools.xhtml import xhtml_ns
from atomtools.xml import define_namespace, XMLObject, xml_ns

# Namespace
#
atom_ns = define_namespace("atom", "http://www.w3.org/2005/Atom")


class AtomCommon(XMLObject):
    """Basic construct for all Atom elements.
    
    The optional attribute *base* defines the base for relative URLs for
    this and any inner elements.

    The optional *lang* attribute indicates the natural language for this
    and any inner element.
    """
    def __init__(self, base=None, lang=None, **kwargs):
        super(AtomCommon, self).__init__(**kwargs)
        self.base = base
        self.lang = lang

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(AtomCommon, cls).from_xml(element,
                base=element.attrib.get(QName(xml_ns, "base")),
                lang=element.attrib.get(QName(xml_ns, "lang")),
                **kwargs)

    def prepare_xml(self, element):
        super(AtomCommon, self).prepare_xml(element)
        if self.base is not None:
            element.attrib[QName(xml_ns, "base")] = self.base
        if self.lang is not None:
            element.attrib[QName(xml_ns, "lang")] = self.lang


class AtomText(AtomCommon):
    """3.1.  Text Constructs

    The attribute *type* contains the type of the text which itself is in
    the attribute *text*. Its class depends on the value of *type*.

    There are three types defined: The type of ``"text"`` indicates plain
    text by way of a Unicode string. The type of ``"html"`` indicates
    HTML text. In this case, the text will still be a Unicode string and
    contain the textual representation of the HTML. Finally, if the type
    is ``"xhtml"``, the text is a element tree element, specifically, a
    xthml:div element.

    The text is never sanitized. If you are doing anything with it, you
    should check that it doesn't contain any malicious crap, such as
    xhtml:script elements.
    """
    def __init__(self, type="text", text=None, **kwargs):
        super(AtomText, self).__init__(**kwargs)
        self.type = type
        self.text = text

    @classmethod
    def from_xml(cls, element, **kwargs):
        type = element.attrib.get("type", "text").lower().strip()
        if type in ("text", "html"):
            text = flatten_xml_content(element)
        elif type == "xhtml":
            text = wrap_xml_tree(element, QName(xhtml_ns, "dvi"))
        return super(AtomText, cls).from_xml(element, type=type, text=text,
                                             **kwargs)

    def prepare_xml(self, element):
        super(AtomText, self).prepare_xml(element)
        if self.type is not None:
            element.attrib["type"] = self.type
        if self.type is not None and self.type.lower() == "xhtml":
            if self.text is None:
                element.append(QName(xhtml_ns, "div"))
            elif hasattr(self.text, "create_xml"):
                self.text.create_xml(element)
            else:
                element.append(self.text)
        elif self.text:
            element.text = unicode(self.text)


class AtomPerson(AtomCommon):
    """3.2.  Person Constructs

    The person construct describes a person.

    The *name* attribute contains the human-readable name for the person.
    The optional *uri* attribute contains an IRI associated with the person.
    The optional *email* attribute contains the person's email address.
    """
    def __init__(self, name=None, uri=None, email=None, **kwargs):
        super(AtomPerson, self).__init__(**kwargs)
        self.name = name
        self.uri = uri
        self.email = email

    @classmethod
    def from_xml(cls, element, **kwargs):
        for sub in element:
            if sub.tag == QName(atom_ns, "name"):
                kwargs["name"] = sub.text
            elif sub.tag == QName(atom_ns, "uri"):
                kwargs["uri"] = sub.text
            elif sub.tag == QName(atom_ns, "email"):
                kwargs["email"] = sub.text
        return super(AtomPerson, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AtomPerson, self).prepare_xml(element)
        create_text_xml(self.name, element, QName(atom_ns, "name"))
        if self.uri:
            create_text_xml(self.uri, element, QName(atom_ns, "uri"))
        if self.email:
            create_text_xml(self.email, element, QName(atom_ns, "email"))


class AtomDate(AtomCommon):
    """3.3.  Date Constructs

    A date construct contains a date and time in a specific format.
    """
    # XXX This is missing proper time offset support. We'll add that soon.
    #     (Note to self: RFC 3339.)
    #
    date_re = re.compile(r"(\d\d\d\d)-(\d\d)-(\d\d)T"
                         r"(\d\d):(\d\d):(\d\d)(\.\d+)?"
                         r"(Z|[-+](\d\d):(\d\d))")

    def __init__(self, datetime=None, **kwargs):
        super(AtomDate, self).__init__(**kwargs)
        self.datetime = datetime

    @classmethod
    def from_xml(cls, element, **kwargs):
        m = cls.date_re.match(element.text)
        if m is not None:
            (year, mon, day, hour, minute,
             sec, frac, off, offhour, offmin) = m.groups()
            if offhour is None:
                tz = TzInfoUTC()
            else:
                tz = TzInfoFixedOffset(int(offhour) * 60 + int(offmin))
            if frac:
                msec = int(float(frac) * 1000000)
            else:
                msec = 0
            dt = datetime(int(year), int(mon), int(day), int(hour),
                          int(minute), int(sec), msec, tz)
        else:
            dt = None
        return super(AtomDate, cls).from_xml(element, datetime=dt, **kwargs)

    def prepare_xml(self, element):
        if self.datetime is None:
            raise IncompleteObjectError, "datetime must not be None"
        super(AtomDate, self).prepare_xml(element)
        dt = self.datetime
        if dt.microsecond:
            frac = (".%06i" % dt.microsecond).rstrip("0")
        else:
            frac = ""
        if dt.tzinfo:
            tz = dt.tzinfo.tzname(dt)
        else:
            tz = "Z"
        element.text = ("%04d-%02d-%02dT%02d:%02d:%02d%s%s" 
                          % (dt.year, dt.month, dt.day, dt.hour,
                             dt.minute, dt.second, frac, tz))
        print element.text


class AtomContent(AtomCommon):
    """4.1.3.  The "atom:content" Element

    Contains either content of a certain type or a link to the actual
    content instead.

    The *type* attribute contains the media type of the content or one of
    "text", "html", "xhtml" in which case the content is text of that
    type. Composite media types are not supported. If *type* is ``None``,
    it is ``"text"``.

    The actual content lives in *content*. Its class depends on the value
    of *type*. For textual content, it will be a Unicode string. For XML
    content it will be an element tree element assuming the content is a
    single XML element or the content element itself if it is more complex.
    For binary content, it will be a binary string.

    See section 4.1.3.3. for how XML is parsed and generated. We support
    arbitrary media types. If you want to limit types in your derived
    class, overide :meth:`allow_type`.
    """
    def __init__(self, type=None, src=None, content=None, **kwargs):
        super(AtomContent, self).__init__(**kwargs)
        self.type = type
        self.src = src
        self.content = content

    @classmethod
    def from_xml(cls, element, **kwargs):
        type = element.attrib.get("type", "text").lower()
        src = element.attrib.get("src")
        if src:
            content = None
        elif type in ("text", "html"):
            content = flatten_xml_content(element)
        elif type == "xhtml":
            content = wrap_xml_tree(element, QName(xhtml_ns, "div"))
        elif (type in ('text/xml', 'application/xml',
                       'text/xml-external-parsed-entity',
                       'application/xml-external-parsed-entity',
                       'application/xml-dtd')
              or type.endswith('+xml') or type.endswith('/xml')):
            if len(element) == 1 and not element.text:
                content = element[0]
            else:
                content = element
        elif type.startswith("text/"):
            content = flatten_xml_content(elment)
        else:
            # XXX This is probably not robust enough.
            content = base64.b64decode(element.text)
        return super(AtomContent, cls).from_xml(element, type=type,
                                                src=src, content=content,
                                                **kwargs)

    def create_xml(self, parent, tag=QName(atom_ns, "content")):
        return super(AtomContent, self).create_xml(parent, tag)

    def prepare_xml(self, element):
        super(AtomContent, self).prepare_xml(element)
        if self.type:
            element.attrib["type"] = self.type
        if self.src:
            element.attrib["src"] = src
        elif self.type is None or self.type in ("text", "html"):
            element.text = unicode(self.content)
        elif (self.type in ("xhtml", 'text/xml', 'application/xml',
                            'text/xml-external-parsed-entity',
                            'application/xml-external-parsed-entity',
                            'application/xml-dtd')
              or self.type.endswith('+xml') or self.type.endswith('/xml')):
            if hasattr(self.text, "create_xml"):
                self.content.create_xml(element)
            elif self.content.tag == QName(atom_ns, "content"):
                element.text = self.content.text
                element.extend(self.content)
            else:
                element.append(self.content)
        elif self.type.startswith("text/"):
            element.text = unicode(self.content)
        else:
            element.text = base64.b64encode(self.content)

    def is_binary(self):
        """Is the content binary and needs base-64 encoding?"""
        return (not self.src and self.type
                and self.type not in ("text", "html", 
                                      "xhtml", 'text/xml', 'application/xml',
                                      'text/xml-external-parsed-entity',
                                      'application/xml-external-parsed-entity',
                                      'application/xml-dtd')
                and not self.type.endswith('+xml')
                and not self.type.endswith('/xml'))

class AtomCategory(AtomCommon):
    """4.2.2.  The "atom:category" Element

    Contains information about a category.

    The category's name is given in the attribute *term*. If the term is
    part of a specific scheme, that is given as a IRI in *scheme*. Finally,
    there may be a human-readable label in the attribute *label*.
    """
    def __init__(self, term=None, scheme=None, label=None, **kwargs):
        super(AtomCategory, self).__init__(**kwargs)
        self.term = term
        self.scheme = scheme
        self.label = label

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(AtomCategory, cls).from_xml(element,
                term=element.attrib.get("term"),
                scheme=element.attrib.get("scheme"),
                label=element.attrib.get("label"),
                **kwargs)

    def create_xml(self, parent, tag=QName(atom_ns, "category")):
        return super(AtomCategory, self).create_xml(parent, tag)

    def prepare_xml(self, element):
        super(AtomCategory, self).prepare_xml(element)
        element.attrib["term"] = self.term or ""
        if self.scheme:
            element.attrib["scheme"] = self.scheme
        if self.label:
            element.attrib["label"] = self.label


class AtomGenerator(AtomCommon):
    """4.2.4.  The "atom:generator" Element

    Identifies the user agent that created the XML. There is an *uri* and
    a *version* attribute besides the actual name in *text*.
    """
    def __init__(self, text=None, uri=None, version=None, **kwargs):
        super(AtomGenerator, self).__init__(**kwargs)
        self.text = text
        self.uri = uri
        self.version = version

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(AtomGenerator, cls).from_xml(element,
                text=flatten_xml_content(element),
                uri=element.attrib.get("uri"),
                version=element.attrib.get("version"),
                **kwargs)

    def create_xml(self, parent, tag=QName(atom_ns, "generator")):
        return super(AtomGenerator, self).create_xml(parent, tag)

    def prepare_xml(self, element):
        super(AtomGenerator, self).prepare_xml(element)
        element.text = self.text
        if self.uri:
            element.attrib["uri"] = self.uri
        if self.version:
            element.attrib["version"] = self.version


class AtomLink(AtomCommon):
    """"4.2.7.  The "atom:link" Element

    All you want to know about a link. Specifically, the attribute *href*
    contains the actual IRI, optional *rel* contains the relation type, the
    optional attribute *type* contains the media type, the optional
    *hreflang* the natural language of the linked dcument, optional
    *title* the document's title, and optional *length* the length in
    octets.
    """
    def __init__(self, href=None, rel=None, type=None, hreflang=None,
                 title=None, length=None, **kwargs):
        super(AtomLink, self).__init__(**kwargs)
        self.href = href
        self.rel = rel
        self.type = type
        self.hreflang = hreflang
        self.title = title
        self.length = length

    @classmethod
    def from_xml(cls, element, **kwargs):
        return super(AtomLink, cls).from_xml(element,
                href=element.attrib.get("href"),
                rel=element.attrib.get("rel"),
                type=element.attrib.get("type"),
                hreflang=element.attrib.get("hreflang"),
                title=element.attrib.get("title"),
                length=element.attrib.get("length"),
                **kwargs)

    def create_xml(self, parent, tag=QName(atom_ns, "link")):
        return super(AtomLink, self).create_xml(parent, tag)

    def prepare_xml(self, element):
        super(AtomLink, self).prepare_xml(element)
        element.attrib["href"] = self.href or ""
        if self.rel is not None:
            element.attrib["rel"] = self.rel
        if self.type is not None:
            element.attrib["type"] = self.type
        if self.hreflang is not None:
            element.attrib["hreflang"] = self.hreflang
        if self.title is not None:
            element.attrib["title"] = self.title
        if self.length is not None:
            element.attrib["length"] = self.length

class AtomMeta(AtomCommon):
    """Meta data common to atom:source, atom:entry, and atom:feed."""
    inner_factory = {
        "author": AtomPerson.from_xml,
        "category": AtomCategory.from_xml,
        "contributor": AtomPerson.from_xml,
        "link": AtomLink.from_xml,
        "rights": AtomText.from_xml,
        "title": AtomText.from_xml,
        "updated": AtomDate.from_xml,
    }

    def __init__(self, authors=(), categories=(), contributors=(),
                 id=None, links=(), rights=(), title=None, updated=None,
                 **kwargs):
        super(AtomMeta, self).__init__(**kwargs)
        self.authors = list(authors)
        self.categories = list(categories)
        self.contributors = list(contributors)
        self.id = id
        self.links = list(links)
        self.rights = rights
        self.title = title
        self.updated = updated

    @classmethod
    def from_xml(cls, element, **kwargs):
        kwargs.setdefault("authors", [])
        kwargs.setdefault("categories", [])
        kwargs.setdefault("contributors", [])
        kwargs.setdefault("links", [])
        for sub in element:
            if sub.tag == QName(atom_ns, "author"):
                kwargs["authors"].append(cls.inner_from_xml("author", sub))
            elif sub.tag == QName(atom_ns, "category"):
                kwargs["categories"].append(cls.inner_from_xml("category",
                                                               sub))
            elif sub.tag == QName(atom_ns, "contributor"):
                kwargs["contributors"].append(
                        cls.inner_from_xml("contributor", sub))
            elif sub.tag == QName(atom_ns, "id"):
                kwargs["id"] = from_text_xml(sub)
            elif sub.tag == QName(atom_ns, "link"):
                kwargs["links"].append(cls.inner_from_xml("link", sub))
            elif sub.tag == QName(atom_ns, "rights"):
                kwargs["rights"] = cls.inner_from_xml("rights", sub)
            elif sub.tag == QName(atom_ns, "title"):
                kwargs["title"] = cls.inner_from_xml("title", sub)
            elif sub.tag == QName(atom_ns, "updated"):
                kwargs["updated"] = cls.inner_from_xml("updated", sub)
        return super(AtomMeta, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AtomMeta, self).prepare_xml(element)
        for author in self.authors:
            author.create_xml(element, QName(atom_ns, "author"))
        for category in self.categories:
            category.create_xml(element, QName(atom_ns, "category"))
        for contributor in self.contributors:
            contributor.create_xml(element, QName(atom_ns, "contributor"))
        if self.id is not None:
            create_text_xml(self.id, element, QName(atom_ns, "id"))
        for link in self.links:
            link.create_xml(element, QName(atom_ns, "link"))
        if self.rights:
            self.rights.create_xml(element, QName(atom_ns, "rights"))
        if self.title:
            self.title.create_xml(element, QName(atom_ns, "title"))
        if self.updated:
            self.updated.create_xml(element, QName(atom_ns, "updated"))

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


class AtomSource(AtomMeta):
    """4.2.11. The "atom:source" Element

    Collects all the meta data of a feed which is copied if an entry is
    copied. Also serves as the base for feed.

    There is loads of attributes. See the source.
    """
    inner_factory = {
        "generator": AtomGenerator.from_xml,
        "subtitle": AtomText.from_xml,
    }

    def __init__(self, generator=None, icon=None, logo=None, subtitle=None,
                 **kwargs):
        super(AtomSource, self).__init__(**kwargs)
        self.generator = generator
        self.icon = icon
        self.logo = logo
        self.subtitle = subtitle

    @classmethod
    def from_xml(cls, element, **kwargs):
        for sub in element:
            if sub.tag == QName(atom_ns, "generator"):
                kwargs["generator"] = cls.inner_from_xml("generator", sub)
            elif sub.tag == QName(atom_ns, "icon"):
                kwargs["icon"] = from_text_xml(sub)
            elif sub.tag == QName(atom_ns, "logo"):
                kwargs["logo"] = from_text_xml(sub)
            elif sub.tag == QName(atom_ns, "subtitle"):
                kwargs["subtitle"] = cls.inner_from_xml("subtitle", sub)
        return super(AtomSource, cls).from_xml(element, **kwargs)

    def create_xml(self, parent, tag=QName(atom_ns, "source")):
            return super(AtomSource, self).create_xml(parent, tag)

    def prepare_xml(self, element):
        super(AtomSource, self).prepare_xml(element)
        if self.generator:
            self.generator.create_xml(element, QName(atom_ns, "generator"))
        if self.icon is not None:
            create_text_xml(self.icon, element, QName(atom_ns, "icon"))
        if self.logo is not None:
            create_text_xml(self.logo, element, QName(atom_ns, "logo"))
        if self.subtitle:
            self.subtitle.create_xml(element, QName(atom_ns, "subtitle"))


class AtomEntry(AtomMeta):
    """4.1.2. The "atom:entry" Element

    An individual feed entry with some meta data and the content.
    """
    inner_factory = {
        "content": AtomContent.from_xml,
        "published": AtomDate.from_xml,
        "source": AtomSource.from_xml,
        "summary": AtomText.from_xml,
    }
    content_type = "application/atom+xml;type=entry"

    def __init__(self, content=None, published=None, source=None,
                 summary=None, **kwargs):
        super(AtomEntry, self).__init__(**kwargs)
        self.content = content
        self.published = published
        self.source = source
        self.summary = summary

    @classmethod
    def from_xml(cls, element, **kwargs):
        for sub in element:
            if sub.tag == QName(atom_ns, "content"):
                kwargs["content"] = cls.inner_from_xml("content", sub)
            elif sub.tag == QName(atom_ns, "publised"):
                kwargs["published"] = cls.inner_from_xml("published", sub)
            elif sub.tag == QName(atom_ns, "source"):
                kwargs["source"] = cls.inner_from_xml("source", sub)
            elif sub.tag == QName(atom_ns, "summary"):
                kwargs["summary"] = cls.inner_from_xml("summary", sub)
        return super(AtomEntry, cls).from_xml(element, **kwargs)

    def create_xml(self, parent, tag=QName(atom_ns, "entry")):
        return super(AtomEntry, self).create_xml(parent, tag)

    def create_root_xml(self, tag=QName(atom_ns, "entry"),
                        element_class=None):
        return super(AtomEntry, self).create_root_xml(tag, element_class)

    def prepare_xml(self, element):
        super(AtomEntry, self).prepare_xml(element)
        if self.content:
            self.content.create_xml(element, QName(atom_ns, "content"))
        if self.published:
            self.published.create_xml(element, QName(atom_ns, "published"))
        if self.source:
            self.source.create_xml(element, QName(atom_ns, "source"))
        if self.summary:
            self.summary.create_xml(element, QName(atom_ns, "summary"))

    # A bunch of helpers to make life easier
    #
    def get_authors(self):
        """Return all authors."""
        res = []
        if self.authors:
            res.extend(self.authors)
        if self.source and self.source.authors:
            res.extend(self.source.authors)
        return res


class AtomFeed(AtomSource):
    """4.1.1.  The "atom:feed" Element

    Puts it all together: Basically an :class:`AtomSource` with a list of
    :class:`AtomEntry`. There is some extra conditions for the meta-data.
    Certain elements must be present. This is enforced by
    :meth:`prepare_xml`.
    """
    inner_factory = {
        "entry": AtomEntry.from_xml
    }
    content_type = "application/atom+xml"
    
    def __init__(self, entries=(), **kwargs):
        super(AtomFeed, self).__init__(**kwargs)
        self.entries = list(entries)

    @classmethod
    def from_xml(cls, element, **kwargs):
        entries = kwargs.setdefault("entries", [])
        for sub in element:
            if sub.tag == QName(atom_ns, "entry"):
                entries.append(cls.inner_from_xml("entry", sub))
        return super(AtomFeed, cls).from_xml(element, **kwargs)

    def create_xml(self, parent, tag=QName(atom_ns, "feed")):
        return super(AtomFeed, self).create_xml(parent, tag)

    def create_root_xml(self, tag=QName(atom_ns, "feed"),
                        element_class=None):
        return super(AtomFeed, self).create_root_xml(tag, element_class)

    def prepare_xml(self, element):
        super(AtomFeed, self).prepare_xml(element)
        for entry in self.entries:
            entry.create_xml(element, QName(atom_ns, "entry"))

