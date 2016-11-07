/*
 * WhatwgCanonicalizerTest.java - unit tests for WhatwgCanonicalizer
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
import com.google.gson.JsonElement;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import org.junit.Ignore;
import org.junit.Test;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

import static org.junit.Assert.*;

public class WhatwgCanonicalizerTest {

    static Gson gson = new Gson();

    @Test
    @Ignore("TODO: ip address, protocol-specific edge cases not implemented")
    public void testW3cTestData() throws IOException {
        try (InputStream stream = getClass().getResourceAsStream("/urltestdata.json")) {
            JsonReader reader = new JsonReader(new InputStreamReader(stream, StandardCharsets.UTF_8));
            reader.beginArray();
            while (reader.hasNext()) {
                // skip comments
                if (reader.peek() == JsonToken.STRING) {
                    reader.nextString();
                    continue;
                }

                W3cTestCase testCase = gson.fromJson(reader, W3cTestCase.class);

                if (testCase.base.equals("about:blank") && testCase.href != null && !testCase.href.startsWith("about:")) {
                    ParsedUrl url = ParsedUrl.parse(testCase.input);
                    Canonicalizer.WHATWG.canonicalize(url);

                    assertEquals(testCase.protocol, bytesToUnicode(url.scheme + url.colonAfterScheme));
                    assertEquals(testCase.username, bytesToUnicode(url.username));
                    assertEquals(testCase.password, bytesToUnicode(url.password));
                    assertEquals(testCase.host, bytesToUnicode(url.hostPort()));
                    assertEquals(testCase.hostname, bytesToUnicode(url.host()));
                    assertEquals(testCase.username, bytesToUnicode(url.username));
                    assertEquals(testCase.password, bytesToUnicode(url.password));
                    assertEquals(testCase.pathname, bytesToUnicode(url.path));
                    assertEquals(testCase.search, bytesToUnicode(url.questionMark + url.query));
                    assertEquals(testCase.hash, bytesToUnicode(url.fragment.isEmpty() ? "" : (url.hashSign + url.fragment)));
                    assertEquals(testCase.href, bytesToUnicode(url.toString()));
                }
            }
            reader.endArray();
        }
    }

    public String bytesToUnicode(String bytes) {
        return new String(bytes.getBytes(StandardCharsets.ISO_8859_1), StandardCharsets.UTF_8);
    }

    public static class W3cTestCase {
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
    }
}