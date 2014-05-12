"""Tests for sitemapper: Python based crawler and sitemap generator"""

import sys

from shlex import split

from sitemapper.crawler import parse_args
from sitemapper.crawler import Crawler
from sitemapper.crawler import main


def test_parse_args():
    """Tests for sitemapper.crawler.parse_args"""
    args = parse_args(split("www.example.com"))
    assert args.site == 'www.example.com'
    assert args.insecure is False
    assert args.debug is False
    assert args.exclude == []

    args = parse_args(split("--insecure https://www.example.com"))
    assert args.site == 'https://www.example.com'
    assert args.insecure is True
    assert args.debug is False
    assert args.exclude == []

    args = parse_args(split("-d --exclude test http://www.example.com"))
    assert args.site == 'http://www.example.com'
    assert args.insecure is False
    assert args.debug is True
    assert args.exclude == ['test']

    args = parse_args(split("--debug -x test1 -x test2 example.com"))
    assert args.site == 'example.com'
    assert args.insecure is False
    assert args.debug is True
    assert args.exclude == ['test1', 'test2']


def test_crawler():
    """Tests for sitemapper.crawler.Crawler"""

    sys.argv = split("sitemapper www.example.com")
    crawler = Crawler()
    assert crawler.site == 'http://www.example.com'
    assert crawler.sitemap == {}
    assert crawler.verify == True
    assert crawler.args.debug == False
    assert crawler.args.exclude == []

    sys.argv = split("sitemapper --debug www.example.com")
    crawler = Crawler()
    assert crawler.site == 'http://www.example.com'
    assert crawler.sitemap == {}
    assert crawler.verify == True
    assert crawler.args.debug == True
    assert crawler.args.exclude == []


def test_main():
    """Tests for sitemapper.crawler.main"""
    sys.argv = split("sitemapper --debug www.tabner.com")
    try:
        main()
    except Exception as exc:
        raise
