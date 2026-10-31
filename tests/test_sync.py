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
