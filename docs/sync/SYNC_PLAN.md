# Sync plan: HeritageGraph-Nepal ↔ HeritageGraph ontology 1.0.1

**Branch:** `sync/ontology` (from `main` at `b59658d`). **Target:** ontology 1.0.1, `main` of
CAIRNepal/heritagegraphontology at `f2f1780` (vendored in `ontology/`, see `ontology/SOURCE.md`).

**Baseline:** `docs/sync/alignment_v1.0.0_baseline.md`, produced by `tools/sync/check_alignment.py` on dataset v1.0.0:
- SHACL: **75,641 results** in 14 groups on 16,050 nodes;
- **7 undeclared classes, 23 undeclared properties** and 6 undeclared IRI values.

**Goal ("synced"):**
1. The dataset ships the exact files of a tagged ontology version.
2. It uses only terms that version declares.
3. It validates against that version's shapes with 0 results, or every remaining result is explained.

**How we work:** one change at a time. Each change is made in the builder (`build_kg.py`), comes with a test, and is checked by
rerunning `check_alignment.py` on a scratch build (never in `releases/` or `latest/`). Each one is logged in
`docs/sync/SYNC_LOG.md`.

**Three kinds of gap, by which side has to change:**
- **A.** The ontology already has the right term and says so. The dataset switches to it; nothing to decide.
- **B.** The dataset breaks a shape rule and must change, but how is a modelling choice.
- **C.** The ontology is too strict or lacks a term. The ontology repo has to change; the dataset can't fix it alone.

---

## A. Exact equivalents: the ontology names the term (no decision needed)

Source: the ontology's LinkML file publishes these classes and slots under CRM IRIs. In each case the dataset already writes the
CRM term as well, so the `hg:` term is a duplicate and can simply be dropped.

| # | dataset writes | ontology's term | uses | change |
|---|---|---|---|---|
| A1 | `hg:HumanMadeObject` | `crm:E22_Human-Made_Object` (already on every object) | 3,748 | drop the hg type |
| A2 | `hg:Production` | `crm:E12_Production` (already present) | 1,808 | drop |
| A3 | `hg:ConditionAssessment` | `crm:E14_Condition_Assessment` (already present) | 1,592 | drop |
| A4 | `hg:Place` | `crm:E53_Place` | 1,021 | replace (places are only `schema:Place` today) |
| A5 | `hg:DestructionEvent` | `crm:E6_Destruction` (already present) | 695 | drop (whether these events *are* destructions is a typing question, see later) |
| A6 | `hg:TransferOfCustody` | `crm:E10_Transfer_of_Custody` (already present) | 284 | drop |
| A7 | `hg:hasCurrentLocation` | `crm:P55_has_current_location` | 1,631 | replace |
| A8 | `hg:hasConditionAssessment` | `crm:P34i_was_assessed_by` (already present) | 1,577 | drop |
| A9 | `hg:hasEvent`, `hg:isEventOf` | `crm:P12i_was_present_at`, `crm:P12_occurred_in_the_presence_of` (already present) | 5,098 each | drop |
| A10 | `hg:conditionType` → `hg:Good`, `hg:Damaged`, … (undeclared IRIs) | `hg:hasConditionType` → `hg:ConditionType#Good` … on the condition state (already present) | 1,659 | drop |
| A11 | DANAM pages (objects of `prov:wasDerivedFrom`) and the DANAM site (object of `prov:used`) are untyped | the shapes require `prov:Entity` | 5,909 + 1 SHACL results | type them `prov:Entity` |

**Effect:** −5,910 SHACL results; 6 undeclared classes, 5 undeclared properties and the 5 condition-value IRIs disappear.
Queries in `queries/` that use these `hg:` terms must switch to the CRM terms; the switch will be tested.

## B. The dataset must change; how is a modelling choice

