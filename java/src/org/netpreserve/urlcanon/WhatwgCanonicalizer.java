/*
 * WhatwgCanonicalizer.java - WHATWG-compatible url canonicalizer
 * Java port of canon.py
 *
 * Copyright (C) 2016 National Library of Australia
 * Copyright (C) 2016-2017 Internet Archive
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

package org.netpreserve.urlcanon;

import java.net.IDN;
import java.nio.charset.Charset;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.nio.charset.StandardCharsets.UTF_8;
import static java.util.regex.Pattern.CASE_INSENSITIVE;

class WhatwgCanonicalizer implements Canonicalizer {
    private static final String SLASH = "/";
    private static final String TWO_SLASHES = "//";
    private static final Pattern SPECIAL_PATH_SEGMENT_REGEX = Pattern.compile("(?:([.]|%2e)([.]|%2e)?|[^/\\\\]*)(?:[/\\\\]|\\Z)", CASE_INSENSITIVE);
    private static final Pattern NONSPECIAL_PATH_SEGMENT_REGEX = Pattern.compile("(?:([.]|%2e)([.]|%2e)?|[^/]*)(?:/|\\Z)", CASE_INSENSITIVE);
    /*
     * > The C0 control percent-encode set are C0 controls and all code points
     * > greater than U+007E.
     * > The path percent-encode set is the C0 control percent-encode set and
     * > code points U+0020, '"', "#", "<", ">", "?", "`", "{", and "}".
     * > If byte is less than 0x21, greater than 0x7E, or is 0x22, 0x23, 0x3C,
     * > or 0x3E, append byte, percent encoded, to url's query.
     * > The userinfo percent-encode set is the path percent-encode set and code
     * > points "/", ":", ";", "=", "@", "[", "\", "]", "^", and "|".
     */
    private static final boolean[] C0_ENCODE = buildEncodeSet("[\\x00-\\x1f\\x7f-\\xff]");
    private static final boolean[] PATH_ENCODE = buildEncodeSet("[\\x00-\\x20\\x7f-\\xff\"#<>?`{}]");
    private static final boolean[] QUERY_ENCODE = buildEncodeSet("[\\x00-\\x20\\x22\\x23\\x3c\\x3e\\x7f-\\xff]");
    private static final boolean[] USERINFO_ENCODE = buildEncodeSet("[\\x00-\\x20\\x7f-\\xff\"#<>?`{}/:;=@\\x5b\\x5c\\x5d\\x5e\\x7c]");
    private static final boolean[] HOST_ENCODE = buildEncodeSet("[\\x00-\\x20\\x7f-\\xff]");

    private static final Pattern TAB_AND_NEWLINE_REGEX = Pattern.compile("[\\x09\\x0a\\x0d]");

    static boolean[] buildEncodeSet(String regex) {
        boolean[] array = new boolean[256];
        Pattern pattern = Pattern.compile(regex);
        for (int i = 0; i < 256; i++) {
            array[i] = pattern.matcher(Character.toString((char) i)).matches();
        }
        return array;
    }

    static String removeTabsAndNewlines(String s) {
        return TAB_AND_NEWLINE_REGEX.matcher(s).replaceAll("");
    }

    static void removeLeadingTrailingJunk(ParsedUrl url) {
        url.setLeadingJunk("");
        url.setTrailingJunk("");
    }

    static void removeTabsAndNewlines(ParsedUrl url) {
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

    static void lowercaseScheme(ParsedUrl url) {
        url.setScheme(url.getScheme().toLowerCase(Locale.US));
    }

    static void fixBackslashes(ParsedUrl url) {
        if (ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme())) {
            url.setSlashes(url.getSlashes().replace('\\', '/'));
            String path = url.getPath();
            if (!path.isEmpty()) {
                char c = path.charAt(0);
                if (c == '/' || c == '\\') {
                    url.setPath(path.replace('\\',  '/'));
                }
            }
        }
    }

    static String resolvePathDots(String path, boolean special) {
        if (!path.isEmpty() && (path.charAt(0) == '/' || (special && path.charAt(0) == '\\'))) {
            StringBuilder buf = new StringBuilder(path.length());
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
            return buf.toString();
        } else {
            return path;
        }
    }

    static void normalizePathDots(ParsedUrl url) {
        url.setPath(resolvePathDots(url.getPath(), ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme())));
    }

    public static String pctDecode(String str, Charset charset) {
        StringBuilder sb = new StringBuilder(str.length());
        byte[] buf = new byte[16];
        int len = 0;
        int i = 0;
        while (i < str.length()) {
            while (true) {
                if (i + 3 > str.length()) break;
                if (str.charAt(i) != '%') break;
                int digit1 = Character.digit(str.charAt(i + 1), 16);
                if (digit1 == -1) break;
                int digit2 = Character.digit(str.charAt(i + 2), 16);
                if (digit2 == -1) break;
                buf[len++] = (byte) (digit1 << 4 | digit2);
                i += 3;
            }
            if (len > 0) {
                sb.append(new String(buf, 0, len, charset));
                len = 0;
            } else {
                sb.append(str.charAt(i));
                i++;
            }
        }
        return sb.toString();
    }

    private static boolean isHexDigit(char c) {
        return (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F') || (c >= '0' && c <= '9');
    }


    static String pctEncode(String str, boolean[] encodeSet, Charset charset) {
        StringBuilder buf = new StringBuilder(str.length());
        for (int i = 0; i < str.length();) {
            int codepoint = str.codePointAt(i);
            int len = Character.charCount(codepoint);

            if (codepoint > 0xff || encodeSet[codepoint]) {
                byte[] encoded = str.substring(i, i + len).getBytes(charset);
                for (byte b : encoded) {
                    buf.append('%');
                    buf.append(Character.toUpperCase(Character.forDigit((b & 0xff) >> 4, 16)));
                    buf.append(Character.toUpperCase(Character.forDigit(b & 0xf, 16)));
                }
            } else {
                buf.append(str, i, i + len);
            }
            i += len;
        }
        return buf.toString();
    }

    void pctEncodePath(ParsedUrl url, Charset charset) {
        boolean[] encodeSet;
        if (!url.getPath().isEmpty() && url.getPath().charAt(0) == '/'
                || ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme())) {
            encodeSet = PATH_ENCODE;
        } else {
            encodeSet = C0_ENCODE;
        }
        url.setPath(pctEncode(url.getPath(), encodeSet, charset));
    }

    void pctEncodeFragment(ParsedUrl url, Charset charset) {
        url.setFragment(pctEncode(url.getFragment(), C0_ENCODE, charset));
    }

    void pctEncodeQuery(ParsedUrl url, Charset charset) {
        url.setQuery(pctEncode(url.getQuery(), QUERY_ENCODE, charset));
    }

    static void emptyPathToSlash(ParsedUrl url) {
        if (url.getPath().isEmpty() && !url.getHost().isEmpty()
                && ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme())) {
            url.setPath(SLASH);
        }
    }

    static void elideDefaultPort(ParsedUrl url) {
        if (hasDefaultPort(url)) {
            url.setColonBeforePort("");
            url.setPort("");
        }
    }

    private static boolean hasDefaultPort(ParsedUrl url) {
        Integer defaultPort = ParsedUrl.SPECIAL_SCHEMES.get(url.getScheme());
        int port = (int) CharSequences.parseLong(url.getPort());
        return defaultPort != null && port == defaultPort.intValue();
    }

    static String normalizeIpAddress(String host) {
        if (host.startsWith("[") && host.endsWith("]")) {
            short[] ipv6 = IpAddresses.parseIpv6(host.substring(1, host.length() - 1));
            if (ipv6 == null) return host;
            return "[" + IpAddresses.formatIpv6(ipv6) + "]";
        }
        long ipv4 = IpAddresses.parseIpv4(host);
        if (ipv4 != -1) {
            return IpAddresses.formatIpv4(ipv4);
        }
        return host;
    }

    public static void normalizeIpAddress(ParsedUrl url) {
        url.setHost(normalizeIpAddress(url.getHost()));
    }

    public static void cleanUpUserinfo(ParsedUrl url) {
        if (url.getPassword().isEmpty()) {
            url.setColonBeforePassword("");
            if (url.getUsername().isEmpty()) {
                url.setAtSign("");
            }
        }
        if (url.getUsername().isEmpty()
                && url.getColonBeforePassword().isEmpty()
                && url.getPassword().isEmpty()) {
            url.setAtSign("");
        }
    }

    /**
     * path "a/b/c" => "/a/b/c" if scheme is special
     */
    public static void leadingSlash(ParsedUrl url) {
        String path = url.getPath();
        if (ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme())
                && (path.isEmpty() || path.charAt(0) != '/')) {
            StringBuilder b = new StringBuilder(path.length() + 1);
            b.append('/');
            b.append(path);
            url.setPath(b.toString());
        }
    }

    public static void twoSlashes(ParsedUrl url) {
        if (!url.getSlashes().isEmpty() || ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme())) {
            url.setSlashes(TWO_SLASHES);
        }
    }

    public static void punycodeSpecialHost(ParsedUrl url, Charset charset) {
        if (ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme())) {
            String host = url.getHost();
            if (charset != UTF_8) {
                // XXX: hack to match python behaviour, attempt to interpret as utf8 for punycoding
                host = new String(host.getBytes(charset), UTF_8);
                if (host.contains("\ufffd")) { // contains non-utf8 junk
                    return; // leave unmodified
                }
            }
            try {
                String ascii = Idn.load().toAscii(host);
                url.setHost(ascii.toLowerCase());
            } catch (IllegalArgumentException e) {
                // leave unmodified
            }
        }
    }

    static void pctEncodeHost(ParsedUrl url, Charset charset) {
        url.setHost(pctEncode(url.getHost(), HOST_ENCODE, charset));
    }

    static void pctDecodeHost(ParsedUrl url, Charset charset) {
        if (ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme())) {
            url.setHost(pctDecode(url.getHost(), charset));
        }
    }

    static void pctEncodeUserinfo(ParsedUrl url, Charset charset) {
        url.setUsername(pctEncode(url.getUsername(), USERINFO_ENCODE, charset));
        url.setPassword(pctEncode(url.getPassword(), USERINFO_ENCODE, charset));
    }

    @Override
    public void canonicalize(ParsedUrl url) {
        canonicalize(url, UTF_8);
    }

    public void canonicalize(ParsedUrl url, Charset charset) {
        removeLeadingTrailingJunk(url);
        removeTabsAndNewlines(url);
        lowercaseScheme(url);
        elideDefaultPort(url);
        cleanUpUserinfo(url);
        twoSlashes(url);
        pctDecodeHost(url, charset);
        normalizeIpAddress(url);
        punycodeSpecialHost(url, charset);
        pctEncodeHost(url, charset);
        fixBackslashes(url);
        pctEncodePath(url, charset);
        elideDefaultPort(url);
        leadingSlash(url);
        normalizePathDots(url);
        emptyPathToSlash(url);
        pctEncodeUserinfo(url, charset);
        pctEncodeQuery(url, charset);
        pctEncodeFragment(url, charset);
    }
}
