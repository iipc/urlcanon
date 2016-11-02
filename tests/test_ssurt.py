# -*- coding: utf-8 -*-
'''
test_ssurt.py - unit tests for the ssurt package

Copyright (C) 2016 Internet Archive

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

import ssurt

def test_parse_url():
    assert str(ssurt.parse_url("https://user:pass@www.example.org:1443/path")) == "https://user:pass@www.example.org:1443/path"
    assert str(ssurt.parse_url("random!!garbage")) == "random!!garbage"
    assert str(ssurt.parse_url("screenshot+http://user:pass@www.example.org:1443/path")) == "screenshot+http://user:pass@www.example.org:1443/path"
    assert str(ssurt.parse_url("http:/日本.jp:80//.././[FÜNKY]")) == "http://日本.jp:80//.././[FÜNKY]"
    assert str(ssurt.parse_url("https://[2001:db8::1:0:0:1]:8080/")) == "https://[2001:db8::1:0:0:1]:8080/"
    assert str(ssurt.parse_url("ssh://git@github.com/smola/galimatias.git")) == "ssh://git@github.com/smola/galimatias.git"
    assert str(ssurt.parse_url("dns:example.com")) == "dns:example.com"
    assert str(ssurt.parse_url(":")) == ":"
    assert str(ssurt.parse_url("::")) == "::"
    assert str(ssurt.parse_url("x:[/]/foo")) == "x:[/]/foo"
    assert str(ssurt.parse_url("//noscheme.tld/foo.html?query#frag")) == "//noscheme.tld/foo.html?query#frag"

    # These tests come from URLParserTest.java
    assert str(ssurt.parse_url("http://www.archive.org/index.html#foo")) == 'http://www.archive.org/index.html#foo'
    assert str(ssurt.parse_url("http://www.archive.org/")) == 'http://www.archive.org/'
    assert str(ssurt.parse_url("http://www.archive.org")) == 'http://www.archive.org'
    assert str(ssurt.parse_url("http://www.archive.org?")) == 'http://www.archive.org?'
    assert str(ssurt.parse_url("http://www.archive.org:8080/index.html?query#foo")) == 'http://www.archive.org:8080/index.html?query#foo'
    assert str(ssurt.parse_url("http://www.archive.org:8080/index.html?#foo")) == 'http://www.archive.org:8080/index.html?#foo'
    assert str(ssurt.parse_url("http://www.archive.org:8080?#foo")) == 'http://www.archive.org:8080?#foo'
    assert str(ssurt.parse_url(u"http://bücher.ch:8080?#foo")) == u'http://bücher.ch:8080?#foo'
    assert str(ssurt.parse_url(u"dns:bücher.ch")) == u'dns:bücher.ch'
    assert str(ssurt.parse_url(u"http://bücher.ch:8080?#foo")) == u"http://bücher.ch:8080?#foo"
    assert str(ssurt.parse_url(u"dns:bücher.ch")) == u"dns:bücher.ch"

    ###From Tymm:
    assert str(ssurt.parse_url("http:////////////////www.vikings.com")) == 'http://www.vikings.com'
    # assert str(ssurt.parse_url("http://https://order.1and1.com")) == 'https://order.1and1.com'

    ###From Common Crawl, host ends with ':' without a port number
    # assert str(ssurt.parse_url("http://mineral.galleries.com:/minerals/silicate/chabazit/chabazit.htm")) == 'http://mineral.galleries.com/minerals/silicate/chabazit/chabazit.htm'

    assert ssurt.parse_url("mailto:bot@archive.org").scheme == b'mailto'
    assert str(ssurt.parse_url("mailto:bot@archive.org")) == 'mailto:bot@archive.org'


