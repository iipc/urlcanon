SSURT
=====

Superior SURT. Sensible SURT. Smug SURT.

Transforms ``scheme://userinfo@domain.tld:port/path?query#fragment`` into
``tld,domain,//port:scheme@userinfo:/path?query#fragment``.

Old-school Heritrix SURT is described at
http://crawler.archive.org/articles/user_manual/glossary.html#surt. SSURT
resolves the following issues with Heritrix SURTs:

1. Matching everything from a domain required a separate rule for each
   protocol.
2. Correct parsing of a SURT is awkward due to ")" being allowed in userinfo
   but also used to delimit it.
3. Reversible. This should be true: unSSURT(SSURT(url)) = url.

Example SSURT prefixes::

    au,gov,nla,                     => *.nla.gov.au
    au,gov,nla,//                   => everything on host 'nla.gov.au' regardless of scheme and port
    au,gov,nla,//8000:              => everything on port 8000 on host 'nla.gov.au'
    au,gov,nla,//:http              => http and no port specified on host 'nla.gov.au' any userinfo
    au,gov,nla,//8000:http:         => http on port 8000 on host 'nla.gov.au' blank userinfo
    au,gov,nla,//8000:http@foo:bar: => http on port 8000 on host 'nla.gov.au' userinfo 'foo:bar'
    10.                             => everything in ipv4 subnet 10.0.0.0/8, assuming IP address canonicalization
    [2001:0db8:                     => everything in ipv6 subnet 2001:0db8/32, assuming IP address canonicalization
    [2001:0db8:0000:0042:0000:8a2e:0370:7334]:80:ws:/chat

Indicative grammar (grammars alone are not powerful enough to describe URL
parsing)::

    SSURT = [ [ ssurt_host ] "//" ] ] [ [ port ] ":" ] [ [ scheme ] [ "@" [ userinfo ] ] ":" ] path [ "?" [ query ] ] [ "#" [ fragment ] ]
    ssurt_host = revdomain "," / IPv4address / "[" IPv6address "]"

SSURT does not imply any particular canonicalization. Funky uncanonicalized
urls can be represented in SSURT format.
