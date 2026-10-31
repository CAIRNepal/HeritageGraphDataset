Syncs the dataset with HeritageGraph ontology **1.0.1** (`f2f1780`, vendored in `ontology/`). Only the dataset side changes; the ontology is not modified.

**Result** (scratch build, same inputs as v1.0.0):
- SHACL results: 75,641 → **4,012**.
- Undeclared terms: 36 → **0**.

One commit per plan item, each with a test that fails before and passes after. Details: `docs/sync/SYNC_PLAN.md`, `docs/sync/SYNC_LOG.md`, `docs/sync/alignment_after_sync.md`.

**What changed**
- **A1–A11:** `hg:` duplicates of CRM terms are dropped or replaced (E22, E12, E14, E53, E6, E10, P55, P34i, P12/P12i). DANAM pages are typed `prov:Entity`.
- **B1:** `crm:P46_is_composed_of` is used only for architectural elements; other objects use `hgn:containsObject`.
- **B2:** one ontology style per structure; AAT concepts move to `crm:P2_has_type`.
- **B3:** `hg:existenceStatus` is no longer written.
- **B4:** one condition type per condition state; the others go in a note.
- **C1a:** `rdfs:label` is a single plain string; tagged labels move to `skos:prefLabel`.
- **C1b:** identifiers become `crm:E42_Identifier` nodes.
- **R1:** reused DANAM object numbers no longer merge objects.
- **E1–E9:** the remaining undeclared terms move to existing terms (E55 types, an E53 place hierarchy) or to the extension vocabulary `vocab/hgn.ttl` (11 terms).
- **S1:** release statistics count the classes the builder now writes.
- **Queries:** queries in `queries/` that used changed terms are updated, with row counts checked before and after. Query 01 (1,212 → 606) and query 04 (9,012 → 9,001) changed, for reasons given in the log.

**Not done yet**
- **B5:** religious traditions (3,812 results). Waiting on a decision about the DANAM value "Unspecified".
- **C1c:** 200 temples have no style in DANAM and are left as they are.

Releases and `latest/` are untouched.
