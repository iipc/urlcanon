'''
ssurt/parse.py - url parser

based on https://gist.github.com/ato/b9875c45171d082ca6c6738640347ecb and
https://github.com/iipc/webarchive-commons/blob/master/src/main/java/org/archive/url/URLParser.java

Copyright (C) 2016 Alex Osborne
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

class ParsedUrl:
    def __init__(self,
            scheme=None, userinfo=None, host=None, port=None, path=b'',
            query=None, fragment=None):
        self.scheme = scheme
        self.userinfo = userinfo
        self.host = host
        self.port = port
        self.path = path
        self.query = query
        self.fragment = fragment

    def __str__(self):
        components = [
            self.scheme or b'',
            b':' if self.scheme is not None else b'',
            b'//' if self.host is not None else b'',
            self.userinfo or b'',
            b'@' if self.userinfo is not None else b'',
            self.host or b'',
            b':' if self.port is not None else b'',
            self.port if self.port else b'',
            self.path,
            b'?' if self.query is not None else b'',
            self.query or b'',
            b'#' if self.fragment is not None else b'',
            self.fragment or b''
        ]
        return b''.join(components).decode('utf-8')

URL_REGEX = re.compile(rb'''
\A
(?:
   (?P<scheme> [a-zA-Z] [a-zA-Z0-9+.-]* )
: )?
(?P<authority>
  (?P<slashes> /+ )
  (?:
     (?P<userinfo> [^/?#\[\]@]* )
     @
  )?
  (?P<host>
      (?P<ip6> \[ [^\]]* \] )
    | (?P<ip4> [0-9]+ \. [0-9]+ \. [0-9]+ \. [0-9]+ )
    | (?P<domain> [^:/?#\[\]@]+ )
  )
  (?: :
    (?P<port> [0-9]+ )
  )?
)?
(?P<path> [^?#]* )
(?:
  [?]
  (?P<query> [^?#]* )
)?
(?:
  [#]
  (?P<fragment> .* )
)?
\Z
''', re.VERBOSE | re.DOTALL)
# ([^?#]*)(\\?([^#]*))?)?(#(.*))?

def parse_url(u):
    if not isinstance(u, bytes):
        x = u.encode('utf-8')
    else:
        x = u
    m = URL_REGEX.match(x)
    return ParsedUrl(
            scheme=m.group('scheme'), userinfo=m.group('userinfo'),
            host=m.group('host'), port=m.group('port'), path=m.group('path'),
            query=m.group('query'), fragment=m.group('fragment'))
