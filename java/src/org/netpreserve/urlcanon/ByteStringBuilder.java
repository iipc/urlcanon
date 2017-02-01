/*
 * ByteStringBuilder.java - builder of byte strings
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

import java.util.Arrays;

import static java.nio.charset.StandardCharsets.UTF_8;

/**
 * An analogue of StringBuilder for ByteStrings.
 */
public class ByteStringBuilder {
    byte[] data;
    int length;

    public ByteStringBuilder(int capacity) {
        data = new byte[capacity];
        length = 0;
    }

    public ByteString toByteString() {
        return new ByteString(data, 0, length);
    }

    public ByteStringBuilder append(CharSequence s, int start, int end) {
        if (start > end) {
            throw new IllegalArgumentException("start > end");
        }
        ensureCapacity(length + (end - start));
        int j = length;
        for (int i = start; i < end; i++) {
            data[j++] = (byte) s.charAt(i);
        }
        length = j;
        return this;
    }

    private void ensureCapacity(int capacity) {
        if (data.length < capacity) {
            data = Arrays.copyOf(data, capacity);
        }
    }

    public ByteStringBuilder append(CharSequence s) {
        append(s, 0, s.length());
        return this;
    }

    public String toString() {
        return new String(data, 0, length, UTF_8);
    }

    public void setLength(int length) {
        ensureCapacity(length);
        this.length = length;
    }

    public int length() {
        return length;
    }

    public void append(char c) {
        setLength(length + 1);
        data[length - 1] = (byte)c;
    }

    public byte[] toByteArray() {
        return Arrays.copyOf(data, length);
    }
}
