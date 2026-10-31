"""One test per sync item (docs/sync/SYNC_PLAN.md). Each failed on the builder before its change and passes after."""
from rdflib import RDF, Namespace, URIRef

HG = Namespace("https://cair-nepal.org/heritagegraph/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
PROV = Namespace("http://www.w3.org/ns/prov#")
RES = Namespace("https://data.cairnepal.org/heritage/resource/")


def typed(g, cls):
    return set(g.subjects(RDF.type, cls))


def uses(g, prop):
    return sum(1 for _ in g.triples((None, prop, None)))


def test_a1_human_made_object_is_crm_e22(graph):
    assert not typed(graph, HG.HumanMadeObject)
    objects = {s for s in graph.subjects(CRM["P46i_forms_part_of"], None)}
    assert objects and objects <= typed(graph, CRM["E22_Human-Made_Object"])


def test_a2_production_is_crm_e12(graph):
    assert not typed(graph, HG.Production)
    assert len(typed(graph, CRM["E12_Production"])) == 1808


def test_a3_condition_assessment_is_crm_e14(graph):
    assert not typed(graph, HG.ConditionAssessment)
    assert len(typed(graph, CRM["E14_Condition_Assessment"])) == 1592


def test_a4_place_is_crm_e53(graph):
    assert not typed(graph, HG.Place)
    places = set(graph.objects(None, CRM["P53_has_former_or_current_location"]))
    assert len(places) == 1021 and places <= typed(graph, CRM["E53_Place"])


def test_a5_destruction_is_crm_e6(graph):
    assert not typed(graph, HG.DestructionEvent)
    assert len(typed(graph, CRM["E6_Destruction"])) == 695


def test_a6_transfer_is_crm_e10(graph):
    assert not typed(graph, HG.TransferOfCustody)
    assert len(typed(graph, CRM["E10_Transfer_of_Custody"])) == 284


def test_a7_current_location_is_crm_p55(graph):
    assert uses(graph, HG.hasCurrentLocation) == 0
    assert uses(graph, CRM["P55_has_current_location"]) == 1631


def test_a8_condition_assessment_link_is_crm_p34i(graph):
    assert uses(graph, HG.hasConditionAssessment) == 0
    assert uses(graph, CRM["P34i_was_assessed_by"]) == 1577


def test_a9_event_links_are_crm_p12(graph):
    assert uses(graph, HG.hasEvent) == 0 and uses(graph, HG.isEventOf) == 0
    assert uses(graph, CRM["P12_occurred_in_the_presence_of"]) == 5098
    assert uses(graph, CRM["P12i_was_present_at"]) == 5098


def test_a10_condition_type_only_on_condition_state(graph):
    assert uses(graph, HG.conditionType) == 0
    for v in ("Good", "Damaged", "Ruined", "Restored"):
        assert not any(True for _ in graph.triples((None, None, HG[v])))
    assert uses(graph, HG.hasConditionType) > 0


def test_a11_sources_are_prov_entities(graph):
    sources = set(graph.objects(None, PROV.wasDerivedFrom)) | set(graph.objects(None, PROV.used))
    assert sources and sources <= typed(graph, PROV.Entity)


def test_v0_extension_vocabulary_matches_builder_and_declares_used_terms(graph):
    import os, rdflib, build_kg
    from rdflib import OWL, RDF as R
    vocab = rdflib.Graph().parse(os.path.join(os.path.dirname(__file__), "..", "vocab", "hgn.ttl"))
    assert str(dict(vocab.namespaces())["hgn"]) == build_kg.HGN_BASE
    declared = set(vocab.subjects(R.type, None))
    used = {t for s, p, o in graph for t in (p, o) if str(t).startswith(build_kg.HGN_BASE)}
    assert used <= declared, sorted(used - declared)
    for t in declared - set(vocab.subjects(R.type, OWL.Ontology)):
        for p in (rdflib.RDFS.label, rdflib.RDFS.comment, rdflib.RDFS.isDefinedBy):
            assert vocab.value(t, p) is not None, (t, p)


HGN = Namespace("https://w3id.org/heritagegraph-nepal/vocab#")


def test_b1_p46_only_for_architectural_elements(graph):
    parts = set(graph.objects(None, CRM["P46_is_composed_of"]))
    assert parts and parts <= typed(graph, HG.ArchitecturalElement)
    assert uses(graph, HG.containsObject) == 0 and uses(graph, HG.isObjectOf) == 0
    # one link per object row (7,160); 7,155 before R1, when reused object numbers merged nodes
    assert uses(graph, CRM["P46_is_composed_of"]) + uses(graph, HGN.containsObject) == 7160
    assert uses(graph, HGN.isObjectOf) == uses(graph, HGN.containsObject)


def test_b2_one_ontology_style_aat_on_p2(graph):
    from collections import Counter
    styles = Counter(s for s, o in graph.subject_objects(HG.hasArchitecturalStyle))
    assert styles and max(styles.values()) == 1
    assert all(str(o).startswith(str(HG) + "ArchitecturalStyle#") for o in graph.objects(None, HG.hasArchitecturalStyle))
    aat = [o for o in graph.objects(None, CRM["P2_has_type"]) if str(o).startswith("http://vocab.getty.edu/aat/")]
    assert len(aat) == 606  # all AAT concepts DANAM lists (598 monuments, 8 with two)
    # first style DANAM lists is kept; the second goes in a note (DANAM lists Dome, then Shikhara)
    m = RES["monument/168523f7-0f40-477f-87d9-820220ea2723"]
    assert graph.value(m, HG.hasArchitecturalStyle) == HG["ArchitecturalStyle#Dome"]
    assert "Shikhara" in str(graph.value(m, CRM["P3_has_note"]))


def test_b3_no_existence_status(graph):
    assert uses(graph, HG.existenceStatus) == 0


def test_b4_one_condition_type_per_state_rest_in_note(graph):
    from collections import Counter
    per_state = Counter(s for s, _ in graph.subject_objects(HG.hasConditionType))
    assert per_state and max(per_state.values()) == 1
    m = RES["monument/00cf6d20-71a7-4382-9746-ac988a0bd323"]  # DANAM: Ruined|Damaged
    state = RES["condition_state/00cf6d20-71a7-4382-9746-ac988a0bd323"]
    assert graph.value(state, HG.hasConditionType) == HG["ConditionType#Ruined"]
    assert "Damaged" in str(graph.value(state, CRM["P3_has_note"]))
    assert {str(o) for o in graph.objects(m, HG.conditionStatus)} == {"Ruined", "Damaged"}


def test_c1a_plain_string_label_and_tagged_pref_labels(graph):
    from rdflib import RDFS, SKOS, Literal
    labels = list(graph.subject_objects(RDFS.label))
    assert labels and all(l.language is None and l.datatype in (None, rdflib_xsd_string()) for _, l in labels)
    for s, l in labels[:2000]:
        assert Literal(str(l), lang="en") in set(graph.objects(s, SKOS.prefLabel))
    m = RES["monument/0077a8d9-2e9d-4626-8dd0-04272b780ea9"]
    assert Literal("जोगेश्वर मन्दिर", lang="ne") in set(graph.objects(m, SKOS.prefLabel))


def rdflib_xsd_string():
    from rdflib import XSD
    return XSD.string


def identifiers(graph, node, kind):
    return {str(graph.value(i, CRM["P190_has_symbolic_content"])) for i in graph.objects(node, CRM["P1_is_identified_by"])
            if (i, CRM["P2_has_type"], kind) in graph}


def test_c1b_identifiers_are_crm_e42(graph):
    from rdflib import DCTERMS
    assert uses(graph, DCTERMS.identifier) == 0
    m = RES["monument/0077a8d9-2e9d-4626-8dd0-04272b780ea9"]
    assert identifiers(graph, m, HGN.DanamResourceId) == {"0077a8d9-2e9d-4626-8dd0-04272b780ea9"}
    o = next(graph.subjects(HGN.isObjectOf, None))
    assert len(identifiers(graph, o, HGN.DanamObjectNumber)) == 1
    ids = set(graph.objects(None, CRM["P1_is_identified_by"]))
    assert ids <= typed(graph, CRM["E42_Identifier"])


def test_r1_reused_object_numbers_give_distinct_nodes(graph):
    from rdflib import RDFS
    nodes = [RES["object/kat1150-014_1"], RES["object/kat1150-014_2"]]
    assert not any(True for _ in graph.triples((RES["object/kat1150-014"], None, None)))
    assert {str(graph.value(n, RDFS.label)) for n in nodes} == {"Garuḍanārāyaṇa", "Gaṇeśa (B)"}
    for n in nodes:
        assert len(list(graph.objects(n, RDFS.label))) == 1
        assert identifiers(graph, n, HGN.DanamObjectNumber) == {"KAT1150-014"}
