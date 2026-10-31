# Sync log

One entry per change, newest last. Each entry: what changed, the test that fails before and passes after, and the counts before/after from `tools/sync/step_check.py` (scratch build in `build/sync/`, alignment by `tools/sync/check_alignment.py`, query rows without LIMIT).

## S0: baseline: dataset v1.0.0 builder against ontology 1.0.1

- Triples: **221,364**.
- SHACL results: **75,641** (14 groups).
- Undeclared terms: **36** (7 classes, 23 properties, 6 IRI values).
- Queries (rows without LIMIT): `01_monuments_by_aat_style.rq` 1,212, `02_historical_timeline.rq` 5,313, `03_spatial_geosparql.rq` 1,626, `04_monument_sacred_objects.rq` 9,012, `05_provenance_audit.rq` 5,098, `06_condition_threats.rq` 1,794, `07_deities_traditions.rq` 1,049

## A1: drop hg:HumanMadeObject (objects keep crm:E22_Human-Made_Object)

- Test: `tests/test_sync.py::test_a1_human_made_object_is_crm_e22`.
- Triples: 221,364 → **217,616**.
- SHACL results: 75,641 → **75,641** (14 groups).
- Undeclared terms: 36 → **35** (6 classes, 23 properties, 6 IRI values).
- Queries (rows without LIMIT): **changed:** `04_monument_sacred_objects.rq` 9012 → 9008
- Query rows changed, accepted: query 04 loses 4 rows from two merged object nodes (kat1150-014, tok0090-001: DANAM reuses each number for two objects, one plain). Each node used to list hg:HumanMadeObject beside its other class. Resolved by the reused-object-numbers item.
- Query 04 updated: an object with no non-CRM class now shows crm:E22_Human-Made_Object (was hg:HumanMadeObject).

## A2: drop hg:Production (events keep crm:E12_Production)

- Test: `tests/test_sync.py::test_a2_production_is_crm_e12`.
- Triples: 217,616 → **215,808**.
- SHACL results: 75,641 → **75,641** (14 groups).
- Undeclared terms: 35 → **34** (5 classes, 23 properties, 6 IRI values).
- Queries (rows without LIMIT): unchanged.
- Query 02 updated: an event with no non-CRM class now shows its specific CRM class (crm:E12_Production instead of hg:Production).

## A3: drop hg:ConditionAssessment (assessments and assessment events keep crm:E14_Condition_Assessment)

- Test: `tests/test_sync.py::test_a3_condition_assessment_is_crm_e14`.
- Triples: 215,808 → **214,216**.
- SHACL results: 75,641 → **75,641** (14 groups).
- Undeclared terms: 34 → **33** (4 classes, 23 properties, 6 IRI values).
- Queries (rows without LIMIT): unchanged.

## A4: replace hg:Place with crm:E53_Place

- Test: `tests/test_sync.py::test_a4_place_is_crm_e53`.
- Triples: 214,216 → **214,216**.
- SHACL results: 75,641 → **76,662** (14 groups).
- Undeclared terms: 33 → **32** (3 classes, 23 properties, 6 IRI values).
- Queries (rows without LIMIT): unchanged.
- **Deviation from the plan (+1,021 SHACL results, expected ±0).** All are `rdfs:label` datatype, one per place: typed `crm:E53_Place`, the 1,021 places now fall under the ontology's place shape, and their `@en` labels fail `sh:datatype xsd:string` like every other label. Same cause as C1a, and removed by the C1a fix. No modelling choice involved.

## A5: drop hg:DestructionEvent (events keep crm:E6_Destruction)

- Test: `tests/test_sync.py::test_a5_destruction_is_crm_e6`.
- Triples: 214,216 → **213,521**.
- SHACL results: 76,662 → **76,662** (14 groups).
- Undeclared terms: 32 → **31** (2 classes, 23 properties, 6 IRI values).
- Queries (rows without LIMIT): unchanged.
- Whether these events are destructions is a typing question, out of scope here.

## A6: drop hg:TransferOfCustody (events keep crm:E10_Transfer_of_Custody)

- Test: `tests/test_sync.py::test_a6_transfer_is_crm_e10`.
- Triples: 213,521 → **213,237**.
- SHACL results: 76,662 → **76,662** (14 groups).
- Undeclared terms: 31 → **30** (1 classes, 23 properties, 6 IRI values).
- Queries (rows without LIMIT): unchanged.

## A7: replace hg:hasCurrentLocation with crm:P55_has_current_location

- Test: `tests/test_sync.py::test_a7_current_location_is_crm_p55`.
- Triples: 213,237 → **213,237**.
- SHACL results: 76,662 → **76,662** (14 groups).
- Undeclared terms: 30 → **29** (1 classes, 22 properties, 6 IRI values).
- Queries (rows without LIMIT): unchanged.
- Query 03 switched to crm:P55_has_current_location.

## A8: drop hg:hasConditionAssessment (crm:P34i_was_assessed_by stays)

- Test: `tests/test_sync.py::test_a8_condition_assessment_link_is_crm_p34i`.
- Triples: 213,237 → **211,660**.
- SHACL results: 76,662 → **76,662** (14 groups).
- Undeclared terms: 29 → **28** (1 classes, 21 properties, 6 IRI values).
- Queries (rows without LIMIT): unchanged.
- Query 06 switched to crm:P34i_was_assessed_by.

## A9: drop hg:hasEvent and hg:isEventOf (crm:P12i_was_present_at / crm:P12_occurred_in_the_presence_of stay)

