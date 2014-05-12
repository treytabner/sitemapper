"""Tests for sitemapper: Python based crawler and sitemap generator"""

from shlex import split
import sys

from sitemapper.crawler import parse_args
from sitemapper.crawler import Crawler
from sitemapper.crawler import main


def test_parse_args():
    """Tests for sitemapper.crawler.parse_args"""
    sys.argv = split("sitemapper www.example.com")
    args = parse_args()
    assert args.site == 'www.example.com'
    assert args.insecure is False
    assert args.debug is False
    assert args.exclude == []

    sys.argv = split("sitemapper --insecure https://www.example.com")
    args = parse_args()
    assert args.site == 'https://www.example.com'
    assert args.insecure is True
    assert args.debug is False
    assert args.exclude == []

    sys.argv = split("sitemapper -d --exclude test http://www.example.com")
    args = parse_args()
    assert args.site == 'http://www.example.com'
    assert args.insecure is False
    assert args.debug is True
    assert args.exclude == ['test']

    sys.argv = split("sitemapper --debug -x test1 -x test2 example.com")
    args = parse_args()
    assert args.site == 'example.com'
    assert args.insecure is False
    assert args.debug is True
    assert args.exclude == ['test1', 'test2']


def test_crawler():
    """Tests for sitemapper.crawler.Crawler"""

    crawler = Crawler('www.example.com')
    assert crawler.site == 'http://www.example.com'
    assert crawler.sitemap == {}
    assert crawler.verify is True
    assert crawler.debug is False
    assert crawler.exclude == []

    crawler = Crawler('www.example.com', debug=True)
    assert crawler.site == 'http://www.example.com'
    assert crawler.sitemap == {}
    assert crawler.verify is True
    assert crawler.debug is True
    assert crawler.exclude == []

    crawler = Crawler('https://www.example.com', insecure=True)
    assert crawler.site == 'https://www.example.com'
    assert crawler.sitemap == {}
    assert crawler.verify is False
    assert crawler.debug is False
    assert crawler.exclude == []

    crawler = Crawler('https://www.example.com', exclude=['test1'])
    assert crawler.site == 'https://www.example.com'
    assert crawler.sitemap == {}
    assert crawler.verify is True
    assert crawler.debug is False
    assert crawler.exclude == ['test1']


def test_main():
    """Tests for sitemapper.crawler.main"""
    sys.argv = split("sitemapper --debug www.tabner.com")
    main()
