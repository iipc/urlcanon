urlcanon
========

.. image:: https://travis-ci.org/iipc/urlcanon.svg?branch=master
    :target: https://travis-ci.org/iipc/urlcanon
    :alt: build status

.. image:: https://maven-badges.herokuapp.com/maven-central/org.netpreserve/urlcanon/badge.svg
    :target: https://maven-badges.herokuapp.com/maven-central/org.netpreserve/urlcanon
    :alt: maven central

.. image:: https://javadoc.io/badge2/org.netpreserve/urlcanon/javadoc.svg
    :target: https://javadoc.io/doc/org.netpreserve/urlcanon
    :alt: javadoc

A URL canonicalization (normalization) library for Python and Java.

It currently provides:

* A URL parser which preserves the input bytes exactly
* A precanned canonicalization ruleset that tries to match the normalization
  implicit in the `parsing rules used by browsers
  <https://url.spec.whatwg.org/>`_
* An alternative URL serialization suitable for sorting and prefix-matching:
  `SSURT <ssurt.rst>`_.

**Status:** Stable and in production use for some time. But no API or output
stability guarantees yet. There are differences in features between Java and
Python versions.

Examples
--------

Python
~~~~~~

.. code:: python

    >>> import urlcanon
    >>> input_url = "http://///EXAMPLE.com:80/foo/../bar"
    >>> parsed_url = urlcanon.parse_url(input_url)
    >>> print(parsed_url)
    http://///EXAMPLE.com:80/foo/../bar
    >>> urlcanon.whatwg(parsed_url)
    <urlcanon.parse.ParsedUrl object at 0x10eb13a58>
    >>> print(parsed_url)
    http://example.com/bar
    >>> print(parsed_url.ssurt())
    b'com,example,//:http/bar'
    >>>
    >>> rule = urlcanon.MatchRule(ssurt=b'com,example,//:http/bar')
    >>> urlcanon.whatwg.rule_applies(rule, b'https://example..com/bar/baz')
    False
    >>> urlcanon.whatwg.rule_applies(rule, b'HTtp:////eXAMple.Com/bar//baz//..///quu')
    True

Python releases are available in PyPI:

.. code:: sh

    pip install urlcanon

Java
~~~~

.. code:: java

    String inputUrl = "http://///EXAMPLE.com:80/foo/../bar";
    ParsedUrl parsedUrl = ParsedUrl.parseUrl(inputUrl);

    System.out.println(parsedUrl);
    // http://///EXAMPLE.com:80/foo/../bar

    Canonicalizer.WHATWG.canonicalize(parsedUrl);

    System.out.println(parsedUrl);
    // http://example.com/bar

    System.out.println(parsedUrl.ssurt());
    // "com,example,//:http/bar"

Java releases are available in the Maven Central repository:

.. code:: xml

    <dependency>
        <groupId>org.netpreserve</groupId>
        <artifactId>urlcanon</artifactId>
        <version>0.3.0</version>
    </dependency>

Internationalized domain names
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Java version of urlcanon will use `ICU4J <icu-project.org>`_ for punycode encoding if available. Otherwise it will
fall back to java.net.IDN which does not support the newer IDNA2008 rules. So if you need correct IDN handling make
sure to add ICU4J to your project:

.. code:: xml

    <dependency>
        <groupId>com.ibm.icu</groupId>
        <artifactId>icu4j</artifactId>
        <version>53.1</version>
    </dependency>

License
-------

* Copyright (C) 2016-2018 Internet Archive
* Copyright (C) 2016-2020 National Library of Australia

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this software except in compliance with the License. You may
obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
