package org.netpreserve.urlcanon;

interface Idn {
    /**
     * Attempt to load the best available IDN implementation. Will use ICU4J if its available and otherwise will
     * fallback to java.net.IDN.
     */
    static Idn load() {
        try {
            return new IdnIcu4j();
        } catch (NoClassDefFoundError e) {
            return new IdnJava();
        }
    }

    String toAscii(String name);
}
