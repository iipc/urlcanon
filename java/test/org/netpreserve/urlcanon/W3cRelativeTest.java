package org.netpreserve.urlcanon;

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import org.junit.Ignore;
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
public class W3cRelativeTest {
    private static Gson gson = new Gson();

    @Parameterized.Parameter
    public TestData test;

    @Parameterized.Parameters(name = "{index} {0}")
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

                if (test.base != null) {
                    tests.add(test);
                }
            }
            reader.endArray();
        }
        return tests;
    }

    @Test
    @Ignore
    public void test() throws IOException {
        ParsedUrl base = ParsedUrl.parseUrl(test.base);
        ParsedUrl input = ParsedUrl.parseUrl(test.input);
        ParsedUrl url = base.resolve(input);
        Canonicalizer.WHATWG.canonicalize(url);

        assertEquals("href of " + test.input, test.href, url.toString());
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
            return base + " " + input;
        }
    }
}
