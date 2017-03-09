'''
urlcanon/canon.py - url canonicalization

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
import ipaddress
import urlcanon
import urlcanon.parse
try:
    from urllib.parse import unquote_to_bytes as urllib_pct_decode
except ImportError:
    from urllib import unquote as urllib_pct_decode
import idna

class Canonicalizer:
    def __init__(self, steps):
        self.steps = steps

    def __call__(self, url):
        return self.canonicalize(url)

    def canonicalize(self, url):
        for step in self.steps:
            step(url)
        return url

    @staticmethod
    def remove_leading_trailing_junk(url):
        url.leading_junk = b''
        url.trailing_junk = b''

    TAB_AND_NEWLINE_REGEX = re.compile(br'[\x09\x0a\x0d]')
    @staticmethod
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

    @staticmethod
    def lowercase_scheme(url):
        url.scheme = url.scheme.lower()

    @staticmethod
    def fix_backslashes(url):
        if url.scheme in urlcanon.SPECIAL_SCHEMES:
            url.slashes = b'/' * len(url.slashes)
            url.path = url.path.replace(b'\\', b'/')

    SPECIAL_PATH_SEPARATORS_REGEX = re.compile(br'[^/\\]')
    SPECIAL_PATH_SEGMENTS_REGEX = re.compile(br'[/\\]')
    NONSPECIAL_PATH_SEPARATORS_REGEX = re.compile(br'[^/]')
    NONSPECIAL_PATH_SEGMENTS_REGEX = re.compile(br'/')
    PATH_DOTS_REGEX = re.compile(br'\A([.]|%2e)([.]|%2e)?\Z', re.IGNORECASE)
    @staticmethod
    def resolve_path_dots(path, special=False):
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
        if special:
            path_separators_re = Canonicalizer.SPECIAL_PATH_SEPARATORS_REGEX
            path_segments_re = Canonicalizer.SPECIAL_PATH_SEGMENTS_REGEX
        else:
            path_separators_re = Canonicalizer.NONSPECIAL_PATH_SEPARATORS_REGEX
            path_segments_re = Canonicalizer.NONSPECIAL_PATH_SEGMENTS_REGEX

        if path and (path[0:1] == b'/' or special and path[0:1] == b'\\'):
            separators_bytes = path_separators_re.sub(b'', path)
            separators = [separators_bytes[i:i+1]
                         for i in range(len(separators_bytes))]
            segments = path_segments_re.split(path)[1:]
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

    @staticmethod
    def normalize_path_dots(url):
        url.path = Canonicalizer.resolve_path_dots(
                url.path, special=url.scheme in urlcanon.SPECIAL_SCHEMES)

    PCT2E_REGEX = re.compile(br'%2e', re.IGNORECASE)
    @staticmethod
    def decode_path_2e(url):
        url.path = Canonicalizer.PCT2E_REGEX.sub(b'.', url.path)

    # > The C0 control percent-encode set are C0 controls and all code points
    # > greater than U+007E.
    C0_ENCODE_REGEX = re.compile(br'[\x00-\x1f\x7f-\xff]')
    # > The path percent-encode set is the C0 control percent-encode set and
    # > code points U+0020, '"', "#", "<", ">", "?", "`", "{", and "}".
    DEFAULT_ENCODE_REGEX = re.compile(br'[\x00-\x20\x7f-\xff"#<>?`{}]')
    # > If byte is less than 0x21, greater than 0x7E, or is 0x22, 0x23, 0x3C,
    # > or 0x3E, append byte, percent encoded, to url's query.
    QUERY_ENCODE_REGEX = re.compile(br'[\x00-\x20\x22\x23\x3c\x3e\x7f-\xff]')

    @staticmethod
    def pct_encode(bs, encode_re):
        '''
        Returns the result of replacing bytes in `bs` that match `encode_re`
        with percent-encoded versions.
        '''
        def pct_encode_byte(m):
            # return b'%%%02X' % ord(m.group()) # doesn't work in python 3.4
            return ('%%%02X' % ord(m.group())).encode('ascii')
        return encode_re.sub(pct_encode_byte, bs)

    @staticmethod
    def pct_encode_path(url):
        # "cannot-be-a-base-URL path state" vs "path state" encodings differ
        if url.path[:1] == b'/' or url.scheme in urlcanon.SPECIAL_SCHEMES:
            encode_re = Canonicalizer.DEFAULT_ENCODE_REGEX
        else:
            encode_re = Canonicalizer.C0_ENCODE_REGEX
        url.path = Canonicalizer.pct_encode(url.path, encode_re)

    @staticmethod
    def pct_encode_fragment(url):
        url.fragment = Canonicalizer.pct_encode(
                url.fragment, Canonicalizer.C0_ENCODE_REGEX)

    @staticmethod
    def pct_encode_query(url):
        url.query = Canonicalizer.pct_encode(
                url.query, Canonicalizer.QUERY_ENCODE_REGEX)

    @staticmethod
    def pct_encode_nonspecial_host(url):
        if url.host and not url.scheme in urlcanon.SPECIAL_SCHEMES:
            url.host = Canonicalizer.pct_encode(
                    url.host, Canonicalizer.C0_ENCODE_REGEX)

    @staticmethod
    def empty_path_to_slash(url):
        if (not url.path and url.authority
                and url.scheme in urlcanon.SPECIAL_SCHEMES):
            url.path = b'/'

    @staticmethod
    def dotted_decimal(num):
        if num is None:
            return None
        return str(ipaddress.IPv4Address(num)).encode('utf-8')

    @staticmethod
    def normalize_ip_address(url):
        if url.ip4 is not None:
            url.host = Canonicalizer.dotted_decimal(url.ip4)
        elif url.ip6 is not None:
            url.host = b'[' + str(
                ipaddress.IPv6Address(url.ip6)).encode('utf-8') + b']'

    @staticmethod
    def elide_default_port(url):
        if (url.scheme in urlcanon.SPECIAL_SCHEMES
                and url.port == urlcanon.SPECIAL_SCHEMES[url.scheme]):
            url.colon_before_port = b''
            url.port = b''

    @staticmethod
    def clean_up_userinfo(url):
        if not url.password:
            url.colon_before_password = b''
            if not url.username:
                url.at_sign = b''

    @staticmethod
    def two_slashes(url):
        if url.slashes or url.authority or url.scheme == b'file':
            url.slashes = b'//'

    @staticmethod
    def punycode_special_host(url):
        if url.host and url.scheme in urlcanon.SPECIAL_SCHEMES:
            try:
                # IDNA2008
                url.host = idna.encode(url.host.decode('utf-8'), uts46=True)
            except (idna.IDNAError, UnicodeDecodeError):
                # try IDNA2003
                url.host = url.host.decode('utf-8').encode('idna')

    @staticmethod
    def leading_slash(url):
        '''
        b'a/b/c' => b'/a/b/c' if scheme is special
        '''
        if url.scheme in urlcanon.SPECIAL_SCHEMES and url.path[:1] != b'/':
            url.path = b'/' + url.path

    @staticmethod
    def remove_fragment(url):
        url.hash_sign = b''
        url.fragment = b''

    @staticmethod
    def pct_decode_repeatedly(url):
        def _pct_decode_repeatedly(orig):
            if not orig:
                return orig
            val = orig
            while val:
                new_val = urllib_pct_decode(val)
                if new_val == val:
                    return val
                val = new_val
        url.scheme = _pct_decode_repeatedly(url.scheme)
        url.username = _pct_decode_repeatedly(url.username)
        url.password = _pct_decode_repeatedly(url.password)
        url.host = _pct_decode_repeatedly(url.host)
        url.port = _pct_decode_repeatedly(url.port)
        url.path = _pct_decode_repeatedly(url.path)
        url.query = _pct_decode_repeatedly(url.query)

    # https://developers.google.com/safe-browsing/v4/urls-hashing
    # > In the URL, percent-escape all characters that are <= ASCII 32, >= 127,
    # > "#", or "%". The escapes should use uppercase hex characters.
    GOOGLE_PCT_ENCODE_BYTES = re.compile(br'[\x00-\x20\x7f-\xff#%]')
    @staticmethod
    def google_pct_encode(url):
        def _pct_encode(unencoded):
            return Canonicalizer.GOOGLE_PCT_ENCODE_BYTES.sub(
                    lambda m: ('%%%02X' % ord(m.group())).encode('ascii'),
                    unencoded)
        url.scheme = _pct_encode(url.scheme)
        url.username = _pct_encode(url.username)
        url.password = _pct_encode(url.password)
        url.host = _pct_encode(url.host)
        url.port = _pct_encode(url.port)
        url.path = _pct_encode(url.path)
        url.query = _pct_encode(url.query)

    @staticmethod
    def reparse_host(url):
        url.ip4, url.ip6 = urlcanon.parse_ipv4or6(url.host)

    @staticmethod
    def default_scheme_http(url):
        if not url.scheme:
            url.scheme = b'http'
            url.colon_after_scheme = b':'
            if url.path:
                urlcanon.parse.parse_pathish(url, url.path)

    @staticmethod
    def collapse_consecutive_slashes(url):
        url.path = re.sub(b'//+', b'/', url.path)

    @staticmethod
    # https://developers.google.com/safe-browsing/v4/urls-hashing
    # 1. Remove all leading and trailing dots.
    # 2. Replace consecutive dots with a single dot.
    def fix_host_dots(url):
        if url.host:
            url.host = re.sub(br'^\.+', b'', url.host)
            url.host = re.sub(br'\.+$', b'', url.host)
            url.host = re.sub(br'\.{2,}', b'.', url.host)

    @staticmethod
    def pct_decode_host(url):
        if url.host and url.scheme in urlcanon.SPECIAL_SCHEMES:
            url.host = urllib_pct_decode(url.host)

Canonicalizer.WHATWG = Canonicalizer([
    Canonicalizer.remove_leading_trailing_junk,
    Canonicalizer.remove_tabs_and_newlines,
    Canonicalizer.lowercase_scheme,
    Canonicalizer.elide_default_port,
    Canonicalizer.clean_up_userinfo,
    Canonicalizer.two_slashes,
    Canonicalizer.pct_decode_host,
    Canonicalizer.reparse_host,
    Canonicalizer.normalize_ip_address,
    Canonicalizer.punycode_special_host,
    Canonicalizer.pct_encode_nonspecial_host,
    Canonicalizer.fix_backslashes,
    Canonicalizer.pct_encode_path,
    Canonicalizer.leading_slash,
    Canonicalizer.normalize_path_dots,
    Canonicalizer.empty_path_to_slash,
    Canonicalizer.pct_encode_query,
    Canonicalizer.pct_encode_fragment,
])

# http://web.archive.org/web/20130116211349/https://developers.google.com/safe-browsing/developers_guide_v2#Canonicalization
# differs from google, does not remove port, matching surt library
Canonicalizer.Google = Canonicalizer([
    Canonicalizer.remove_leading_trailing_junk,
    Canonicalizer.default_scheme_http,
    Canonicalizer.remove_tabs_and_newlines,
    Canonicalizer.lowercase_scheme,
    Canonicalizer.fix_backslashes,
    Canonicalizer.pct_encode_path,
    Canonicalizer.empty_path_to_slash,
    Canonicalizer.elide_default_port,
    Canonicalizer.clean_up_userinfo,
    Canonicalizer.leading_slash,
    Canonicalizer.two_slashes,
    Canonicalizer.remove_fragment,
    Canonicalizer.pct_decode_repeatedly,
    Canonicalizer.normalize_path_dots,
    Canonicalizer.fix_host_dots,
    Canonicalizer.collapse_consecutive_slashes,
    Canonicalizer.punycode_special_host,
    Canonicalizer.reparse_host,
    Canonicalizer.normalize_ip_address,
    Canonicalizer.google_pct_encode,
    # Canonicalizer.remove_port,
])

