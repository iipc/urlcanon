'''
urlcanon/__init__.py - URL canonicalization library, python version

Copyright (C) 2016 National Library of Australia
Copyright (C) 2016-2018 Internet Archive

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
from .parse import parse_url, ParsedUrl, parse_ipv4, parse_ipv4or6
from .canon import (
        Canonicalizer, whatwg, google, semantic_precise, semantic, aggressive,
        normalize_host)
from .rules import MatchRule, url_matches_domain, host_matches_domain

__all__ = ['parse_url', 'ParsedUrl', 'parse_ipv4', 'parse_ipv4or6',
           'Canonicalizer', 'whatwg', 'google', 'semantic_precise', 'semantic',
           'MatchRule', 'SPECIAL_SCHEMES', 'reverse_host', 'ssurt_host',
           'host_matches_domain', 'url_matches_domain', 'normalize_host',
           'aggressive']

SPECIAL_SCHEMES = {
    b'ftp': b'21',
    b'gopher': b'70',
    b'http': b'80',
    b'https': b'443',
    b'ws': b'80',
    b'wss': b'443',
    b'file': None,
}

def reverse_host(host, trailing_comma=True):
    '''
    Reverse dotted segments. Swap commas and dots. Add a trailing comma.
    b"x,y.b.c" => b"c,b,x.y,"
    '''
    parts_reversed = []
    for part in reversed(host.split(b'.')):
        parts_reversed.append(part.replace(b',', b'.'))
    if trailing_comma:
        parts_reversed.append(b'')
    return b','.join(parts_reversed)

def ssurt_host(host, trailing_comma=True):
    '''Reverse host unless it's an IPv4 or IPv6 address.'''
    if not host or host[:1] == b'[' or parse_ipv4(host):
        return host
    else:
        return reverse_host(host, trailing_comma)
