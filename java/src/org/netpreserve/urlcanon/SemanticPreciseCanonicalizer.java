/*
 * SemanticPreciseCanonicalizer.java
 *
 * Copyright (C) 2016-2017 National Library of Australia
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

import java.nio.charset.Charset;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.regex.Pattern;

import static java.nio.charset.StandardCharsets.UTF_8;
import static org.netpreserve.urlcanon.WhatwgCanonicalizer.buildEncodeSet;

/**
 * Precise semantic canonicalizer, semantic in the sense that the intention is
 * to canonicalize urls that "mean" the same thing, that you would expect to
 * load the same stuff and look the same way if you pasted them into the
 * location bar of your browser.
 *
 * Does everything WHATWG does and also some cleanup:
 * - sets default scheme http: if scheme is missing
 * - removes extraneous dots in the host
 * And these additional steps:
 * - collapses consecutive slashes in the path
 * - standardizes percent encodings so that different encodings of the same-ish
 *   thing match
 * - sorts query params
 * - removes userinfo
 */
public class SemanticPreciseCanonicalizer implements Canonicalizer {
    @Override
    public void canonicalize(ParsedUrl url) {
        canonicalize(url, UTF_8);
    }

    public void canonicalize(ParsedUrl url, Charset charset) {
        WhatwgCanonicalizer.removeLeadingTrailingJunk(url);
        defaultSchemeHttp(url);
        WhatwgCanonicalizer.removeTabsAndNewlines(url);
        WhatwgCanonicalizer.lowercaseScheme(url);
        WhatwgCanonicalizer.elideDefaultPort(url);
        WhatwgCanonicalizer.cleanUpUserinfo(url);
        WhatwgCanonicalizer.twoSlashes(url);
        pctDecodeRepeatedlyExceptQuery(url, charset);
        // TODO: reparse_host,
        WhatwgCanonicalizer.normalizeIpAddress(url);
        fixHostDots(url);
        WhatwgCanonicalizer.punycodeSpecialHost(url, charset);
        removeUserinfo(url);
        lessDumbPctEncode(url, charset);
        lessDumbPctRecodeQuery(url, charset);
        WhatwgCanonicalizer.fixBackslashes(url);
        WhatwgCanonicalizer.leadingSlash(url);
        WhatwgCanonicalizer.normalizePathDots(url);
        collapseConsecutiveSlashes(url);
        WhatwgCanonicalizer.emptyPathToSlash(url);
        alphaReorderQuery(url);

    }

