"""Tests for sitemapper: Python based crawler and sitemap generator"""


def test_fix_site():
    """Tests for sitemapper.main.fix_site"""
    from sitemapper.main import fix_site

    assert fix_site('treytabner.com') == 'http://treytabner.com'
    assert fix_site('http://treytabner.com') == 'http://treytabner.com'
    assert fix_site('https://treytabner.com') == 'https://treytabner.com'
    assert fix_site('ssh://treytabner.com') == 'ssh://treytabner.com'


def test_check_link():
    """Tests for sitemapper.main.check_link"""
    from sitemapper.main import check_link

    # Local links
    assert check_link({'href': '/contact'}, 'href') is True
    assert check_link({'src': 'example.png'}, 'src') is True
    assert check_link({'src': '/assets/test.js'}, 'src') is True

    # Off-site and other stuff
    assert check_link({'href': '//example.com/file'}, 'href') is False
    assert check_link({'href': 'http://example.com/location'}, 'href') is False
    assert check_link({'rel': ['stylesheet']}, 'rel') is False
    assert check_link({'class': ['menu']}, 'class') is False
    assert check_link({'type': 'text/javascript'}, 'type') is False
    assert check_link({'value': 'submit'}, 'value') is False


def test_parse_args():
    """Tests for sitemapper.main.parse_args"""
    from shlex import split
    from sitemapper.main import parse_args

    args = parse_args(split("www.example.com"))
    assert args.site == 'www.example.com'
    assert args.insecure is False
    assert args.verbose is None
    assert args.exclude == []

    args = parse_args(split("--insecure -v https://www.example.com"))
    assert args.site == 'https://www.example.com'
    assert args.insecure is True
    assert args.verbose is 1
    assert args.exclude == []

    args = parse_args(split("-vv --exclude test http://www.example.com"))
    assert args.site == 'http://www.example.com'
    assert args.insecure is False
    assert args.verbose is 2
    assert args.exclude == ['test']

    args = parse_args(split("--verbose -x test1 -x test2 example.com"))
    assert args.site == 'example.com'
    assert args.insecure is False
    assert args.verbose is 1
    assert args.exclude == ['test1', 'test2']
