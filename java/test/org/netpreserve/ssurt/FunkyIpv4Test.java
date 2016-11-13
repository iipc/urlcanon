package org.netpreserve.ssurt;

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
import java.util.ArrayList;
import java.util.List;

import static java.nio.charset.StandardCharsets.UTF_8;
import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class FunkyIpv4Test {

    @Parameter(value = 0)
    public String input;

    @Parameter(value = 1)
    public String expected;

    @Parameters(name = "{index} {0} -> {1}")
    public static List<Object[]> loadData() throws IOException {
        List<Object[]> tests = new ArrayList<>();
        try (InputStream stream = FunkyIpv4Test.class.getResourceAsStream("/funky_ipv4.json");
             JsonReader reader = new JsonReader(new InputStreamReader(stream, UTF_8))) {
            reader.beginObject();
            while (reader.hasNext()) {
                String input = reader.nextName();
                String expected;
                if (reader.peek() == JsonToken.NULL) {
                    reader.nextNull();
                    expected = null;
                } else {
                    expected = reader.nextString();
                }
                tests.add(new Object[]{input, expected});
            }
            reader.endObject();
        }
        return tests;
    }

    @Test
    public void test() {
        assertEquals(expected, WhatwgCanonicalizer.dottedDecimal(new ByteString(input)).toString());
    }
}