    static String removeLeadingTrailingAndDuplicateChars(String s, char charToRemove) {
        if (s.indexOf(charToRemove) == -1) return s;
        StringBuilder sb = new StringBuilder();
        char prev = charToRemove; // to remove leading
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c != charToRemove || prev != charToRemove) {
                sb.append(c);
            }
            prev = c;
        }
        // remove trailing
        if (sb.charAt(sb.length() - 1) == charToRemove) {
            sb.setLength(sb.length() - 1);
        }
        return sb.toString();
    }

    private void fixHostDots(ParsedUrl url) {
        url.setHost(removeLeadingTrailingAndDuplicateChars(url.getHost(), '.'));
    }

    private static final Pattern TWO_OR_MORE_SLASHES_RE = Pattern.compile("//+");

    private void collapseConsecutiveSlashes(ParsedUrl url) {
        if (ParsedUrl.SPECIAL_SCHEMES.containsKey(url.getScheme())) {
            url.setPath(TWO_OR_MORE_SLASHES_RE.matcher(url.getPath()).replaceAll("/"));
        }
    }

    static void defaultSchemeHttp(ParsedUrl url) {
        if (url.getScheme().isEmpty()) {
            url.setScheme(new String("http"));
            url.setColonAfterScheme(new String(":"));
            if (!url.getPath().isEmpty()) {
                UrlParser.parsePathish(url, url.getPath(), 0, url.getPath().length());
            }
        }
    }

    static void pctDecodeRepeatedlyExceptQuery(ParsedUrl url, Charset charset) {
        url.setScheme(pctDecodeTokenRepeatedly(url.getScheme(), charset));
        url.setUsername(pctDecodeTokenRepeatedly(url.getUsername(), charset));
        url.setPassword(pctDecodeTokenRepeatedly(url.getPassword(), charset));
        url.setHost(pctDecodeTokenRepeatedly(url.getHost(), charset));
        url.setPort(pctDecodeTokenRepeatedly(url.getPort(), charset));
        url.setPath(pctDecodeTokenRepeatedly(url.getPath(), charset));
        url.setFragment(pctDecodeTokenRepeatedly(url.getFragment(), charset));
    }

    static String pctDecodeTokenRepeatedly(String str, Charset charset) {
        for (;;) {
            String decoded = WhatwgCanonicalizer.pctDecode(str, charset);
            if (decoded.equals(str)) {
                return decoded;
            }
            str = decoded;
        }
    }

    static void removeUserinfo(ParsedUrl url) {
        url.setUsername("");
        url.setColonBeforePassword("");
        url.setPassword("");
        url.setAtSign("");
    }

    static final boolean[] GOOGLE_PCT_ENCODE = buildEncodeSet("[\\x00-\\x20\\x7f-\\xff#%]");
    static final boolean[] LESS_DUMB_USERINFO_ENCODE = buildEncodeSet("[\\x00-\\x20\\x7f-\\xff#%:@]");
    static final boolean[] LESS_DUMB_PATH_ENCODE = buildEncodeSet("[\\x00-\\x20\\x7f-\\xff#%?]");

    static void lessDumbPctEncode(ParsedUrl url, Charset charset) {
        url.setScheme(WhatwgCanonicalizer.pctEncode(url.getScheme(), GOOGLE_PCT_ENCODE, charset));
        url.setScheme(WhatwgCanonicalizer.pctEncode(url.getScheme(), GOOGLE_PCT_ENCODE, charset));
        url.setUsername(WhatwgCanonicalizer.pctEncode(url.getUsername(), LESS_DUMB_USERINFO_ENCODE, charset));
        url.setPassword(WhatwgCanonicalizer.pctEncode(url.getPassword(), LESS_DUMB_USERINFO_ENCODE, charset));
        url.setHost(WhatwgCanonicalizer.pctEncode(url.getHost(), GOOGLE_PCT_ENCODE, charset));
        url.setPort(WhatwgCanonicalizer.pctEncode(url.getPort(), GOOGLE_PCT_ENCODE, charset));
        url.setPath(WhatwgCanonicalizer.pctEncode(url.getPath(), LESS_DUMB_PATH_ENCODE, charset));
        url.setFragment(WhatwgCanonicalizer.pctEncode(url.getFragment(), GOOGLE_PCT_ENCODE, charset));
    }

    static final boolean[] LESS_DUMB_QUERY_ENCODE = buildEncodeSet("[\\x00-\\x20\\x7f-\\xff#%&=]");

    private static String pctRecodeQueryPart(String s, Charset charset) {
        String decoded = pctDecodeTokenRepeatedly(s, charset);
        return WhatwgCanonicalizer.pctEncode(decoded, LESS_DUMB_QUERY_ENCODE, charset);
    }

    static void lessDumbPctRecodeQuery(ParsedUrl url, Charset charset) {
        String query = url.getQuery();
        if (query.isEmpty()) {
            return;
        }
        StringBuilder sb = new StringBuilder();
        int i = 0;
        while (i < query.length()) {
            int eq = query.indexOf('=', i);
            int amp = query.indexOf('&', i);
            if (amp == -1) amp = query.length();
            if (eq != -1 && eq < amp) {
                sb.append(pctRecodeQueryPart(query.substring(i, eq), charset));
                sb.append('=');
                i = eq + 1;
            }
            sb.append(pctRecodeQueryPart(query.substring(i, amp), charset));
            if (amp < query.length()) sb.append('&');
            i = amp + 1;
        }
        url.setQuery(sb.toString());
    }

    static void alphaReorderQuery(ParsedUrl url) {
        List<String> params = Arrays.asList(url.getQuery().split("&"));
        Collections.sort(params);
        url.setQuery(String.join("&", params));
    }
}
