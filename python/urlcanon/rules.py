'''
urlcanon/rules.py - url matching rules

Copyright (C) 2017 Internet Archive

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

import urlcanon
import re
import logging

try:
    unicode
except NameError:
    unicode = str

class MatchRule:
    '''
    A url-matching rule, with one or more conditions.

    All conditions must match for a url to be considered a match.

    The supported conditions are `surt`, `ssurt`, `regex`, `domain`,
    `substring`, `parent_url_regex`. All of the values must by bytes objects.

    No canonicalization is performed on any of the conditions. It's the
    caller's responsibility to make sure that `domain` is in a form that their
    urls can match.

    The url passed to `MatchRule.applies` is not canonicalized either. The
    caller should canonicalize it first. Same with `parent_url`. See also
    `urlcanon.Canonicalizer.rule_applies`.

    Here are some examples of valid rules expressed as yaml.

    - domain: bad.domain.com

    # preferred:
    - domain: monkey.org
      substring: bar

    # deprecated version of the same:
    - domain: monkey.org
      url_match: STRING_MATCH
      value: bar

    # preferred:
    - surt: http://(com,woop,)/fuh/

    # deprecated version of the same:
    - url_match: SURT_MATCH
      value: http://(com,woop,)/fuh/

    # preferred:
    - regex: ^https?://(www.)?youtube.com/watch?.*$
      parent_url_regex: ^https?://(www.)?youtube.com/user/.*$

    # deprecated version of the same:
    - url_match: REGEX_MATCH
      value: ^https?://(www.)?youtube.com/watch?.*$
      parent_url_regex: ^https?://(www.)?youtube.com/user/.*$
    '''

    def __init__(
            self, surt=None, ssurt=None, regex=None, domain=None,
            substring=None, parent_url_regex=None,
            url_match=None, value=None):
        '''
        Args:
            surt (bytes):
            ssurt (bytes):
            regex (bytes):
            domain (bytes):
            substring (bytes):
            parent_url_regex (bytes):
            url_match (str, deprecated):
            value (bytes, deprecated):
        '''
        self.surt = surt
        self.ssurt = ssurt
        # append \Z to get a full match (py2 doesn't have re.fullmatch)
        # (regex still works in case of \Z\Z)
        self.regex = regex and re.compile(regex + br'\Z')
        self.domain = domain
        self.substring = substring and substring
        self.parent_url_regex = parent_url_regex and re.compile(
                parent_url_regex + br'\Z')

        if url_match:
            if url_match == 'REGEX_MATCH':
                assert not self.regex
                self.regex = re.compile(value + br'\Z')
            elif url_match == 'SURT_MATCH':
                assert not self.surt
                self.surt = value
            elif url_match == 'STRING_MATCH':
                assert not self.substring
                self.substring = value
            else:
                raise Exception(
                        'invalid scope rule with url_match '
                        '%s' % repr(url_match))

        self.domain_is_ip_address = urlcanon.parse_ipv4or6(
                self.domain) != (None, None)

    def is_domain_match(self, url):
        '''
        Returns true if
         - self.domain is an ip address and url.host is the same ip address
         - self.domain is a domain and url.host is the same domain
         - self.domain is a domain and url.host is a subdomain of it
        '''
        if self.domain == url.host:
            return True

        if (self.domain_is_ip_address
                or urlcanon.parse_ipv4or6(url.host) != (None, None)):
            # if either of self.domain or url.host is an ip address and they're
            # not identical (the first check, above), not a match
            return False

        return urlcanon.reverse_host(url.host).startswith(
                urlcanon.reverse_host(self.domain))

    def applies(self, url, parent_url=None):
        '''
        Returns true if `url` matches `match_rule`.

        All conditions must match for a url to be considered a match.

        The caller should normally canonicalize before `url` and `parent_url`
        passing them to this method.

        Args:
            url (urlcanon.ParsedUrl or bytes or str): already canonicalized url
            parent_url (urlcanon.ParsedUrl or bytes or str, optional): parent
                url, should be supplied if the rule has a `parent_url_regex`
        Returns:
            bool: True if the rule matches, False otherwise
        '''
        if not isinstance(url, urlcanon.ParsedUrl):
            url = urlcanon.parse_url(url)

        if self.domain and not self.is_domain_match(url):
            return False
        if self.surt and not url.surt().startswith(self.surt):
            return False
        if self.ssurt and not url.ssurt().startswith(self.ssurt):
            return False
        if self.substring and not url.__bytes__().find(self.substring) >= 0:
            return False
        if self.regex:
            if not self.regex.match(url.__bytes__()):
                return False
        if self.parent_url_regex:
            if not parent_url:
                return False
            if isinstance(parent_url, urlcanon.ParsedUrl):
                parent_url = parent_url.__bytes__()
            elif isinstance(parent_url, unicode):
                parent_url = parent_url.encode('utf-8')
            if not self.parent_url_regex.match(parent_url):
                return False

        return True
