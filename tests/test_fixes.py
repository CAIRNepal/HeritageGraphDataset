"""One test per fix in round 1 (docs/sync/SYNC_LOG.md, entries F1-F7). Each fails on the builder before its change."""
from rdflib import RDF, RDFS, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS

HG = Namespace("https://cair-nepal.org/heritagegraph/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
PROV = Namespace("http://www.w3.org/ns/prov#")
SCHEMA = Namespace("https://schema.org/")
RES = Namespace("https://data.cairnepal.org/heritage/resource/")
HGN = Namespace("https://w3id.org/heritagegraph-nepal/vocab#")
JOGESVARA = "0077a8d9-2e9d-4626-8dd0-04272b780ea9"  # Jogeśvara Mandira, SKH0510
PAGE = URIRef("https://danam.cats.uni-heidelberg.de/report/" + JOGESVARA)


def test_f1_provenance_danam_source_and_pipeline_software(graph):
    assert not any("antigravity" in str(t).lower() for tr in graph for t in tr)
    danam = RES["agent/danam_heidelberg"]
    assert (danam, RDF.type, PROV.Organization) in graph
    assert str(graph.value(danam, RDFS.label)) == "Digital Archive of Nepalese Arts and Monuments (DANAM)"
    # monument, its events and objects are derived from the DANAM page; the page is attributed to DANAM
    assert (PAGE, PROV.wasAttributedTo, danam) in graph
    assert (RES["monument/" + JOGESVARA], PROV.wasDerivedFrom, PAGE) in graph
    assert (RES[f"event/{JOGESVARA}_0"], PROV.wasDerivedFrom, PAGE) in graph
    assert (RES["object/skh0510-002"], PROV.wasDerivedFrom, PAGE) in graph
    # every event and object is derived from a page attributed to DANAM
    for cls in (CRM["E5_Event"],):
        for s in graph.subjects(RDF.type, cls):
            if (s, CRM["P12_occurred_in_the_presence_of"], None) in graph:
                assert (graph.value(s, PROV.wasDerivedFrom), PROV.wasAttributedTo, danam) in graph
    # the construction activity: pipeline software acting on behalf of CAIR-Nepal
    soft = graph.value(RES["activity/heritagegraph_kg_construction"], PROV.wasAssociatedWith)
    assert (soft, RDF.type, PROV.SoftwareAgent) in graph
    assert graph.value(soft, SCHEMA.codeRepository) == URIRef("https://github.com/CAIRNepal/HeritageGraphDataset")
    assert graph.value(soft, PROV.actedOnBehalfOf) == RES["agent/cair_nepal"]
    assert (RES["agent/cair_nepal"], RDF.type, PROV.Organization) in graph
    assert set(graph.objects(RES["dataset"], PROV.wasAttributedTo)) == {RES["agent/cair_nepal"]}


def test_f3_p44_points_to_the_condition_state(graph):
    targets = set(graph.objects(None, CRM["P44_has_condition"]))
    assert len(targets) == 1577
    assert targets <= set(graph.subjects(RDF.type, CRM["E3_Condition_State"]))
    assert not targets & set(graph.subjects(RDF.type, CRM["E14_Condition_Assessment"]))
    m = RES["monument/" + JOGESVARA]
    assert graph.value(m, CRM["P44_has_condition"]) == RES["condition_state/" + JOGESVARA]
    # the assessment still identifies the same state
    assert (RES["assessment/" + JOGESVARA], CRM["P35_has_identified"], RES["condition_state/" + JOGESVARA]) in graph


def test_f4_deities_get_no_tradition_from_monuments(graph):
    deities = set(graph.subjects(RDF.type, HG.Deity))
    assert len(deities) == 355
    assert not any((d, HG.hasReligiousTradition, None) in graph for d in deities)
    # monuments keep theirs: 1,162 monuments, 1,373 statements
    monuments = set(graph.subjects(RDF.type, HG.ArchitecturalStructure))
    with_trad = {s for s in graph.subjects(HG.hasReligiousTradition, None) if s in monuments}
    assert len(with_trad) == 1162
    assert sum(1 for s, _ in graph.subject_objects(HG.hasReligiousTradition) if s in monuments) == 1373


def test_f5_monument_descriptions_unchanged_from_danam(graph):
    import csv, json, os
    from conftest import MONUMENTS, REPO
    monuments = set(graph.subjects(RDF.type, HG.ArchitecturalStructure))
    descs = [(s, o) for s, o in graph.subject_objects(DCTERMS.description) if s in monuments]
    assert sum(o.language == "en" for _, o in descs) == 1576
    assert sum(o.language == "ne" for _, o in descs) == 1471
    raw = json.load(open(os.path.join(REPO, "data_collection", "data", "raw", JOGESVARA + ".json"), encoding="utf-8"))
    m = RES["monument/" + JOGESVARA]
    got = {o.language: str(o) for o in graph.objects(m, DCTERMS.description)}
    assert got == {"en": raw["description_en"], "ne": raw["description_ne"]}


def test_f6_every_listed_id_has_a_raw_file_and_seven_fetches_failed():
    """The '1,945 distinct IDs' counted the blank value: resourceids.csv has 3 rows with an empty ID."""
    import csv, json, os
    from conftest import REPO
    rows = [r[0].strip() for r in csv.reader(open(os.path.join(REPO, "data_collection", "resourceids.csv"), encoding="utf-8-sig"))][1:]
    assert len(rows) == 1947 and rows.count("") == 3
    ids = set(rows) - {""}
    assert len(ids) == 1944
    raw = os.path.join(REPO, "data_collection", "data", "raw")
    files = {f[:-5] for f in os.listdir(raw) if f.endswith(".json")}
    assert ids == files
    failed = [f for f in files if json.load(open(os.path.join(raw, f + ".json"), encoding="utf-8"))["status"] != "ok"]
    assert len(failed) == 7


def test_f7_metadata_counts_distinct_objects_and_checksums_match(graph, tmp_path, monkeypatch):
    """A scratch release (tmp_path, never releases/ or latest/): objects = distinct object nodes, not monuments too;
    every file matches checksums.sha256. The licence field is not changed here (decision pending)."""
    import json
    import publish_release
    monkeypatch.setattr(publish_release, "dirty_files", lambda repo_dir=None: [])  # this test may run on uncommitted work
    rel, latest = publish_release.create_release("v0.0.0-test", graph=graph, base_dir=str(tmp_path))
    meta = json.load(open(f"{rel}/metadata.json", encoding="utf-8"))
    assert meta["statistics"]["objects"] == 7160  # 7,154 object numbers; 6 numbers are used twice, each row its own node
    assert meta["statistics"]["monuments"] == 1652
    assert publish_release.verify_checksums(rel) == [] and publish_release.verify_checksums(latest) == []
    assert meta["license"] == "https://creativecommons.org/licenses/by/4.0/"


# F2: one real DANAM event per rule of event_typing.py: (event key, name, expected classes, rule number)
F2_EXAMPLES = [
    ("02509f50-336d-423f-ac40-60dffc2d905c_4", "Installation and consecration of a statue of Dīpaṅkara", ("Consecration",), 1),
    ("0316e917-5197-44e7-b865-37ba1be3397b_1", "Addition of a statue", ("Enshrinement",), 2),
    ("72fbb5ec-849f-482d-8003-7206e8ede0a6_1", "Collapse and reconstruction", ("DestructionEvent", "Modification"), 3),
    ("017a4a8f-b183-4e57-9ff9-54ae1145378f_1", "Collapse", ("DestructionEvent",), 4),
    ("0077a8d9-2e9d-4626-8dd0-04272b780ea9_16", "Damage by earthquake", ("DestructionEvent",), 4),
    ("293c1896-a3bb-454a-8fe9-b56ebfadc51c_2", "Renovation and land endowment", ("Modification", "TransferOfCustody"), 5),
    # the description says it followed the 1934 earthquake: background, not a destruction
    ("5bfb6d40-eb4c-11e9-b125-0242ac130002_1", "Rebuilding of the temple", ("Modification",), 6),
    ("02f204ae-8a02-4b50-a82c-b7551b103542_1", "Endowment of lands for daily worship", ("TransferOfCustody",), 7),
    ("0d39368f-4f2c-4b8d-8fad-4040187b6a16_8", "Performance of pacification ritual (śāntisvasti)", ("RitualEvent",), 8),
    ("013ba068-2100-462c-abb9-29c7a0dc6eef_0", "Construction of a phalcā", ("TransferOfCustody",), 9),  # endowment in the description
    ("0077a8d9-2e9d-4626-8dd0-04272b780ea9_6", "Offering pinnacle to newly constructed two storied temple", ("Production",), 11),
    ("34697056-9775-466d-b46d-c83f874b93d3_0", "Unknown event", ("ConditionAssessment",), 12),
    # only the description mentions damage (a flood): not a destruction
    ("e2a4580b-0699-44bf-b0b3-561da8d9fa93_4", "Cleaning of the hiti", ("HistoricalEvent",), 13),
]


def test_f2_event_typing_rules_on_real_events(graph):
    import csv, unicodedata
    from conftest import EVENTS
    from event_typing import classify_event_rule
    rows = {f"{r['resource_id']}_{r['event_index']}": r for r in csv.DictReader(open(EVENTS, encoding="utf-8-sig"))}
    for key, name, classes, rule in F2_EXAMPLES:
        r = rows[key]
        assert unicodedata.normalize("NFC", r["event_name"].strip()) == unicodedata.normalize("NFC", name)
        assert classify_event_rule(r["event_name"].strip(), r["event_description"].strip()) == (classes, rule), name
    # in the graph: the mixed event has both classes
    ev = RES["event/72fbb5ec-849f-482d-8003-7206e8ede0a6_1"]
    assert {CRM["E6_Destruction"], CRM["E11_Modification"]} <= set(graph.objects(ev, RDF.type))


def test_f2_destruction_only_when_the_name_says_so(graph):
    import re
    from event_typing import DAMAGE
    destr = set(graph.subjects(RDF.type, CRM["E6_Destruction"]))
    assert len(destr) == 265
    assert all(re.search(rf"\b({DAMAGE})", str(graph.value(e, RDFS.label)).lower()) for e in destr)
    assert len(set(graph.subjects(RDF.type, CRM["E11_Modification"]))) == 1280
    assert len(set(graph.subjects(RDF.type, CRM["E12_Production"]))) == 1075  # 1,074 at F2; F9 +1
    both = destr & set(graph.subjects(RDF.type, CRM["E11_Modification"]))
    assert len(both) == 27


def test_release_refuses_a_dirty_working_tree(graph, tmp_path, monkeypatch):
    """dirty_files reads git: a modified tracked file counts, an untracked file does not; create_release stops before
    writing anything while the list is not empty."""
    import os, subprocess
    import pytest
    import publish_release
    repo = tmp_path / "repo"
    repo.mkdir()
    git = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)
    git("init", "-q"); git("config", "user.email", "t@example.org"); git("config", "user.name", "t")
    (repo / "build_kg.py").write_text("a\n"); git("add", "."); git("commit", "-q", "-m", "x")
    (repo / "notes.txt").write_text("untracked\n")
    assert publish_release.dirty_files(str(repo)) == []
    (repo / "build_kg.py").write_text("b\n")
    assert publish_release.dirty_files(str(repo)) == ["build_kg.py"]
    monkeypatch.setattr(publish_release, "dirty_files", lambda repo_dir=None: ["build_kg.py"])
    out = tmp_path / "out"
    with pytest.raises(RuntimeError, match="uncommitted changes"):
        publish_release.create_release("v0.0.0-test", graph=graph, base_dir=str(out))
    assert not os.path.exists(out)


def test_f9_grant_does_not_match_granthakuta():
    import csv
    from conftest import EVENTS
    from event_typing import classify_event
    rows = {f"{r['resource_id']}_{r['event_index']}": r for r in csv.DictReader(open(EVENTS, encoding="utf-8-sig"))}
    r = rows["0077a8d9-2e9d-4626-8dd0-04272b780ea9_5"]  # '… a door installed for constructing a śikhara-style (granthakūṭa) temple'
    assert r["event_name"].strip() == "Installing door to build new temple" and "granthakūṭa" in r["event_description"]
    assert classify_event(r["event_name"].strip(), r["event_description"].strip()) == ("Production",)
    assert classify_event("Land grant", "") == ("TransferOfCustody",)
