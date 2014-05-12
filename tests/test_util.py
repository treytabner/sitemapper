"""Tests for sitemapper: Python based crawler and sitemap generator"""


def test_check_link():
    """Tests for sitemapper.util.check_link"""
    from sitemapper.util import check_link

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
    assert check_link({'href': 'mailto:trey@tabner.com'}, 'href') is False


def test_fix_site():
    """Tests for sitemapper.util.fix_site"""
    from sitemapper.util import fix_site

    assert fix_site('treytabner.com') == 'http://treytabner.com'
    assert fix_site('http://treytabner.com') == 'http://treytabner.com'
    assert fix_site('https://treytabner.com') == 'https://treytabner.com'
    assert fix_site('ssh://treytabner.com') == 'ssh://treytabner.com'


def test_fix_root():
    """Tests for sitemapper.util.fix_root"""
    from sitemapper.util import fix_root

    assert (fix_root('http://example.com', '/contact') ==
            'http://example.com/contact')
    assert (fix_root('http://example.com', 'contact') ==
            'http://example.com/contact')


def test_get_key():
    """Tests for sitemapper.util.get_key"""
    from sitemapper.util import get_key

    assert get_key('a') == 'links'
    assert get_key('form') == 'links'
    assert get_key('img') == 'assets'
    assert get_key('link') == 'assets'
    assert get_key('script') == 'assets'


def test_get_base():
    """Tests for sitemapper.util.get_base"""
    from sitemapper.util import get_base

    assert get_base('/example') == '/example'
    assert get_base('/example#footer') == '/example'
    assert get_base('/example?test=1') == '/example'


def test_same_site():
    """Tests for sitemapper.util.same_site"""
    from sitemapper.util import same_site

    assert same_site('http://example.com',
                     'http://example.com') is True
    assert same_site('http://example.com',
                     'http://example.com/new') is True
    assert same_site('http://example.com',
                     'https://example.com') is True
    assert same_site('http://example.com',
                     'https://example.com/new') is True

    assert same_site('http://example.com',
                     'http://other.example.com') is False
    assert same_site('http://example.com',
                     'http://other.example.com/new') is False
    assert same_site('http://example.com',
                     'https://other.example.com') is False
    assert same_site('http://example.com',
                     'https://other.example.com/new') is False
