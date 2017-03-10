/*
 * W3cTestDataTest.java - verify against the w3c's url parser test data
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

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class W3cTestDataTest {

    private static Gson gson = new Gson();
    
    @Parameter
    public TestData test;

    @Parameters(name = "{index} {0}")
    public static List<TestData> testData() throws IOException {
        List<TestData> tests = new ArrayList<>();
        try (InputStream stream = W3cTestDataTest.class.getResourceAsStream("/urltestdata.json")) {
            JsonReader reader = new JsonReader(new InputStreamReader(stream, StandardCharsets.UTF_8));
            reader.beginArray();
            while (reader.hasNext()) {
                // skip comments
                if (reader.peek() == JsonToken.STRING) {
                    reader.nextString();
                    continue;
                }

                TestData test = gson.fromJson(reader, TestData.class);

                if (isAbsoluteUrlTest(test)) {
                    tests.add(test);
                }
            }
            reader.endArray();
        }
        return tests;
    }

    private static boolean isAbsoluteUrlTest(TestData test) {
        return test.base.equals("about:blank") && test.href != null && !test.href.startsWith("about:");
    }

    @Test
    public void test() throws IOException {
        ParsedUrl url = ParsedUrl.parseUrl(test.input);
        Canonicalizer.WHATWG.canonicalize(url);

        assertEquals("scheme of " + test.input, test.protocol, url.getScheme().toString() + url.getColonAfterScheme().toString());
        assertEquals("username of " + test.input, test.username, url.getUsername().toString());
        assertEquals("password of " + test.input, test.password, url.getPassword().toString());
        assertEquals("hostPort of " + test.input, test.host, url.hostPort().toString());
        assertEquals("host of " + test.input, test.hostname, url.getHost().toString());
        assertEquals("username of " + test.input, test.username, url.getUsername().toString());
        assertEquals("path of " + test.input, test.pathname, url.getPath().toString());
        assertEquals("query of " + test.input, test.search,
                url.getQuery().isEmpty() ? "" : url.getQuestionMark().toString() + url.getQuery().toString());
        assertEquals("fragment of " + test.input, test.hash, url.getFragment().isEmpty() ? "" : (url.getHashSign().toString() + url.getFragment().toString()));
        assertEquals("href of " + test.input, test.href, url.toString());
    }

    public static class TestData {
        public String input;
        public String base;
        public String href;
        public String origin;
        public String protocol;
        public String username;
        public String password;
        public String host;
        public String hostname;
        public String port;
        public String pathname;
        public String search;
        public String hash;

        public String toString() {
            return input;
        }
    }
}