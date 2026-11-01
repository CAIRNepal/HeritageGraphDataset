## Fix round 1: data quality before the paper

This PR fixes the problems found while compiling the paper facts: provenance, event typing, the condition link, deity
traditions, missing descriptions, and the release metadata. It also adds the paper-facts script. The ontology stays at
1.0.1. **SHACL: 200 results** (all temples for which DANAM records no style, unchanged). **Undeclared terms: 0.** The
OWL 2 RL closure is consistent. Published files in `releases/v1.0.0/` and `latest/` are not touched.

### Changes (one commit each, logged in `docs/sync/SYNC_LOG.md`)

| Fix | What changed | Statements |
|---|---|---|
| F1 Provenance | The "Antigravity AI Agent (DeepMind)" attribution is removed. Each DANAM report page is a `prov:Entity` attributed to DANAM (`prov:Organization`, named as on its site). Monuments, events and objects are `prov:wasDerivedFrom` their page. The construction activity is associated with the pipeline (`prov:SoftwareAgent`: repository and git commit), which acts on behalf of CAIR-Nepal. Query 05 shows page, source and software. | −12,259 attributions; 13,910 derivations (12,258 new) |
| F2, F9, F10 Event typing | All rules are in `event_typing.py` (18 rules, documented). Destruction only when the event name says so. Renovation, restoration, rebuilding and repair become `crm:E11_Modification`. Donations become `crm:E8_Acquisition` and guṭhī formations `crm:E66_Formation`, decided by the event name. Names that report two happenings get both classes. 'grant' no longer matches 'granthakūṭa'. | see table below |
| F3 Condition | `crm:P44_has_condition` points to the `crm:E3_Condition_State`, not the assessment. | 1,577 |
| F4 Deity traditions | Deities no longer take the tradition of the first monument that names them; DANAM states traditions per monument only. Monuments keep theirs. | −381 |
| F5 Descriptions | `description_en` / `description_ne` written as `dcterms:description` `@en` / `@ne`, unchanged from DANAM. | +3,047 |
| F6 Source funnel | No record is missing: `resourceids.csv` has 3 blank rows, so 1,944 IDs, all collected. 7 fetches failed (4 timeouts, 3 connection resets) and were not retried, so 1,937 records were parsed. Not re-crawled. | – |
| F7 Release metadata | `metadata.json` counts the 7,160 object nodes (not monuments too); every checksum is checked after writing. The licence field is unchanged (decision pending). | – |
| F8 Release safety | The release script refuses to run from a working tree with uncommitted changes. | – |

### Event classes (before → after; an event with two classes counts in both)

| Class | Before | After |
|---|---:|---:|
| `crm:E6_Destruction` | 695 | 265 |
| `crm:E11_Modification` | 0 | 1,280 |
| `crm:E12_Production` | 1,808 | 981 |
| `crm:E8_Acquisition` | 0 | 750 |
| `crm:E66_Formation` | 0 | 34 |
| `crm:E10_Transfer_of_Custody` | 284 | 245 |
| `hg:Consecration` / `hg:Enshrinement` | 128 / 87 | 122 / 74 |
| `hg:RitualEvent` (ritual rules only) | 85 | 80 |
| `crm:E14_Condition_Assessment` (events) | 15 | 16 |
| `hg:HistoricalEvent` | 1,996 | 1,310 |

The pre-change list of the 695 destruction events is in `docs/fixes/F2_destruction_events_before.md`.

### Paper facts

`tools/paper/stats.py` builds the graph into `build/paper/` (never `releases/` or `latest/`) and writes
`docs/paper/FACTS.md` and `docs/paper/numbers.tex` (one LaTeX macro per number). Run it with
`uv run --no-project --with-requirements tools/sync/requirements.txt python tools/paper/stats.py`; it takes about
3 minutes with the OWL closure, and `--skip-owlrl` makes it fast.

### Numbers

| | `main` | this PR |
|---|---:|---:|
| Triples | 224,782 | 229,142 |
| SHACL results | 200 | 200 |
| Undeclared terms | 0 | 0 |
| OWL 2 RL closure | consistent (942,854 triples) | consistent (913,394 triples) |
| Distinct record IDs | 1,945 (counted the blank) | 1,944 |

### Queries (rows without LIMIT)

Only query 02 changed: 5,313 → 5,353. It lists one row per event and class, and events with two classes add a row.
Query 05 was rewritten for the new provenance. Its row count is unchanged: 5,098, one per event.

### Tests

43 tests (`tests/test_sync.py` 31, `tests/test_fixes.py` 12) pass: one per fix, real DANAM events for each event-typing
rule, a scratch release in a temporary directory, and the dirty-tree refusal.

### Not in this PR (open)

- Licence: the graph says CC BY-SA 4.0, `metadata.json` says CC BY 4.0 (decision pending).
- The published v1.0.0 `metadata.json` still reports 8,806 objects and fails its checksum (the file was edited after the
  checksum was written); it is fixed at the next release.
- Instance IRIs (`https://data.cairnepal.org/heritage/resource/`) do not resolve.
- No event has a date: DANAM's event tables carry none.
- Event and object typing are keyword rules, not checked against a manual sample. Known misses: 'Renovation, new
  construction, land endowment and guṭhī formation' (word order) stays modification + transfer.
