/*
 * ParsedUrl.java - url parser
 * Java port of parse.py
 *
 * Copyright (C) 2016 Internet Archive
 * Copyright (C) 2016 National Library of Australia
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.netpreserve.ssurt;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.util.regex.Pattern.DOTALL;

public class ParsedUrl {

    private final static Pattern LEADING_JUNK_REGEX = Pattern.compile("\\A([\\x00-\\x20]*)(.*)\\Z", DOTALL);
    private final static Pattern TRAILING_JUNK_REGEX = Pattern.compile("\\A(.*?)([\\x00-\\x20]*)\\Z", DOTALL);

    private final static Pattern URL_REGEX = Pattern.compile(("\\A" +
            "(?:" +
            "   (?<scheme> [a-zA-Z] [^:]* )" +
            "   (?<colonAfterScheme> : )" +
            ")?" +
            "(?<pathish>" +
            "  ( [/\\\\]* [^/\\\\?#]* )*" +
            ")" +
            "(?:" +
            "  (?<questionMark> [?] )" +
            "  (?<query> [^#]* )" +
            ")?" +
            "(?:" +
            "  (?<hashSign> [#] )" +
            "  (?<fragment> .* )" +
            ")?" +
            "\\Z").replace(" ", ""), DOTALL);

    private final static Pattern PATHISH_SEGMENT_REGEX = Pattern.compile(
            "(?<slashes> [/\\\\]* )(?<segment> [^/\\\\]* )".replace(" ", ""), DOTALL);

    private final static Pattern AUTHORITY_REGEX = Pattern.compile(("\\A" +
            "(?:" +
            "   (?<username> [^:@]* )" +
            "   (" +
            "     (?<colonBeforePassword> : )" +
            "     (?<password> [^@]* )" +
            "   )?" +
            "   (?<atSign> @ )" +
            ")?" +
            "(?<host>" +
            "    (?<ip6> \\[ [^\\]]* \\] )" +
            "  | (?<ip4> [0-9]+ \\. [0-9]+ \\. [0-9]+ \\. [0-9]+ )" +
            "  | (?<domain> [^:]* )" +
            ")" +
            "(?:" +
            "  (?<colonBeforePort> : )" +
            "  (?<port> .* )" +
            ")?" +
            "\\Z").replace(" ", ""), DOTALL);

    /*
     * IMPORTANT: These aren't real strings! This parser operates on arbitrary
     * byte sequences. It even works on invalid UTF-8.
     *
     * Unlike the Python, Java's regex engine can't operate directly on byte
     * sequences. So we use a hacky workaround based on the observation that
     * every possible byte sequence can be represented as a String by "decoding"
     * it as ISO-8859-1.
     *
     * All public accessors that return a String MUST encode these as ISO-8859-1
     * first and then decode again as UTF-8.
     */
    String leadingJunk;
    String trailingJunk;
    String scheme;
    String colonAfterScheme;
    String questionMark;
    String query;
    String hashSign;
    String fragment;
    String slashes;
    String path;
    String username;
    String colonBeforePassword;
    String password;
    String atSign;
    String ip6;
    String ip4;
    String domain;
    String colonBeforePort;
    String port;

    public static ParsedUrl parse(String s) {
        return parse(s.getBytes(StandardCharsets.UTF_8));
    }

    public static ParsedUrl parse(byte[] bytes) {
        ParsedUrl url = new ParsedUrl();

        // decoding hack: see "IMPORTANT" comment above for why we do this
        String input = new String(bytes, StandardCharsets.ISO_8859_1);

        // "leading and trailing C0 controls and space"
        Matcher m = LEADING_JUNK_REGEX.matcher(input);
        if (m.matches()) {
            url.leadingJunk = m.group(1);
            input = m.group(2);
        } else {
            url.leadingJunk = "";
        }

        m = TRAILING_JUNK_REGEX.matcher(input);
        if (m.matches()) {
            input = m.group(1);
            url.trailingJunk = m.group(2);
        } else {
            url.trailingJunk = "";
        }

        // parse url
        m = URL_REGEX.matcher(input);
        if (m.matches()) {
            url.scheme = orBlank(m.group("scheme"));
            url.colonAfterScheme = orBlank(m.group("colonAfterScheme"));
            url.questionMark = orBlank(m.group("questionMark"));
            url.query = orBlank(m.group("query"));
            url.hashSign = orBlank(m.group("hashSign"));
            url.fragment = orBlank(m.group("fragment"));
        } else {
            throw new IllegalStateException("this should be impossible");
        }

        // we parse the authority + path into "pathish" initially so that we can
        // correctly handle file: urls
        String pathish = m.group("pathish");
        if (pathish != null && (pathish.charAt(0) == '/' || pathish.charAt(0) == '\\')) {
            List<String> pathishComponents = new ArrayList<>();
            m = PATHISH_SEGMENT_REGEX.matcher(pathish);
            while (m.find()) {
                pathishComponents.add(m.group("slashes"));
                pathishComponents.add(m.group("segment"));
            }

            String authority;
            String firstComponent = pathishComponents.get(0);
            if (WhatwgCanonicalizer.removeTabsAndNewlines(url.scheme).equalsIgnoreCase("file")
                    && firstComponent.length() >= 3) {
                url.slashes = firstComponent.substring(0, Math.max(firstComponent.length() - 2, 0));
                authority = "";
                url.path = firstComponent.substring(2) + String.join("", pathishComponents.subList(1, pathishComponents.size()));
            } else {
                url.slashes = pathishComponents.get(0);
                authority = pathishComponents.get(1);
                url.path = String.join("", pathishComponents.subList(2, pathishComponents.size()));
            }

            // parse the authority
            m = AUTHORITY_REGEX.matcher(authority);
            if (m.matches()) {
                url.username = orBlank(m.group("username"));
                url.colonBeforePassword = orBlank(m.group("colonBeforePassword"));
                url.password = orBlank(m.group("password"));
                url.atSign = orBlank(m.group("atSign"));
                url.ip6 = orBlank(m.group("ip6"));
                url.ip4 = orBlank(m.group("ip4"));
                url.domain = orBlank(m.group("domain"));
                url.colonBeforePort = orBlank(m.group("colonBeforePort"));
                url.port = orBlank(m.group("port"));
            } else {
                throw new IllegalStateException("this should be impossible");
            }
        } else {
            // pathish doesn't start with / so it's an opaque thing
            url.path = orBlank(pathish);
        }
        return url;
    }

    private static String orBlank(String s) {
        return s != null ? s : "";
    }

    boolean hasAuthority() {
        return !(domain.isEmpty() && ip6.isEmpty() && ip4.isEmpty());
    }
}
