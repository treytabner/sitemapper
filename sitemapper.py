#!/usr/bin/env python2

"""Crawl a website and generate a sitemap, limiting requests to domain only"""

import argparse
import json
import logging
import re
import sys

import requests
import six

from bs4 import BeautifulSoup


# setup log format...


# exception types



class Crawler():
    def __init__(self, site):
        self.site = site
        self.sitemap = {}

    def crawl(self, root='/'):
        if root not in self.sitemap:
            self.sitemap[root] = {}

        r = requests.get(self.site)
        if r.status_code is not requests.codes.ok:
            raise Exception("Error fetching %s: %s" % (self.site, r))

        soup = BeautifulSoup(r.text)
        for i in soup.find_all():
            for attr in i.attrs:
                if ((isinstance(i[attr], six.string_types) and
                     re.compile("^/(?!/)").search(i[attr]))):
                    if attr not in self.sitemap[root]:
                        self.sitemap[root][attr] = []
                    if i[attr] not in self.sitemap[root][attr]:
                        self.sitemap[root][attr].append(i[attr])


    def export(self):
        return self.sitemap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', help="Site to crawl and limit requests to")
    # verify ssl
    # verbose?
    # version?
    # auth support?

    args = parser.parse_args()

    crawler = Crawler(args.site)
    crawler.crawl()
    sitemap = crawler.export()
    print json.dumps(sitemap, sort_keys=True,
                     indent=4, separators=(',', ': '))


if __name__ == "__main__":
    sys.exit(main())
