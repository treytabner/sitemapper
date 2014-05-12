"""Utility functions for Sitemapper"""

import re

import six


def check_link(item, attr):
    """Check if we think the supplied item attribute is a local link"""
    value = item[attr]

    if isinstance(value, six.string_types):
        if re.compile("^/(?!/)").search(value):
            return True
        if value.startswith('mailto:'):
            return False

    if attr in ('href', 'src', 'action', ):
        if not re.compile("//").search(value):
            return True

    return False


def fix_site(site):
    """Return normalized URL for website by adding http:// if necessary"""
    return site if re.compile("://").search(site) \
        else 'http://%s' % site


def fix_root(site, root):
    """Return a normalized URL for the """
    return '%s%s' % (site, root) if root.startswith('/') \
        else '%s/%s' % (site, root)


def get_key(name):
    """Return whether or not the specified item is a link or asset"""
    return 'links' if name in ('a', 'form', ) else 'assets'


def get_base(url):
    """Return the base URL, with no GET parameters or anchors"""
    return re.compile("[\\?#]").split(url)[0]


def same_site(old, new):
    """Compare two sites to see if they are the same domain name"""
    if '://' in old:
        old = old.split('://')[1]

    if '://' in new:
        new = new.split('://')[1]

    return new.startswith(old)
