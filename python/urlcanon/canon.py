# vim: set fileencoding=utf-8:
'''
urlcanon/canon.py - url canonicalization

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
import re
import ipaddress
import urlcanon
import urlcanon.parse
try:
    from urllib.parse import unquote_to_bytes as urllib_pct_decode
except ImportError:
    from urllib import unquote as urllib_pct_decode
import idna
import encodings.idna as idna2003

try:
    unicode
except NameError:
    unicode = str

class Canonicalizer:
    def __init__(self, steps):
        self.steps = steps

    def __call__(self, url):
        return self.canonicalize(url)

    def canonicalize(self, url):
        if not isinstance(url, urlcanon.ParsedUrl):
            url = urlcanon.parse_url(url)
        for step in self.steps:
            step(url)
        return url

    def rule_applies(self, match_rule, url, parent_url=None):
        '''
        Returns true if `self.canonicalize(url)` matches `match_rule`.

        Args:
            match_rule (urlcanon.MatchRule): the rule
            url (urlcanon.ParsedUrl or bytes or str): the (possibly
                uncanonicalized) url to check, can be a `urlcanon.ParsedUrl` or
                a str or bytes
            parent_url (str, optional): parent url (some match rules have
                conditions on the parent url)
        Returns:
            bool: True if the rule matches, False otherwise
        '''
        return match_rule.applies(self.canonicalize(url))

def remove_leading_trailing_junk(url):
    url.leading_junk = b''
    url.trailing_junk = b''

TAB_AND_NEWLINE_REGEX = re.compile(br'[\x09\x0a\x0d]')
def remove_tabs_and_newlines(url):
    url.leading_junk = TAB_AND_NEWLINE_REGEX.sub(b'', url.leading_junk)
    url.scheme = TAB_AND_NEWLINE_REGEX.sub(b'', url.scheme)
    url.colon_after_scheme = TAB_AND_NEWLINE_REGEX.sub(
            b'', url.colon_after_scheme)
    url.slashes = TAB_AND_NEWLINE_REGEX.sub(b'', url.slashes)
    url.username = TAB_AND_NEWLINE_REGEX.sub(b'', url.username)
    url.colon_before_password = TAB_AND_NEWLINE_REGEX.sub(
            b'', url.colon_before_password)
    url.password = TAB_AND_NEWLINE_REGEX.sub(b'', url.password)
    url.at_sign = TAB_AND_NEWLINE_REGEX.sub(b'', url.at_sign)
    url.host = TAB_AND_NEWLINE_REGEX.sub(b'', url.host)
    url.colon_before_port = TAB_AND_NEWLINE_REGEX.sub(
            b'', url.colon_before_port)
    url.port = TAB_AND_NEWLINE_REGEX.sub(b'', url.port)
    url.path = TAB_AND_NEWLINE_REGEX.sub(b'', url.path)
    url.question_mark = TAB_AND_NEWLINE_REGEX.sub(b'', url.question_mark)
    url.query = TAB_AND_NEWLINE_REGEX.sub(b'', url.query)
    url.hash_sign = TAB_AND_NEWLINE_REGEX.sub(b'', url.hash_sign)
    url.fragment = TAB_AND_NEWLINE_REGEX.sub(b'', url.fragment)
    url.trailing_junk = TAB_AND_NEWLINE_REGEX.sub(b'', url.trailing_junk)

def lowercase_scheme(url):
    url.scheme = url.scheme.lower()

def fix_backslashes(url):
    if url.scheme in urlcanon.SPECIAL_SCHEMES:
        url.slashes = b'/' * len(url.slashes)
        url.path = url.path.replace(b'\\', b'/')

SPECIAL_PATH_SEPARATORS_REGEX = re.compile(br'[^/\\]')
SPECIAL_PATH_SEGMENTS_REGEX = re.compile(br'[/\\]')
NONSPECIAL_PATH_SEPARATORS_REGEX = re.compile(br'[^/]')
NONSPECIAL_PATH_SEGMENTS_REGEX = re.compile(br'/')
PATH_DOTS_REGEX = re.compile(br'\A([.]|%2e)([.]|%2e)?\Z', re.IGNORECASE)
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
        path_separators_re = SPECIAL_PATH_SEPARATORS_REGEX
        path_segments_re = SPECIAL_PATH_SEGMENTS_REGEX
    else:
        path_separators_re = NONSPECIAL_PATH_SEPARATORS_REGEX
        path_segments_re = NONSPECIAL_PATH_SEGMENTS_REGEX

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
            m = PATH_DOTS_REGEX.match(old_path[i])
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
    url.path = resolve_path_dots(
            url.path, special=url.scheme in urlcanon.SPECIAL_SCHEMES)

# > The C0 control percent-encode set are C0 controls and all code points
# > greater than U+007E.
C0_ENCODE_RE = re.compile(br'[\x00-\x1f\x7f-\xff]')
# > The path percent-encode set is the C0 control percent-encode set and
# > code points U+0020, '"', "#", "<", ">", "?", "`", "{", and "}".
PATH_ENCODE_RE = re.compile(br'[\x00-\x20\x7f-\xff"#<>?`{}]')
# > If byte is less than 0x21, greater than 0x7E, or is 0x22, 0x23, 0x3C,
# > or 0x3E, append byte, percent encoded, to url's query.
QUERY_ENCODE_RE = re.compile(br'[\x00-\x20\x22\x23\x3c\x3e\x7f-\xff]')
# > The userinfo percent-encode set is the path percent-encode set and code
# > points "/", ":", ";", "=", "@", "[", "\", "]", "^", and "|".
USERINFO_ENCODE_RE = re.compile(
        br'[\x00-\x20\x7f-\xff"#<>?`{}/:;=@\[\\\]\^\|]')

# XXX need to take a closer look at whatwg host parsing, this regex is a hack
# to fix handling of host containing "%20"
HOST_ENCODE_RE = re.compile(br'[\x00-\x20\x7f-\xff]')

def pct_encode(bs, encode_re):
    '''
    Returns the result of replacing bytes in `bs` that match `encode_re`
    with percent-encoded versions.
    '''
    def pct_encode_byte(m):
        # return b'%%%02X' % ord(m.group()) # doesn't work in python 3.4
        return ('%%%02X' % ord(m.group())).encode('ascii')
    return encode_re.sub(pct_encode_byte, bs)

def pct_encode_path(url):
    # "cannot-be-a-base-URL path state" vs "path state" encodings differ
    if url.path[:1] == b'/' or url.scheme in urlcanon.SPECIAL_SCHEMES:
        encode_re = PATH_ENCODE_RE
    else:
        encode_re = C0_ENCODE_RE
    url.path = pct_encode(url.path, encode_re)

def pct_encode_userinfo(url):
    url.username = pct_encode(url.username, USERINFO_ENCODE_RE)
    url.password = pct_encode(url.password, USERINFO_ENCODE_RE)

def pct_encode_fragment(url):
    url.fragment = pct_encode(url.fragment, C0_ENCODE_RE)

def pct_encode_host(url):
    url.host = pct_encode(url.host, HOST_ENCODE_RE)

def empty_path_to_slash(url):
    if (not url.path and url.authority
            and url.scheme in urlcanon.SPECIAL_SCHEMES):
        url.path = b'/'

def dotted_decimal(num):
    if num is None:
        return None
    return str(ipaddress.IPv4Address(num)).encode('utf-8')

def normalize_ip_address(url):
    if url.ip4 is not None:
        url.host = dotted_decimal(url.ip4)
    elif url.ip6 is not None:
        url.host = b'[' + str(
            ipaddress.IPv6Address(url.ip6)).encode('utf-8') + b']'

def elide_default_port(url):
    if (url.scheme in urlcanon.SPECIAL_SCHEMES
            and url.port == urlcanon.SPECIAL_SCHEMES[url.scheme]):
        url.colon_before_port = b''
        url.port = b''

def clean_up_userinfo(url):
    if not url.password:
        url.colon_before_password = b''
        if not url.username:
            url.at_sign = b''

def two_slashes(url):
    if url.slashes or url.authority or url.scheme == b'file':
        url.slashes = b'//'

def punycode_special_host(url):
    if url.host and url.scheme in urlcanon.SPECIAL_SCHEMES:
        # https://github.com/kjd/idna/issues/40#issuecomment-285496926
        try:
            url.host = idna.encode(url.host.decode('utf-8'), uts46=True)
        except:
            try:
                remapped = idna.uts46_remap(url.host.decode('utf-8'))
                labels = remapped.split('.')
                punycode_labels = [idna2003.ToASCII(label) for label in labels]
                url.host = b'.'.join(punycode_labels)
            except:
                pass

def leading_slash(url):
    '''
    b'a/b/c' => b'/a/b/c' if scheme is special
    '''
    if url.scheme in urlcanon.SPECIAL_SCHEMES and url.path[:1] != b'/':
        url.path = b'/' + url.path

def remove_fragment(url):
    url.hash_sign = b''
    url.fragment = b''

def remove_userinfo(url):
    url.username = b''
    url.colon_before_password = b''
    url.password = b''
    url.at_sign = b''

def pct_decode_token_repeatedly(orig):
    if not orig:
        return orig
    val = orig
    while val:
        new_val = urllib_pct_decode(val)
        if new_val == val:
            return val
        val = new_val

def pct_decode_repeatedly(url, skip_query=False):
    url.scheme = pct_decode_token_repeatedly(url.scheme)
    url.username = pct_decode_token_repeatedly(url.username)
    url.password = pct_decode_token_repeatedly(url.password)
    url.host = pct_decode_token_repeatedly(url.host)
    url.port = pct_decode_token_repeatedly(url.port)
    url.path = pct_decode_token_repeatedly(url.path)
    if not skip_query:
        url.query = pct_decode_token_repeatedly(url.query)
    url.fragment = pct_decode_token_repeatedly(url.fragment)

def pct_decode_repeatedly_except_query(url):
    pct_decode_repeatedly(url, True)

def pct_encode_query(url, encode_re=QUERY_ENCODE_RE):
    if not url.query:
        return
    orig_parts = url.query.split(b'&')
    canon_parts = []
    for part in orig_parts:
        orig_key_value = part.split(b'=', 1)
        new_key_value = []
        for token in orig_key_value:
            new_key_value.append(pct_encode(token, encode_re))
        canon_parts.append(b'='.join(new_key_value))
    url.query = b'&'.join(canon_parts)

# https://developers.google.com/safe-browsing/v4/urls-hashing
# > In the URL, percent-escape all characters that are <= ASCII 32, >= 127,
# > "#", or "%". The escapes should use uppercase hex characters.
GOOGLE_PCT_ENCODE_RE = re.compile(br'[\x00-\x20\x7f-\xff#%]')
def google_pct_encode(url):
    url.scheme = pct_encode(url.scheme, GOOGLE_PCT_ENCODE_RE)
    url.username = pct_encode(url.username, GOOGLE_PCT_ENCODE_RE)
    url.password = pct_encode(url.password, GOOGLE_PCT_ENCODE_RE)
    url.host = pct_encode(url.host, GOOGLE_PCT_ENCODE_RE)
    url.port = pct_encode(url.port, GOOGLE_PCT_ENCODE_RE)
    url.path = pct_encode(url.path, GOOGLE_PCT_ENCODE_RE)
    pct_encode_query(url, GOOGLE_PCT_ENCODE_RE)
    url.fragment = pct_encode(url.fragment, GOOGLE_PCT_ENCODE_RE)

LESS_DUMB_USERINFO_ENCODE_RE = re.compile(br'[\x00-\x20\x7f-\xff#%:@]')
LESS_DUMB_PATH_ENCODE_RE = re.compile(br'[\x00-\x20\x7f-\xff#%?]')
def less_dumb_pct_encode(url):
    url.scheme = pct_encode(url.scheme, GOOGLE_PCT_ENCODE_RE)
    url.username = pct_encode(url.username, LESS_DUMB_USERINFO_ENCODE_RE)
    url.password = pct_encode(url.password, LESS_DUMB_USERINFO_ENCODE_RE)
    url.host = pct_encode(url.host, GOOGLE_PCT_ENCODE_RE)
    url.port = pct_encode(url.port, GOOGLE_PCT_ENCODE_RE)
    url.path = pct_encode(url.path, LESS_DUMB_PATH_ENCODE_RE)
    url.fragment = pct_encode(url.fragment, GOOGLE_PCT_ENCODE_RE)

LESS_DUMB_QUERY_ENCODE_RE = re.compile(br'[\x00-\x20\x7f-\xff#%&=]')
def less_dumb_pct_recode_query(url):
    if not url.query:
        return
    orig_parts = url.query.split(b'&')
    canon_parts = []
    for part in orig_parts:
        orig_key_value = part.split(b'=', 1)
        new_key_value = []
        for token in orig_key_value:
            unescaped_token = pct_decode_token_repeatedly(token)
            new_key_value.append(
                    pct_encode(unescaped_token, LESS_DUMB_QUERY_ENCODE_RE))
        canon_parts.append(b'='.join(new_key_value))
    url.query = b'&'.join(canon_parts)

def reparse_host(url):
    url.ip4, url.ip6 = urlcanon.parse_ipv4or6(url.host)

def default_scheme_http(url):
    if not url.scheme:
        url.scheme = b'http'
        url.colon_after_scheme = b':'
        if url.path:
            urlcanon.parse.parse_pathish(url, url.path)

def collapse_consecutive_slashes(url):
    if url.scheme in urlcanon.SPECIAL_SCHEMES:
        url.path = re.sub(b'//+', b'/', url.path)

def fix_host_dots(url):
    '''
    https://developers.google.com/safe-browsing/v4/urls-hashing
    1. Remove all leading and trailing dots.
    2. Replace consecutive dots with a single dot.
    '''
    if url.host:
        url.host = re.sub(br'^\.+', b'', url.host)
        url.host = re.sub(br'\.+$', b'', url.host)
        url.host = re.sub(br'\.{2,}', b'.', url.host)

def pct_decode_host(url):
    if url.host and url.scheme in urlcanon.SPECIAL_SCHEMES:
        url.host = urllib_pct_decode(url.host)

def alpha_reorder_query(url):
    if url.query:
        url.query = b'&'.join(sorted(url.query.split(b'&')))

def https_to_http(url):
    if url.scheme == b'https':
        url.scheme = b'http'

WWWN_RE = re.compile(br'^www\d*\.')
def strip_www(url):
    m = WWWN_RE.match(url.host)
    if m:
        url.host = url.host[len(m.group(0)):]

def lowercase_path(url):
    url.path = url.path.lower()

def lowercase_query(url):
    url.query = url.query.lower()

# can't use the lookbehind in the java version because:
# sre_constants.error: look-behind requires fixed-width pattern
QUERY_SESSIONID_RE = re.compile(
        b'(?i)(&|^)(?:'
        b'jsessionid=[0-9a-z$]{10,}'
        b'|sessionid=[0-9a-z]{16,}'
        b'|phpsessid=[0-9a-z]{16,}'
        b'|sid=[0-9a-z]{16,}'
        b'|aspsessionid[a-z]{8}=[0-9a-z]{16,}'
        b'|cfid=[0-9]+&cftoken=[0-9a-z-]+'
        b')(&|$)')
def strip_session_ids_from_query(url):
    url.query = QUERY_SESSIONID_RE.sub(br'\1\2', url.query)

ASPX_SUFFIX_RE = re.compile(b'.*\\.aspx\\Z')
ASPX_PATH_SESSIONID_RE = re.compile(
        b'(?<=/)\\([0-9a-z]{24}\\)/|'
        b'(?<=/)(?:\\((?:[a-z]\\([0-9a-z]{24}\\))+\\)/)')
PATH_SESSIONID_RE = re.compile(b';jsessionid=[0-9a-z]{32}$');
def strip_session_ids_from_path(url):
    if ASPX_SUFFIX_RE.match(url.path):
        url.path = ASPX_PATH_SESSIONID_RE.sub(b'', url.path)
    url.path = PATH_SESSIONID_RE.sub(b'', url.path)

REDUNDANT_AMPERSAND_RE = re.compile(b'^&+|&+$|(?<=&)&+');
def remove_redundant_ampersands_from_query(url):
    url.query = REDUNDANT_AMPERSAND_RE.sub(b'', url.query)

def omit_question_mark_if_query_empty(url):
    if not url.query:
        url.question_mark = b''

def strip_trailing_slash_unless_empty(parsed_url):
    if parsed_url.path != b'/' and parsed_url.path.endswith(b'/'):
        parsed_url.path = parsed_url.path[:-1]

whatwg = Canonicalizer([
    remove_leading_trailing_junk,
    remove_tabs_and_newlines,
    lowercase_scheme,
    elide_default_port,
    clean_up_userinfo,
    two_slashes,
    pct_decode_host,
    reparse_host,
    normalize_ip_address,
    punycode_special_host,
    pct_encode_host,
    fix_backslashes,
    pct_encode_path,
    leading_slash,
    normalize_path_dots,
    empty_path_to_slash,
    pct_encode_userinfo,
    pct_encode_query,
    pct_encode_fragment,
])

# http://web.archive.org/web/20130116211349/https://developers.google.com/safe-browsing/developers_guide_v2#Canonicalization
# differs from google, does not remove port, matching surt library
google = Canonicalizer([
    remove_leading_trailing_junk,
    default_scheme_http,
    remove_tabs_and_newlines,
    lowercase_scheme,
    fix_backslashes,
    pct_encode_path,
    empty_path_to_slash,
    elide_default_port,
    clean_up_userinfo,
    leading_slash,
    two_slashes,
    remove_fragment,
    pct_decode_repeatedly,
    normalize_path_dots,
    fix_host_dots,
    collapse_consecutive_slashes,
    punycode_special_host,
    reparse_host,
    normalize_ip_address,
    google_pct_encode,
    # remove_port,
])

# 😭 pydoc ignores my docstring
semantic_precise = Canonicalizer([
    remove_leading_trailing_junk,
    default_scheme_http,
    remove_tabs_and_newlines,
    lowercase_scheme,
    elide_default_port,
    clean_up_userinfo,
    two_slashes,
    pct_decode_repeatedly_except_query,
    reparse_host,
    normalize_ip_address,
    fix_host_dots,
    punycode_special_host,
    remove_userinfo,
    less_dumb_pct_encode,
    less_dumb_pct_recode_query,
    fix_backslashes,
    leading_slash,
    normalize_path_dots,
    collapse_consecutive_slashes,
    empty_path_to_slash,
    alpha_reorder_query,
])
'''
Precise semantic canonicalizer.

