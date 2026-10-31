"""How well does a HeritageGraph-Nepal graph follow the HeritageGraph ontology?

Usage:
  python tools/sync/check_alignment.py [--graph latest/heritagegraph-nepal.nt.gz] [--out docs/sync/alignment_<name>]

Checks, against the ontology files vendored in ontology/ (see ontology/SOURCE.md):
  1. Undeclared terms: every hg: or hgn: class (rdf:type object), property and IRI value used in the graph that neither the
     ontology nor the extension vocabulary (vocab/hgn.ttl) declares, with usage counts. Extension (hgn:) terms in use are
     listed separately, with the CRM/ontology term each maps to. For each, the ontology's own LinkML source (HeritageGraph.yaml) is searched for a class or
     slot of the same name: if it has a class_uri / slot_uri, that IRI is the term the ontology means (an exact equivalent).
  2. SHACL: pySHACL with the ontology's shapes, no inference, the whole graph; results grouped by (path, constraint).
Writes <out>.md (readable report) and <out>.json (numbers), and prints a one-line summary.
"""
import argparse, gzip, json, os, re, sys, time
from collections import Counter, defaultdict

import rdflib
import yaml
from pyshacl import validate
from rdflib import OWL, RDF, RDFS, SKOS, BNode, URIRef
from rdflib.namespace import SH

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HG = "https://cair-nepal.org/heritagegraph/"
PREFIX = {"https://cair-nepal.org/heritagegraph/": "hg:", "https://w3id.org/heritagegraph-nepal/vocab#": "hgn:", "http://www.cidoc-crm.org/cidoc-crm/": "crm:",
          "http://www.w3.org/ns/prov#": "prov:", "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
          "http://purl.org/dc/terms/": "dcterms:", "http://www.w3.org/ns/shacl#": "sh:", "http://www.w3.org/2004/02/skos/core#": "skos:"}


def short(t):
    s = str(t)
    for ns, p in PREFIX.items():
        if s.startswith(ns):
            return p + s[len(ns):]
    return s


def load(path):
    g = rdflib.Graph()
    if path.endswith(".gz"):
        g.parse(gzip.open(path), format="nt")
    else:
        g.parse(path)
    return g


def linkml_names(path):
    """name (normalised) -> (kind, linkml name, mapped IRI or None) for classes and slots of the LinkML schema."""
    y = yaml.safe_load(open(path, encoding="utf-8"))
    pre = {k: (v if isinstance(v, str) else v.get("prefix_reference")) for k, v in (y.get("prefixes") or {}).items()}
    def expand(curie):
        if not curie or ":" not in curie or curie.startswith("http"):
            return curie
        p, local = curie.split(":", 1)
        return (pre.get(p) or "") + local if pre.get(p) else curie
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    out = {}
    for name, c in (y.get("classes") or {}).items():
        out[norm(name)] = ("class", name, expand((c or {}).get("class_uri")))
    for name, s in (y.get("slots") or {}).items():
        out.setdefault(norm(name), ("slot", name, expand((s or {}).get("slot_uri"))))
    return out, norm


