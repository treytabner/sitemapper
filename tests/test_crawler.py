"""Tests for sitemapper: Python based crawler and sitemap generator"""


def test_parse_args():
    """Tests for sitemapper.crawler.parse_args"""
    from shlex import split
    from sitemapper.crawler import parse_args

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
