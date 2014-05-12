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


def parse_args():
    """Parse arguments, setup logging and execute sitemap generation"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exclude', '-x', action='append', default=[],
                        help="Exclude URLs matching specified pattern")
    parser.add_argument('--insecure', '-k', action='store_true',
                        help="Disable SSL certificate verification")
    parser.add_argument('--debug', '-d', action='store_true',
                        help="Enable debug logging")
    parser.add_argument('--simulate', '-s', action='store_true',
                        help="Don't actually do anything on the network")
    parser.add_argument('site', help="Site to crawl and limit requests to")
    return parser.parse_args()


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
    def __init__(self, site, **kwargs):
        setup_logging(debug=kwargs.get('debug'))
        self.requests = requests
        self.sitemap = {}
        self.site = util.fix_site(site)
        self.verify = not kwargs.get('insecure', False)
        self.debug = kwargs.get('debug', False)
        self.exclude = kwargs.get('exclude', [])
        self.simulate = kwargs.get('simulate', False)

    def fetch(self, url):
        """Fetch content only if it's on the same domain, ignore binaries"""

        # Fetch headers
        response = self.requests.head(url, verify=self.verify)

        # Only if HTML content was found
        if ((response.status_code != requests.codes['not_found'] and
             'text/html' in response.headers['content-type'])):

            # Only if this is not a redirect to another domain
            location = response.headers.get('location')
            if not location or util.same_site(self.site, location):

                # Fetch the actual content (stream so we can ignore binaries)
                response = self.requests.get(location or url,
                                             verify=self.verify,
                                             stream=True)

                # Return if not an HTTP 200 or not text/html
                if ((response.status_code == requests.codes['ok'] and
                     'text/html' in response.headers['content-type'])):
                    return response.text

    def generate(self, root='/'):
        """Crawl provided website, generating sitemap as we go"""
        url = util.fix_root(self.site, root)

        content = '' if self.simulate else self.fetch(url)
        if content:
            self.sitemap[root] = collections.defaultdict(list)

            # Parse the HTML and clean up
            soup = BeautifulSoup(content)
            for i in soup.find_all():
                for attr in i.attrs:
                    if util.check_link(i, attr):
                        key = util.get_key(i.name)
                        base = util.get_base(i[attr])
                        if base and base not in self.sitemap[root][key]:
                            if ((True not in
                                 [x in base for x in self.exclude])):
                                self.sitemap[root][key].append(base)

            del soup, content

            # Sort links and assets for readability
            if 'assets' in self.sitemap[root]:
                self.sitemap[root]['assets'].sort()

            if 'links' in self.sitemap[root]:
                self.sitemap[root]['links'].sort()

                # Recursively crawl other links that we haven't seen yet
                for i in self.sitemap[root]['links']:
                    if i not in self.sitemap:
                        self.generate(root=i)

        return self.sitemap


def main():
    """Instantiate a crawler, generate the sitemap and display in JSON"""
    args = parse_args()
    crawler = Crawler(args.site,
                      insecure=args.insecure,
                      debug=args.debug,
                      exclude=args.exclude,
                      simulate=args.simulate)
    sitemap = crawler.generate()
    print(json.dumps(sitemap, sort_keys=True,
                     indent=4, separators=(',', ': ')))
