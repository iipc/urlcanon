'''
ssurt/parse.py - url parser

based on https://gist.github.com/ato/b9875c45171d082ca6c6738640347ecb and
https://github.com/iipc/webarchive-commons/blob/master/src/main/java/org/archive/url/URLParser.java

Copyright (C) 2016 National Library of Australia
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
import re
from . import canon

# "leading and trailing C0 controls and space"
LEADING_JUNK_REGEX = re.compile(rb'\A([\x00-\x20]*)(.*)\Z', re.DOTALL)
TRAILING_JUNK_REGEX = re.compile(rb'\A(.*?)([\x00-\x20]*)\Z', re.DOTALL)

URL_REGEX = re.compile(rb'''
\A
(?:
   (?P<scheme> [a-zA-Z] [^:]* )
   (?P<colon_after_scheme> : )
)?
(?P<pathish>
  ( [/\\]* [^/\\?#]* )*
)
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

PATHISH_SEGMENT_REGEX = re.compile(rb'''
(?P<slashes> [/\\]* )
(?P<segment> [^/\\]* )
''', re.VERBOSE | re.DOTALL)

AUTHORITY_REGEX = re.compile(rb'''
\A
(?:
   (?P<username> [^:@]* )
   (
     (?P<colon_before_password> : )
     (?P<password> [^@]* )
   )?
   (?P<at_sign> @ )
)?
(?P<host>
    (?P<ip6> \[ [^\]]* \] )
  | (?P<ip4> [0-9]+ \. [0-9]+ \. [0-9]+ \. [0-9]+ )
  | (?P<domain> [^:]* )
)
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
        self.ip6 = b''
        self.ip4 = b''
        self.domain = b''
        self.colon_before_port = b''
        self.port = b''
        self.path = b''
        self.question_mark = b''
        self.query = b''
        self.hash_sign = b''
        self.fragment = b''
        self.trailing_junk = b''

    @property
    def host(self):
        return self.ip6 or self.ip4 or self.domain

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

    # we parse the authority + path into "pathish" initially so that we can
    # correctly handle file: urls
    if m.group('pathish') and m.group('pathish')[0] in b'/\\':
        pathsegpairs = (n.groups() for n in PATHISH_SEGMENT_REGEX.finditer(
                            m.group('pathish')))
        # flatten the list
        pathish_components = [
                slashes_or_segment for pathsegpair in pathsegpairs
                for slashes_or_segment in pathsegpair]
        if canon.Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.scheme).lower() == b'file' and len(
                        pathish_components[0]) >= 3:
            # file: url
            url.slashes = pathish_components[0][:2]
            authority = b''
            url.path = b''.join(
                    [pathish_components[0][2:]] + pathish_components[1:])
        else:
            url.slashes = pathish_components[0]
            authority = pathish_components[1]
            url.path = b''.join(pathish_components[2:])

        # parse the authority
        m = AUTHORITY_REGEX.match(authority)
        url.username = m.group('username') or b''
        url.colon_before_password = m.group('colon_before_password') or b''
        url.password = m.group('password') or b''
        url.at_sign = m.group('at_sign') or b''
        url.ip6 = m.group('ip6') or b''
        url.ip4 = m.group('ip4') or b''
        url.domain = m.group('domain') or b''
        url.colon_before_port = m.group('colon_before_port') or b''
        url.port = m.group('port') or b''
    else:
        # pathish doesn't start with / so it's an opaque thing
        url.path = m.group('pathish')

    return url

