/*
 * WhatwgCanonicalizer.java - WHATWG-compatible url canonicalizer
 * Java port of canon.py
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

import java.net.IDN;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.util.regex.Pattern.CASE_INSENSITIVE;

class WhatwgCanonicalizer implements Canonicalizer {
    private static final ByteString SLASH = new ByteString("/");
    private static final ByteString TWO_SLASHES = new ByteString("//");
    private static final Pattern SPECIAL_PATH_SEGMENT_REGEX = Pattern.compile("(?:([.]|%2e)([.]|%2e)?|[^/\\\\]*)(?:[/\\\\]|\\Z)", CASE_INSENSITIVE);
    private static final Pattern NONSPECIAL_PATH_SEGMENT_REGEX = Pattern.compile("(?:([.]|%2e)([.]|%2e)?|[^/]*)(?:/|\\Z)", CASE_INSENSITIVE);
    private static final Pattern PCT2D_REGEX = Pattern.compile("%2e", CASE_INSENSITIVE);
    /*
     * > The simple encode set are C0 controls and all code points greater than
     * > U+007E."
     * > The default encode set is the simple encode set and code points U+0020,
     * > '"', "#", "<", ">", "?", "`", "{", and "}".
     */
    private static final Pattern DEFAULT_ENCODE_REGEX = Pattern.compile("[\\x00-\\x20\\x7f-\\xff\"#<>?`{}]");
    private static final Pattern TAB_AND_NEWLINE_REGEX = Pattern.compile("[\\x09\\x0a\\x0d]");

    static ByteString removeTabsAndNewlines(ByteString s) {
        return s.replaceAll(TAB_AND_NEWLINE_REGEX, ByteString.EMPTY);
    }

    void removeLeadingTrailingJunk(ParsedUrl url) {
        url.setLeadingJunk(ByteString.EMPTY);
        url.setTrailingJunk(ByteString.EMPTY);
    }

    void removeTabsAndNewlines(ParsedUrl url) {
        url.setLeadingJunk(removeTabsAndNewlines(url.getLeadingJunk()));
        url.setScheme(removeTabsAndNewlines(url.getScheme()));
        url.setColonAfterScheme(removeTabsAndNewlines(url.getColonAfterScheme()));
        url.setSlashes(removeTabsAndNewlines(url.getSlashes()));
        url.setUsername(removeTabsAndNewlines(url.getUsername()));
        url.setColonBeforePassword(removeTabsAndNewlines(url.getColonBeforePassword()));
        url.setPassword(removeTabsAndNewlines(url.getPassword()));
        url.setAtSign(removeTabsAndNewlines(url.getAtSign()));
        url.setHost(removeTabsAndNewlines(url.getHost()));
        url.setColonBeforePort(removeTabsAndNewlines(url.getColonBeforePort()));
        url.setPort(removeTabsAndNewlines(url.getPort()));
        url.setPath(removeTabsAndNewlines(url.getPath()));
        url.setQuestionMark(removeTabsAndNewlines(url.getQuestionMark()));
        url.setQuery(removeTabsAndNewlines(url.getQuery()));
        url.setHashSign(removeTabsAndNewlines(url.getHashSign()));
        url.setFragment(removeTabsAndNewlines(url.getFragment()));
        url.setTrailingJunk(removeTabsAndNewlines(url.getTrailingJunk()));
    }

    void lowercaseScheme(ParsedUrl url) {
        url.setScheme(url.getScheme().asciiLowerCase());
    }

    void fixBackslashes(ParsedUrl url) {
        if (ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme().toString())) {
            url.setSlashes(url.getSlashes().replace((byte) '\\', (byte) '/'));
            ByteString path = url.getPath();
            if (!path.isEmpty()) {
                char c = path.charAt(0);
                if (c == '/' || c == '\\') {
                    url.setPath(path.replace((byte) '\\', (byte) '/'));
                }
            }
        }
    }

    static ByteString resolvePathDots(ByteString path, boolean special) {
        if (!path.isEmpty() && (path.charAt(0) == '/' || (special && path.charAt(0) == '\\'))) {
            ByteStringBuilder buf = new ByteStringBuilder(path.length());
            buf.append(path.charAt(0));
            Deque<Integer> segmentOffsets = new ArrayDeque<>();
            Matcher m = (special ? SPECIAL_PATH_SEGMENT_REGEX : NONSPECIAL_PATH_SEGMENT_REGEX).matcher(path);
            m.region(1, path.length());
            while (m.lookingAt()) {
                if (m.start(2) != -1) {
                    // "../" => pop last segment
                    buf.setLength(segmentOffsets.isEmpty() ? 1 : segmentOffsets.pop());
                } else if (m.start(1) != -1) {
                    // "./" => do nothing
                } else {
                    // push new segment
                    segmentOffsets.push(buf.length());
                    buf.append(path, m.start(), m.end());
                }
                if (m.end() == path.length()) {
                    break;
                }
                m.region(m.end(), path.length());
            }
            return buf.toByteString();
        } else {
            return path;
        }
    }

    void normalizePathDots(ParsedUrl url) {
        url.setPath(resolvePathDots(url.getPath(), ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme().toString())));
    }

    void decodePath2e(ParsedUrl url) {
        url.setPath(url.getPath().replaceAll(PCT2D_REGEX, "."));
    }

    void pctEncodePath(ParsedUrl url) {
        ByteStringBuilder buf = new ByteStringBuilder(url.getPath().length());
        Matcher m = DEFAULT_ENCODE_REGEX.matcher(url.getPath());
        int pos = 0;
        while (m.find()) {
            buf.append(url.getPath(), pos, m.start());
            buf.append('%');
            int b = (url.getPath().charAt(m.start())) & 0xff;
            buf.append(Character.toUpperCase(Character.forDigit(b >> 4, 16)));
            buf.append(Character.toUpperCase(Character.forDigit(b & 0xf, 16)));
            pos = m.end();
        }
        buf.append(url.getPath(), pos, url.getPath().length());
        url.setPath(buf.toByteString());
    }

    void emptyPathToSlash(ParsedUrl url) {
        if (url.getPath().isEmpty() && !url.getHost().isEmpty()) {
            url.setPath(SLASH);
        }
    }

    void elideDefaultPort(ParsedUrl url) {
        if (hasDefaultPort(url)) {
            url.setColonBeforePort(ByteString.EMPTY);
            url.setPort(ByteString.EMPTY);
        }
    }

    private boolean hasDefaultPort(ParsedUrl url) {
        switch ((int)CharSequences.parseLong(url.getPort())) {
            case 21:
                return url.getScheme().equalsIgnoreCase("ftp");
            case 70:
                return url.getScheme().equalsIgnoreCase("gopher");
            case 80:
                return url.getScheme().equalsIgnoreCase("http") || url.getScheme().equalsIgnoreCase("ws");
            case 443:
                return url.getScheme().equalsIgnoreCase("https") || url.getScheme().equalsIgnoreCase("wss");
        }
        return false;
    }

    static ByteString normalizeIpAddress(ByteString host) {
        long ipv4 = IpAddresses.parseIpv4(host);
        if (ipv4 != -1) {
            return new ByteString(IpAddresses.formatIpv4(ipv4));
        }
        return host;
    }

    public static void normalizeIpAddress(ParsedUrl url) {
        url.setHost(normalizeIpAddress(url.getHost()));
    }

    public static void elideAtSignForEmptyUserinfo(ParsedUrl url) {
        if (url.getUsername().isEmpty()
                && url.getColonBeforePassword().isEmpty()
                && url.getPassword().isEmpty()) {
            url.setAtSign(ByteString.EMPTY);
        }
    }

    /**
     * path "a/b/c" => "/a/b/c" if scheme is special
     */
    public static void leadingSlash(ParsedUrl url) {
        ByteString path = url.getPath();
        if (ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme().toString())
                && (path.isEmpty() || path.charAt(0) != '/')) {
            ByteStringBuilder b = new ByteStringBuilder(path.length() + 1);
            b.append('/');
            b.append(path);
            url.setPath(b.toByteString());
        }
    }

    public static void twoSlashes(ParsedUrl url) {
        if (!url.getSlashes().isEmpty() || ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme().toString())) {
            url.setSlashes(TWO_SLASHES);
        }
    }

    public static void punycode(ParsedUrl url) {
        // TODO: IDNA2008? https://bugs.openjdk.java.net/browse/JDK-6988055
        String ascii = IDN.toASCII(url.getHost().toString(), IDN.ALLOW_UNASSIGNED);
        url.setHost(new ByteString(ascii));
    }

    public void canonicalize(ParsedUrl url) {
        removeLeadingTrailingJunk(url);
        removeTabsAndNewlines(url);
        lowercaseScheme(url);
        fixBackslashes(url);
        normalizePathDots(url);
        decodePath2e(url);
        pctEncodePath(url);
        normalizeIpAddress(url);
        emptyPathToSlash(url);
        elideDefaultPort(url);
        elideAtSignForEmptyUserinfo(url);
        leadingSlash(url);
        twoSlashes(url);
        punycode(url);
    }
}
