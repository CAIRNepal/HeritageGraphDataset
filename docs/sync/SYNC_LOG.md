# Sync log

One entry per change, newest last. Each entry: what changed, the test that fails before and passes after, and the counts before/after from `tools/sync/step_check.py` (scratch build in `build/sync/`, alignment by `tools/sync/check_alignment.py`, query rows without LIMIT).

## S0: baseline: dataset v1.0.0 builder against ontology 1.0.1

- Triples: **221,364**.
- SHACL results: **75,641** (14 groups).
- Undeclared terms: **36** (7 classes, 23 properties, 6 IRI values).
- Queries (rows without LIMIT): `01_monuments_by_aat_style.rq` 1,212, `02_historical_timeline.rq` 5,313, `03_spatial_geosparql.rq` 1,626, `04_monument_sacred_objects.rq` 9,012, `05_provenance_audit.rq` 5,098, `06_condition_threats.rq` 1,794, `07_deities_traditions.rq` 1,049
