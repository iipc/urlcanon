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

package org.netpreserve.urlcanon;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class ParsedUrl {
    final static Map<String,Integer> SPECIAL_SCHEMES = initSpecialSchemes();

    private static Map<String, Integer> initSpecialSchemes() {
        Map<String,Integer> map = new HashMap<>();
        map.put("ftp", 21);
        map.put("gopher", 70);
        map.put("http", 80);
        map.put("https", 443);
        map.put("ws", 80);
        map.put("wss", 443);
        map.put("file", null);
        return map;
    }

    private String leadingJunk;
    private String trailingJunk;
    private String scheme;
    private String colonAfterScheme;
    private String questionMark;
    private String query;
    private String hashSign;
    private String fragment;
    private String slashes;
    private String path;
    private String username;
    private String colonBeforePassword;
    private String password;
    private String atSign;
    private String host;
    private String colonBeforePort;
    private String port;

    //-------------------------------------------------------------------------
    //region URL Parsing
    //-------------------------------------------------------------------------

    ParsedUrl() {
    }

    private ParsedUrl(ParsedUrl base, ParsedUrl relative) {
        leadingJunk = relative.leadingJunk;
        trailingJunk = relative.trailingJunk;
        scheme = relative.scheme;
        colonAfterScheme = relative.colonAfterScheme;
        questionMark = relative.questionMark;
        query = relative.query;
        hashSign = relative.hashSign;
        fragment = relative.fragment;
        slashes = relative.slashes;
        path = relative.path;
        username = relative.username;
        colonBeforePassword = relative.colonBeforePassword;
        password = relative.password;
        atSign = relative.atSign;
        host = relative.host;
        colonBeforePort = relative.colonBeforePort;
        port = relative.port;

        if (!slashes.isEmpty()) {
            if (scheme.isEmpty()) {
                scheme = base.scheme;
            }
            return;
        }

        if (!scheme.isEmpty() && !scheme.equalsIgnoreCase(base.scheme)) {
            return;
        }

        if (scheme.isEmpty() || scheme.equalsIgnoreCase(base.scheme)) {
            scheme = base.scheme;
            colonAfterScheme = base.colonAfterScheme;
            username = base.username;
            colonBeforePassword = base.colonBeforePassword;
            password = base.password;
            atSign = base.atSign;
            host = base.host;
            colonBeforePort = base.colonBeforePort;
            port = base.port;
        }

        if (path.isEmpty() && !relative.host.isEmpty()) {
            path = relative.host;
        }

        if (path.isEmpty() || path.charAt(0) == '/') {
            return;
        }

        String dirname = base.dirname();
        StringBuilder builder = new StringBuilder(dirname.length() + path.length());
        builder.append(dirname);
        builder.append(path);
        path = builder.toString();
    }

    private String dirname() {
        for (int i = path.length() - 1; i >= 0; i--) {
            if (path.charAt(i) == '/') {
                return path.substring(0, i + 1);
            }
        }
        return "";
    }

    public static ParsedUrl parseUrl(byte[] bytes) {
        return parseUrl(new String(bytes));
    }

    public static ParsedUrl parseUrl(String input) {
        return UrlParser.parseUrl(input);
    }

    //-------------------------------------------------------------------------
    //endregion
    //-------------------------------------------------------------------------

    //-------------------------------------------------------------------------
    //region URL Formatting
    //-------------------------------------------------------------------------


    public String toString() {
        return leadingJunk
                + scheme
                + colonAfterScheme
                + slashes
                + username
                + colonBeforePassword
                + password
                + atSign
                + host
                + colonBeforePort
                + port
                + path
                + questionMark
                + query
                + hashSign
                + fragment
                + trailingJunk;
    }

    //-------------------------------------------------------------------------
    //endregion
    //-------------------------------------------------------------------------

    //-------------------------------------------------------------------------
    //region SSURT Formatting
    //-------------------------------------------------------------------------

    /**
     * Format this URL with a field order suitable for sorting.
     */
    public String ssurt() {
        String ssurtHost = ssurtHost(host);
        StringBuilder builder = new StringBuilder(leadingJunk.length() + scheme.length() + colonAfterScheme.length()
                + slashes.length() + username.length() + colonBeforePassword.length() + password.length()
                + atSign.length() + ssurtHost.length() + colonBeforePort.length() + port.length() + path.length()
                + questionMark.length() + query.length() + hashSign.length()
                + fragment.length() + trailingJunk.length());
        builder.append(leadingJunk);
        builder.append(ssurtHost);
        builder.append(slashes);
        builder.append(port);
        builder.append(colonBeforePort);
        builder.append(scheme);
        builder.append(atSign);
        builder.append(username);
        builder.append(colonBeforePassword);
        builder.append(password);
        builder.append(colonAfterScheme);
        builder.append(path);
        builder.append(questionMark);
        builder.append(query);
        builder.append(hashSign);
        builder.append(fragment);
        builder.append(trailingJunk);
        return builder.toString();
    }

    /**
     * Reverse host unless it's an IPv4 or IPv6 address.
     */
    static String ssurtHost(String host) {
        if (host.isEmpty()) {
            return host;
        } else if (host.charAt(0) == '[') {
            return host;
        } else if (IpAddresses.parseIpv4(host) != -1) {
            return host;
        } else {
            return reverseHost(host);
        }
    }

    /**
     * Reverse dotted segments. Swap commas and dots. Add a trailing comma.
     *
     * "x,y.b.c" => "c,b,x.y,"
     */
    static String reverseHost(String host) {
        StringBuilder buf = new StringBuilder(host.length() + 1);
        String nocommas = host.replace(",", ".");
        int j = host.length();
        for (int i = host.length() - 1; i >= 0; i--) {
            if (host.charAt(i) == '.') {
                buf.append(nocommas, i + 1, j);
                buf.append(',');
                j = i;
            }
        }
        buf.append(nocommas, 0, j);
        buf.append(',');
        return buf.toString();
    }

    //-------------------------------------------------------------------------
    //endregion
    //-------------------------------------------------------------------------

    //-------------------------------------------------------------------------
    //region Accessors: Calculated
    //-------------------------------------------------------------------------

    String hostPort() {
        StringBuilder builder = new StringBuilder(host.length() + colonBeforePort.length() + port.length());
        builder.append(host);
        builder.append(colonBeforePort);
        builder.append(port);
        return builder.toString();
    }

    //-------------------------------------------------------------------------
    //endregion
    //-------------------------------------------------------------------------

    //-------------------------------------------------------------------------
    //region Accessors: Simple
    //-------------------------------------------------------------------------

    public String getLeadingJunk() {
        return leadingJunk;
    }

    public void setLeadingJunk(String leadingJunk) {
        this.leadingJunk = Objects.requireNonNull(leadingJunk);
    }

    public String getTrailingJunk() {
        return trailingJunk;
    }

    public void setTrailingJunk(String trailingJunk) {
        this.trailingJunk = Objects.requireNonNull(trailingJunk);
    }

    public String getScheme() {
        return scheme;
    }

    public void setScheme(String scheme) {
        this.scheme = Objects.requireNonNull(scheme);
    }

    public String getColonAfterScheme() {
        return colonAfterScheme;
    }

    public void setColonAfterScheme(String colonAfterScheme) {
        this.colonAfterScheme = Objects.requireNonNull(colonAfterScheme);
    }

    public String getQuestionMark() {
        return questionMark;
    }

    public void setQuestionMark(String questionMark) {
        this.questionMark = Objects.requireNonNull(questionMark);
    }

    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = Objects.requireNonNull(query);
    }

    public String getHashSign() {
        return hashSign;
    }

    public void setHashSign(String hashSign) {
        this.hashSign = Objects.requireNonNull(hashSign);
    }

    public String getFragment() {
        return fragment;
    }

    public void setFragment(String fragment) {
        this.fragment = Objects.requireNonNull(fragment);
    }

    public String getSlashes() {
        return slashes;
    }

    public void setSlashes(String slashes) {
        this.slashes = Objects.requireNonNull(slashes);
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = Objects.requireNonNull(path);
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = Objects.requireNonNull(username);
    }

    public String getColonBeforePassword() {
        return colonBeforePassword;
    }

    public void setColonBeforePassword(String colonBeforePassword) {
        this.colonBeforePassword = Objects.requireNonNull(colonBeforePassword);
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = Objects.requireNonNull(password);
    }

    public String getAtSign() {
        return atSign;
    }

    public void setAtSign(String atSign) {
        this.atSign = Objects.requireNonNull(atSign);
    }

    public String getHost() {
        return host;
    }

    public void setHost(String host) {
        this.host = Objects.requireNonNull(host);
    }

    public String getColonBeforePort() {
        return colonBeforePort;
    }

    public void setColonBeforePort(String colonBeforePort) {
        this.colonBeforePort = Objects.requireNonNull(colonBeforePort);
    }

    public String getPort() {
        return port;
    }

    public void setPort(String port) {
        this.port = Objects.requireNonNull(port);
    }

    public ParsedUrl resolve(ParsedUrl relative) {
        return new ParsedUrl(this, relative);
    }

    //-------------------------------------------------------------------------
    //endregion
    //-------------------------------------------------------------------------
}
