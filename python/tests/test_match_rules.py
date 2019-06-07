# -*- coding: utf-8 -*-
'''
test_match_rules.py - unit tests for urlcanon.MatchRule

Copyright (C) 2017 Internet Archive

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import urlcanon

def test_match_rules():
    rule = urlcanon.MatchRule(
            surt=urlcanon.semantic(b'http://example.com/foo/bar').surt())
    assert not rule.applies('hTTp://EXAmple.com.../FOo/Bar#zuh')
    assert rule.applies('http://example.com/foo/bar')
    assert not rule.applies('http://example.com/foo/baz')

    rule = urlcanon.MatchRule(
        surt=urlcanon.semantic(b'http://example.com/foo/bar').surt(), exact=True)
    assert not rule.applies('hTTp://EXAmple.com.../FOo/Bar#zuh')
    assert rule.applies('http://example.com/foo/bar')
    assert not rule.applies('http://example.com/foo/baz')
    assert not rule.applies('http://example.com/foo/bar/baz')

    rule = urlcanon.MatchRule(
            ssurt=urlcanon.semantic(b'http://example.com/foo/bar').ssurt())
    assert not rule.applies('hTTp://EXAmple.com.../FOo/Bar#zuh')
    assert rule.applies(b'http://example.com/foo/bar')
    assert not rule.applies('http://example.com/foo/baz')

    rule = urlcanon.MatchRule(
            ssurt=urlcanon.semantic('http://example.com/foo/bar').ssurt().decode('ascii'))
    assert not rule.applies('hTTp://EXAmple.com.../FOo/Bar#zuh')
    assert rule.applies(b'http://example.com/foo/bar')
    assert not rule.applies('http://example.com/foo/baz')

    rule = urlcanon.MatchRule(
            url_match='REGEX_MATCH', value=b'^.*/audio_file/.*\.mp3$')
    assert not rule.applies('http://foo.com/some.mp3')
    assert rule.applies('http://foo.com/blah/audio_file/some.mp3')

    rule = urlcanon.MatchRule(
            url_match='SURT_MATCH', value=b'http://(com,vimeocdn,')
    assert rule.applies('http://a.b.vimeocdn.com/blahblah')
    assert not rule.applies('https://a.b.vimeocdn.com/blahblah')

    rule = urlcanon.MatchRule(
            url_match='STRING_MATCH', value=b'ec-media.soundcloud.com')
    rule = urlcanon.MatchRule(
            regex=b'^https?://twitter\.com.*$')

    rule = urlcanon.MatchRule(substring=b'facebook.com')
    assert rule.applies('https://www.facebook.com/whatevz')

    rule = urlcanon.MatchRule(
            regex=b'^https?://(www.)?youtube.com/watch?.*$',
            parent_url_regex=b'^https?://(www.)?youtube.com/user/.*$')
    assert not rule.applies('https://www.youtube.com/watch?v=dUIn5OAPS5s')
    assert rule.applies(
            'https://www.youtube.com/watch?v=dUIn5OAPS5s',
            parent_url='https://www.youtube.com/user/SonoraSantaneraVEVO')

    rule = urlcanon.MatchRule(
            domain=b'twitter.com', url_match='REGEX_MATCH',
            value=b'^.*lang=(?!en).*$')
    assert not rule.applies('https://twitter.com/twit')
    assert not rule.applies('https://twitter.com/twit?lang=en')
    assert rule.applies('https://twitter.com/twit?lang=es')

    rule = urlcanon.MatchRule(domain=b'example.com')
    assert not rule.applies('https://twitter.com')
    assert rule.applies('https://example.com')
    assert rule.applies('https://abc.example.com')

    rule = urlcanon.MatchRule(domain=b'example.com', exact=True)
    assert not rule.applies('https://twitter.com')
    assert rule.applies('https://example.com')
    assert not rule.applies('https://abc.example.com')


def test_url_matches_domain():
    assert urlcanon.url_matches_domain('http://1.2.3.4/', '1.2.3.4')
    assert urlcanon.url_matches_domain(b'scheme://1.2.3.4', '1.2.3.4')
    assert urlcanon.url_matches_domain('ftp://1.2.3.4/a/b/c/d', b'1.2.3.4')
    assert urlcanon.url_matches_domain(b'http://1.2.3.4', b'1.2.3.4')
    assert urlcanon.url_matches_domain(
            'http://foo.example.com', 'example.com')
    assert not urlcanon.url_matches_domain(
            'http://example.com', 'foo.example.com')
    assert not urlcanon.url_matches_domain(
            'http://foo.EXAMPLE.COM', 'example.com')
    assert urlcanon.url_matches_domain(
            urlcanon.whatwg('http://foo.EXAMPLE.COM'), 'example.com')
    assert not urlcanon.url_matches_domain('http://☃.net', 'xn--n3h.net')
    assert urlcanon.url_matches_domain('http://☃.net', '☃.net')
    assert urlcanon.url_matches_domain('http://😬.☃.net', '☃.net')
    assert not urlcanon.url_matches_domain(
            'http://😬.☃.net', urlcanon.normalize_host('☃.net'))
    assert urlcanon.url_matches_domain(
            urlcanon.whatwg('https://😬.☃.net'),
            urlcanon.normalize_host('☃.net'))


def test_url_matches_domain_exactly():
    assert urlcanon.url_matches_domain_exactly('http://1.2.3.4/', '1.2.3.4')
    assert urlcanon.url_matches_domain_exactly(b'scheme://1.2.3.4', '1.2.3.4')
    assert urlcanon.url_matches_domain_exactly('ftp://1.2.3.4/a/b/c/d', b'1.2.3.4')
    assert urlcanon.url_matches_domain_exactly(b'http://1.2.3.4', b'1.2.3.4')
    assert not urlcanon.url_matches_domain_exactly(
        'http://foo.example.com', 'example.com')
    assert not urlcanon.url_matches_domain_exactly(
        'http://example.com', 'foo.example.com')
    assert not urlcanon.url_matches_domain_exactly(
        'http://foo.EXAMPLE.COM', 'example.com')
    assert not urlcanon.url_matches_domain_exactly(
        urlcanon.whatwg('http://foo.EXAMPLE.COM'), 'example.com')
    assert not urlcanon.url_matches_domain_exactly('http://☃.net', 'xn--n3h.net')
    assert urlcanon.url_matches_domain_exactly('http://☃.net', '☃.net')
    assert not urlcanon.url_matches_domain_exactly('http://😬.☃.net', '☃.net')
    assert not urlcanon.url_matches_domain_exactly(
        'http://😬.☃.net', urlcanon.normalize_host('☃.net'))
    assert not urlcanon.url_matches_domain_exactly(
        urlcanon.whatwg('https://😬.☃.net'),
        urlcanon.normalize_host('☃.net'))


def test_host_matches_domain():
    assert urlcanon.host_matches_domain('1.2.3.4', '1.2.3.4')
    assert urlcanon.host_matches_domain(b'1.2.3.4', '1.2.3.4')
    assert urlcanon.host_matches_domain('1.2.3.4', b'1.2.3.4')
    assert urlcanon.host_matches_domain(b'1.2.3.4', b'1.2.3.4')
    assert urlcanon.host_matches_domain('foo.example.com', 'example.com')
    assert not urlcanon.host_matches_domain('example.com', 'foo.example.com')
    assert not urlcanon.host_matches_domain('foo.EXAMPLE.COM', 'example.com')
    assert urlcanon.host_matches_domain(
            urlcanon.normalize_host('foo.EXAMPLE.COM'), 'example.com')
    assert not urlcanon.host_matches_domain('☃.net', 'xn--n3h.net')
    assert urlcanon.host_matches_domain('☃.net', '☃.net')
    assert urlcanon.host_matches_domain('😬.☃.net', '☃.net')
    assert not urlcanon.host_matches_domain(
            '😬.☃.net', urlcanon.normalize_host('☃.net'))
    assert urlcanon.host_matches_domain(
            urlcanon.normalize_host('😬.☃.net'),
            urlcanon.normalize_host('☃.net'))


def test_host_matches_domain_exactly():
    assert urlcanon.host_matches_domain_exactly('1.2.3.4', '1.2.3.4')
    assert urlcanon.host_matches_domain_exactly(b'1.2.3.4', '1.2.3.4')
    assert urlcanon.host_matches_domain_exactly('1.2.3.4', b'1.2.3.4')
    assert urlcanon.host_matches_domain_exactly(b'1.2.3.4', b'1.2.3.4')
    assert not urlcanon.host_matches_domain_exactly('foo.example.com', 'example.com')
    assert not urlcanon.host_matches_domain_exactly('example.com', 'foo.example.com')
    assert not urlcanon.host_matches_domain_exactly('foo.EXAMPLE.COM', 'example.com')
    assert not urlcanon.host_matches_domain_exactly(
            urlcanon.normalize_host('foo.EXAMPLE.COM'), 'example.com')
    assert not urlcanon.host_matches_domain_exactly('☃.net', 'xn--n3h.net')
    assert urlcanon.host_matches_domain_exactly('☃.net', '☃.net')
    assert not urlcanon.host_matches_domain_exactly('😬.☃.net', '☃.net')
    assert not urlcanon.host_matches_domain_exactly(
            '😬.☃.net', urlcanon.normalize_host('☃.net'))
    assert not urlcanon.host_matches_domain_exactly(
            urlcanon.normalize_host('😬.☃.net'),
            urlcanon.normalize_host('☃.net'))
