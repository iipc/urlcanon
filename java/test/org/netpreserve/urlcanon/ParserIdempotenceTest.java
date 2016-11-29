/*
 * ParserIdempotenceTest.java - what goes in must come out
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

package org.netpreserve.urlcanon;

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
        assertEquals(test, ParsedUrl.parseUrl(test.getBytes()).toString());
    }
}