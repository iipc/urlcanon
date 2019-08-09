package org.netpreserve.urlcanon;

import com.google.gson.stream.JsonReader;
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

import static java.nio.charset.StandardCharsets.UTF_8;
import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class SemanticPreciseTest {

    @Parameterized.Parameter(value = 0)
    public String input;

    @Parameterized.Parameter(value = 1)
    public String expected;

    @Parameterized.Parameters(name = "{index} {0} -> {1}")
    public static List<Object[]> loadData() throws IOException {
        List<Object[]> tests = new ArrayList<>();
        try (InputStream stream = FunkyIpv4Test.class.getResourceAsStream("/semantic_precise.json");
             JsonReader reader = new JsonReader(new InputStreamReader(stream, UTF_8))) {
            reader.beginObject();
            while (reader.hasNext()) {
                String input = reader.nextName();
                String expected = reader.nextString();
                tests.add(new Object[]{input, expected});
            }
            reader.endObject();
        }
        return tests;
    }

    @Test
    public void test() {
        String bs = new String(input.getBytes(StandardCharsets.ISO_8859_1));
        ParsedUrl url = ParsedUrl.parseUrl(bs);
        Canonicalizer.SEMANTIC_PRECISE.canonicalize(url);
        assertEquals(expected, url.toString());
    }
}
