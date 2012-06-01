"""Atom for Messaging

These are a few Atom extensions to allow using Atom and Atompub for
messaging. Mostly, they reflect the fact that messages are not fully
blown atom:entries -- they don't have titles and summaries and some of
the other elements.

For now, the documentation is the code here. We'll add proper specs later.
"""

from __future__ import absolute_import
from xml.etree.ElementTree import QName

from atomtools.atompub import AppEntry, AppFeed
from atomtools.xml import define_namespace

# Namespace
#
ames_ns = define_namespace("ames", "http://www.alipedis.com/2012/ames")

class AmesPost(AppEntry):
    """An entry without requirement to have a title.
    
    """
    content_type = "application/x-ames+xml;type=post"

    def create_xml(self, parent, tag=QName(ames_ns, "post")):
        return super(AmesPost, self).create_xml(parent, tag)

    def create_root_xml(self, tag=QName(ames_ns, "post"),
                        element_class=None):
        return super(AmesPost, self).create_root_xml(tag, element_class)


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
        posts = kwargs.setdefault("posts", [])
        for sub in element:
            if sub.tag == QName(ames_ns, "post"):
                posts.append(cls.inner_from_xml("post", sub))
        return super(AmesFeed, cls).from_xml(element, **kwargs)

    def prepare_xml(self, element):
        super(AmesFeed, self).prepare_xml(element)
        for post in self.posts:
            post.create_xml(element, QName(ames_ns, "post"))

