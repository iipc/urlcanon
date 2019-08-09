/*
 * CharSequences.java - utility methods operating on CharSequence
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

import java.util.regex.Matcher;

class CharSequences {
    /**
     * Parses an unsigned long. This differs from Long.parseLong in that it doesn't support negative
     * numbers and it returns -1 rather than throwing an exception (which was slow).
     */
    static long parseUnsignedLongNoThrow(CharSequence s, int start, int end, int radix) {
        long n = 0;
        for (int i = start; i < end; i++) {
            int digit = Character.digit(s.charAt(i), radix);
            if (digit == -1) {
               return -1;
            }
            n = n * radix + digit;
        }
        return n;
    }


    public static long parseLong(CharSequence s) {
        return parseUnsignedLongNoThrow(s, 0, s.length(), 10);
    }

    static String group(Matcher matcher, int group) {
        String g = matcher.group(group);
        return g == null ? "" : g;
    }
}
