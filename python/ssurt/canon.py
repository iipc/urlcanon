'''
ssurt/canon.py - url canonicalization

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
import ipaddress
import ssurt

class Canonicalizer:
    def __init__(self, steps):
        self.steps = steps

    def __call__(self, url):
        for step in self.steps:
            step(url)
        return url

    def remove_leading_trailing_junk(url):
        url.leading_junk = b''
        url.trailing_junk = b''

    TAB_AND_NEWLINE_REGEX = re.compile(rb'[\x09\x0a\x0d]')
    def remove_tabs_and_newlines(url):
        url.leading_junk = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.leading_junk)
        url.scheme = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(b'', url.scheme)
        url.colon_after_scheme = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.colon_after_scheme)
        url.slashes = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(b'', url.slashes)
        url.username = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.username)
        url.colon_before_password = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.colon_before_password)
        url.password = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.password)
        url.at_sign = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(b'', url.at_sign)
        url.host = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(b'', url.host)
        url.colon_before_port = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.colon_before_port)
        url.port = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(b'', url.port)
        url.path = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(b'', url.path)
        url.question_mark = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.question_mark)
        url.query = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(b'', url.query)
        url.hash_sign = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.hash_sign)
        url.fragment = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.fragment)
        url.trailing_junk = Canonicalizer.TAB_AND_NEWLINE_REGEX.sub(
                b'', url.trailing_junk)

    def lowercase_scheme(url):
        url.scheme = url.scheme.lower()

    def fix_backslashes(url):
        url.slashes = b'/' * len(url.slashes)
        if url.path and url.path[0] in b'/\\':
            url.path = url.path.replace(b'\\', b'/')

    SPECIAL_PATH_SEPARATORS_REGEX = re.compile(rb'[^/\\]')
    SPECIAL_PATH_SEGMENTS_REGEX = re.compile(rb'[/\\]')
    NONSPECIAL_PATH_SEPARATORS_REGEX = re.compile(rb'[^/]')
    NONSPECIAL_PATH_SEGMENTS_REGEX = re.compile(rb'/')
    PATH_DOTS_REGEX = re.compile(rb'\A([.]|%2e)([.]|%2e)?\Z', re.IGNORECASE)
    def resolve_path_dots(path):
        '''
        /./ => /
        /. => /
        /.. => /
        /../ => /
        /..// => //
        //..// => //
        /foo/./ => /foo/
        /foo/. => /foo/
        /foo/ => /foo/
        /foo/.. => /
        /.../ => /.../
        //.../ => //.../
        /././ => /
        /././. => /
        /.././../. => /
        '''
        if path and path[0] in b'/\\':
            separators_bytes = Canonicalizer.PATH_SEPARATORS_REGEX.sub(b'', path)
            separators = [separators_bytes[i:i+1]
                         for i in range(len(separators_bytes))]
            segments = Canonicalizer.PATH_SEGMENTS_REGEX.split(path)[1:]
            old_path = [None] * (len(separators) + len(segments))
            old_path[::2] = separators
            old_path[1::2] = segments

            new_path = []
            i = 0
            while i < len(old_path):
                m = Canonicalizer.PATH_DOTS_REGEX.match(old_path[i])
                if m:
                    if m.group(2): # ..
                        if len(new_path) > 1:
                            new_path.pop() # pop preceding /
                        if len(new_path) > 1:
                            new_path.pop() # pop preceding path segment
                    i += 1 # skip following /
                else:
                    new_path.append(old_path[i])
                i += 1
            return b''.join(new_path)
        else:
            return path

    def normalize_path_dots(url):
        url.path = Canonicalizer.resolve_path_dots(url.path)

    PCT2E_REGEX = re.compile(rb'%2e', re.IGNORECASE)
    def decode_path_2e(url):
        url.path = Canonicalizer.PCT2E_REGEX.sub(b'.', url.path)

    # > The simple encode set are C0 controls and all code points greater than
    # > U+007E."
    # > The default encode set is the simple encode set and code points U+0020,
    # > '"', "#", "<", ">", "?", "`", "{", and "}".
    DEFAULT_ENCODE_REGEX = re.compile(rb'[\x00-\x20\x7f-\xff"#<>?`{}]')
    def pct_encode_path(url):
        url.path = Canonicalizer.DEFAULT_ENCODE_REGEX.sub(
                lambda m: b'%%%02X' % m.group()[0], url.path)

    def empty_path_to_slash(url):
        if not url.path and url.authority:
            url.path = b'/'

    def dotted_decimal(num):
        if num is None:
            return None
        return str(ipaddress.IPv4Address(num)).encode('utf-8')

    def normalize_ip_address(url):
        if url.ip4:
            url.host = Canonicalizer.dotted_decimal(url.ip4)
        # XXX ip6?

    def elide_default_port(url):
        if (url.scheme in ssurt.SPECIAL_SCHEMES
                and url.port == ssurt.SPECIAL_SCHEMES[url.scheme]):
            url.colon_before_port = b''
            url.port = b''

    def elide_at_sign_for_empty_userinfo(url):
        if (not url.username
            and not url.colon_before_password
            and not url.password):
            url.at_sign = b''

    def two_slashes(url):
        if url.slashes or url.authority or (
                url.scheme == b'file' and url.path):
            url.slashes = b'//'

    def punycode(url):
        # IDNA2008? see https://github.com/kennethreitz/requests/issues/3687#issuecomment-261590419
        if url.host:
            url.host = url.host.decode('utf-8').encode('idna')

Canonicalizer.WHATWG = Canonicalizer([
    Canonicalizer.remove_leading_trailing_junk,
    Canonicalizer.remove_tabs_and_newlines,
    Canonicalizer.lowercase_scheme,
    Canonicalizer.fix_backslashes,
    Canonicalizer.normalize_path_dots,
    Canonicalizer.decode_path_2e,
    Canonicalizer.pct_encode_path,
    Canonicalizer.empty_path_to_slash,
    Canonicalizer.normalize_ip_address,
    Canonicalizer.elide_default_port,
    Canonicalizer.elide_at_sign_for_empty_userinfo,
    Canonicalizer.two_slashes,
    Canonicalizer.punycode,
])
