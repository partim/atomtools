"""Atom for Messaging

These are a few Atom extensions to allow using Atom and Atompub for
messaging. Mostly, they reflect the fact that messages are not fully
blown atom:entries -- they don't have titles and summaries and some of
the other elements.

You can find the documentation in doc/ames in the source distribution.
"""

from atomtools.atom import (AtomCategory, AtomCommon, AtomDate, AtomEntry,
                            AtomLink, AtomPerson, AtomText, atom_ns)
from atomtools.atompub import AppFeed
from atomtools.utils import create_text_xml, from_text_xml
from atomtools.xml import QName, define_namespace

# Namespace
#
ames_ns = define_namespace("ames", "http://www.alipedis.com/2012/ames")

class AmesPost(AtomCommon):
    """An entry without requirement to have a title.
    
    """
    inner_factory = {
        "entry": AtomEntry.from_xml,

        "author": AtomPerson.from_xml,
        "category": AtomCategory.from_xml,
        "content": AtomText.from_xml,
        "link": AtomLink.from_xml,
        "published": AtomDate.from_xml,
        "rights": AtomText.from_xml,
        "updated": AtomDate.from_xml,
    }
    standard_tag = QName(ames_ns, "post")
    content_type = "application/x-ames+xml"

    def __init__(self, authors=(), categories=(), content=None, id=None,
                 links=(), published=None, rights=None, updated=None,
                 **kwargs):
        super(AmesPost, self).__init__(**kwargs)
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
            elif sub.tag == QName(ames_ns, "content"):
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
        return super(AmesPost, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AmesPost, self).prepare_xml(element)
        for author in self.authors:
            author.create_xml(element, QName(atom_ns, "author"))
        for category in self.categories:
            category.create_xml(element, QName(atom_ns, "category"))
        if self.content:
            self.content.create_xml(element, QName(ames_ns, "content"))
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


class AmesFeed(AppFeed):
    """An atom:feed with ames:posts.
    
    """
    inner_factory = {
        "post": AmesPost.from_xml,
    }

    def __init__(self, posts=(), **kwargs):
        super(AmesFeed, self).__init__(**kwargs)
        self.posts = list(posts)

    @classmethod
    def from_xml(cls, element, **kwargs):
        entries = kwargs.setdefault("entries", [])
        for sub in element:
            if sub.tag == QName(ames_ns, "post"):
                entries.append(cls.inner_from_xml("post", sub))
        return super(AmesFeed, cls).from_xml(element, **kwargs)

