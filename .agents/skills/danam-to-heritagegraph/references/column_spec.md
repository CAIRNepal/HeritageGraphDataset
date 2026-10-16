# Column specification

Original DANAM columns are never edited. Derived or provenance columns are always *appended*.

## monuments.csv
All 46 input columns verbatim, then: `danam_code` (e.g. SKH0510, parsed from `name_devanagari` after `||`),
`name_ne` (Devanagari name without the code), `ontology_class`, `aat_style`, `condition_types`, `mapping_notes`.
Rows with no `monument_name` and no `description_en` (status "ok" but empty — DANAM returns these for dead pages) go to
`skipped_rows.csv` with their `resource_id`/`url`/`scraped_at`, not into monuments.csv.

## events.csv
Required, in this order (the user's schema):
`resource_id, monument_name, event_index, event_name, event_description, date_bce_ce, period, year_ss_ns_vs, nepali_month, paksha, tithi, sources`
Appended provenance columns: `ontology_class, evidence_text, extraction_method, confidence`.

| column | rule |
|---|---|
| resource_id, monument_name | copied verbatim from monuments.csv (monument_name keeps any "(before 608 CE)" suffix) |
| event_index | 0-based, chronological *as the text presents them*, contiguous per resource_id |
| event_name | short noun phrase, sentence case, e.g. "Renovation of the temple", "Theft"; `unknown` when the text records an undecipherable event |
| event_description | one or two sentences, stays close to the source wording; do not add facts |
| date_bce_ce | `1689 CE` / `1300 BCE`; blank if no year. Use the year as written in the source, even if it looks wrong — flag it in event_description instead |
| period | period the text names; otherwise derive from the CE year with `heritage_dates.period_for` (Licchavi <879, Early medieval <1200, Malla <1769, Śāha <1846, Rāṇā <1951, Post-Rāṇā) |
| year_ss_ns_vs | era label + year exactly as written: `NS 809`, `VS 2065`, `ŚS 1422`, `MS 32`. Blank if the text gives only CE — never back-compute an era year |
| nepali_month | canonical spelling from `heritage_dates.MONTHS` (Phālguna, Māgha, Āśvina …) |
| paksha | `Śukla` (bright) or `Kṛṣṇa` (dark) |
| tithi | integer 1–15 as digits; full moon/new moon → leave blank and say so in event_description |
| sources | the citation(s) exactly as they appear in the sentence, `; `-separated, e.g. `(T. Siṃha1136, p. 15, folio 23A)`. Blank when the sentence has none |
| ontology_class | see ontology_mapping.md |
| evidence_text | the **verbatim** sentence(s) from `description_en` that support the row — validate.py checks it is a substring |
| extraction_method | `llm_from_description` (default), `source_table` (parsed from a DANAM events table, no evidence_text needed), `rule` |
| confidence | high (explicit statement) / medium (needed interpretation) / low (ambiguous) |

## objects.csv
Required: `resource_id, monument_name, object_index, object_id, object_name, object_type, object_material, object_location, date_bce_ce, date_vs_ns`
Appended: `ontology_class, evidence_text, extraction_method, confidence`.

`object_id` is the DANAM pattern `AAA0000-000` copied from the text; its prefix should equal the monument's `danam_code`.
An ID with another prefix belongs to another monument record (e.g. CHG0160-004 mentioned inside CHG0170): still emit it
only when it is meaningfully described in this record, and expect a WARN from validate.py. `object_type` is the plain
category (Toraṇa, Statue, Pillar, Stone lion), `object_material` only if stated (stone, silver, gilded copper),
`object_location` the stated position ("sanctum", "north of the temple"). `date_vs_ns` follows the same label rule as
`year_ss_ns_vs`.