- Test: `tests/test_sync.py::test_a9_event_links_are_crm_p12`.
- Triples: 211,660 → **201,464**.
- SHACL results: 76,662 → **76,662** (14 groups).
- Undeclared terms: 28 → **26** (1 classes, 19 properties, 6 IRI values).
- Queries (rows without LIMIT): unchanged.
- Queries 02 and 05 switched to the CRM properties.

## A10: drop hg:conditionType and its undeclared values hg:Good/Damaged/Ruined/Restored (hg:hasConditionType -> hg:ConditionType#… on the condition state stays)

- Test: `tests/test_sync.py::test_a10_condition_type_only_on_condition_state`.
- Triples: 201,464 → **199,805**.
- SHACL results: 76,662 → **76,662** (14 groups).
- Undeclared terms: 26 → **21** (1 classes, 18 properties, 2 IRI values).
- Queries (rows without LIMIT): unchanged.

## A11: type the DANAM pages (prov:wasDerivedFrom) and the DANAM site (prov:used) as prov:Entity

- Test: `tests/test_sync.py::test_a11_sources_are_prov_entities`.
- Triples: 199,805 → **201,458**.
- SHACL results: 76,662 → **70,752** (12 groups).
- Undeclared terms: 21 → **21** (1 classes, 18 properties, 2 IRI values).
- Queries (rows without LIMIT): unchanged.

## V0: add the extension vocabulary vocab/hgn.ttl (no terms yet; base IRI HGN_BASE in the builder) and check against ontology + vocabulary

- Test: `tests/test_sync.py::test_v0_extension_vocabulary_matches_builder_and_declares_used_terms`.
- Triples: 201,458 → **201,458**.
- SHACL results: 70,752 → **70,752** (12 groups).
- Undeclared terms: 21 → **20** (1 classes, 18 properties, 1 IRI values).
- Extension terms used: 0.
- Queries (rows without LIMIT): unchanged.
- Checker: undeclared terms are now counted in hg: and hgn:, against the ontology plus vocab/hgn.ttl; extension terms are listed separately. The bare namespace IRI hg: (object of void:vocabulary) is no longer counted as an undeclared term (a vocabulary reference, not a term use): 21 → 20.

## B1: crm:P46_is_composed_of only for hg:ArchitecturalElement; other objects linked by hgn:containsObject / hgn:isObjectOf

- Test: `tests/test_sync.py::test_b1_p46_only_for_architectural_elements`.
- Triples: 201,458 → **187,148**.
- SHACL results: 70,752 → **53,159** (11 groups).
- Undeclared terms: 20 → **18** (1 classes, 16 properties, 1 IRI values).
- Extension terms used: 2.
- Queries (rows without LIMIT): unchanged.
- Query 04 now follows crm:P46_is_composed_of|hgn:containsObject. hg:containsObject / hg:isObjectOf are no longer written (the CRM or hgn: property carries each link).

## B2: one ontology style on hg:hasArchitecturalStyle (first DANAM lists); AAT concepts only on crm:P2_has_type; further styles in a note

- Test: `tests/test_sync.py::test_b2_one_ontology_style_aat_on_p2`.
- Triples: 187,148 → **186,542**.
- SHACL results: 53,159 → **49,529** (9 groups).
- Undeclared terms: 18 → **18** (1 classes, 16 properties, 1 IRI values).
- Extension terms used: 2.
- Queries (rows without LIMIT): **changed:** `01_monuments_by_aat_style.rq` 1212 → 606
- Query rows changed, accepted: query 01 1,212 → 606: it used to return each monument twice, once with the AAT concept and once with the ontology style value (labelled 'Other AAT Style'). The 606 AAT answers are unchanged.
- The 8 monuments with two styles (first kept, second in crm:P3_has_note): 168523f7-0f40-477f-87d9-820220ea2723 (Dome, Shikhara), 170a68d0-e68d-11e9-b125-0242ac130002 (Pagoda, Dome), 20c0e0a0-2b7f-491a-81aa-41dddec3276b (Shikhara, Dome), 28cc6491-dcc2-4cdd-9ee3-4aac928db2d8 (Pagoda, Dome), a2cfeca7-18cd-4ba6-8793-4390725a1375 (Shikhara, Dome), c07ed9a8-8a2b-4453-9478-803722743140 (Dome, Shikhara), c2add511-115d-4d83-bcef-db8ed170a594 (Dome, Shikhara), ca5145f4-e083-451b-a8b6-ae548aefe518 (Shikhara, Dome). Query 01 reads the AAT concept from crm:P2_has_type.

## B3: stop writing hg:existenceStatus (DANAM records condition, not existence)

- Test: `tests/test_sync.py::test_b3_no_existence_status`.
- Triples: 186,542 → **184,996**.
- SHACL results: 49,529 → **48,853** (7 groups).
- Undeclared terms: 18 → **17** (1 classes, 16 properties, 0 IRI values).
- Extension terms used: 2.
- Queries (rows without LIMIT): unchanged.
- Checked first: no shape has sh:minCount ≥ 1 on hg:existenceStatus (13 shapes, all sh:maxCount 1 only).

## B4: one condition type per condition state (first DANAM lists); the others in a note; the monument literal keeps all

- Test: `tests/test_sync.py::test_b4_one_condition_type_per_state_rest_in_note`.
- Triples: 184,996 → **184,992**.
- SHACL results: 48,853 → **48,640** (6 groups).
- Undeclared terms: 17 → **17** (1 classes, 16 properties, 0 IRI values).
- Extension terms used: 2.
- Queries (rows without LIMIT): unchanged.
