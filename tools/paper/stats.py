"""Facts and numbers for the HeritageGraph-Nepal dataset paper.

Builds the graph from the same inputs as the sync checks (tests/conftest.py) into a scratch directory, measures it, and
writes two files, so that every number in the paper comes from one run of this script:
  docs/paper/numbers.tex   one LaTeX macro per number, e.g. \\newcommand{\\numMonuments}{1{,}652}
  docs/paper/FACTS.md      the facts, sections A-K; every number in it is produced here, none is typed by hand

Usage:
  python tools/paper/stats.py [--build-dir build/paper] [--out-dir docs/paper] [--skip-owlrl] [--check-iris]

--skip-owlrl   skip the OWL 2 RL closure (slow); section D then says it was not run
--check-iris   make one HTTP request to a dataset instance IRI to see whether it resolves (off by default)
Never writes to releases/ or latest/.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import date
from importlib.metadata import version as pkg_version

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [REPO, os.path.join(REPO, "tests")]
csv.field_size_limit(10**9)

import build_kg  # noqa: E402
from conftest import EVENTS, MONUMENTS, OBJECTS  # noqa: E402
from rdflib import BNode, Graph, Literal, Namespace, URIRef  # noqa: E402
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD  # noqa: E402

HG, CRM, PROV, HGN, RES = build_kg.HG, build_kg.CRM, build_kg.PROV, build_kg.HGN, build_kg.RES
GEO = build_kg.GEO
EXPORTS = os.path.join(REPO, "data_collection", "data", "exports")
RAW = os.path.join(REPO, "data_collection", "data", "raw")
PREFIXES = {str(HG): "hg:", str(HGN): "hgn:", str(CRM): "crm:", str(PROV): "prov:", str(RES): "res:", str(RDFS): "rdfs:",
            str(SKOS): "skos:", str(DCTERMS): "dcterms:", str(GEO): "geo:", "http://www.opengis.net/ont/geosparql#": "geosparql:",
            "https://schema.org/": "schema:", "http://vocab.getty.edu/aat/": "aat:", str(OWL): "owl:", str(RDF): "rdf:"}


def short(t) -> str:
    s = str(t)
    for ns, p in PREFIXES.items():
        if s.startswith(ns):
            return p + s[len(ns):]
    return s


# ── number registry: every number goes through N(), which also defines its LaTeX macro ─────────────────────────────

DIGITS = "Zero One Two Three Four Five Six Seven Eight Nine".split()
MACROS: dict[str, str] = {}


def macro_name(key: str) -> str:
    key = re.sub(r"\d", lambda m: DIGITS[int(m.group())], key)
    words = re.findall(r"[A-Za-z]+", key)
    return "num" + "".join(w[:1].upper() + w[1:] for w in words)


def N(key: str, value, digits: int = 1) -> str:
    """Register a number under a macro name; return it formatted for Markdown."""
    name = macro_name(key)
    if isinstance(value, float):
        md = f"{value:,.{digits}f}"
    else:
        md = f"{int(value):,}"
    tex = md.replace(",", "{,}")
    if name in MACROS and MACROS[name] != tex:
        raise ValueError(f"macro {name} defined twice with different values")
    MACROS[name] = tex
    return md


def pct(part: int, whole: int) -> float:
    return 100.0 * part / whole if whole else 0.0


def md_table(header: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in r) + " |" for r in rows]
    return out


def read_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


# ── the DANAM field → graph mapping (documentation; coverage numbers are computed) ─────────────────────────────────

MONUMENT_FIELDS = {
    "resource_id": "`crm:P1_is_identified_by` → `crm:E42_Identifier` of kind `hgn:DanamResourceId`; also the monument IRI",
    "url": "`prov:wasDerivedFrom` and `schema:url` → the DANAM page (`prov:Entity`)",
    "scraped_at": "`prov:generatedAtTime`",
    "status": "not used",
    "monument_name": "`rdfs:label`, `skos:prefLabel @en`, `dcterms:title`",
    "anglicized_name": "`schema:alternateName` (when different from the name)",
    "name_devanagari": "used only when `name_ne` is empty: `schema:name @ne`, `skos:prefLabel @ne`",
    "monument_type": "only when `ontology_class` is empty: keyword rules give the class",
    "main_deity": "`hgn:hasMainDeity` → `hg:Deity`",
    "religion": "`hg:hasReligiousTradition` → `hgn:tradition-…` (`hg:ReligiousTradition`); \"Unspecified\" gives none",
    "province": "`crm:E53_Place` with `hg:placeType` \"province\", in the `crm:P89_falls_within` chain",
    "district": "`crm:E53_Place` with `hg:placeType` \"district\"",
    "municipality": "`crm:E53_Place` with `hg:placeType` \"municipality\"",
    "tola": "`crm:E53_Place` with `hg:placeType` \"tola\"; the lowest level present is the monument's `crm:P55_has_current_location`",
    "coordinates_lat": "`geo:lat`; with the longitude, `geosparql:hasGeometry` → WKT point",
    "coordinates_lon": "`geo:long`",
    "coordinates_geojson": "not used (same point as lat/lon)",
    "description_en": "not used (source text for event extraction; not written to the graph)",
    "description_ne": "not used",
    "num_storeys": "`hgn:numberOfStoreys` (whole numbers only)",
    "monument_length": "not used", "monument_depth": "not used", "monument_height": "not used", "monument_diameter": "not used",
    "monument_shape": "`crm:P2_has_type` → `crm:E55_Type` in `res:scheme/shape`",
    "num_roofs": "`hgn:numberOfRoofs` (whole numbers only)",
    "roof_type": "`crm:P2_has_type` → `crm:E55_Type` in `res:scheme/roof-type`",
    "wall_thickness": "not used",
    "brick_type": "`crm:P2_has_type` → `crm:E55_Type` in `res:scheme/brick-type`",
    "num_plinth": "not used", "base_plinth_width": "not used", "base_plinth_depth": "not used", "base_plinth_height": "not used",
    "top_plinth_width": "not used", "top_plinth_depth": "not used", "top_plinth_height": "not used",
    "profile_at_base": "not used", "edge_at_platform": "not used", "platform_floor": "not used",
    "monument_assessment": "`crm:E14_Condition_Assessment` (`crm:P34i_was_assessed_by`) with `crm:P3_has_note`, `rdfs:comment`",
    "identified_threats": "`hgn:identifiedThreats` on the assessment",
    "references": "`dcterms:references` (text)",
    "editorial_team": "not used",
    "event_count": "not used (DANAM's counter)", "object_count": "not used (DANAM's counter)",
    "danam_code": "`crm:E42_Identifier` of kind `hgn:DanamCode`; `owl:sameAs` `res:monument/<code>` (derived in staging)",
    "name_ne": "`schema:name @ne`, `skos:prefLabel @ne` (derived in staging)",
    "ontology_class": "`rdf:type` `hg:<class>` (or `hgn:BuddhistMonument`) (derived in staging)",
    "aat_style": "`crm:P2_has_type` → `aat:` concept; first mapped one also `hg:hasArchitecturalStyle` → `hg:ArchitecturalStyle#…` (derived in staging)",
    "condition_types": "`hgn:conditionStatus` (all values); first one `hg:hasConditionType` on the `crm:E3_Condition_State` (derived in staging)",
    "mapping_notes": "not used (staging notes)",
}
EVENT_FIELDS = {
    "resource_id": "`crm:P12_occurred_in_the_presence_of` → monument (inverse `crm:P12i_was_present_at`)",
    "monument_name": "not used (key check only)",
    "event_index": "part of the event IRI `res:event/<resource_id>_<index>`",
    "event_name": "`rdfs:label`; with the description, keyword rules give the class",
    "event_description": "`dcterms:description`, `rdfs:comment`",
    "date_bce_ce": "`hg:dateBCE_CE`; its year `hg:calendarYear`",
    "period": "`hg:historicalPeriod`",
    "year_ss_ns_vs": "`hg:inscriptionalDateEra`",
    "nepali_month": "`hg:nepaliMonth`", "paksha": "`hg:paksha`", "tithi": "`hg:tithi`",
    "sources": "`dcterms:source`, `prov:hadPrimarySource` (text)",
}
OBJECT_FIELDS = {
    "resource_id": "`hgn:isObjectOf` (or `crm:P46i_forms_part_of` for architectural elements) → monument",
    "monument_name": "not used (key check only)",
    "object_index": "not used",
    "object_id": "object IRI `res:object/<number>`; `crm:E42_Identifier` of kind `hgn:DanamObjectNumber`",
    "object_name": "`rdfs:label`; with the type, keyword rules give the class",
    "object_type": "`hg:objectType` (text)",
    "object_material": "`hg:material` and `crm:P45_consists_of` (text)",
    "object_location": "`hg:locationWithinMonument` (text)",
    "date_bce_ce": "`hg:dateBCE_CE`",
    "date_vs_ns": "`hg:inscriptionalDateEra`",
}

QUESTIONS = {
    "01_monuments_by_aat_style.rq": "Which monuments have which architectural style (Getty AAT concept), and what are their DANAM codes?",
    "02_historical_timeline.rq": "What events happened at each monument, of what type (one row per event and type), and in which period or era year?",
    "03_spatial_geosparql.rq": "Where is each monument: coordinates, point geometry, district, municipality and tola?",
    "04_monument_sacred_objects.rq": "Which objects does each monument contain or consist of, with class, DANAM number, material and position?",
    "05_provenance_audit.rq": "For each event, which DANAM page is it derived from, who is that page attributed to, and which software (repository, commit) built the graph on whose behalf?",
    "06_condition_threats.rq": "What condition does DANAM record for each monument, and which threats and assessments?",
    "07_deities_traditions.rq": "Which main deity and which religious traditions does each monument have?",
}

WORKED_EXAMPLE = "0077a8d9-2e9d-4626-8dd0-04272b780ea9"


# ── main ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build-dir", default=os.path.join(REPO, "build", "paper"))
    ap.add_argument("--out-dir", default=os.path.join(REPO, "docs", "paper"))
    ap.add_argument("--skip-owlrl", action="store_true")
    ap.add_argument("--check-iris", action="store_true")
    a = ap.parse_args()
    for d in (a.build_dir, a.out_dir):
        if os.path.abspath(d).startswith((os.path.join(REPO, "releases"), os.path.join(REPO, "latest"))):
            sys.exit("refusing to write into releases/ or latest/")
    os.makedirs(a.build_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    L: list[str] = []

    # ── build (timed) ────────────────────────────────────────────────────────────────────────────────────────────
    t0 = time.time()
    g, _ = build_kg.build_knowledge_graph(MONUMENTS, EVENTS, OBJECTS)
    t_build = time.time() - t0
    files = {}
    t0 = time.time()
    for fmt, name in (("turtle", "heritagegraph-nepal.ttl"), ("nt", "heritagegraph-nepal.nt"), ("json-ld", "heritagegraph-nepal.jsonld")):
        path = os.path.join(a.build_dir, name)
        g.serialize(path, format=fmt, encoding="utf-8")
        files[fmt] = path
    with open(files["nt"], "rb") as src, gzip.open(files["nt"] + ".gz", "wb") as dst:
        dst.write(src.read())
    files["nt.gz"] = files["nt"] + ".gz"
    t_serialize = time.time() - t0

    # staging step, rerun into the scratch directory (timed), to check it reproduces staging/monuments.csv
    stage_dir = os.path.join(a.build_dir, "staging")
    t0 = time.time()
    prep = subprocess.run([sys.executable, os.path.join(REPO, ".agents", "skills", "danam-to-heritagegraph", "scripts", "prepare.py"),
                           "--input", os.path.join(EXPORTS, "monuments.csv"), "--outdir", stage_dir], capture_output=True, text=True)
    t_stage = time.time() - t0
    stage_ok = prep.returncode == 0 and os.path.exists(os.path.join(stage_dir, "monuments.csv"))
    stage_same = stage_ok and read_csv(os.path.join(stage_dir, "monuments.csv")) == read_csv(MONUMENTS)

    # alignment check (undeclared terms, SHACL)
    t0 = time.time()
    chk = subprocess.run([sys.executable, os.path.join(REPO, "tools", "sync", "check_alignment.py"), "--graph", files["nt"],
                          "--out", os.path.join(a.build_dir, "alignment")], capture_output=True, text=True, check=True)
    t_check = time.time() - t0
    align = json.load(open(os.path.join(a.build_dir, "alignment.json")))

    # ── A. Versions ──────────────────────────────────────────────────────────────────────────────────────────────
    onto = Graph().parse(os.path.join(REPO, "ontology", "HeritageGraph.ttl"))
    onto_version = ", ".join(str(v) for v in onto.objects(None, OWL.versionInfo))
    source_md = open(os.path.join(REPO, "ontology", "SOURCE.md"), encoding="utf-8").read()
    onto_commit = (re.search(r"\b(f2f1780[0-9a-f]*)\b", source_md) or re.search(r"\b([0-9a-f]{7,40})\b", source_md)).group(1)
    commit, dirty = git("rev-parse", "HEAD"), git("status", "--porcelain", "--untracked-files=no")
    L += [f"# Facts and numbers for the HeritageGraph-Nepal paper", "",
          f"Generated by `tools/paper/stats.py` on {date.today().isoformat()}; do not edit by hand. Every number here is also a "
          "LaTeX macro in `numbers.tex`. Rerun the script after any change to the builder or data.", "",
          "## A. Versions", ""]
    L += md_table(["item", "version"], [
        ["Dataset commit (this build)", f"`{commit[:10]}`" + (" (with uncommitted changes)" if dirty else "")],
        ["HeritageGraph ontology", f"{onto_version}, commit `{onto_commit}` (vendored in `ontology/`, see `ontology/SOURCE.md`)"],
        ["Python", platform.python_version()],
        ["rdflib", pkg_version("rdflib")], ["pySHACL", pkg_version("pyshacl")], ["owlrl", pkg_version("owlrl")],
        ["Machine", f"{platform.system()} {platform.machine()}"],
    ])

    # ── B. Source funnel ─────────────────────────────────────────────────────────────────────────────────────────
    ids = read_csv(os.path.join(REPO, "data_collection", "resourceids.csv"))
    id_col = next(iter(ids[0]))
    raw_json = [f for f in os.listdir(RAW) if f.endswith(".json")]
    id_values = [r[id_col].strip() for r in ids]
    real_ids = {v for v in id_values if v}
    no_raw = sorted(real_ids - {f[:-5] for f in raw_json})
    raw_status = {f[:-5]: json.load(open(os.path.join(RAW, f), encoding="utf-8")) for f in raw_json}
    failed = {k: v for k, v in raw_status.items() if v.get("status") != "ok"}
    timeouts = sum("Timeout" in (v.get("error") or "") for v in failed.values())
    resets = sum("ERR_CONNECTION_RESET" in (v.get("error") or "") for v in failed.values())
    export_mon = read_csv(os.path.join(EXPORTS, "monuments.csv"))
    skipped = read_csv(os.path.join(REPO, "staging", "skipped_rows.csv"))
    mons = read_csv(MONUMENTS)
    mon_by_id = {m["resource_id"]: m for m in mons}
    ev_rows, ob_rows = read_csv(EVENTS), read_csv(OBJECTS)
    ev_kept = [r for r in ev_rows if r["resource_id"] in mon_by_id]
    ob_kept = [r for r in ob_rows if r["resource_id"] in mon_by_id]
    L += ["", "## B. Source funnel", ""]
    L += md_table(["stage", "count", "source"], [
        ["Record IDs listed", N("SourceIdRows", len(ids)), "`data_collection/resourceids.csv`, rows"],
        ["Blank rows", N("SourceIdBlank", sum(1 for v in id_values if not v)), "same file, rows with an empty ID (`\"\"`)"],
        ["Distinct record IDs", N("SourceIdsDistinct", len(real_ids)), "same file, distinct non-empty values"],
        ["IDs without a raw file", N("SourceIdsNoRaw", len(no_raw)), ", ".join(no_raw) or "every ID has one"],
        ["Records collected (raw JSON)", N("SourceRawJson", len(raw_json)), "`data_collection/data/raw/*.json`"],
        ["Failed fetches", N("SourceFailed", len(failed)),
         f"raw JSON with `status: error`, not retried: {N('SourceFailedTimeout', timeouts)} page-load timeouts (30 s), "
         f"{N('SourceFailedReset', resets)} connection resets (`data_collection/scraper.log`)"],
        ["Records parsed (exported)", N("SourceParsed", len(export_mon)), "`data_collection/data/exports/monuments.csv`, rows"],
        ["DANAM fields per record", N("SourceFields", len(export_mon[0])), "columns of the export"],
        ["Empty records (skipped)", N("SourceEmpty", len(skipped)), "`staging/skipped_rows.csv`, rows"],
        ["Monuments", N("Monuments", len(mons)), "`staging/monuments.csv`, rows"],
        ["Staged columns (DANAM + derived)", N("StagedColumns", len(mons[0])), "columns of `staging/monuments.csv`"],
        ["Event rows", N("EventRows", len(ev_rows)), "`data_collection/data/exports/events.csv`"],
        ["Event rows of kept monuments", N("EventRowsKept", len(ev_kept)), "same, `resource_id` in staging"],
        ["Object rows", N("ObjectRows", len(ob_rows)), "`data_collection/data/exports/objects.csv`"],
        ["Object rows of kept monuments", N("ObjectRowsKept", len(ob_kept)), "same, `resource_id` in staging"],
        ["Distinct object numbers", N("ObjectIdsDistinct", len({r['object_id'].strip() for r in ob_kept if r['object_id'].strip()})), "`object_id`, kept rows"],
    ])
    scraped = sorted(m["scraped_at"][:10] for m in mons if m.get("scraped_at"))
    L += ["", f"Collection dates (`scraped_at`): {scraped[0]} to {scraped[-1]}."]

    # ── C. Graph statistics ──────────────────────────────────────────────────────────────────────────────────────
    typed = defaultdict(set)
    for s, o in g.subject_objects(RDF.type):
        typed[o].add(s)
    monuments = typed[HG.ArchitecturalStructure]
    events = typed[CRM.E5_Event]
    objects = set(g.subjects(HGN.isObjectOf, None)) | set(g.subjects(CRM.P46i_forms_part_of, None))
    L += ["", "## C. Graph statistics", ""]
    L += md_table(["measure", "count"], [
        ["Triples", N("Triples", len(g))],
        ["Distinct subjects", N("Subjects", len(set(g.subjects())))],
        ["Classes used (`rdf:type` objects)", N("ClassesUsed", len(typed))],
        ["Properties used", N("PropertiesUsed", len(set(g.predicates())))],
        ["Monuments", N("Monuments", len(monuments))],
        ["Events", N("Events", len(events))],
        ["Objects", N("Objects", len(objects))],
        ["Condition assessments of monuments", N("Assessments", len(set(g.objects(None, CRM.P34i_was_assessed_by))))],
        ["Places", N("Places", len(typed[CRM.E53_Place]))],
        ["Deities", N("Deities", len(typed[HG.Deity]))],
        ["Point geometries", N("Geometries", len(set(g.objects(None, URIRef("http://www.opengis.net/ont/geosparql#hasGeometry")))))],
    ])
    L += ["", "**Instances per class (top 20)**", ""]
    top = sorted(((len(v), short(k)) for k, v in typed.items()), reverse=True)[:20]
    L += md_table(["class", "instances"], [[f"`{c}`", N(f"Class {c.replace(':', ' ')}", n)] for n, c in top])

    ev_per = [sum(1 for _ in g.objects(m, CRM.P12i_was_present_at)) for m in monuments]
    ob_per = [sum(1 for _ in g.objects(m, HGN.containsObject)) + sum(1 for _ in g.objects(m, CRM.P46_is_composed_of)) for m in monuments]
    L += ["", "**Per monument**", ""]
    L += md_table(["", "min", "median", "max", "monuments with none"], [
        ["events", N("EventsPerMonumentMin", min(ev_per)), N("EventsPerMonumentMedian", float(statistics.median(ev_per))),
         N("EventsPerMonumentMax", max(ev_per)), N("MonumentsWithoutEvents", ev_per.count(0))],
        ["objects", N("ObjectsPerMonumentMin", min(ob_per)), N("ObjectsPerMonumentMedian", float(statistics.median(ob_per))),
         N("ObjectsPerMonumentMax", max(ob_per)), N("MonumentsWithoutObjects", ob_per.count(0))],
    ])

    def has(p, m, test=None):
        return any(test(o) if test else True for o in g.objects(m, p))
    def has_type_in(scheme):
        return lambda m: any((t, SKOS.inScheme, RES[f"scheme/{scheme}"]) in g for t in g.objects(m, CRM.P2_has_type))
    nM = len(monuments)
    coverage = [
        ("Architectural style (ontology value)", lambda m: has(HG.hasArchitecturalStyle, m)),
        ("AAT style concept", lambda m: has(CRM.P2_has_type, m, lambda o: str(o).startswith("http://vocab.getty.edu/aat/"))),
        ("Condition assessment", lambda m: has(CRM.P34i_was_assessed_by, m)),
        ("Condition value", lambda m: has(HGN.conditionStatus, m)),
        ("Identified threats", lambda m: any((x, HGN.identifiedThreats, None) in g for x in g.objects(m, CRM.P34i_was_assessed_by))),
        ("Location (place)", lambda m: has(CRM.P55_has_current_location, m)),
        ("Coordinates", lambda m: has(GEO.lat, m)),
        ("Main deity", lambda m: has(HGN.hasMainDeity, m)),
        ("Religious tradition", lambda m: has(HG.hasReligiousTradition, m)),
        ("Number of storeys", lambda m: has(HGN.numberOfStoreys, m)),
        ("Number of roofs", lambda m: has(HGN.numberOfRoofs, m)),
        ("Roof type", has_type_in("roof-type")),
        ("Brick / masonry type", has_type_in("brick-type")),
        ("Ground-plan shape", has_type_in("shape")),
        ("DANAM code", lambda m: any((i, CRM.P2_has_type, HGN.DanamCode) in g for i in g.objects(m, CRM.P1_is_identified_by))),
        ("Nepali name", lambda m: any(getattr(o, "language", None) == "ne" for o in g.objects(m, SKOS.prefLabel))),
        ("References text", lambda m: has(DCTERMS.references, m)),
        ("At least one event", lambda m: has(CRM.P12i_was_present_at, m)),
        ("At least one object", lambda m: has(HGN.containsObject, m) or has(CRM.P46_is_composed_of, m)),
    ]
    L += ["", f"**Field coverage** (share of the {N('Monuments', nM)} monuments)", ""]
    rows = []
    for label, test in coverage:
        n = sum(1 for m in monuments if test(m))
        rows.append([label, N(f"Coverage {label} N", n), N(f"Coverage {label} Pct", pct(n, nM)) + " %"])
    L += md_table(["field", "monuments", "share"], rows)

    def dist(title, key, counter, total=None):
        nonlocal L
        L += ["", f"**{title}**", ""]
        rs = [[k, N(f"{key} {k}", v)] + ([N(f"{key} {k} Pct", pct(v, total)) + " %"] if total else []) for k, v in counter.most_common()]
        L += md_table(["value", "monuments"] + (["share"] if total else []), rs)

    mtype = Counter()
    for c in (HG.Temple, HG.Pati, HG.Sattal, HG.Chaitya, HG.Stupa, HG.Dharmashala, HG.DhungeDhara, HG.Pokhari, HG.KumariHouse, HGN.BuddhistMonument):
        if typed[c] & monuments:
            mtype[short(c)] = len(typed[c] & monuments)
    mtype["only hg:ArchitecturalStructure (no subtype)"] = sum(
        1 for m in monuments if not any(short(t) in mtype for t in g.objects(m, RDF.type)))
    dist("Monument types (a monument can have more than one)", "Type", mtype)
    styles = Counter(short(g.value(m, HG.hasArchitecturalStyle)).split("#")[-1] if g.value(m, HG.hasArchitecturalStyle) else "none recorded" for m in monuments)
    dist("Architectural style (ontology value)", "Style", styles, nM)
    cond = Counter()
    for m in monuments:
        st = [g.value(s, HG.hasConditionType) for a_ in g.objects(m, CRM.P34i_was_assessed_by) for s in g.objects(a_, CRM.P35_has_identified)]
        st = [s for s in st if s is not None]
        cond[str(st[0]).split("#")[-1] if st else "none recorded"] += 1
    dist("Condition (first value DANAM lists, on the condition state)", "Condition", cond, nM)
    trad = Counter()
    for m in monuments:
        ts = [str(g.value(t, RDFS.label)) for t in g.objects(m, HG.hasReligiousTradition)]
        for t in ts:
            trad[t] += 1
        if not ts:
            trad["none recorded"] += 1
    dist("Religious tradition (a monument can have more than one)", "Tradition", trad, nM)
    district = Counter()
    for m in monuments:
        p, d = g.value(m, CRM.P55_has_current_location), None
        while p is not None:
            if str(g.value(p, HG.placeType)) == "district":
                d = str(g.value(p, RDFS.label))
            p = g.value(p, CRM.P89_falls_within)
        district[d or "not stated"] += 1
    dist("District (as DANAM states it)", "District", district, nM)
    province = Counter((("Province " + m["province"].strip()) if m["province"].strip() else "not stated") for m in mons)
    dist("Province (as DANAM states it)", "Province", province, nM)

    L += ["", "**File sizes** (this build, scratch directory)", ""]
    L += md_table(["file", "MB"], [[os.path.basename(p), N(f"Size {k}", os.path.getsize(p) / 1e6) + " MB"]
                                    for k, p in (("ttl", files["turtle"]), ("jsonld", files["json-ld"]), ("nt", files["nt"]), ("ntgz", files["nt.gz"]))])

    # ── D. Validation ────────────────────────────────────────────────────────────────────────────────────────────
    s = align["summary"]
    L += ["", "## D. Validation", "", f"Ontology {onto_version} shapes, pySHACL without inference, whole graph "
          f"(`tools/sync/check_alignment.py`, {N('CheckSeconds', t_check, 0)} s).", ""]
    L += md_table(["path", "constraint", "results", "focus nodes"],
                  [[f"`{r['path']}`", r["constraint"], N(f"Shacl {r['path']} {r['constraint']}", r["results"]), r["focus_nodes"]] for r in align["shacl"]])
    L += ["", f"SHACL results in total: **{N('ShaclResults', s['shacl_results'])}**. Undeclared terms (classes, properties, "
          f"values in `hg:`/`hgn:` declared neither by the ontology nor by `vocab/hgn.ttl`): **"
          f"{N('UndeclaredTerms', s['undeclared_classes'] + s['undeclared_properties'] + s['undeclared_iri_values'])}**."]
    temples_no_style = sorted(m for m in typed[HG.Temple] if g.value(m, HG.hasArchitecturalStyle) is None)
    L += ["", f"The remaining results are the {N('TemplesWithoutStyle', len(temples_no_style))} temples for which DANAM records no "
          "architectural style: every `hg:Temple` must have one (`sh:minCount 1`), and none is guessed."]
    # sync table from the log
    log = open(os.path.join(REPO, "docs", "sync", "SYNC_LOG.md"), encoding="utf-8").read()
    steps = []
    for block in re.split(r"\n(?=## )", log):
        mh = re.match(r"## (\S+): (.+)", block)
        sh = re.search(r"SHACL results: (?:[\d,]+ → )?\*\*([\d,]+)\*\*", block)
        un = re.search(r"Undeclared terms: (?:[\d,]+ → )?\*\*([\d,]+)\*\*", block)
        if mh and sh:
            steps.append((mh.group(1), mh.group(2), int(sh.group(1).replace(",", "")), int(un.group(1).replace(",", "")) if un else None))
    L += ["", "**Alignment steps** (from `docs/sync/SYNC_LOG.md`; each step has a test and its own commit)", ""]
    L += md_table(["step", "change", "SHACL results after", "undeclared terms after"],
                  [[i, t, N(f"Sync {i} Shacl", sh_), N(f"Sync {i} Undeclared", un_) if un_ is not None else ""] for i, t, sh_, un_ in steps])
    if steps:
        L += ["", f"From the baseline to the end: SHACL results {N('ShaclBaseline', steps[0][2])} → {N('ShaclFinal', steps[-1][2])}, "
              f"undeclared terms {N('UndeclaredBaseline', steps[0][3])} → {N('UndeclaredFinal', steps[-1][3])}, in {N('SyncSteps', len(steps) - 1)} steps."]
    # OWL 2 RL closure
    L += ["", "**OWL 2 RL closure** (owlrl, graph plus the ontology, no axiomatic or datatype triples)", ""]
    if a.skip_owlrl:
        L += ["Not run in this build (`--skip-owlrl`)."]
    else:
        import owlrl
        from owlrl.Closure import ERRNS as _ERRNS
        cg = Graph()
        for t in g:
            cg.add(t)
        cg.parse(os.path.join(REPO, "ontology", "HeritageGraph.ttl"))
        before = len(cg)
        t0 = time.time()
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics, axiomatic_triples=False, datatype_axioms=False).expand(cg)
        t_rl = time.time() - t0
        errs = [str(o) for e in cg.subjects(RDF.type, _ERRNS.ErrorMessage) for o in cg.objects(e, _ERRNS.error)]
        nothing = len(set(cg.subjects(RDF.type, OWL.Nothing)))
        L += md_table(["measure", "value"], [
            ["Triples before (graph + ontology)", N("RlBefore", before)], ["Triples after closure", N("RlAfter", len(cg))],
            ["Inferred triples", N("RlInferred", len(cg) - before)], ["Inconsistency messages", N("RlErrors", len(errs))],
            ["Individuals typed `owl:Nothing`", N("RlNothing", nothing)], ["Seconds", N("RlSeconds", t_rl, 0)]])
        if errs:
            kinds = Counter(re.sub(r"<[^>]+>|\"[^\"]*\"", "…", e)[:160] for e in errs)
            L += ["", "Inconsistency messages, grouped:", ""] + md_table(["message (IRIs elided)", "count"], [[k, N(f"Rl Err {i}", v)] for i, (k, v) in enumerate(kinds.most_common(10))])

    # ── E. Mapping table ─────────────────────────────────────────────────────────────────────────────────────────
    L += ["", "## E. Mapping: DANAM field → graph", "",
          "Coverage = records with a non-empty value. \"Derived\" columns are added in staging (`prepare.py`).", ""]
    for title, key, table, rows_ in (("Monument record (`staging/monuments.csv`)", "Mon", MONUMENT_FIELDS, mons),
                                     ("Event table (`events.csv`)", "Ev", EVENT_FIELDS, ev_kept),
                                     ("Object table (`objects.csv`)", "Ob", OBJECT_FIELDS, ob_kept)):
        cols = list(rows_[0])
        missing = [c for c in cols if c not in table]
        if missing:
            raise SystemExit(f"mapping table lacks fields: {missing}")
        L += [f"**{title}**", ""]
        L += md_table(["field", "non-empty", "written as"],
                      [[f"`{c}`", N(f"Field {key} {c}", sum(1 for r in rows_ if (r.get(c) or "").strip())), table[c]] for c in cols])
        L += [""]
    used = sum(1 for c in mons[0] if not MONUMENT_FIELDS[c].startswith("not used"))
    L += [f"Of the {N('StagedColumns', len(mons[0]))} monument columns, {N('MonumentFieldsUsed', used)} are written to the graph."]

    # ── F. Extension vocabulary ──────────────────────────────────────────────────────────────────────────────────
    vocab = Graph().parse(os.path.join(REPO, "vocab", "hgn.ttl"))
    ext = align.get("extension", [])
    L += ["", "## F. Extension vocabulary (`vocab/hgn.ttl`)", "",
          f"Namespace `{build_kg.HGN_BASE}` (provisional). Terms in use: **{N('ExtensionTerms', len(ext))}** "
          f"({N('ExtensionProperties', sum(1 for e in ext if e['kind'] == 'property'))} properties, "
          f"{N('ExtensionClasses', sum(1 for e in ext if e['kind'] == 'class'))} class, "
          f"{N('ExtensionConcepts', sum(1 for e in ext if e['kind'] == 'concept'))} concepts and schemes).", ""]
    L += md_table(["kind", "term", "label", "maps to", "uses"],
                  [[e["kind"], f"`{e['term']}`", str(vocab.value(URIRef(e["term"].replace("hgn:", build_kg.HGN_BASE)), RDFS.label) or ""),
                    e["maps_to"] or "—", N(f"Ext {e['term'].replace('hgn:', '')}", e["uses"])] for e in ext])

    # ── G. Source issues ─────────────────────────────────────────────────────────────────────────────────────────
    L += ["", "## G. Source issues (reported, not corrected; details in `docs/sync/SOURCE_ISSUES.md`)", ""]
    by_number = defaultdict(list)
    for r in ob_kept:
        if r["object_id"].strip():
            by_number[r["object_id"].strip()].append(r)
    reused = {k: v for k, v in by_number.items() if len(v) > 1}
    codes = defaultdict(list)
    for m in mons:
        if m["danam_code"].strip():
            codes[m["danam_code"].strip()].append(m)
    shared = {k: v for k, v in codes.items() if len(v) > 1}
    rel_only = [m for m in mons if m["religion"].strip() == "Unspecified"]
    rel_combo = [m for m in mons if "Unspecified" in build_kg.split_listed(m["religion"]) and m["religion"].strip() != "Unspecified"]
    ll_sep = [m for m in mons if re.search(r"\sll\s", m.get("name_devanagari", ""))]
    ex_reused = next(iter(sorted(reused)))
    ex_temple = mon_by_id[str(temples_no_style[0]).rsplit("/", 1)[1]] if temples_no_style else None
    sun = by_number.get("SUN0010-004", [])
    rows = [
        ["Object number given to two objects", N("ReusedObjectNumbers", len(reused)),
         f"{ex_reused}: " + "; ".join(r["object_name"] for r in reused[ex_reused]) + f" ({mon_by_id[reused[ex_reused][0]['resource_id']]['url']})"],
        ["SUN0010-004: probably one statue listed twice", N("SunListedTwice", len(sun)),
         "; ".join(r["object_name"] for r in sun) + (f" ({mon_by_id[sun[0]['resource_id']]['url']})" if sun else "")],
        ["DANAM code shared by two records", N("SharedDanamCodes", len(shared)),
         "; ".join(f"{k}: " + ", ".join(m["url"] for m in v) for k, v in shared.items()) + " (one record is an empty duplicate)"],
        ["Code written after `ll` instead of `||`", N("CodeSeparatorLl", len(ll_sep)), ", ".join(m["url"] for m in ll_sep[:2])],
        ["Temple without a style", N("TemplesWithoutStyle", len(temples_no_style)),
         f"{ex_temple['monument_name']} ({ex_temple['url']})" if ex_temple else ""],
        ["Religion \"Unspecified\" (alone)", N("ReligionUnspecified", len(rel_only)), f"{rel_only[0]['monument_name']} ({rel_only[0]['url']})"],
        ["Religion \"Unspecified\" in a combination", N("ReligionUnspecifiedCombo", len(rel_combo)),
         f"\"{rel_combo[0]['religion']}\": {rel_combo[0]['monument_name']} ({rel_combo[0]['url']})"],
        ["Half-storey values (not written)", N("HalfStoreys", sum(1 for m in mons if re.fullmatch(r"\d+\.\d+", m["num_storeys"].strip()))),
         ", ".join(sorted({m["num_storeys"].strip() for m in mons if re.fullmatch(r"\d+\.\d+", m["num_storeys"].strip())}))],
    ]
    L += md_table(["issue", "count", "example"], rows)

    # ── H. Competency questions ──────────────────────────────────────────────────────────────────────────────────
    L += ["", "## H. Competency questions (`queries/`)", "",
          "Row counts are without the queries' `LIMIT`; example rows are the three most complete rows (fewest empty cells), in the query's order.", ""]
    for p in sorted(f for f in os.listdir(os.path.join(REPO, "queries")) if f.endswith(".rq")):
        text = open(os.path.join(REPO, "queries", p), encoding="utf-8").read()
        body = re.sub(r"(?im)^\s*LIMIT\s+\d+\s*$", "", text)
        qres = g.query(body)
        res = list(qres)
        L += [f"**{p}**: {QUESTIONS.get(p, '(no question text)')} Rows: {N(f'Query {p[:2]} Rows', len(res))}.", ""]
        head = [str(v) for v in qres.vars]
        best = sorted(range(len(res)), key=lambda i: (-sum(c is not None and str(c) != "" for c in res[i]), i))[:3]
        L += md_table(head, [[(short(c) if isinstance(c, URIRef) else (str(c)[:70] + ("…" if len(str(c)) > 70 else ""))) if c is not None else ""
                              for c in res[i]] for i in sorted(best)])
        L += [""]

    # ── I. Pipeline ──────────────────────────────────────────────────────────────────────────────────────────────
    L += ["## I. Pipeline", ""]
    L += md_table(["stage", "what it does", "input", "output"], [
        ["1. Collection", "Playwright reads each DANAM record page (2–4 s apart), one JSON per record; exports three tables",
         "`data_collection/resourceids.csv`", "`data_collection/data/raw/*.json`, `data_collection/data/exports/{monuments,events,objects}.csv`"],
        ["2. Staging", "keeps the DANAM fields, adds derived columns (code, Nepali name, class, AAT style, condition), separates empty records",
         "`exports/monuments.csv`", "`staging/monuments.csv`, `staging/skipped_rows.csv`, candidate files"],
        ["3. Graph", "RDF from the staged monuments and DANAM's event and object tables", "`staging/monuments.csv`, `exports/events.csv`, `exports/objects.csv`",
         "graph in memory; Turtle, N-Triples, JSON-LD"],
        ["4. Checks", "undeclared terms and SHACL against the ontology; tests", "built graph, `ontology/`, `vocab/hgn.ttl`", "alignment report"],
        ["5. Release", "serialisations, `metadata.json`, checksums", "built graph", "`releases/<version>/`, `latest/`"],
    ])
    L += ["", f"Runtimes on this machine ({platform.system()} {platform.machine()}): staging {N('StagingSeconds', t_stage, 1)} s"
          f" (rerun into the scratch directory; reproduces `staging/monuments.csv` exactly: {'yes' if stage_same else 'no'}), "
          f"graph build {N('BuildSeconds', t_build, 1)} s, serialisation of all formats {N('SerializeSeconds', t_serialize, 1)} s, "
          f"alignment check {N('CheckSeconds', t_check, 0)} s. Collection is not timed here (it contacts DANAM)."]

    # ── J. Worked example ────────────────────────────────────────────────────────────────────────────────────────
    m = mon_by_id[WORKED_EXAMPLE]
    mu = RES[f"monument/{WORKED_EXAMPLE}"]
    L += ["", "## J. Worked example", "", f"{m['monument_name']}, DANAM page {m['url']}.", "", "**Staged record (key fields)**", ""]
    keys = ["resource_id", "danam_code", "monument_name", "name_ne", "monument_type", "ontology_class", "aat_style", "religion",
            "main_deity", "province", "district", "municipality", "tola", "coordinates_lat", "coordinates_lon", "num_storeys",
            "num_roofs", "roof_type", "condition_types", "event_count", "object_count"]
    L += md_table(["field", "value"], [[f"`{k}`", m.get(k, "")] for k in keys])
    ev_m = sorted(g.objects(mu, CRM.P12i_was_present_at))
    ob_m = sorted(set(g.objects(mu, HGN.containsObject)) | set(g.objects(mu, CRM.P46_is_composed_of)))
    L += ["", f"In the graph: {N('ExampleEvents', len(ev_m))} events and {N('ExampleObjects', len(ob_m))} objects. "
          "Triples of the monument, its first event and its first object (long literals trimmed to 70 characters):", ""]
    ttl = []
    shown = {CRM.P12i_was_present_at: set(ev_m[:2]), HGN.containsObject: set(ob_m[:2]), CRM.P46_is_composed_of: set(ob_m[:2])}
    for node in [mu] + ev_m[:1] + ob_m[:1]:
        sub = Graph(bind_namespaces="none")
        for k, v in g.namespaces():
            sub.bind(k, v, override=True, replace=True)
        sub.bind("geo", GEO, override=True, replace=True)
        for p_, o_ in g.predicate_objects(node):
            if node == mu and p_ in shown and o_ not in shown[p_]:
                continue
            if isinstance(o_, Literal) and len(str(o_)) > 70:
                o_ = Literal(str(o_)[:70] + "…", lang=o_.language, datatype=o_.datatype)
            sub.add((node, p_, o_))
        ttl += [l for l in sub.serialize(format="turtle").splitlines() if not l.startswith("@prefix") and l.strip()] + [""]
    L += [f"Of the monument's links to events and objects, two of each are shown.", "", "```turtle"] + ttl[:60] + \
         (["# … (trimmed)"] if len(ttl) > 60 else []) + ["```"]

    # ── K. Known open issues ─────────────────────────────────────────────────────────────────────────────────────
    software_attr = sum(1 for _, o_ in g.subject_objects(PROV.wasAttributedTo) if (o_, RDF.type, PROV.SoftwareAgent) in g)
    danam_agent = RES["agent/danam_heidelberg"]
    pages = set(g.subjects(PROV.wasAttributedTo, danam_agent))
    derived = sum(1 for _, o_ in g.subject_objects(PROV.wasDerivedFrom) if o_ in pages)
    desc_en = sum(1 for m_ in monuments for o_ in g.objects(m_, DCTERMS.description) if getattr(o_, "language", None) == "en")
    desc_ne = sum(1 for m_ in monuments for o_ in g.objects(m_, DCTERMS.description) if getattr(o_, "language", None) == "ne")
    import publish_release
    next_objects = publish_release.compute_graph_stats(g)["objects"]
    graph_licence = [str(o) for o in g.objects(None, DCTERMS.license)]
    meta = json.load(open(os.path.join(REPO, "latest", "metadata.json")))
    manifest = dict(reversed(l.split()) for l in open(os.path.join(REPO, "latest", "checksums.sha256")) if l.strip())
    bad_sums = [f for f, h in manifest.items() if sha256(os.path.join(REPO, "latest", f)) != h]
    rel = Graph().parse(gzip.open(os.path.join(REPO, "latest", "heritagegraph-nepal.nt.gz")), format="nt")
    rel_objects = len(set(rel.subjects(URIRef(str(HG) + "isObjectOf"), None)))
    res_iris = {t for tr in g for t in (tr[0], tr[2]) if isinstance(t, URIRef) and str(t).startswith(str(RES))}
    res_triples = sum(1 for s_, p_, o_ in g if str(s_).startswith(str(RES)) or (isinstance(o_, URIRef) and str(o_).startswith(str(RES))))
    resolve = "not checked in this run (use `--check-iris`)"
    if a.check_iris:
        import urllib.request
        try:
            urllib.request.urlopen(urllib.request.Request(str(mu), method="HEAD"), timeout=10)
            resolve = f"`{short(mu)}` resolved on {date.today().isoformat()}"
        except Exception as e:  # noqa: BLE001
            resolve = f"`{mu}` did not resolve on {date.today().isoformat()} ({type(e).__name__})"
    date_props = (HG.dateBCE_CE, HG.calendarYear, HG.inscriptionalDateEra, HG.historicalPeriod, CRM["P4_has_time-span"])
    undated = [e for e in events if not any((e, p_, None) in g for p_ in date_props)]
    reno = re.compile(r"renovat|restor|rebuil|repair|reconstruct|refurbish", re.I)
    destr = typed[CRM.E6_Destruction]
    from event_typing import DAMAGE, RULES
    modif = typed[CRM.E11_Modification]
    destr_no_damage_name = [e for e in destr if not re.search(rf"\b({DAMAGE})", str(g.value(e, RDFS.label)).lower())]
    destr_reno_only = [e for e in destr - modif if reno.search(str(g.value(e, RDFS.label)))]
    deity_trad = list(g.subject_objects(HG.hasReligiousTradition))
    deity_trad = [(s_, o_) for s_, o_ in deity_trad if s_ in typed[HG.Deity]]
    naming = defaultdict(set)
    for mm in monuments:
        d_ = g.value(mm, HGN.hasMainDeity)
        if d_ is not None:
            naming[d_].add(frozenset(g.objects(mm, HG.hasReligiousTradition)))
    conflicting = [d_ for d_, sets in naming.items() if len(sets) > 1]
    p45_literals = sum(1 for _, _, o_ in g.triples((None, CRM.P45_consists_of, None)) if isinstance(o_, Literal))
    L += ["", "## K. Issues fixed in round 1 (`fix/round1`; measured on the current graph)", ""]
    L += md_table(["issue", "now", "measured"], [
        ["AI-agent provenance (F1)", "no statement is attributed to a software agent; DANAM report pages are attributed to DANAM "
         "(`prov:Organization`); monuments, events and objects are `prov:wasDerivedFrom` their page; the construction activity is "
         "associated with the pipeline software, acting on behalf of CAIR-Nepal",
         f"{N('AgentAttributions', software_attr)} attributions to software; {N('DanamPages', len(pages))} pages attributed to DANAM; "
         f"{N('DerivedFromPage', derived)} `prov:wasDerivedFrom` statements"],
        ["`crm:P44_has_condition` target (F3)", "points to the `crm:E3_Condition_State`",
         f"{N('ConditionTargetWrong', sum(1 for _, o_ in g.subject_objects(CRM.P44_has_condition) if o_ in typed[CRM.E14_Condition_Assessment]))} statements still point to an assessment"],
        ["Deity tradition rule (F4)", "deities get no tradition (DANAM states traditions per monument only)",
         f"{N('DeityTraditionStatements', len(deity_trad))} deity tradition statements; before the fix "
         f"{N('DeitiesConflicting', len(conflicting))} deities were named by monuments with different traditions"],
        ["Monument descriptions (F5)", "`dcterms:description` with `@en` / `@ne`, as in DANAM",
         f"{N('DescriptionsEn', desc_en)} English, {N('DescriptionsNe', desc_ne)} Nepali; "
         f"{N('DescriptionsNotWritten', sum(1 for m_ in mons if m_['description_en'].strip()) - desc_en)} English descriptions missing"],
        ["`metadata.json` object count (F7)", "the release step counts distinct object nodes (not monuments too) and checks every checksum after writing; "
         "the published v1.0.0 files are not regenerated",
         f"next release: {N('NextReleaseObjects', next_objects)} objects"],
        ["Event typing: renovations typed as destruction (F2, F9, F10)", f"all {N('EventRules', len(RULES) + 1)} event-typing rules are in "
         "`event_typing.py`; destruction (`crm:E6_Destruction`) only when the event name says so; renovation, restoration, "
         "rebuilding and repair in the name give `crm:E11_Modification`; donations in the name give `crm:E8_Acquisition`, guṭhī "
         "formations `crm:E66_Formation`; names that report two happenings give both classes",
         f"{N('DestructionEvents', len(destr))} destruction events ({N('DestructionWithoutDamageName', len(destr_no_damage_name))} "
         f"without a damage word in the name; {N('DestructionRenovation', len(destr_reno_only))} with a repair word in the name but no "
         f"`crm:E11`); {N('ModificationEvents', len(modif))} modification events; {N('DestructionAndModification', len(destr & modif))} "
         f"both; {N('ModificationAndTransfer', len(modif & typed[CRM.E10_Transfer_of_Custody]))} modification and transfer; "
         f"{N('AcquisitionEvents', len(typed[CRM.E8_Acquisition]))} donations (`crm:E8_Acquisition`, F10); "
         f"{N('FormationEvents', len(typed[CRM.E66_Formation]))} guṭhī formations (`crm:E66_Formation`, F10)"],
    ])
    L += ["", "## K2. Known open issues (not fixed yet)", ""]
    L += md_table(["issue", "what is wrong", "affected"], [
        ["Licence mismatch", f"graph `dcterms:license`: {', '.join(graph_licence)}; `latest/metadata.json`: {meta.get('license')}", "1 dataset description"],
        ["`metadata.json` counts (published v1.0.0)", f"v1.0.0 reports {N('MetaObjects', meta['statistics']['objects'])} objects; the v1.0.0 graph has "
         f"{N('ReleaseObjects', rel_objects)} (the count includes the {N('Monuments', len(mons))} monuments, which are also `crm:E22`)", "1 file"],
        ["`metadata.json` checksum (published v1.0.0)", "the file was edited after its checksum was written; file(s) in `latest/` whose SHA-256 differs from `checksums.sha256`: " + (", ".join(bad_sums) or "none"),
         f"{N('BadChecksums', len(bad_sums))} file(s)"],
        ["Non-resolving IRIs", f"instance IRIs use `{RES}`; {resolve}",
         f"{N('ResIris', len(res_iris))} IRIs in {N('ResTriples', res_triples)} triples"],
        ["Missing event dates", "the event tables carry no dates; no event has a date, period or time-span",
         f"{N('UndatedEvents', len(undated))} of {N('Events', len(events))} events"],
        ["Event typing (keyword rules)", "events are still typed by keyword rules (`event_typing.py`), not checked against a "
         "manual sample; e.g. the keyword 'grant' also matches 'granthakūṭa' (a temple style), so 'Installing door to build new "
         "temple' is a transfer of custody",
         f"{N('Events', len(events))} events; {N('GrantMatches', sum(1 for e in events if re.search(r'\bgranth', ' '.join(str(o) for p_ in (RDFS.label, DCTERMS.description) for o in g.objects(e, p_)).lower())))} events contain 'granth…'"],
        ["Object typing (keyword rules)", "objects are typed by keyword rules; not evaluated against a manual sample", f"{N('Objects', len(objects))} objects"],
        ["Materials as text (found while compiling)", "the builder writes object materials as text on `crm:P45_consists_of`, where "
         "CIDOC-CRM expects a `crm:E57_Material`; the current export has no materials, so it does not show yet",
         f"{N('MaterialLiterals', p45_literals)} statements now"],
    ])

    # ── write ────────────────────────────────────────────────────────────────────────────────────────────────────
    with open(os.path.join(a.out_dir, "FACTS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(a.out_dir, "numbers.tex"), "w", encoding="utf-8") as f:
        f.write("% Generated by tools/paper/stats.py; do not edit by hand.\n")
        f.write(f"% Dataset commit {commit[:10]}; ontology {onto_version} ({onto_commit}); {date.today().isoformat()}\n")
        for name in sorted(MACROS):
            f.write(f"\\newcommand{{\\{name}}}{{{MACROS[name]}}}\n")
    print(f"wrote {a.out_dir}/FACTS.md and numbers.tex ({len(MACROS)} macros); build {t_build:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
