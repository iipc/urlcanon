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

import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.util.regex.Pattern.CASE_INSENSITIVE;
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

    private final static Pattern PATHISH_REGEX = Pattern.compile(("" +
            "(?<slashes> [/\\\\]* )" +
            "(?<authority> [^/\\\\]* )" +
            "(?<path> [/\\\\] .* )?"
    ).replace(" ", ""), DOTALL);

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

    private final static Pattern FILE_SCHEME_WITH_SPACES_AND_TABS = Pattern.compile(
            "[ \\t]*f[ \\t]*i[ \\t]*l[ \\t]*e[ \\t]*", CASE_INSENSITIVE);

    private ByteString leadingJunk;
    private ByteString trailingJunk;
    private ByteString scheme;
    private ByteString colonAfterScheme;
    private ByteString questionMark;
    private ByteString query;
    private ByteString hashSign;
    private ByteString fragment;
    private ByteString slashes;
    private ByteString path;
    private ByteString username;
    private ByteString colonBeforePassword;
    private ByteString password;
    private ByteString atSign;
    private ByteString ip6;
    private ByteString ip4;
    private ByteString domain;
    private ByteString colonBeforePort;
    private ByteString port;

    //-------------------------------------------------------------------------
    //region URL Parsing
    //-------------------------------------------------------------------------

    private ParsedUrl() {
    }

    public static ParsedUrl parse(String s) {
        return parse(new ByteString(s));
    }

    public static ParsedUrl parse(byte[] bytes) {
        return parse(new ByteString(bytes));
    }

    public static ParsedUrl parse(ByteString input) {
        ParsedUrl url = new ParsedUrl();

        // "leading and trailing C0 controls and space"
        Matcher m = LEADING_JUNK_REGEX.matcher(input);
        if (m.matches()) {
            url.leadingJunk = group(input, m, 1);
            input = group(input, m, 2);
        } else {
            url.leadingJunk = ByteString.EMPTY;
        }

        m = TRAILING_JUNK_REGEX.matcher(input);
        if (m.matches()) {
            url.trailingJunk = group(input, m, 2);
            input = group(input, m, 1);
        } else {
            url.trailingJunk = ByteString.EMPTY;
        }

        // parse url
        m = URL_REGEX.matcher(input);
        if (m.matches()) {
            url.scheme = group(input, m, "scheme");
            url.colonAfterScheme = group(input, m, "colonAfterScheme");
            url.questionMark = group(input, m, "questionMark");
            url.query = group(input, m, "query");
            url.hashSign = group(input, m, "hashSign");
            url.fragment = group(input, m, "fragment");
        } else {
            throw new AssertionError("URL_REGEX didn't match");
        }

        // we parse the authority + path into "pathish" initially so that we can
        // correctly handle file: urls
        ByteString pathish = group(input, m, "pathish");
        if (!pathish.isEmpty() && (pathish.charAt(0) == '/' || pathish.charAt(0) == '\\')) {
            m = PATHISH_REGEX.matcher(pathish);
            if (!m.matches()) {
                throw new AssertionError("PATHISH_REGEX didn't match");
            }

            ByteString slashes = group(pathish, m, "slashes");
            ByteString authority = group(pathish, m, "authority");
            ByteString path = group(pathish, m, "path");

            if (slashes.length() >= 3 && FILE_SCHEME_WITH_SPACES_AND_TABS.matcher(url.scheme).matches()) {
                // special case file URLs with triple slash and no authority
                // "file:///foo/bar.html" => {slashes: "//", authority: "", path: "/foo/bar.html}
                url.slashes = slashes.subSequence(0, 2);
                url.path = new ByteStringBuilder((slashes.length() - 2) + authority.length() + path.length())
                        .append(slashes, 2, slashes.length())
                        .append(authority)
                        .append(path)
                        .toByteString();
                authority = ByteString.EMPTY;
            } else {
                url.slashes = slashes;
                url.path = path;
            }

            // parse the authority
            m = AUTHORITY_REGEX.matcher(authority);
            if (m.matches()) {
                url.username = group(authority, m, "username");
                url.colonBeforePassword = group(authority, m, "colonBeforePassword");
                url.password = group(authority, m, "password");
                url.atSign = group(authority, m, "atSign");
                url.ip6 = group(authority, m, "ip6");
                url.ip4 = group(authority, m, "ip4");
                url.domain = group(authority, m, "domain");
                url.colonBeforePort = group(authority, m, "colonBeforePort");
                url.port = group(authority, m, "port");
            } else {
                throw new AssertionError("AUTHORITY_REGEX didn't match");
            }
        } else {
            // pathish doesn't start with / so it's an opaque thing
            url.path = pathish;
            url.slashes = ByteString.EMPTY;
            url.username = ByteString.EMPTY;
            url.colonBeforePassword = ByteString.EMPTY;
            url.password = ByteString.EMPTY;
            url.atSign = ByteString.EMPTY;
            url.ip6 = ByteString.EMPTY;
            url.ip4 = ByteString.EMPTY;
            url.domain = ByteString.EMPTY;
            url.colonBeforePort = ByteString.EMPTY;
            url.port = ByteString.EMPTY;
        }
        return url;
    }

    private static ByteString group(ByteString input, Matcher matcher, int group) {
        int start = matcher.start(group);
        if (start == -1) {
            return ByteString.EMPTY;
        } else {
            return input.subSequence(start, matcher.end(group));
        }
    }

    private static ByteString group(ByteString input, Matcher matcher, String group) {
        int start = matcher.start(group);
        if (start == -1) {
            return ByteString.EMPTY;
        } else {
            return input.subSequence(start, matcher.end(group));
        }
    }

    //-------------------------------------------------------------------------
    //endregion
    //-------------------------------------------------------------------------

    //-------------------------------------------------------------------------
    //region URL Formatting
    //-------------------------------------------------------------------------

    public byte[] toByteArray() {
        return buildUrl().toByteArray();
    }

    public ByteString toByteString() {
        return buildUrl().toByteString();
    }

    public String toString() {
        return buildUrl().toString();
    }

    private ByteStringBuilder buildUrl() {
        ByteString host = host();
        ByteStringBuilder builder = new ByteStringBuilder(leadingJunk.length() + scheme.length() + colonAfterScheme.length()
                + slashes.length() + username.length() + colonBeforePassword.length() + password.length()
                + atSign.length() + host.length() + colonBeforePort.length() + port.length() + path.length()
                + questionMark.length() + query.length() + hashSign.length()
                + fragment.length() + trailingJunk.length());
        builder.append(leadingJunk);
        builder.append(scheme);
        builder.append(colonAfterScheme);
        builder.append(slashes);
        builder.append(username);
        builder.append(colonBeforePassword);
        builder.append(password);
        builder.append(atSign);
        builder.append(host);
        builder.append(colonBeforePort);
        builder.append(port);
        builder.append(path);
        builder.append(questionMark);
        builder.append(query);
        builder.append(hashSign);
        builder.append(fragment);
        builder.append(trailingJunk);
        return builder;
    }

    //-------------------------------------------------------------------------
    //endregion
    //-------------------------------------------------------------------------

    //-------------------------------------------------------------------------
    //region Accessors: Calculated
    //-------------------------------------------------------------------------

    public ByteString host() {
        if (!ip6.isEmpty()) {
            return ip6;
        } else if (!ip4.isEmpty()) {
            return ip4;
        } else {
            return domain;
        }
    }

    ByteString hostPort() {
        ByteString host = host();
        ByteStringBuilder builder = new ByteStringBuilder(host.length() + colonBeforePort.length() + port.length());
        builder.append(host);
        builder.append(colonBeforePort);
        builder.append(port);
        return builder.toByteString();
    }

    //-------------------------------------------------------------------------
    //endregion
    //-------------------------------------------------------------------------

    //-------------------------------------------------------------------------
    //region Accessors: Simple
    //-------------------------------------------------------------------------

    public ByteString getLeadingJunk() {
        return leadingJunk;
    }

    public void setLeadingJunk(ByteString leadingJunk) {
        this.leadingJunk = Objects.requireNonNull(leadingJunk);
    }

    public ByteString getTrailingJunk() {
        return trailingJunk;
    }

    public void setTrailingJunk(ByteString trailingJunk) {
        this.trailingJunk = Objects.requireNonNull(trailingJunk);
    }

    public ByteString getScheme() {
        return scheme;
    }

    public void setScheme(ByteString scheme) {
        this.scheme = Objects.requireNonNull(scheme);
    }

    public ByteString getColonAfterScheme() {
        return colonAfterScheme;
    }

    public void setColonAfterScheme(ByteString colonAfterScheme) {
        this.colonAfterScheme = Objects.requireNonNull(colonAfterScheme);
    }

    public ByteString getQuestionMark() {
        return questionMark;
    }

    public void setQuestionMark(ByteString questionMark) {
        this.questionMark = Objects.requireNonNull(questionMark);
    }

    public ByteString getQuery() {
        return query;
    }

    public void setQuery(ByteString query) {
        this.query = Objects.requireNonNull(query);
    }

    public ByteString getHashSign() {
        return hashSign;
    }

    public void setHashSign(ByteString hashSign) {
        this.hashSign = Objects.requireNonNull(hashSign);
    }

    public ByteString getFragment() {
        return fragment;
    }

    public void setFragment(ByteString fragment) {
        this.fragment = Objects.requireNonNull(fragment);
    }

    public ByteString getSlashes() {
        return slashes;
    }

    public void setSlashes(ByteString slashes) {
        this.slashes = Objects.requireNonNull(slashes);
    }

    public ByteString getPath() {
        return path;
    }

    public void setPath(ByteString path) {
        this.path = Objects.requireNonNull(path);
    }

    public ByteString getUsername() {
        return username;
    }

    public void setUsername(ByteString username) {
        this.username = Objects.requireNonNull(username);
    }

    public ByteString getColonBeforePassword() {
        return colonBeforePassword;
    }

    public void setColonBeforePassword(ByteString colonBeforePassword) {
        this.colonBeforePassword = Objects.requireNonNull(colonBeforePassword);
    }

    public ByteString getPassword() {
        return password;
    }

    public void setPassword(ByteString password) {
        this.password = Objects.requireNonNull(password);
    }

    public ByteString getAtSign() {
        return atSign;
    }

    public void setAtSign(ByteString atSign) {
        this.atSign = Objects.requireNonNull(atSign);
    }

    public ByteString getIp6() {
        return ip6;
    }

    public void setIp6(ByteString ip6) {
        this.ip6 = Objects.requireNonNull(ip6);
    }

    public ByteString getIp4() {
        return ip4;
    }

    public void setIp4(ByteString ip4) {
        this.ip4 = Objects.requireNonNull(ip4);
    }

    public ByteString getDomain() {
        return domain;
    }

    public void setDomain(ByteString domain) {
        this.domain = Objects.requireNonNull(domain);
    }

    public ByteString getColonBeforePort() {
        return colonBeforePort;
    }

    public void setColonBeforePort(ByteString colonBeforePort) {
        this.colonBeforePort = Objects.requireNonNull(colonBeforePort);
    }

    public ByteString getPort() {
        return port;
    }

    public void setPort(ByteString port) {
        this.port = Objects.requireNonNull(port);
    }

    //-------------------------------------------------------------------------
    //endregion
    //-------------------------------------------------------------------------
}
