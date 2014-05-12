"""Tests for sitemapper: Python based crawler and sitemap generator"""

from shlex import split
import sys

from mock import Mock

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


def test_crawler_generate():
    """Tests for sitemapper.crawler.Crawler.generate"""
    crawler = Crawler('www.example.com')
    mock_requests = crawler.requests
    crawler.requests.head = Mock()
    crawler.requests.get = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'content-type': 'text/html'}
    mock_response.text = """
<html>
<head>
<title>Test</title>
<script src="/asset1" />
</head>
<body>
<ul>
<li><a href="/location1">Location 1</a></li>
<li><a href="/location2">Location 2</a></li>
<li><a href="/location3">Location 3</a></li>
</ul>
</body>
</html>
"""
    mock_requests.get.return_value = mock_response
    mock_requests.head.return_value = mock_response
    sitemap = crawler.generate()
    assert '/' in sitemap
    assert 'links' in sitemap['/']
    assert 'assets' in sitemap['/']
    assert '/location1' in sitemap
    assert 'links' in sitemap['/location1']
    assert 'assets' in sitemap['/location1']
    assert '/location2' in sitemap
    assert 'links' in sitemap['/location2']
    assert 'assets' in sitemap['/location2']
    assert '/location3' in sitemap
    assert 'links' in sitemap['/location3']
    assert 'assets' in sitemap['/location3']


def test_crawler_main():
    """Tests for sitemapper.crawler.main"""
    sys.argv = split("sitemapper -s www.example.com")
    main()
