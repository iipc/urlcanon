package org.netpreserve.urlcanon;

import java.net.IDN;

/**
 * Java's built-in IDN implementation.
 *
 * Doesn't support IDNA2008 https://bugs.openjdk.java.net/browse/JDK-6988055
 */
class IdnJava implements Idn {
    @Override
    public String toAscii(String name) {
        return IDN.toASCII(name, IDN.ALLOW_UNASSIGNED);
    }
}
