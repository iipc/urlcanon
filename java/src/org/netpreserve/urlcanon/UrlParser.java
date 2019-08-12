package org.netpreserve.urlcanon;

class UrlParser {
    static ParsedUrl parseUrl(String s) {
        ParsedUrl url = new ParsedUrl();
        int pos = 0;
        int len = s.length();

        // leading control chars and spaces
        while (pos < len && s.charAt(pos) <= 0x20) pos++;
        url.setLeadingJunk(s.substring(0, pos));

        // trailing control chars and spaces
        while (pos < len && s.charAt(len - 1) <= 0x20) len--;
        url.setTrailingJunk(s.substring(len));

        // scheme [a-zA-Z] [^:]* :
        if (pos < len && ((s.charAt(pos) >= 'a' && s.charAt(pos) <= 'z') || (s.charAt(pos) >= 'A' && s.charAt(pos) <= 'Z'))) {
            int schemeStart = pos;
            while (pos < len && s.charAt(pos) != ':') pos++;

            if (pos < len && s.charAt(pos) == ':') {
                url.setScheme(s.substring(schemeStart, pos));
                url.setColonAfterScheme(":");
                pos++;
            } else { // no colon
                pos = schemeStart; // backtrack
                url.setScheme("");
                url.setColonAfterScheme("");
            }
        } else {
            url.setScheme("");
            url.setColonAfterScheme("");
        }

        // pathish [^?#]*
        int pathishStart = pos;
        while (pos < len && s.charAt(pos) != '#' && s.charAt(pos) != '?') pos++;
        parsePathish(url, s, pathishStart, pos);

        // query string \? [^#]*
        if (pos < len && s.charAt(pos) == '?') {
            pos++;
            url.setQuestionMark("?");
            int queryStart = pos;
            while (pos < len && s.charAt(pos) != '#') pos++;
            url.setQuery(s.substring(queryStart, pos));
        } else {
            url.setQuestionMark("");
            url.setQuery("");
        }

        // fragment # .*
        if (pos < len && s.charAt(pos) == '#') {
            pos++;
            url.setHashSign("#");
            url.setFragment(s.substring(pos, len));
        } else {
            url.setHashSign("");
            url.setFragment("");
        }

        return url;
    }

    static void parsePathish(ParsedUrl url, String s, int pos, int end) {
        String cleanScheme = removeTabsAndNewlinesAndLowercase(url.getScheme());
        boolean isSpecial = ParsedUrl.SPECIAL_SCHEMES.containsKey(cleanScheme);
        boolean isFile = cleanScheme.equals("file");
        int slashCount = 0;

        // slashes [\\/\r\n\y]*
        int slashesStart = pos;
        loop: while (pos < end) {
            switch (s.charAt(pos)) {
                case '\\':
                    if (!isSpecial) { // special schemes allow backslashes
                        break loop;
                    }
                    // fallthrough
                case '/':
                    if (isFile || !isSpecial) {
                        if (slashCount == 2) break loop;
                        slashCount++;
                    }
                    // fallthrough
                case '\r':
                case '\n':
                case '\t':
                    pos++;
                    continue;
                default:
                    break loop;
            }
        }
        url.setSlashes(s.substring(slashesStart, pos));

        if (isFile) {
            if (slashCount != 2) {
                // no host? treat entire pathish as path
                url.setPath(s.substring(slashesStart, end));
                url.setSlashes("");
                url.setUsername("");
                url.setColonBeforePassword("");
                url.setPassword("");
                url.setAtSign("");
                url.setHost("");
                url.setColonBeforePort("");
                url.setPort("");
                return;
            }

            // host [^/\\]*
            int startOfHost = pos;
            while (pos < end && s.charAt(pos) != '/' && s.charAt(pos) != '\\') pos++;
            url.setHost(s.substring(startOfHost, pos));
            url.setUsername("");
            url.setColonBeforePassword("");
            url.setPassword("");
            url.setAtSign("");
            url.setColonBeforePort("");
            url.setPort("");
        } else if (isSpecial) {

            // authority [^/\\]*
            int startOfAuthority = pos;
            while (pos < end && s.charAt(pos) != '/' && s.charAt(pos) != '\\') pos++;
            parseAuthority(url, s, startOfAuthority, pos);

        } else { // non special scheme
            if (!removeTabsAndNewlinesAndLowercase(url.getSlashes()).equals("//")) {
                // no double-slash? treat as opaque
                url.setPath(s.substring(slashesStart, end));
                url.setSlashes("");
                url.setUsername("");
                url.setColonBeforePassword("");
                url.setPassword("");
                url.setAtSign("");
                url.setHost("");
                url.setColonBeforePort("");
                url.setPort("");
                return;
            }

            // authority [^/]*
            int startOfAuthority = pos;
            while (pos < end && s.charAt(pos) != '/') pos++;
            parseAuthority(url, s, startOfAuthority, pos);
        }

        // path [/\\\\] .*
        url.setPath(s.substring(pos, end));
    }

    private static void parseAuthority(ParsedUrl url, String s, int pos, int end) {
        // userinfo (.*@)?
        int userinfoStart = pos;
        int userinfoEnd = -1;
        for (int i = pos; i < end; i++) {
            if (s.charAt(i) == '@') {
                userinfoEnd = i;
            }
        }
        if (userinfoEnd != -1) {
            parseUserinfo(url, s, userinfoStart, userinfoEnd);
            pos = userinfoEnd + 1;
            url.setAtSign("@");
        } else { // no userinfo
            url.setUsername("");
            url.setColonBeforePassword("");
            url.setPassword("");
            url.setAtSign("");
        }

        // maybe ipv6 host \[[^]]*\]
        int hostStart = pos;
        if (pos < end && s.charAt(pos) == '[') {
            pos++;
            while (pos < end && s.charAt(pos) != ']') pos++;
            if (pos < end && s.charAt(pos) == ']') {
                pos++;
                if (pos < end && s.charAt(pos) != ':') {
                    // backtrack
                    pos = hostStart;
                }
            }
        }

        // host [^:]*
        while (pos < end && s.charAt(pos) != ':') pos++;
        url.setHost(s.substring(hostStart, pos));

        // port :.*
        if (pos < end && s.charAt(pos) == ':') {
            pos++;
            url.setColonBeforePort(":");
            url.setPort(s.substring(pos, end));
        } else {
            url.setColonBeforePort("");
            url.setPort("");
        }
    }

    private static void parseUserinfo(ParsedUrl url, String s, int i, int end) {
        // username
        int usernameStart = i;
        while (i < end && s.charAt(i) != ':') i++;
        url.setUsername(s.substring(usernameStart, i));

        // password
        if (i < end && s.charAt(i) == ':') {
            url.setColonBeforePassword(":");
            i++;
            url.setPassword(s.substring(i, end));
        } else {
            url.setColonBeforePassword("");
            url.setPassword("");
        }
    }

    private static String removeTabsAndNewlinesAndLowercase(String s) {
        StringBuilder sb = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\t' || c == '\n' || c == '\r') continue;
            if (c >= 'A' && c <= 'Z') c += 32; // convert ascii caps to lowercase
            sb.append(c);
        }
        return sb.toString();
    }
}
