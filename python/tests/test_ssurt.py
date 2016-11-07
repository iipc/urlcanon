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
import os
import json

def test_parser_idempotence():
    for s in [
            "https://user:pass@www.example.org:1443/path",
            "file:///usr/bin",
            "file:/usr/bin",
            "https://user@www.example.org:1443/path",
            "random!!garbage",
            "screenshot:http://user:pass@www.example.org:1443/path",
            "http:/日本.jp:80//.././[FÜNKY]",
            "https://[2001:db8::1:0:0:1]:8080/",
            "ssh://git@github.com/smola/galimatias.git",
            "dns:example.com",
            ":",
            "::",
            "x:[/]/foo",
            "//noscheme.tld/foo.html?query#frag",
            "http://www.archive.org/index.html#foo",
            "http://www.archive.org/",
            "http://www.archive.org",
            "http://www.archive.org?",
            "http://www.archive.org:8080/index.html?query#foo",
            "http://www.archive.org:8080/index.html?#foo",
            "http://www.archive.org:8080?#foo",
            u"http://bücher.ch:8080?#foo",
            u"dns:bücher.ch",
            u"http://bücher.ch:8080?#foo",
            u"dns:bücher.ch",
            "http:////////////////www.vikings.com",
            "http://https://order.1and1.com",
            # ends with ':' without a port number
            "http://mineral.galleries.com:/minerals/silicate/chabazit/chabazit.htm",
            "mailto:bot@archive.org",
            "file:///usr/bin",
            "file:/usr/bin",
            "file://usr/bin",
            " ",
            "\u0000 \u0000",
            " file://usr/bin   ",
            "\tx\t",
            "\nx\n",
            "\rx\nx\r",
            "\tx\t",
            "\tx\t",
            "\tx\t",
            "\tht\ttps://us\ter\t:\tpa\tss\t@w\tww.ex\tample.o\trg:\t1\t443\t/pa\tth?que\try#fra\tgment\t",
            "\nht\ntps://us\ner\n:\npa\nss\n@w\nww.ex\nample.o\nrg:\n1\n443\n/pa\nth?que\nry#fra\ngment\n",]:
        assert str(ssurt.parse_url(s)) == s

