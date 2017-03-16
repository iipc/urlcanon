/*
 * SemanticCanonicalizer.java
 *
 * Copyright (C) 2016-2017 National Library of Australia
 * Copyright (C) 2016-2017 Internet Archive
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

/**
 * Like semantic_precise but removes the fragment from
 * the url, thus considers urls which differ only in the fragment to be
 * equivalent to each other.
 */
public class SemanticCanonicalizer implements Canonicalizer {
    @Override
    public void canonicalize(ParsedUrl url) {
        Canonicalizer.SEMANTIC_PRECISE.canonicalize(url);
        removeFrament(url);
    }

    static void removeFrament(ParsedUrl url) {
        url.setHashSign(ByteString.EMPTY);
        url.setFragment(ByteString.EMPTY);
    }
}
