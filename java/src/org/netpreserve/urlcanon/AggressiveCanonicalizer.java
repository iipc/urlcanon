/*
 * AggressiveCanonicalizer.java - aggressive url canonicalizer
 *
 * Copyright (C) 2017 National Library of Australia
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

import java.util.regex.Pattern;

/**
 * For fuzzyier matching. Similar to the rules Wayback uses.
 *
 * Does everything semantic does and then:
 * - changes https scheme to http (other schemes like ftp are unaffected)
 * - removes www from hostname
 * - lowercases path and query
 * - strips common session ids from path and query
 */
public class AggressiveCanonicalizer implements Canonicalizer {
    @Override
    public void canonicalize(ParsedUrl url) {
        Canonicalizer.SEMANTIC.canonicalize(url);
        httpsToHttp(url);
        stripWww(url);
        lowercasePath(url);
        lowercaseQuery(url);
        stripSessionIdsFromQuery(url);
        stripSessionIdsFromPath(url);
    }

    static void httpsToHttp(ParsedUrl url) {
        if (url.getScheme().equalsIgnoreCase("https")) {
            url.setScheme(new ByteString("http"));
        }
    }

    private static final Pattern WWW_RE = Pattern.compile("^www[0-9]*\\.");

    static void stripWww(ParsedUrl url) {
        url.setHost(url.getHost().replaceAll(WWW_RE, ""));
    }

    static void lowercasePath(ParsedUrl url) {
        url.setPath(url.getPath().asciiLowerCase());
    }

    static void lowercaseQuery(ParsedUrl url) {
        url.setQuery(url.getQuery().asciiLowerCase());
    }

    private static final Pattern QUERY_SESSIONID_RE = Pattern.compile(
            "(?i)(?<=&|^)(?:" +
                    "jsessionid=[0-9a-z$]{10,}"
                    + "|sessionid=[0-9a-z]{16,}"
                    + "|phpsessid=[0-9a-z]{16,}"
                    + "|sid=[0-9a-z]{16,}"
                    + "|aspsessionid[a-z]{8}=[0-9a-z]{16,}"
                    + "|cfid=[0-9]+&cftoken=[0-9a-z-]+"
                    + ")(?:&|$)");

    static void stripSessionIdsFromQuery(ParsedUrl url) {
        url.setQuery(url.getQuery().replaceAll(QUERY_SESSIONID_RE, ""));
    }

    private static final Pattern ASPX_SUFFIX_RE = Pattern.compile(".*\\.aspx$");
    private static final Pattern ASPX_PATH_SESSIONID_RE = Pattern.compile(
            "(?<=/)\\([0-9a-z]{24}\\)/|" +
            "(?<=/)(?:\\((?:[a-z]\\([0-9a-z]{24}\\))+\\)/)");
    private static final Pattern PATH_SESSIONID_RE = Pattern.compile(";jsessionid=[0-9a-z]{32}$");

    static void stripSessionIdsFromPath(ParsedUrl url) {
        ByteString path = url.getPath();
        if (ASPX_SUFFIX_RE.matcher(path).matches()) {
            path = path.replaceAll(ASPX_PATH_SESSIONID_RE, "");
        }
        path = path.replaceAll(PATH_SESSIONID_RE, "");
        url.setPath(path);
    }
}
