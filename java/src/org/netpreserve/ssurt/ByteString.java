/*
 * ByteString.java - byte strings
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

import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.nio.charset.StandardCharsets.UTF_8;

/**
 * An immutable sequence of bytes. Similar to the 'bytes' type in Python.
 *
 * This class implements CharSequence so that we can operate on bytes using Java regular expressions. This
 * is necessary as operations on URLs are specified in terms of bytes not unicode characters.
 *
 * The CharSequence methods in this class operate effectively as if this were a ISO-8859-1 String, but when we convert
 * to and from String we decode and encode as UTF-8.
 */
public class ByteString implements CharSequence {

    public static final ByteString EMPTY = new ByteString(new byte[0]);

    private final byte[] data;

    /**
     * Convert a String to a ByteString by encoding the chars as UTF-8 bytes.
     */
    public ByteString(String s) {
        this(s.getBytes(UTF_8));
    }

    public ByteString(byte[] data) {
        this(data, 0, data.length);
    }

    public ByteString(byte[] data, int off, int len) {
        this.data = Arrays.copyOfRange(data, off, off + len);
    }

    /**
     * The number of bytes in this ByteString.
     */
    @Override
    public int length() {
        return data.length;
    }

    /**
     * The char of the byte value at the given index. No charset decoding is performed.
     */
    @Override
    public char charAt(int index) {
        return (char) (data[index] & 0xFF);
    }

    @Override
    public ByteString subSequence(int start, int end) {
        return new ByteString(data, start, end - start);
    }

    /**
     * Convert this byte sequence to a String by decoding it as UTF-8.
     *
     * Beware: For non-ASCII strings, this deviates from the contract of CharSequence as
     * toString() != charAt(0) + ... + charAt(length).
     */
    public String toString() {
        return new String(data, UTF_8);
    }

    /**
     * Return a copy as a byte array.
     */
    public byte[] toByteArray() {
        return Arrays.copyOf(data, data.length);
    }

    /**
     * True if this byte string has a length of zero.
     */
    public boolean isEmpty() {
        return data.length == 0;
    }

    public static ByteString join(ByteString delimiter, Iterable<? extends CharSequence> sequence) {
        int size = 0;
        for (CharSequence s: sequence) {
            size += s.length();
        }
        ByteStringBuilder builder = new ByteStringBuilder(size);
        for (CharSequence s: sequence) {
            builder.append(s);
        }
        return builder.toByteString();
    }

    public ByteString replaceAll(Pattern pattern, CharSequence replacement) {
        ByteStringBuilder buf = new ByteStringBuilder(length());
        int pos = 0;
        Matcher m = pattern.matcher(this);
        while (m.find()) {
            buf.append(this, pos, m.start());
            buf.append(replacement);
            pos = m.end();
        }
        buf.append(this, pos, length());
        return buf.toByteString();
    }

    /**
     * Return a copy of this byte string with all bytes matching target replaced.
     */
    public ByteString replace(byte target, byte replacement) {
        byte[] dest = new byte[length()];
        for (int i = 0; i < data.length; i++) {
            byte b = data[i];
            if (b == target) {
                dest[i] = replacement;
            } else  {
                dest[i] = data[i];
            }
        }
        return new ByteString(dest);
    }

    private byte lowerCaseByte(byte b) {
        if ('A' <= b && b <= 'Z') {
            return (byte)(b - 'A' + 'a');
        } else {
            return b;
        }
    }

    /**
     * Return a copy of this byte string with ASCII letters lower cased.
     */
    public ByteString asciiLowerCase() {
        byte[] out = new byte[length()];
        for (int i = 0; i < data.length; i++) {
            out[i] = lowerCaseByte(data[i]);
        }
        return new ByteString(out);
    }

    public boolean equalsIgnoreCase(CharSequence s) {
        int len = s.length();
        if (len != data.length) {
            return false;
        }
        for (int i = 0; i < len; i++) {
            if (lowerCaseByte(data[i]) != lowerCaseByte((byte)s.charAt(i))) {
                return false;
            }
        }
        return true;
    }
}
