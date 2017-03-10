/*
 * ByteStringTest.java - byte string tests
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

import org.junit.Test;

import java.util.regex.Pattern;

import static java.nio.charset.StandardCharsets.ISO_8859_1;
import static org.junit.Assert.assertEquals;

public class ByteStringTest {

    @Test
    public void testCharAt() {
        ByteString bs = new ByteString("Â©z".getBytes(ISO_8859_1));
        assertEquals('Â', bs.charAt(0));
        assertEquals('©', bs.charAt(1));
        assertEquals('z', bs.charAt(2));
    }

    @Test
    public void testReplaceAll() {
        assertEquals("1-2-3-4", new ByteString("1:2,3:4")
                .replaceAll(Pattern.compile("[:,]"), "-").toString());
    }

    @Test
    public void testAsciiLowercase() {
        assertEquals("abcdef123@[", new ByteString("AbCDef123@[")
                .asciiLowerCase().toString());
    }

    @Test
    public void testPctDecode() {
        assertEquals("1 2\u007f3\uD83D\uDE2C4",
                new ByteString("1%202%7f3%f0%9f%98%Ac4").pctDecode().toString());
    }
}
