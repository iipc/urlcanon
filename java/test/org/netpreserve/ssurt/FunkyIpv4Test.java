/*
 * FunkyIpv4Test.java - test parsing of unusual ipv4 addresses
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
        long ipv4 = IpAddresses.parseIpv4(new ByteString(input));
        String formatted = ipv4 == -1 ? null : IpAddresses.formatIpv4(ipv4);
        assertEquals(expected, formatted);
    }
}