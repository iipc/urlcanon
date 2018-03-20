urlcanon
========

.. image:: https://travis-ci.org/iipc/urlcanon.svg?branch=master
    :target: https://travis-ci.org/iipc/urlcanon
    :alt: build status

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
        <version>0.1.1</version>
    </dependency>

License
-------

* Copyright (C) 2016-2017 Internet Archive
* Copyright (C) 2016-2017 National Library of Australia

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this software except in compliance with the License. You may
obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
