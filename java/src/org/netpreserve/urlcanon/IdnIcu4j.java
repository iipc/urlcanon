package org.netpreserve.urlcanon;

import com.ibm.icu.text.IDNA;

class IdnIcu4j implements Idn {
    private final IDNA idna = IDNA.getUTS46Instance(IDNA.NONTRANSITIONAL_TO_ASCII);

    public String toAscii(String name) {
        return idna.nameToASCII(name, new StringBuilder(), new IDNA.Info()).toString();
    }
}
