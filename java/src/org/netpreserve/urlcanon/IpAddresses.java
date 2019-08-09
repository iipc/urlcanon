/*
 * IpAddresses.java - ip address parsing and formatting
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

class IpAddresses {

    static String formatIpv4(long ipv4) {
        if (ipv4 < 0) {
            throw new IllegalArgumentException("value " + ipv4);
        }
        return String.format("%d.%d.%d.%d", ipv4 >> 24, (ipv4 >> 16) & 0xff,
                (ipv4 >> 8) & 0xff, ipv4 & 0xff);
    }

    static long parseIpv4(String host) {
        long ipv4 = 0;
        int startOfPart = 0;

        for (int i = 0;; i++) {
            // find the end of this part
            int endOfPart = host.indexOf(".", startOfPart);
            if (endOfPart == -1) {
                endOfPart = host.length();
            }

            // if a part is empty or there's more than 4 return failure
            if (startOfPart == endOfPart || i >= 4) {
                return -1;
            }

            long part = parseIpv4Num(host, startOfPart, endOfPart);
            if (part == -1) return -1; // not a number

            // if this is the last part (or second-last part and last part is empty)
            if (endOfPart >= host.length() - 1) {
                if (part >= (1L << (8 * (4 - i)))) {
                    return -1; // too big
                }

                // 1.2 => 1.0.0.2
                ipv4 <<= 8 * (4 - i);
                ipv4 += part;
                return ipv4;
            }

            // if any but the last item is larger than 255 return failure
            if (part > 255) {
                return -1;
            }
            ipv4 = ipv4 * 256 + part;
            startOfPart = endOfPart + 1;
        }
    }

    private static long parseIpv4Num(String host, int start, int end) {
        int radix = 10;
        if (end - start >= 2 && host.charAt(start) == '0') {
            char c = host.charAt(start + 1);
            if (c == 'x' || c == 'X') {
                radix = 16;
                start += 2;
            } else {
                radix = 8;
                start++;
            }
        }
        return CharSequences.parseUnsignedLongNoThrow(host, start, end, radix);
    }
}
