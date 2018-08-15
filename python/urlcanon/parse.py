'''
urlcanon/parse.py - url parser

based on https://gist.github.com/ato/b9875c45171d082ca6c6738640347ecb and
https://github.com/iipc/webarchive-commons/blob/master/src/main/java/org/archive/url/URLParser.java

Copyright (C) 2016 National Library of Australia
Copyright (C) 2016-2017 Internet Archive

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
import re
from . import canon
import ipaddress
import urlcanon

# "leading and trailing C0 controls and space"
LEADING_JUNK_REGEX = re.compile(br'\A([\x00-\x20]*)(.*)\Z', re.DOTALL)
TRAILING_JUNK_REGEX = re.compile(br'\A(.*?)([\x00-\x20]*)\Z', re.DOTALL)

URL_REGEX = re.compile(br'''
\A
(?:
   (?P<scheme> [a-zA-Z] [^:]* )
   (?P<colon_after_scheme> : )
)?
(?P<pathish> [^?#]* )
(?:
  (?P<question_mark> [?] )
  (?P<query> [^#]* )
)?
(?:
  (?P<hash_sign> [#] )
  (?P<fragment> .* )
)?
\Z
''', re.VERBOSE | re.DOTALL)

SPECIAL_PATHISH_REGEX = re.compile(br'''
\A
(?P<slashes> [/\\\r\n\t]* )
(?P<authority> [^/\\]* )
(?P<path> [/\\] .* )?
\Z
''', re.VERBOSE | re.DOTALL)

NONSPECIAL_PATHISH_REGEX = re.compile(br'''
\A
(?P<slashes> [\r\n\t]* (?:/[\r\n\t]*){2} )
(?P<authority> [^/]* )
(?P<path> / .* )?
\Z
''', re.VERBOSE | re.DOTALL)

FILE_PATHISH_REGEX = re.compile(br'''
\A
(?P<slashes> [\r\n\t]* (?:[/\\][\r\n\t]*){2} )
(?P<host> [^/\\]* )
(?P<path> [/\\] .* )?
\Z
''', re.VERBOSE | re.DOTALL)

AUTHORITY_REGEX = re.compile(br'''
\A
(?:
   (?P<username> [^:]* )
   (
     (?P<colon_before_password> : )
     (?P<password> .* )
   )?
   (?P<at_sign> @ )
)?
(?P<host> \[[^]]*\] | [^:]* )
(?:
  (?P<colon_before_port> : )
  (?P<port> .* )
)?
\Z
''', re.VERBOSE | re.DOTALL)

class ParsedUrl:
    def __init__(self):
        self.leading_junk = b''
        self.scheme = b''
        self.colon_after_scheme = b''
        self.slashes = b''
        self.username = b''
        self.colon_before_password = b''
        self.password = b''
        self.at_sign = b''
        self.ip6 = None  # numeric value
        self.ip4 = None  # numeric value
        self.host = b''
        self.colon_before_port = b''
        self.port = b''
        self.path = b''
        self.question_mark = b''
        self.query = b''
        self.hash_sign = b''
        self.fragment = b''
        self.trailing_junk = b''

    @property
    def host_port(self):
        return self.host + self.colon_before_port + self.port

    @property
    def userinfo(self):
        return self.username + self.colon_before_password + self.password

    @property
    def authority(self):
        return self.userinfo + self.at_sign + self.host_port

    def __bytes__(self):
        return (self.leading_junk + self.scheme + self.colon_after_scheme
                + self.slashes + self.authority + self.path
                + self.question_mark + self.query + self.hash_sign
                + self.fragment + self.trailing_junk)

    def __str__(self):
        return self.__bytes__().decode('utf-8')

    def ssurt(self):
        '''
        Format this URL with a field order suitable for sorting.
        '''
        ssurt_host = urlcanon.ssurt_host(self.host)
        return (self.leading_junk + ssurt_host + self.slashes +
                self.port + self.colon_before_port  +
                self.scheme + self.at_sign + self.username +
                self.colon_before_password + self.password +
                self.colon_after_scheme + self.path +
                self.question_mark + self.query + self.hash_sign +
                self.fragment + self.trailing_junk)

    def surt(self, trailing_comma=True, with_scheme=True):
        result = self.leading_junk
        if with_scheme:
            result += self.scheme + self.colon_after_scheme + self.slashes
        if self.host:
            surt_host = b''
            if with_scheme:
                surt_host += b'('
            surt_host += urlcanon.ssurt_host(self.host, trailing_comma=False)
            surt_host += self.colon_before_port + self.port
            if trailing_comma:
                surt_host += b','
            result += surt_host + b')'
        result += (self.path + self.question_mark + self.query
                + self.hash_sign + self.fragment + self.trailing_junk)
        return result

    def surt_ancestry(self):
        # For now, we only support SURT parts for certain cases.
        if self.scheme not in urlcanon.SPECIAL_SCHEMES.keys():
            return []

        result = []
        parts = []

        # Build a list of all of the parts of the SURT.
        parts.append(
            self.scheme + self.colon_after_scheme + self.slashes)
        if self.host:
            parts.append(parts.pop() + b'(')
            for part in urlcanon.ssurt_host(
                    self.host, trailing_comma=False).split(b','):
                parts.append(part + b',')
            # Closing paren is its own part to allow for incomplete and
            # incomplete hosts
            # (e.g: http://(com,examle) and http://(com,example )
            if self.port:
                parts.append(self.colon_before_port + self.port + b')')
            else:
                parts.append(b')')
        # Remove initial b'' which appears due to leading slash on the path.
        path_parts = self.path.split(b'/')
        if path_parts[0] == b'':
            path_parts.remove(b'')
        for part in path_parts:
            parts.append(b'/' + part)
        if self.query:
            parts.append(self.question_mark + self.query)
        if self.fragment:
            parts.append(self.hash_sign + self.fragment)
        if self.trailing_junk:
            parts.append(self.trailing_junk)

        # Build a list of SURT fragments.
        while parts != []:
            result.append(b''.join(parts))
            parts.pop()

        return result


def parse_ipv4(host):
    def _parse_num(s):
        if len(s) >= 2 and s[:2] in (b'0x', b'0X', '0x', '0X'):
            if len(s) >= 3:
                return int(s[2:], base=16)
            else:
                return 0
        elif len(s) >= 2 and s[:1] in (b'0', '0'):
            return int(s[1:], base=8)
        elif len(s) == 0:
            return 0
        else:
            return int(s)

    try:
        parts = host.split(b'.')
        if parts[-1] == b"":
            parts.pop()
        if len(parts) == 1:
            ip4 = _parse_num(parts[0])
        elif len(parts) == 2:
            part1 = _parse_num(parts[1])
            if part1 >= 2**24:
                raise Exception(
                        '%s not a valid ipv4 address: last part must be less '
                        'than 2**24' % repr(host))
            ip4 = _parse_num(parts[0]) * 2**24 + _parse_num(parts[1])
        elif len(parts) == 3:
            part1 = _parse_num(parts[1])
            if part1 >= 2**8:
                raise Exception(
                        '%s not a valid ipv4 address: middle part must be '
                        'less than 256' % repr(host))
            part2 = _parse_num(parts[2])
            if part2 >= 2**16:
                raise Exception(
                        '%s not a valid ipv4 address: last part must be less '
                        'than 2**16' % repr(host))
            ip4 = (_parse_num(parts[0]) * 2**24
                     + part1 * 2**16 + _parse_num(parts[2]))
        elif len(parts) == 4:
            part1 = _parse_num(parts[1])
            part2 = _parse_num(parts[2])
            part3 = _parse_num(parts[3])
            if part1 >= 2**8 or part2 >= 2**8 or part3 >= 2**8:
                raise Exception(
                        '%s not a valid ipv4 address: all parts must be less '
                        'than 256' % repr(host))
            ip4 = (_parse_num(parts[0]) * 2**24
                     + part1 * 2**16 + part2 * 2**8 + part3)
        else: # len(parts) > 4
            return None
        if ip4 >= 2**32:
            raise Exception(
                    '%s not a valid ipv4 address: value must be less than '
                    '2**32' % repr(host))
        return ip4
    except:
        return None

def parse_ipv4or6(host):
    '''
    Returns tuple (ip4, ip6). Values are integers or None. Both values will be
    None if host does not parse as an ip address, otherwise exactly one of the
    two will have a value. Follows WHATWG rules rules for parsing, which are
    intended to match browser behavior.
    '''
    if host and host[:1] == b'[' and host[-1:] == b']':
        try:
            ip6 = ipaddress.IPv6Address(host.decode('utf-8')[1:-1])
            return None, int(ip6)
        except:
            return None, None
    else:
        return parse_ipv4(host), None

def parse_pathish(url, pathish):
    '''
    Parses "pathish", which is the section of the url after the scheme,
    including the authority, if any, and populates fields of "url".
    '''
    clean_scheme = canon.TAB_AND_NEWLINE_REGEX.sub(b'', url.scheme).lower()
    if clean_scheme == b'file':
        m = FILE_PATHISH_REGEX.match(pathish)
        if m:  # file://host/path...
            url.slashes = m.group('slashes') or b''
            url.host = m.group('host') or b''
            url.path = m.group('path') or b''
        else:
            url.path = pathish
    else:
        if clean_scheme in urlcanon.SPECIAL_SCHEMES:
            m = SPECIAL_PATHISH_REGEX.match(pathish)
        else:
            m = NONSPECIAL_PATHISH_REGEX.match(pathish)

        if m:
            url.slashes = m.group('slashes') or b''
            url.path = m.group('path') or b''
            authority = m.group('authority')
            m = AUTHORITY_REGEX.match(authority)
            url.username = m.group('username') or b''
            url.colon_before_password = m.group('colon_before_password') or b''
            url.password = m.group('password') or b''
            url.at_sign = m.group('at_sign') or b''
            url.host = m.group('host') or b''
            url.ip4, url.ip6 = parse_ipv4or6(url.host)
            url.colon_before_port = m.group('colon_before_port') or b''
            url.port = m.group('port') or b''
        else: # no authority
            url.path = pathish

    return url

def parse_url(u):
    if not isinstance(u, bytes):
        parse_me = u.encode('utf-8')
    else:
        parse_me = u

    url = ParsedUrl()

    # "leading and trailing C0 controls and space"
    m = LEADING_JUNK_REGEX.match(parse_me)
    url.leading_junk = m.group(1)
    parse_me = m.group(2)
    m = TRAILING_JUNK_REGEX.match(parse_me)
    parse_me = m.group(1)
    url.trailing_junk = m.group(2)

    # parse url
    m = URL_REGEX.match(parse_me)
    url.scheme = m.group('scheme') or b''
    url.colon_after_scheme = m.group('colon_after_scheme') or b''
    url.question_mark = m.group('question_mark') or b''
    url.query = m.group('query') or b''
    url.hash_sign = m.group('hash_sign') or b''
    url.fragment = m.group('fragment') or b''

    if m.group('pathish'):
        parse_pathish(url, m.group('pathish'))

    return url
