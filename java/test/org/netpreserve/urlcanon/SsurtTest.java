package org.netpreserve.urlcanon;

import com.google.gson.stream.JsonReader;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import static java.nio.charset.StandardCharsets.ISO_8859_1;
import static java.nio.charset.StandardCharsets.UTF_8;
import static org.junit.Assert.*;

@RunWith(Parameterized.class)
public class SsurtTest {

    @Parameterized.Parameter(value = 0)
    public String type;

    @Parameterized.Parameter(value = 1)
    public String input;

    @Parameterized.Parameter(value = 2)
    public String expected;

    @Parameterized.Parameters(name = "{index} {0} {1} -> {2}")
    public static List<Object[]> loadData() throws IOException {
        List<Object[]> tests = new ArrayList<>();
        try (InputStream stream = SsurtTest.class.getResourceAsStream("/ssurt.json");
             JsonReader reader = new JsonReader(new InputStreamReader(stream, UTF_8))) {
            reader.beginObject();
            while (reader.hasNext()) {
                String type = reader.nextName();
                reader.beginObject();
                while (reader.hasNext()) {
                    String input = reader.nextName();
                    String expected = reader.nextString();
                    tests.add(new Object[]{type, input, expected});
                }
                reader.endObject();
            }
            reader.endObject();
        }
        return tests;
    }

    @Test
    public void test() {
        switch (type) {
            case "ssurtHost":
                assertEquals(expected, ParsedUrl.ssurtHost(input));
                break;
            case "reverseHost":
                assertEquals(expected, ParsedUrl.reverseHost(input));
                break;
            case "ssurt":
                assertEquals(expected, ParsedUrl.parseUrl(input).ssurt());
                break;
            case "surt":
                assertEquals(expected, ParsedUrl.parseUrl(input).surt());
                break;
            case "surtWithoutScheme":
                ParsedUrl parsedUrl = ParsedUrl.parseUrl(input);
                parsedUrl.setScheme("");
                parsedUrl.setColonAfterScheme("");
                parsedUrl.setSlashes("");
                assertEquals(expected, parsedUrl.surt());
                break;
            case "surtWithoutTrailingComma":
                assertEquals(expected, ParsedUrl.parseUrl(input).surtWithoutTrailingComma());
                break;
            default:
                fail("unimplemented test type: " + type);
        }
        ParsedUrl url = ParsedUrl.parseUrl(input);
        //assertEquals(expected, url.surt());
    }
}