def path_str(results, p):
    if p is None:
        return "(none)"
    if isinstance(p, BNode):
        inv = results.value(p, SH.inversePath)
        return "^" + short(inv) if inv is not None else "[complex path]"
    return short(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--graph", default=os.path.join(REPO, "latest", "heritagegraph-nepal.nt.gz"))
    ap.add_argument("--ontology", default=os.path.join(REPO, "ontology", "HeritageGraph.ttl"))
    ap.add_argument("--shapes", default=os.path.join(REPO, "ontology", "HeritageGraph.shacl.ttl"))
    ap.add_argument("--vocab", default=os.path.join(REPO, "vocab", "hgn.ttl"))
    ap.add_argument("--linkml", default=os.path.join(REPO, "ontology", "HeritageGraph.yaml"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(REPO, "docs", "sync", "alignment_" + re.sub(r"\W+", "_", os.path.relpath(a.graph, REPO)).strip("_"))
    g, onto, shapes = load(a.graph), load(a.ontology), load(a.shapes)
    version = [str(v) for v in onto.objects(None, OWL.versionInfo)]

    # 1. undeclared terms (in the ontology's hg: namespace or the extension's hgn: namespace)
    vocab = load(a.vocab) if os.path.exists(a.vocab) else rdflib.Graph()
    hgn = str(dict(vocab.namespaces()).get("hgn", "")) or None
    spaces = tuple(n for n in (HG, hgn) if n)
    ours = lambda t: isinstance(t, URIRef) and str(t).startswith(spaces)
    kinds = (OWL.Class, RDFS.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, RDF.Property)
    declared = {s for src in (onto, vocab) for t in kinds for s in src.subjects(RDF.type, t)}
    # enumeration values / concepts: typed individuals in the ontology (hg:X#Y) or the vocabulary
    individuals = ({s for s in onto.subjects(RDF.type, None) if str(s).startswith(HG) and "#" in str(s)}
                   | {s for s in vocab.subjects(RDF.type, None) if s not in declared})
    namespace_iris = {URIRef(n) for n in spaces} | {URIRef(n.rstrip("#/")) for n in spaces}  # e.g. void:vocabulary values
    cls = Counter(o for o in g.objects(None, RDF.type) if ours(o) and o not in declared and o not in individuals)
    props = Counter(p for p in g.predicates() if ours(p) and p not in declared)
    used_values = Counter(o for o in g.objects() if ours(o) and o not in declared and o not in individuals and o not in cls
                          and o not in namespace_iris and not any(True for _ in g.predicates(None, o) if _ == RDF.type))
    names, norm = linkml_names(a.linkml)
    def equiv(term):
        if not str(term).startswith(HG):
            return None, None
        local = str(term)[len(HG):]
        hit = names.get(norm(local))
        if not hit:
            return None, None
        kind, name, iri = hit
        return f"LinkML {kind} `{name}`", (short(iri) if iri and iri != str(term) else None)
    undeclared = []
    for kind, ctr in (("class", cls), ("property", props), ("IRI value", used_values)):
        for t, n in sorted(ctr.items(), key=lambda kv: (-kv[1], str(kv[0]))):
            where, iri = equiv(t)
            undeclared.append({"kind": kind, "term": short(t), "uses": n, "linkml": where, "ontology_iri": iri})

    # extension terms in use, with what each maps to
    ext = []
    if hgn:
        use = Counter()
        for s, p, o in g:
            for t in (p, o) if p != RDF.type else (o,):
                if isinstance(t, URIRef) and str(t).startswith(hgn) and (t in declared or t in individuals):
                    use[t] += 1
        for t, n in sorted(use.items(), key=lambda kv: (-kv[1], str(kv[0]))):
            maps = [f"{short(p)} {short(o)}" for p in (RDFS.subClassOf, RDFS.subPropertyOf, SKOS.closeMatch, SKOS.exactMatch, SKOS.broadMatch)
                    for o in vocab.objects(t, p)]
            kind = ("class" if (t, RDF.type, OWL.Class) in vocab else "property" if t in declared else "concept")
            ext.append({"kind": kind, "term": short(t), "uses": n, "maps_to": "; ".join(maps)})

    # 2. SHACL
    t0 = time.time()
    conforms, results, _ = validate(g, shacl_graph=shapes, inference="none", abort_on_first=False, meta_shacl=False,
                                    advanced=False, allow_warnings=True, allow_infos=True)
    groups = defaultdict(lambda: {"results": 0, "focus": set()})
    for r in results.subjects(RDF.type, SH.ValidationResult):
        k = (path_str(results, results.value(r, SH.resultPath)), short(results.value(r, SH.sourceConstraintComponent)).replace("sh:", ""),
             short(results.value(r, SH.resultSeverity)).replace("sh:", ""))
        groups[k]["results"] += 1
        groups[k]["focus"].add(results.value(r, SH.focusNode))
    shacl_rows = sorted(({"path": k[0], "constraint": k[1], "severity": k[2], "results": v["results"], "focus_nodes": len(v["focus"])}
                         for k, v in groups.items()), key=lambda r: (-r["results"], r["path"]))
    total = sum(r["results"] for r in shacl_rows)
    focus = len({f for v in groups.values() for f in v["focus"]})

    summary = {"graph": os.path.relpath(a.graph, REPO), "triples": len(g), "ontology_version": version,
               "undeclared_classes": len(cls), "undeclared_properties": len(props), "undeclared_iri_values": len(used_values),
               "extension_terms": len(ext),
               "shacl_conforms": conforms, "shacl_results": total, "shacl_focus_nodes": focus, "shacl_groups": len(shacl_rows),
               "shacl_seconds": round(time.time() - t0, 1)}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"summary": summary, "undeclared": undeclared, "extension": ext, "shacl": shacl_rows}, open(out + ".json", "w"), indent=1)
    L = [f"# Alignment of `{summary['graph']}` with the HeritageGraph ontology {', '.join(version)}", "",
         "Generated by `tools/sync/check_alignment.py`; do not edit by hand. Ontology files: `ontology/` (see `ontology/SOURCE.md`).", "",
         "## Summary", "", "| check | value |", "|---|---|"]
    L += [f"| {k.replace('_', ' ')} | {v:,} |" if isinstance(v, int) and not isinstance(v, bool) else f"| {k.replace('_', ' ')} | {v} |" for k, v in summary.items()]
    L += ["", "## 1. Terms used but not declared in the ontology", "",
          "*LinkML* = a class or slot of the same name in the ontology's LinkML source. *Ontology IRI* = the IRI that LinkML "
          "class or slot is published under, i.e. the declared term the ontology means (an exact equivalent). Empty = the "
          "ontology has no such term.", "",
          "| kind | term | uses | LinkML | ontology IRI |", "|---|---|---|---|---|"]
    L += [f"| {u['kind']} | `{u['term']}` | {u['uses']:,} | {u['linkml'] or '—'} | {('`' + u['ontology_iri'] + '`') if u['ontology_iri'] else '—'} |" for u in undeclared]
    L += ["", "## 1b. Extension terms in use (vocab/hgn.ttl)", "", "| kind | term | uses | maps to |", "|---|---|---|---|"]
    L += [f"| {e['kind']} | `{e['term']}` | {e['uses']:,} | {e['maps_to'] or '—'} |" for e in ext]
    L += ["", "## 2. SHACL results by property and constraint", "",
          f"pySHACL, ontology shapes, no inference, the whole graph. Conforms: **{conforms}**; {total:,} results on {focus:,} focus nodes.", "",
          "| path | constraint | severity | results | focus nodes |", "|---|---|---|---|---|"]
    L += [f"| `{r['path']}` | {r['constraint']} | {r['severity']} | {r['results']:,} | {r['focus_nodes']:,} |" for r in shacl_rows]
    open(out + ".md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
