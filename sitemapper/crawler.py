#!/usr/bin/env python2

"""Crawl a website and generate a sitemap, limiting requests to domain only"""

import argparse
import collections
import json
import logging
import sys

import requests

from bs4 import BeautifulSoup

from sitemapper import util


def parse_args(args=sys.argv[1:]):
    """Parse arguments, setup logging and execute sitemap generation"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exclude', '-x', action='append', default=[],
                        help="Exclude URLs matching specified pattern")
    parser.add_argument('--insecure', '-k', action='store_true',
                        help="Disable SSL certificate verification")
    parser.add_argument('--debug', '-d', action='store_true',
                        help="Enable debug logging")
    parser.add_argument('site', help="Site to crawl and limit requests to")
    return parser.parse_args(args=args)


def setup_logging(debug=False):
    """Setup logging based on specified verbosity"""
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    log_format = "[%(asctime)s] %(module)s %(levelname)s: %(message)s"
    logging.basicConfig(format=log_format, level=log_level,
                        datefmt='%c', stream=sys.stderr)


class Crawler(object):
    """Crawler that fetches website content and generates a sitemap"""
    def __init__(self):
        self.args = parse_args()
        setup_logging(debug=self.args.debug)

        self.sitemap = collections.defaultdict(dict)
        self.verify = not self.args.insecure
        self.site = util.fix_site(self.args.site)

    def fetch(self, url):
        """Fetch content only if it's on the same domain, ignore binaries"""

        # Fetch headers
        response = requests.head(url, verify=self.verify)

        # Return if not found or not text/html, we don't want binaries
        if ((response.status_code == requests.codes['not_found'] or
             'text/html' not in response.headers['content-type'])):
            logging.debug("Skipping binary or content not found: %s", url)
            return

        # Bail if this is a redirect to another domain
        location = response.headers.get('location')
        if location and not util.same_site(self.site, location):
            logging.debug("Skipping content on another domain: %s", location)
            return

        # Fetch the actual content
        response = requests.get(location or url, verify=self.verify)

        # Return if not an HTTP 200 or not text/html
        if ((response.status_code != requests.codes['ok'] or
             'text/html' not in response.headers['content-type'])):
            return

        return response.text

    def generate(self, root='/'):
        """Crawl provided website, generating sitemap as we go"""
        url = util.fix_root(self.site, root)
        self.sitemap[root] = collections.defaultdict(list)

        content = self.fetch(url)
        if not content:
            return

        # Parse the HTML and clean up
        soup = BeautifulSoup(content)
        for i in soup.find_all():
            for attr in i.attrs:
                if util.check_link(i, attr):
                    key = util.get_key(i.name)
                    base = util.get_base(i[attr])
                    if base and base not in self.sitemap[root][key]:
                        if True not in [x in base for x in self.args.exclude]:
                            self.sitemap[root][key].append(base)

        del soup, content

        self.sitemap[root]['links'].sort()
        self.sitemap[root]['assets'].sort()

        # Recursively crawl other links that we haven't seen yet
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
