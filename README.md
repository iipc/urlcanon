urlcanon
========

[![Build Status](https://travis-ci.org/iipc/urlcanon.svg?branch=master)](https://travis-ci.org/iipc/urlcanon)

A URL canonicalization (normalization) library for Python and Java.

It currently provides:

* A URL parser which preserves the input bytes exactly
* A precanned canonicalization ruleset that tries to match the normalization implicit in the [parsing rules used by browsers](https://url.spec.whatwg.org/)
* An alternative URL serialization suitable for sorting and prefix-matching

**Status:** Early development. No API or output stability guarantees yet.

## Examples

### Python

```python
input_url = "http://///EXAMPLE.com:80/foo/../bar"
parsed_url = urlcanon.parse_url(input_url)

print(parsed_url)
# http://///EXAMPLE.com:80/foo/../bar

urlcanon.Canonicalizer.WHATWG(parsed_url)

print(parsed_url)
# http://example.com/bar

print(parsed_url.ssurt())
# b'com,example,//:http/bar'

```

### Java

```java
String inputUrl = "http://///EXAMPLE.com:80/foo/../bar";
ParsedUrl parsedUrl = ParsedUrl.parseUrl(inputUrl);

System.out.println(parsedUrl);
// http://///EXAMPLE.com:80/foo/../bar

Canonicalizer.WHATWG.canonicalize(parsedUrl);

System.out.println(parsedUrl);
// http://example.com/bar

System.out.println(parsedUrl.ssurt());
// "com,example,//:http/bar"
```

## License

Copyright 2016 Internet Archive

Copyright 2016 National Library of Australia

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this software except in compliance with the License. You may
obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
