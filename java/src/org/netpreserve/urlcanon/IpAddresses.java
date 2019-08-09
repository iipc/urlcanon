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

    static short[] parseIpv6(String host) {
        short[] addr = new short[8];
        String[] groups = host.split(":", 10);
        if (groups.length < 3 || groups.length > 9) {
            return null;
        }

        boolean hasIp4 = groups[groups.length - 1].indexOf('.') != -1;
        boolean seenDoubleColon = false;
        int j = 0;
        for (int i = 0; i < groups.length; i++) {
            String group = groups[i];

            // expand ::
            if (group.isEmpty()) {
                if (seenDoubleColon) {
                    return null; // allowed only once
                }
                seenDoubleColon = true;

                // leading
                if (i == 0) {
                    if (groups[1].isEmpty()) { // leading ::
                        i++;
                    } else { // leading :
                        return null; // not allowed
                    }
                }

                // trailing
                if (i == groups.length - 2 && groups[i + 1].isEmpty()) {
                    i++;
                }

                j = addr.length - (groups.length - i) + 1;
                if (hasIp4) j--;
                continue;
            }

            // handle ip4 in last group
            if (i == groups.length - 1 && hasIp4) {
                if (j != 6) { // must be the 7th & 8th short
                    return null;
                }

                long ip4 = parseIpv4(group);
                if (ip4 == -1) {
                    return null;
                }
                addr[6] = (short)(ip4 >>> 16);
                addr[7] = (short)ip4;
                return addr;
            }

            long value = CharSequences.parseUnsignedLongNoThrow(group, 0, group.length(), 16);
            if (value == -1) {
                return null; // not a number
            }
            if (j >= addr.length) {
                return null;
            }
            addr[j++] = (short)value;
        }
        if (!seenDoubleColon && groups.length != 8) {
            return null;
        }
        return addr;
    }

    static String formatIpv6(short[] addr) {
        // find longest sequence of zeroes
        int zeroesStart = addr.length;
        int zeroesLen = 0;
        {
            int curStart = 0;
            int curLen = 0;
            for (int i = 0; i < addr.length; i++) {
                if (addr[i] == 0) {
                    if (curLen == 0) {
                        curStart = i;
                    }
                    curLen++;
                } else {
                    if (curLen > 1 && curLen > zeroesLen) {
                        zeroesLen = curLen;
                        zeroesStart = curStart;
                    }
                    curLen = 0;
                }
            }
            if (curLen > 1 && curLen > zeroesLen) {
                zeroesLen = curLen;
                zeroesStart = curStart;
            }
        }

        // print
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < zeroesStart; i++) {
            sb.append(Integer.toHexString(addr[i] & 0xffff));
            if (i < addr.length - 1) sb.append(':');
        }
        if (zeroesStart == 0) sb.append(':');
        for (int i = zeroesStart + zeroesLen; i < addr.length; i++) {
            sb.append(':').append(Integer.toHexString(addr[i] & 0xffff));
        }
        if (zeroesLen > 0 && zeroesStart + zeroesLen == addr.length) sb.append(':');
        return sb.toString();
    }

    static long parseIpv4(String host) {
        long ipv4 = 0;
        int startOfPart = 0;

        if (host.isEmpty()) {
            return -1;
        }

        for (int i = 0;; i++) {
            // find the end of this part
            int endOfPart = host.indexOf(".", startOfPart);
            if (endOfPart == -1) {
                endOfPart = host.length();
            }

            // if there's more than 4 return failure
            if (i >= 4) {
                return -1;
            }

            long part;
            if (startOfPart == endOfPart) { // treat empty parts as zero
                part = 0;
            } else {
                part = parseIpv4Num(host, startOfPart, endOfPart);
                if (part == -1) return -1; // not a number
            }

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
