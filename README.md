# Sitemapper

Sitemapper is a Python-based website crawler that generates a sitemap in JSON for a specified website.

## Installation

To install Sitemapper, run:

> pip install -e .

This will install any dependencies such as Python requests and BeautifulSoup.

## Execution

To execute Sitemapper, run:

> sitemapper --help
> sitemapper www.tabner.com
> sitemapper --debug --exclude community www.digitalocean.com

The --debug option will print output for the various HTTP requests to stderr.

The --exclude option will cause the crawler to exclude certain URLs that may otherwise cause problems.
