package org.netpreserve.urlcanon;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class ParserUrlTest {
    @Test
    public void testReverseHost() {
        assertEquals(",", ParsedUrl.reverseHost(new ByteString("")).toString());
        assertEquals("x,", ParsedUrl.reverseHost(new ByteString("x")).toString());
        assertEquals("z,y,x,", ParsedUrl.reverseHost(new ByteString("x.y.z")).toString());
        assertEquals(",z,y,x,", ParsedUrl.reverseHost(new ByteString("x.y.z.")).toString());
        assertEquals(",z,y,a.b,", ParsedUrl.reverseHost(new ByteString("a,b.y.z.")).toString());
    }

    @Test
    public void testSsurtHost() {
        assertEquals("1.2.3.4", ParsedUrl.ssurtHost(new ByteString("1.2.3.4")).toString());
        assertEquals("0x80", ParsedUrl.ssurtHost(new ByteString("0x80")).toString());
        assertEquals("z,y,x,", ParsedUrl.ssurtHost(new ByteString("x.y.z")).toString());
    }

    @Test
    public void testSsurt() {
        assertEquals("org,example,foo,//:81:http@user:pass/path?query#frag", ParsedUrl.parse("http://user:pass@foo.example.org:81/path?query#frag").ssurt().toString());
    }
}
