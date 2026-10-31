# Ontology files in this repository

The dataset follows the HeritageGraph ontology at
[CAIRNepal/heritagegraphontology](https://github.com/CAIRNepal/heritagegraphontology). The files here are exact copies;
they are never edited here. Changes the dataset needs are proposed to the ontology repository.

| file | ontology version | source | SHA-256 |
|---|---|---|---|
| `HeritageGraph.ttl` | 1.0.1 | `main`, commit `f2f1780` (ontology files unchanged since `70f7995`). 1.0.1 has **no git tag** yet. | `c2818dc0fc30437d013c7e8a37eb2877993961b0336a564becbf39a2bae0bc67` |
| `HeritageGraph.shacl.ttl` | 1.0.1 | same | `80ed52cfdcef00878b930665ee8f8d685cb31c8b23a87b2e8669de872b790a5d` |
| `HeritageGraph.yaml` | 1.0.1 (LinkML source of both files above) | same | `2a3736bddb5a4631841424446bc2711052906e0007cf6219ac6e249a5a61b883` |
| `archive/HeritageGraph-1.0.0.ttl` | 1.0.0 | tag `v1.0.0` (`2bd4e37`); the copy dataset release v1.0.0 was built with | `52a64aa0a79f79e2936fc79f6ed8f21d7a792f74c8b46ec687d0001309888092` |
| `archive/HeritageGraph-1.0.0.shacl.ttl` | 1.0.0 | tag `v1.0.0` | `c15d9a65585a582c4da45f5bcdc36dcc53bd54d9a444d441c492817f9c05d743` |

`.agents/skills/danam-to-heritagegraph/references/HeritageGraph.ttl` is the same file as `HeritageGraph.ttl`.

**Refresh:** download `ontology/HeritageGraph.ttl`, `ontology/HeritageGraph.shacl.ttl` and `ontology/HeritageGraph.yaml` from the ontology repository at
the new commit or tag, replace the three files, copy the TTL to the skill's `references/`, and update this table.
