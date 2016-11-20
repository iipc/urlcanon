/*
 * ResolvePathDotsTest.java - test resolving . and .. in paths
 *
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

import com.google.gson.stream.JsonReader;
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
public class ResolvePathDotsTest {

    @Parameter(value = 0)
    public boolean special;

    @Parameter(value = 1)
    public String input;

    @Parameter(value = 2)
    public String expected;

    @Parameters(name = "{index} special={0} input={1}")
    public static List<Object[]> loadData() throws IOException {
        List<Object[]> tests = new ArrayList<>();
        try (InputStream stream = ResolvePathDotsTest.class.getResourceAsStream("/path_dots.json");
             JsonReader reader = new JsonReader(new InputStreamReader(stream, UTF_8))) {
            reader.beginObject();
            while (reader.hasNext()) {
                boolean special = isSpecial(reader.nextName());
                reader.beginObject();
                while (reader.hasNext()) {
                    String input = reader.nextName();
                    String expected = reader.nextString();
                    tests.add(new Object[]{special, input, expected});
                }
                reader.endObject();
            }
            reader.endObject();
        }
        return tests;
    }

    private static boolean isSpecial(String type) throws IOException {
        if (type.equals("special")) {
            return true;
        } else if (type.equals("nonspecial")) {
            return false;
        } else {
            throw new IllegalArgumentException("unimplemented test type: " + type);
        }
    }

    @Test
    public void test() {
        assertEquals(expected, WhatwgCanonicalizer.resolvePathDots(new ByteString(input), special).toString());
    }
}