| # | problem (SHACL results) | options | suggestion |
|---|---|---|---|
| B1 | `crm:P46_is_composed_of` links monuments to murtis, bells, lions …, but the shapes allow it only for `hg:ArchitecturalElement` (17,593) | (a) use P46 only for architectural elements, and keep `hg:containsObject` for all objects (an undeclared term, see C); (b) drop the link for non-architectural objects | (a) |
| B2 | `hg:hasArchitecturalStyle` holds two values per monument, the AAT concept and the ontology's style value; the shape allows one value from its list (3,630) | keep only the ontology's style value on it; the AAT concept stays on `crm:P2_has_type`. For the 8 monuments with two styles, keep the first DANAM lists and note the other | as described |
| B3 | `hg:existenceStatus` takes the value `ExistenceStatus#Ruined`, which is not in the ontology's list, and up to 3 values per monument (676) | (a) one value derived from the condition: Ruined → PartiallyExtant, else Extant; (b) stop writing existence status (DANAM records condition, not existence) | your call; (b) is the most faithful, (a) keeps a value |
| B4 | `hg:hasConditionType` has up to 3 values per condition state; the shape allows 1 (213) | keep the first DANAM lists and put the others in a note (the monument-level condition literals keep all values) | as described |
| B5 | `hg:hasReligiousTradition` holds text (e.g. "Hindu, Buddhist"); the shape requires an IRI of class `hg:ReligiousTradition`, and **the ontology defines no such IRIs** (3,812) | (a) the ontology adds tradition values (C); (b) the dataset defines its own SKOS concepts until then | (a) if you can change the ontology; (b) as a stopgap |

**Effect:** −25,924 SHACL results (B1–B5).

## C. The ontology repo has to change

### C1. Shapes that are stricter than correct data (SHACL results)

| # | problem | proposed change in the ontology | results |
|---|---|---|---|
| C1a | Labels with a language tag (`"…"@en`, `@ne`) fail `sh:datatype xsd:string` | allow `rdf:langString`; one label per language (`sh:uniqueLang`) | 25,280 |
| C1b | DANAM identifiers (uuids, object numbers) fail `sh:datatype xsd:anyURI`. Cause: the LinkML `id` slot is mapped to `dcterms:identifier` | separate the node IRI from identifier strings; identifiers are strings | 18,311 |
| C1c | Every `hg:Temple` must have a style, but DANAM gives none for 200 temples | `sh:minCount 0` (or a warning) | 200 |
| — | 6 object nodes have two English labels (`rdfs:label` maxCount, 16) | **not an ontology problem**: DANAM uses 6 object numbers for two different objects each, and the builder merges them | 16 |

### C2. Terms the dataset needs that the ontology lacks (no SHACL results; the shapes are open)

| term | uses | what it is |
|---|---|---|
| `hg:BuddhistMonument` (class) | 215 | Buddhist monastic building (bāhāḥ, vihāra) |
| `hg:containsObject` / `hg:isObjectOf` | 7,155 each | monument holds a movable object (see B1) |
| `hg:hasMainDeity` | 1,049 | monument → main deity |
| `hg:danamCode` | 1,627 | DANAM site code |
| `hg:eventIndex` | 5,098 | position of the event in the DANAM record |
| `hg:extractionMethod` | 5,098 | how the row was obtained |
| `hg:conditionStatus` | 1,659 | condition as a literal on the monument (all values DANAM lists) |
| `hg:identifiedThreats` | 572 | threats text on the assessment |
| `hg:numStoreys`, `hg:numRoofs`, `hg:roofType`, `hg:brickType`, `hg:monumentShape` | 1,495 / 1,304 / 1,227 / 1,365 / 81 | building attributes |
| `hg:province`, `hg:district`, `hg:municipality`, `hg:tola` | 1,010 / 252 / 1,016 / 968 | place attributes |
| `hg:skill` | 1 | **remove** (belongs to the AI-agent attribution, which is wrong anyway) |

For each C2 term: either the ontology declares it, or the dataset maps it to a declared term, or drops it. This is
decision D1 below.

---

## Not part of the sync (later steps, after it)

These come up in review but are not about the ontology:
- provenance that attributes content to an "AI agent";
- the licence conflict, and `metadata.json` counts and checksum;
- IRIs that do not resolve;
- missing event dates;
- typing errors (e.g. renovations typed as destruction).

---

## Order and decisions

1. **A1–A11** (no decision needed). Expected after: 69,731 results.
2. **B1–B5**, after your decisions. Expected after: 43,807 results, all in group C1.
3. **C**, as issues or PRs in the ontology repo. Once a new ontology version is tagged, vendor it here and rerun.

**Decisions needed:**
- **D1:** for C1 and C2, will you change the ontology repo (issues/PRs and a new tagged version, e.g. 1.0.2 or 1.1.0)? Or should
  the dataset avoid every undeclared term (map or drop) and accept the C1 results?
- **B3:** existence status: (a) derive one value, or (b) stop writing it?
- **B5:** religious traditions: (a) wait for ontology values, or (b) dataset SKOS concepts now?
- **Go-ahead** for A1–A11.