def test_resolve_path_dots():
    # tests generated from browser using this html/js
    #
    # <html>
    # <head>
    # <title>browser url canonicalization test</title>
    # </head>
    # <body>
    # <a id='url' href='http://example.com/'>i am your link</a>
    # <script>
    # var e = document.getElementById('url');
    #
    # var SEPARATORS = ['/'];  // , '\\']
    # var SEGMENTS = ['', '.', '..', 'foo'];
    #
    # function all_the_paths(len, path) {
    #     if (path.length >= len) {
    #         var p = path.join('')
    #         e.setAttribute('href', 'http://example.com' + p);
    #         // console.log(p + ' => ' + e.pathname);
    #         console.log("assert ssurt.Canonicalizer.resolve_path_dots(b'" + p + "') == b'" + e.pathname + "'");
    #         return
    #     }
    #     path.push('');
    #     if (path.length % 2 == 1) {
    #         for (var i = 0; i < SEPARATORS.length; i++) {
    #             path[path.length-1] = SEPARATORS[i]
    #             all_the_paths(len, path)
    #         }
    #     } else {
    #         for (var i = 0; i < SEGMENTS.length; i++) {
    #             path[path.length-1] = SEGMENTS[i]
    #             all_the_paths(len, path)
    #         }
    #     }
    #     path.pop()
    # }
    #
    # for (var i = 1; i < 9; i++) {
    #     all_the_paths(i, []);
    # }
    #
    # </script>
    # </body>
    # </html>
    #
    assert ssurt.Canonicalizer.resolve_path_dots(b'/') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///.') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///foo') == b'///foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/.') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/foo') == b'//foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//.') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//foo') == b'/foo//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/.') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/foo') == b'/foo/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'////') == b'////'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///./') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///../') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///foo/') == b'///foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.//') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//././') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./foo/') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo//') == b'//foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/./') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/../') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/foo/') == b'//foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.///') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//./') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//foo/') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././/') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo//') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/./') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/foo/') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..///') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//./') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//foo/') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././/') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo//') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/./') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/foo/') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo///') == b'/foo///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//./') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//../') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//foo/') == b'/foo//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.//') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/././') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./foo/') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo//') == b'/foo/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/./') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/../') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/foo/') == b'/foo/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'////') == b'////'
    assert ssurt.Canonicalizer.resolve_path_dots(b'////.') == b'////'
    assert ssurt.Canonicalizer.resolve_path_dots(b'////..') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'////foo') == b'////foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///./') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///./.') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///./..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///./foo') == b'///foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///../') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///../.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///../foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///foo/') == b'///foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///foo/.') == b'///foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///foo/..') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'///foo/foo') == b'///foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.//') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.//.') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.//..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.//foo') == b'///foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//././') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//././.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//././foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./foo/') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./foo/.') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./foo/..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//./foo/foo') == b'//foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//..//.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//..//..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//..//foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.././.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.././foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../foo/.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../foo/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//../foo/foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo//') == b'//foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo//.') == b'//foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo//..') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo//foo') == b'//foo//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/./') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/./.') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/./..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/./foo') == b'//foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/../') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/../.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/../foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/foo/') == b'//foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/foo/.') == b'//foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/foo/..') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//foo/foo/foo') == b'//foo/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.///') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.///.') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.///..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.///foo') == b'///foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//./') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//./.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//./..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//./foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//foo/') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//foo/.') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//foo/..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.//foo/foo') == b'//foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././/') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././/.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././/foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./././.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./././foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././foo/.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././foo/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/././foo/foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./..//.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./..//..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./..//foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./.././.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./.././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./.././foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../foo/.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../foo/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./../foo/foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo//') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo//.') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo//..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo//foo') == b'/foo//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/./') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/./.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/./..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/./foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/foo/') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/foo/.') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/foo/..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/./foo/foo/foo') == b'/foo/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..///') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..///.') == b'///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..///..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..///foo') == b'///foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//./') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//./.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//./..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//./foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//foo/') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//foo/.') == b'//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//foo/..') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..//foo/foo') == b'//foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././/') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././/.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././/foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../././.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../././foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././foo/.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././foo/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.././foo/foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../..//.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../..//..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../..//foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../.././.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../.././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../.././foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../foo/.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../foo/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../../foo/foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo//') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo//.') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo//..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo//foo') == b'/foo//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/./') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/./.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/./..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/./foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/foo/') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/foo/.') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/foo/..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/../foo/foo/foo') == b'/foo/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo///') == b'/foo///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo///.') == b'/foo///'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo///..') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo///foo') == b'/foo///foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//./') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//./.') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//./..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//./foo') == b'/foo//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//../') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//../.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//../foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//foo/') == b'/foo//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//foo/.') == b'/foo//foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//foo/..') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo//foo/foo') == b'/foo//foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.//') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.//.') == b'/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.//..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.//foo') == b'/foo//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/././') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/././.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/././foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./foo/') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./foo/.') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./foo/..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/./foo/foo') == b'/foo/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/..//') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/..//.') == b'//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/..//..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/..//foo') == b'//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.././') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.././.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.././..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/.././foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../../') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../../.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../../foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../foo/') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../foo/.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../foo/..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/../foo/foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo//') == b'/foo/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo//.') == b'/foo/foo//'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo//..') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo//foo') == b'/foo/foo//foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/./') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/./.') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/./..') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/./foo') == b'/foo/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/../') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/../.') == b'/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/../..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/../foo') == b'/foo/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/foo/') == b'/foo/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/foo/.') == b'/foo/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/foo/..') == b'/foo/foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo/foo/foo/foo') == b'/foo/foo/foo/foo'

    # some backslash stuff
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\') == b'\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\') == b'\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\.') == b'\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\..') == b'\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\foo') == b'\\foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/\\') == b'/\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.\\') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..\\') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo\\') == b'/foo\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\/') == b'\\/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\\\') == b'\\\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\./') == b'\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\.\\') == b'\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\../') == b'\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\..\\') == b'\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\foo/') == b'\\foo/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\foo\\') == b'\\foo\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/\\') == b'/\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/\\.') == b'/\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/\\..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/\\foo') == b'/\\foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.\\') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.\\.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.\\..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.\\foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..\\') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..\\.') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..\\..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/..\\foo') == b'/foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo\\') == b'/foo\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo\\.') == b'/foo\\'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo\\..') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/foo\\foo') == b'/foo\\foo'
    assert ssurt.Canonicalizer.resolve_path_dots(b'\\/') == b'\\/'

    assert ssurt.Canonicalizer.resolve_path_dots(b'/.../') == b'/.../'
    assert ssurt.Canonicalizer.resolve_path_dots(b'//.../') == b'//.../'

    assert ssurt.Canonicalizer.resolve_path_dots(b'/%2e/') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/%2e./') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.%2e/') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/%2E/') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/%2E./') == b'/'
    assert ssurt.Canonicalizer.resolve_path_dots(b'/.%2E/') == b'/'

def test_w3c_test_data():
    tests = []
    path = os.path.join(os.path.dirname(__file__), 'urltestdata.json')
    canon = ssurt.Canonicalizer.WHATWG
    with open(path, 'rb') as f:
        tests = json.loads(f.read().decode('utf-8'))
    for test in tests:
        if (isinstance(test, dict) and test.get('base') == 'about:blank'
                and 'href' in test):
            url = ssurt.parse_url(test['input'])
            canon(url)
            try:
                assert test['protocol'].encode('utf-8') == (
                        url.scheme + url.colon_after_scheme)
                assert test['username'].encode('utf-8') == url.username
                assert test['password'].encode('utf-8') == url.password
                assert test['host'].encode('utf-8') == url.host_port
                assert test['hostname'].encode('utf-8') == url.host
                assert test['pathname'].encode('utf-8') == url.path
                assert test['search'].encode('utf-8') == (
                        url.question_mark + url.query)
                assert test['hash'].encode('utf-8') == (
                        url.fragment and (url.hash_sign + url.fragment) or b'')
                assert test['href'] == str(url)
            except:
                print('failed\n   input=%s\n   url=%s\n' % (test, vars(url)))
                raise

