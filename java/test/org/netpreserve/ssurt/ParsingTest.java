/*
 * ParsingTest.java - checks the parser breaks URLs into the correct fields
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

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class ParsingTest {

    private static Gson gson = new Gson();

    @Parameterized.Parameter
    public String input;

    @Parameterized.Parameter(value = 1)
    public Expected expected;

    @Parameterized.Parameters(name = "{index} {0}")
    public static List<Object[]> testData() throws IOException {
        List<Object[]> tests = new ArrayList<>();
        try (InputStream stream = W3cTestDataTest.class.getResourceAsStream("/parsing.json")) {
            JsonReader reader = new JsonReader(new InputStreamReader(stream, StandardCharsets.UTF_8));
            reader.beginObject();
            while (reader.hasNext()) {
                String input = reader.nextName();
                Expected expected = gson.fromJson(reader, Expected.class);
                tests.add(new Object[]{input, expected});
            }
            reader.endObject();
        }
        return tests;
    }

    @Test
    public void test() throws IOException {
        ParsedUrl url = ParsedUrl.parse(input);
        assertEquals("at_sign", expected.at_sign, url.getAtSign().toString());
        assertEquals("colon_after_scheme", expected.colon_after_scheme, url.getColonAfterScheme().toString());
        assertEquals("colon_before_password", expected.colon_before_password, url.getColonBeforePassword().toString());
        assertEquals("colon_before_port", expected.colon_before_port, url.getColonBeforePort().toString());
        assertEquals("fragment", expected.fragment, url.getFragment().toString());
        assertEquals("hash_sign", expected.hash_sign, url.getHashSign().toString());
        assertEquals("host", expected.host, url.getHost().toString());
        //assertEquals("ip4", expected.ip4, url.getIp4().toString());
        //assertEquals("ip6", expected.ip6, url.getIp6().toString());
        assertEquals("leading_junk", expected.leading_junk, url.getLeadingJunk().toString());
        assertEquals("password", expected.password, url.getPassword().toString());
        assertEquals("path", expected.path, url.getPath().toString());
        assertEquals("port", expected.port, url.getPort().toString());
        assertEquals("query", expected.query, url.getQuery().toString());
        assertEquals("question_mark", expected.question_mark, url.getQuestionMark().toString());
        assertEquals("scheme", expected.scheme, url.getScheme().toString());
        assertEquals("slashes", expected.slashes, url.getSlashes().toString());
        assertEquals("trailing_junk", expected.trailing_junk, url.getTrailingJunk().toString());
        assertEquals("username", expected.username, url.getUsername().toString());
    }

    public static class Expected {
        public String at_sign;
        public String colon_after_scheme;
        public String colon_before_password;
        public String colon_before_port;
        public String fragment;
        public String hash_sign;
        public String host;
        public String ip4;
        public String ip6;
        public String leading_junk;
        public String password;
        public String path;
        public String port;
        public String query;
        public String question_mark;
        public String scheme;
        public String slashes;
        public String trailing_junk;
        public String username;
    }
}
