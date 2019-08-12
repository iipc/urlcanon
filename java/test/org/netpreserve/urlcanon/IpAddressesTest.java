package org.netpreserve.urlcanon;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.netpreserve.urlcanon.IpAddresses.formatIpv6;
import static org.netpreserve.urlcanon.IpAddresses.parseIpv6;

public class IpAddressesTest {
    @Test
    public void testIpv6() {
        assertEquals("1::", formatIpv6(parseIpv6("1:0:0::")));
        assertEquals("1:0:2::", formatIpv6(parseIpv6("1:0:2::")));
        assertEquals("ffff::c000:280", formatIpv6(parseIpv6("ffff::192.0.2.128")));
        assertEquals("ffff:2::3:c000:280", formatIpv6(parseIpv6("ffff:02::3:192.0.2.128")));
        assertEquals("ffff::203", formatIpv6(parseIpv6("ffff::0.0.2.3")));
        assertEquals("1::2", formatIpv6(parseIpv6("1::2")));
        assertEquals("1::2", formatIpv6(parseIpv6("1:0:0::2")));
        assertEquals("1:0:2::3:4:5", formatIpv6(parseIpv6("1:0:2:0:0:3:4:5")));
        assertEquals("1::2:0:3:4:5", formatIpv6(parseIpv6("1:0:0:2:0:3:4:5")));
        assertEquals("1:0:2:0:3:0:4:0", formatIpv6(parseIpv6("1:0:2:0:3:0:4:0")));
        assertEquals("::ffff:c000:280", formatIpv6(parseIpv6("::ffff:192.0.2.128")));
        assertNull(parseIpv6("bogus"));
        assertNull(parseIpv6("1:2:3:4:5:6:7:8:9"));
        assertNull(parseIpv6("1:2"));
        assertNull(parseIpv6("1:2:3"));
        assertNull(parseIpv6("1::2::3"));
    }
}
