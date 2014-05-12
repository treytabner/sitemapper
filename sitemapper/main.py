#!/usr/bin/env python2

"""Crawl a website and generate a sitemap, limiting requests to domain only"""

import argparse
import collections
import json
import logging
import re
import sys

import requests
import six

from bs4 import BeautifulSoup


def check_link(item, attr):
    """Check if we think the supplied item attribute is a local link"""
    value = item[attr]

    if isinstance(value, six.string_types):
        if re.compile("^/(?!/)").search(value):
            return True
        if value.startswith('mailto:'):
            return False

    if attr in ('href', 'src', 'action', ):
        if re.compile("//").search(value):
            return False
        else:
            return True

    return False


def fix_site(site):
    """Return normalized URL for website by adding http:// if necessary"""
    return site if re.compile("://").search(site) \
        else 'http://%s' % site


def parse_args(args=sys.argv[1:]):
    """Parse arguments, setup logging and execute sitemap generation"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exclude', '-x', action='append', default=[],
                        help="Exclude URLs matching specified pattern")
    parser.add_argument('--insecure', '-k', action='store_true',
                        help="Disable SSL certificate verification")
    parser.add_argument('--verbose', '-v', action='count',
                        help="Enable verbose logging")
    parser.add_argument('site', help="Site to crawl and limit requests to")
    return parser.parse_args(args=args)


def setup_logging(verbosity):
    """Setup logging based on specified verbosity"""
    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity > 1:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    log_format = "[%(asctime)s] %(module)s %(levelname)s: %(message)s"
    logging.basicConfig(format=log_format, level=log_level,
                        datefmt='%c', stream=sys.stdout)


class Crawler(object):
    """Crawler that fetches website content and generates a sitemap"""
    def __init__(self):
        self.args = parse_args()
        setup_logging(self.args.verbose)

        self.sitemap = collections.defaultdict(dict)
        self.verify = not self.args.insecure
        self.site = fix_site(self.args.site)

    def generate(self, root='/'):
        """Crawl provided website, generating sitemap as we go"""
        if root.startswith('/'):
            url = '%s%s' % (self.site, root)
        else:
            url = '%s/%s' % (self.site, root)

        response = requests.get(url, verify=self.verify)
        if ((response.status_code != requests.codes['ok'] or
             'text/html' not in response.headers['content-type'])):
            return

        self.sitemap[root] = collections.defaultdict(list)
        soup = BeautifulSoup(response.text)
        for i in soup.find_all():
            for attr in i.attrs:
                if check_link(i, attr):
                    if i.name in ('a', 'form', ):
                        key = 'links'
                    else:
                        key = 'assets'

                    what = re.compile("[\\?#]").split(i[attr])[0]
                    if what not in self.sitemap[root][key]:
                        if True not in [x in what for x in self.args.exclude]:
                            self.sitemap[root][key].append(what)
        del soup, response

        self.sitemap[root]['links'].sort()
        self.sitemap[root]['assets'].sort()

        for i in self.sitemap[root]['links']:
            if i not in self.sitemap:
                self.generate(root=i)

        return self.sitemap


def main():
    """Instantiate a crawler, generate the sitemap and display in JSON"""
    crawler = Crawler()
    sitemap = crawler.generate()
    print(json.dumps(sitemap, sort_keys=True,
                     indent=4, separators=(',', ': ')))


if __name__ == "__main__":
    sys.exit(main())