Semantic in the sense that the intention is to canonicalize urls that "mean"
the same thing, that you would expect to load the same stuff and look the same
way if you pasted them into the location bar of your browser.

Does everything WHATWG does and also some cleanup:
- sets default scheme http: if scheme is missing
- removes extraneous dots in the host
And these additional steps:
- collapses consecutive slashes in the path
- standardizes percent encodings so that different encodings of the same-ish
  thing match
- sorts query params
- removes userinfo
'''

# Semantic canonicalizer. Like semantic_precise but removes the fragment from
# the url, thus considers urls which differ only in the fragment to be
# equivalent to each other.
semantic = Canonicalizer(
        semantic_precise.steps + [remove_fragment])

aggressive = Canonicalizer(
        semantic.steps + [
            https_to_http,
            strip_www,
            lowercase_path,
            lowercase_query,
            strip_session_ids_from_query,
            strip_session_ids_from_path,
            strip_trailing_slash_unless_empty,
            remove_redundant_ampersands_from_query,
            omit_question_mark_if_query_empty,
            alpha_reorder_query]) # sort again after lowercasing

def normalize_host(host):
    '''
    Normalize a host. Does the same stuff that the semantic canonicalizer
    does to the host part of a url.
    '''
    url = urlcanon.ParsedUrl()
    url.scheme = b'http'   # treat it as "special"
    if isinstance(host, unicode):
        url.host = host.encode('utf-8')
    else:
        url.host = host
    url.host = pct_decode_token_repeatedly(url.host)
    reparse_host(url)
    normalize_ip_address(url)
    fix_host_dots(url)
    punycode_special_host(url)
    url.host = pct_encode(url.host, GOOGLE_PCT_ENCODE_RE)
    return url.host
