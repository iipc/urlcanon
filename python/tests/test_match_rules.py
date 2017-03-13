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
            ssurt=urlcanon.semantic(b'http://example.com/foo/bar').ssurt())
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

