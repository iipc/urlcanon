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
import pytest

def load_json_bytes(json_bytes):
    '''
    The python json parser only operates on strings, not bytes. :( This
    hacky workaround is based on the observation that every possible byte
    sequence can be represented as a str by "decoding" it as ISO-8859-1. It's
    not very efficient, but oh well.
    '''
    def rebytify_data_structure(obj):
        if isinstance(obj, dict):
            bd = {}
            for orig_key in obj:
                new_key = rebytify_data_structure(orig_key)
                new_value = rebytify_data_structure(obj[orig_key])
                bd[new_key] = new_value
            return bd
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = rebytify_data_structure(obj[i])
            return obj
        elif isinstance(obj, str):
            return obj.encode('latin1')
        else: # a number or None
            return obj
    obj = json.loads(json_bytes.decode('latin1'))
    return rebytify_data_structure(obj)

def test_parser_idempotence():
    path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'testdata',
            'idempotence.json')
    with open(path, 'rb') as f:
        inputs = load_json_bytes(f.read())
    for s in inputs:
        assert ssurt.parse_url(s).__bytes__() == s

def load_funky_ipv4_data():
    path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'testdata',
        'funky_ipv4.json')
    with open(path, 'rb') as f:
        inputs = load_json_bytes(f.read())
        return [(unresolved, inputs[unresolved]) for unresolved in inputs]

@pytest.mark.parametrize('unresolved,expected', load_funky_ipv4_data())
def test_funky_ipv4(unresolved, expected):
    ip4 = ssurt.parse._attempt_ipv4or6(unresolved)[0]
    assert ssurt.Canonicalizer.dotted_decimal(ip4) == expected


def load_path_dots_data():
    # Most of path_dots.json was generated in the browser using this html/js.
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
    path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'testdata',
            'path_dots.json')
    with open(path, 'rb') as f:
        inputs = load_json_bytes(f.read())
    testdata = []
    for (unresolved, expected) in inputs[b'special'].items():
        testdata.append((unresolved, True, expected))
    for (unresolved, expected) in inputs[b'nonspecial'].items():
        testdata.append((unresolved, False, expected))
    return testdata

@pytest.mark.parametrize(
        'unresolved,is_special,expected', load_path_dots_data())
def test_resolve_path_dots(unresolved, is_special, expected):
    assert ssurt.Canonicalizer.resolve_path_dots(
            unresolved, special=is_special) == expected

def load_w3c_test_data():
    path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'testdata',
        'urltestdata.json')
    with open(path, 'rb') as f:
        # load_json_bytes doesn't work for urltestdata.json because it contains
        # unicode character escapes beyond \u00ff such as \u0300
        tests = json.loads(f.read().decode('utf-8'))
        return [test for test in tests if is_absolute_url_test(test)]

def is_absolute_url_test(test):
    return (isinstance(test, dict) and test.get('base') == 'about:blank'
            and 'href' in test and test['input'][0] != '#')

@pytest.mark.parametrize("test", load_w3c_test_data())
def test_w3c_test_data(test):
    canon = ssurt.Canonicalizer.WHATWG
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

def load_parsing():
    path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'testdata',
            'parsing.json')
    with open(path, 'rb') as f:
        inputs = load_json_bytes(f.read())
        return inputs.items()

@pytest.mark.parametrize("input,parsed_fields", load_parsing())
def test_parsing(input, parsed_fields):
    parsed_url = ssurt.parse_url(input)
    assert parsed_url.leading_junk == parsed_fields[b'leading_junk']
    assert parsed_url.scheme == parsed_fields[b'scheme']
    assert parsed_url.colon_after_scheme == parsed_fields[b'colon_after_scheme']
    assert parsed_url.slashes == parsed_fields[b'slashes']
    assert parsed_url.username == parsed_fields[b'username']
    assert parsed_url.colon_before_password == parsed_fields[b'colon_before_password']
    assert parsed_url.password == parsed_fields[b'password']
    assert parsed_url.at_sign == parsed_fields[b'at_sign']
    assert parsed_url.ip6 == parsed_fields[b'ip6']
    assert parsed_url.ip4 == parsed_fields[b'ip4']
    assert parsed_url.host == parsed_fields[b'host']
    assert parsed_url.colon_before_port == parsed_fields[b'colon_before_port']
    assert parsed_url.port == parsed_fields[b'port']
    assert parsed_url.path == parsed_fields[b'path']
    assert parsed_url.question_mark == parsed_fields[b'question_mark']
    assert parsed_url.query == parsed_fields[b'query']
    assert parsed_url.hash_sign == parsed_fields[b'hash_sign']
    assert parsed_url.fragment == parsed_fields[b'fragment']
    assert parsed_url.trailing_junk == parsed_fields[b'trailing_junk']

def load_our_whatwg_test_data():
    path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'testdata',
        'supplemental_whatwg.json')
    with open(path, 'rb') as f:
        jb = load_json_bytes(f.read())
    return jb.items()

@pytest.mark.parametrize(
        'uncanonicalized,canonicalized', load_our_whatwg_test_data())
def test_supplemental_whatwg(uncanonicalized, canonicalized):
    url = ssurt.parse_url(uncanonicalized)
    ssurt.Canonicalizer.WHATWG(url)
    assert url.__bytes__() == canonicalized
