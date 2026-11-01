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
