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


class Crawler():
    def __init__(self, site, insecure=False, exclude=[]):
        if re.compile("^http(s?)://").search(site):
            self.site = site
        else:
            self.site = 'http://%s' % site

        self.sitemap = collections.defaultdict(dict)
        self.verify = not insecure
        self.exclude = exclude

    def check(self, item, attr):
        value = item[attr]

        if isinstance(value, six.string_types):
            if re.compile("^/(?!/)").search(value):
                return True
            if value.startswith('mailto:'):
                return False

        elif attr in ('href', 'src', 'action', ):
            if re.compile("^http(s?)://").search(value):
                return False
            else:
                return True

    def crawl(self, root='/'):
        if root.startswith('/'):
            url = '%s%s' % (self.site, root)
        else:
            url = '%s/%s' % (self.site, root)

        r = requests.get(url, verify=self.verify)
        if ((r.status_code != requests.codes.ok or
             'text/html' not in r.headers['content-type'])):
            return

        self.sitemap[root] = collections.defaultdict(list)
        soup = BeautifulSoup(r.text)
        for i in soup.find_all():
            for attr in i.attrs:
                if self.check(i, attr):
                    if i.name in ('a', 'form', ):
                        key = 'links'
                    else:
                        key = 'assets'

                    what = re.compile("[\\?#]").split(i[attr])[0]
                    if what not in self.sitemap[root][key]:
                        if True not in [x in what for x in self.exclude]:
                            self.sitemap[root][key].append(what)
        del soup, r

        self.sitemap[root]['links'].sort()
        self.sitemap[root]['assets'].sort()

        for i in self.sitemap[root]['links']:
            if i not in self.sitemap:
                self.crawl(root=i)

        return self.sitemap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exclude', '-x', action='append', default=[],
                        help="Exclude URLs matching specified pattern")
    parser.add_argument('--insecure', '-k', action='store_true',
                        help="Disable SSL certificate verification")
    parser.add_argument('--verbose', '-v', action='count',
                        help="Enable verbose logging")
    parser.add_argument('site', help="Site to crawl and limit requests to")

    args = parser.parse_args()
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose > 1:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    log_format = "[%(asctime)s] %(module)s %(levelname)s: %(message)s"
    logging.basicConfig(format=log_format, level=log_level,
                        datefmt='%c', stream=sys.stdout)

    crawler = Crawler(args.site, args.insecure, args.exclude)
    sitemap = crawler.crawl()
    print(json.dumps(sitemap, sort_keys=True,
                     indent=4, separators=(',', ': ')))


if __name__ == "__main__":
    sys.exit(main())
