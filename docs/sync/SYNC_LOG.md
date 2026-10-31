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
