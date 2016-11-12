package org.netpreserve.ssurt;

import com.google.gson.Gson;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.List;

import static java.nio.charset.StandardCharsets.UTF_8;
import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
public class ParserIdempotenceTest {

    private static Gson gson = new Gson();

    @Parameter
    public String test;

    @Parameters(name = "{index} {0}")
    public static List<String> loadData() throws IOException {
        try (InputStream stream = ParserIdempotenceTest.class.getResourceAsStream("/idempotence.json");
             InputStreamReader reader = new InputStreamReader(stream, UTF_8)) {
            return Arrays.asList(gson.fromJson(reader, String[].class));
        }
    }

    @Test
    public void test() {
        assertEquals(test, ParsedUrl.parse(test.getBytes()).toString());
    }
}