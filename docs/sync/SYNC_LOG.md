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

## B5: religious traditions (STOPPED before applying: one open question)

Source column `religion` (monuments; the builder also copies it to the monument's main deity). 1,523 monuments have a value, 46 distinct strings; 129 are blank. Split on `,` they give 10 distinct values:

| source value | monuments | proposed concept (`hgn:`, typed `hg:ReligiousTradition` and `skos:Concept`, in `hgn:ReligiousTraditionScheme`) |
|---|---|---|
| Buddhist | 441 | `hgn:tradition-Buddhist`, prefLabel "Buddhist"@en |
| Unspecified | 376 | **open question** (see below) |
| Hindu | 275 | `hgn:tradition-Hindu`, prefLabel "Hindu"@en |
| Shaiva | 256 | `hgn:tradition-Shaiva`, prefLabel "Shaiva"@en |
| Shakta | 151 | `hgn:tradition-Shakta`, prefLabel "Shakta"@en |
| Hindu-Buddhist | 119 | `hgn:tradition-HinduBuddhist`, prefLabel "Hindu-Buddhist"@en |
| Vaishnava | 113 | `hgn:tradition-Vaishnava`, prefLabel "Vaishnava"@en |
| Folk | 9 | `hgn:tradition-Folk`, prefLabel "Folk"@en |
| Shamanistic | 7 | `hgn:tradition-Shamanistic`, prefLabel "Shamanistic"@en |
| Sikh | 2 | `hgn:tradition-Sikh`, prefLabel "Sikh"@en |

Each concept's label is the DANAM string as written. "Hindu-Buddhist" is kept as its own concept, because DANAM uses it as a value of its own, distinct from "Hindu, Buddhist". No hierarchy (e.g. Shaiva under Hindu) is added, because DANAM does not state one.

**Open question:** 361 monuments, and 15 more in combinations, have the value "Unspecified". It reads as "DANAM does not know", not as a tradition. Options: (a) leave it out, so those monuments get no tradition ("blank beats guessed"); (b) make it a concept `hgn:tradition-Unspecified` so the source value is kept. This is a modelling choice not covered by the task, so B5 is not applied yet.

All distinct source strings with their counts:

- `Unspecified` 361
- `Buddhist` 321
- `Shaiva` 196
- `Shakta` 132
- `Hindu-Buddhist` 112
- `Hindu` 98
- `Vaishnava` 93
- `Hindu, Buddhist` 63
- `Buddhist, Hindu` 43
- `Hindu, Shaiva` 18
- `Shaiva, Hindu` 16
- `Hindu, Vaishnava` 7
- `Hindu, Unspecified` 6
- `Shaiva, Shakta` 5
- `Vaishnava, Shaiva` 5
- `Buddhist, Unspecified` 5
- `Vaishnava, Hindu` 4
- `Hindu, Shakta, Shaiva` 3
- `Sikh` 2
- `Hindu, Shakta` 2
- `Folk` 2
- `Folk, Shamanistic, Hindu` 2
- `Shakta, Shaiva` 2
- `Hindu-Buddhist, Buddhist` 2
- `Shaiva, Hindu-Buddhist` 2
- `Shaiva, Vaishnava` 1
- `Shamanistic, Folk, Shaiva, Hindu` 1
- `Shamanistic, Folk` 1
- `Buddhist, Shaiva` 1
- `Shakta, Vaishnava, Shaiva` 1
- `Shaiva, Hindu, Buddhist` 1
- `Unspecified, Hindu-Buddhist` 1
- `Hindu, Shaiva, Shakta` 1
- `Hindu, Hindu-Buddhist, Buddhist` 1
- `Shakta, Hindu` 1
- `Shaiva, Vaishnava, Shakta` 1
- `Folk, Buddhist, Hindu` 1
- `Shakta, Unspecified` 1
- `Unspecified, Hindu` 1
- `Hindu, Shamanistic` 1
- `Vaishnava, Shaiva, Hindu` 1
- `Shamanistic, Hindu, Hindu-Buddhist, Folk, Buddhist` 1
- `Shakta, Buddhist, Hindu` 1
- `Unspecified, Buddhist` 1
- `Shakta, Hindu, Shaiva` 1
- `Folk, Hindu, Shamanistic` 1

## C1a: rdfs:label is one plain-string English label; language-tagged labels (@en, @ne) on skos:prefLabel

- Test: `tests/test_sync.py::test_c1a_plain_string_label_and_tagged_pref_labels`.
- Triples: 184,992 → **203,511**.
- SHACL results: 48,640 → **22,339** (5 groups).
- Undeclared terms: 17 → **17** (1 classes, 16 properties, 0 IRI values).
- Extension terms used: 2.
- Queries (rows without LIMIT): unchanged.
- Findings checked first: the xsd:string constraint is on rdfs:label (58 shapes: sh:datatype xsd:string, sh:maxCount 1, 18 also sh:minCount 1); skos:prefLabel and skos:altLabel are not constrained by any shape. Monuments' Nepali names (schema:name @ne) are also given as skos:prefLabel @ne.

## C1b: DANAM identifiers as crm:E42_Identifier (crm:P1_is_identified_by, crm:P190_has_symbolic_content, kind on crm:P2_has_type) instead of dcterms:identifier

- Test: `tests/test_sync.py::test_c1b_identifiers_are_crm_e42`.
- Triples: 203,511 → **229,929**.
- SHACL results: 22,339 → **4,028** (4 groups).
- Undeclared terms: 17 → **17** (1 classes, 16 properties, 0 IRI values).
- Extension terms used: 4.
- Queries (rows without LIMIT): unchanged.
- Checked first: no shape constrains crm:P1_is_identified_by or crm:P190_has_symbolic_content, and none targets crm:E42_Identifier. Kinds: hgn:DanamResourceId (monuments), hgn:DanamObjectNumber (objects). Query 04 reads the object number from the identifier node.

## R1: reused DANAM object numbers: one node per object row

- Test: `tests/test_sync.py::test_r1_reused_object_numbers_give_distinct_nodes`.
- Triples: 229,929 → **229,968**.
- SHACL results: 4,028 → **4,012** (3 groups).
- Undeclared terms: 17 → **17** (1 classes, 16 properties, 0 IRI values).
- Extension terms used: 4.
- Queries (rows without LIMIT): **changed:** `04_monument_sacred_objects.rq` 9008 → 9001
- Query rows changed, accepted: query 04 9,008 → 9,001: the merged nodes used to multiply their two labels by their classes; each object now has one label.
- The 6 numbers (node IRIs now <number>_1, <number>_2; both keep the DANAM number as identifier): LAL2570-001 (Śikharakūṭa Caitya; Statue of Donor) https://danam.cats.uni-heidelberg.de/report/1798db32-ecce-11e9-8bc4-0242ac130002 · KAT2130-003 (Lion; lion) https://danam.cats.uni-heidelberg.de/report/41dddca9-4465-44d7-9e66-330391c7f252 · LAL0841-006 in two monuments (Viṣṇu; Licchavi Caitya) https://danam.cats.uni-heidelberg.de/report/5d44f5b8-70f8-11ea-966a-0242ac130006 and https://danam.cats.uni-heidelberg.de/report/5f27520c-348e-43da-8160-a2e2729a37c7 · KAT1150-014 (Garuḍanārāyaṇa; Gaṇeśa (B)) https://danam.cats.uni-heidelberg.de/report/7171bc5b-58ee-4d5d-9808-c118c20022de · SUN0010-004 (Statue of Jalaśayana Viṣṇu on the south…; Jalaśayana Viṣṇu; possibly the same statue listed twice, kept as two nodes as instructed) https://danam.cats.uni-heidelberg.de/report/872e0e8c-f0ba-11e9-a3c8-0242ac130002 · TOK0090-001 (Umāmaheśvara; Bell) https://danam.cats.uni-heidelberg.de/report/a0c8744f-2928-4961-b072-638c22e48522. Links monument→object: 7,155 → 7,160 (one per row).

## C1c: temples without a style (left as they are)

Every `hg:Temple` must have one `hg:hasArchitecturalStyle` (`sh:minCount 1`). DANAM gives no style for these 200 temples (their `aat_style` is blank), so they stay without one: 200 SHACL results, by decision.

<details><summary>The 200 temples</summary>

| monument | DANAM code | page |
|---|---|---|
| Agnimaṭha (before 1403 CE) | LAL0280 | https://danam.cats.uni-heidelberg.de/report/1e2335a0-f62a-11e9-a3c8-0242ac130002 |
| Anantanārāyaṇa | PPK0220 | https://danam.cats.uni-heidelberg.de/report/9752a039-ad65-4746-967d-d929708e2add |
| Aryālaghāṭa | KAT2735 | https://danam.cats.uni-heidelberg.de/report/789caaca-6d46-4532-9e19-5c246b03e727 |
| Āgaṃchẽ | SKH0080 | https://danam.cats.uni-heidelberg.de/report/0d31ecbb-8716-4c9d-9765-2a9bb3df8426 |
| Balabhadra (c. 685 CE) | LAL0040 | https://danam.cats.uni-heidelberg.de/report/489cc406-57c1-11ea-b4c2-0242ac130006 |
| Basantapur Bāhāḥ | KAT2060 | https://danam.cats.uni-heidelberg.de/report/ec4c5daf-9b79-4bb0-8a72-00410822e759 |
| Bālakumārī  Shrine | KAT0460 | https://danam.cats.uni-heidelberg.de/report/4b258630-add1-4e0a-a29c-ba2cac44462d |
| Baḥsimākva Dyaḥ | SKH0260 | https://danam.cats.uni-heidelberg.de/report/ef3aec8e-b30b-40fc-8c6d-a68adaa941c2 |
| Baṭārabajāra Bhīmasena Shrine | NWK0680 | https://danam.cats.uni-heidelberg.de/report/841f7541-bf44-4d6e-8768-7a2f4baa433b |
| Bekhārāja Bāhāḥ (1892 CE) | LAL0200 | https://danam.cats.uni-heidelberg.de/report/5f0eb57e-e8d0-11e9-8bc4-0242ac130002 |
| Bhadrakālī Dyaḥchẽ | KAT0660 | https://danam.cats.uni-heidelberg.de/report/5f138c22-c608-41f2-8044-b156758e4c12 |
| Bhadrakālī Pīṭha | BKT0450 | https://danam.cats.uni-heidelberg.de/report/20f94fd5-6a84-41a1-8744-c5d77c994e4d |
| Bhadreśvara Śivaliṅga (533 CE) | PPK0518 | https://danam.cats.uni-heidelberg.de/report/abc0bacd-08c7-4755-9b28-213452d31c04 |
| Bhagavatī Asigrāma archaeological remains | DDL0040 | https://danam.cats.uni-heidelberg.de/report/6bb91e99-b953-4be7-855b-70a870f1c1b4 |
| Bhairama Koṭa | NWK0640 | https://danam.cats.uni-heidelberg.de/report/38e903db-8952-4d35-a139-e249b081ade7 |
| Bhairaveśa Mandira (1752 CE) | NWK0630 | https://danam.cats.uni-heidelberg.de/report/bac35fbc-b725-48a1-b24a-bfa91ef8e095 |
| Bhairaveśvara Mandira | NWK0730 | https://danam.cats.uni-heidelberg.de/report/b9965c72-c35d-4a80-8c16-b18805db2ca5 |
| Bhairavī Shrine | LAL2990 | https://danam.cats.uni-heidelberg.de/report/4c6f4501-3d62-4c19-8445-b9927856cee1 |
| Bhajanachẽ | SKH0200 | https://danam.cats.uni-heidelberg.de/report/2ac12f52-a15d-419a-a69a-b7365793665c |
| Bhājaṅgala Lvahaṃ Degaḥ West | KIR0085 | https://danam.cats.uni-heidelberg.de/report/8c6f0d84-8d44-4478-b428-0bd9de407738 |
| Bhaṇḍārībādā Shrine | JUM0031 | https://danam.cats.uni-heidelberg.de/report/fa830245-9aef-48cd-bc16-9b20d4062b16 |
| Bhirat Durbar Temple 1 | JUM0480 | https://danam.cats.uni-heidelberg.de/report/5b3406d3-fe11-4902-b6aa-50b862f58360 |
| Bhirat Durbar Temple 2 | JUM0481 | https://danam.cats.uni-heidelberg.de/report/e081756c-ea13-4d91-8129-1dd53ba57c99 |
| Bhīmasena Shrine (built in 2000 CE) | SKH0044 | https://danam.cats.uni-heidelberg.de/report/285a778e-0352-450b-a044-2749fef0237c |
| Bhuvaneśvarī Shrine | LAL2950 | https://danam.cats.uni-heidelberg.de/report/c501bcf1-1a77-4259-99b9-f5cb452c8f82 |
| Bhīmasena Dyaḥchẽ (1658 CE) | LAL1680 | https://danam.cats.uni-heidelberg.de/report/557a604c-e6a7-11e9-8bc4-0242ac130002 |
| Bhīmasena Shrine | BKT0370 | https://danam.cats.uni-heidelberg.de/report/1cec4a1b-2ea4-42d7-afdc-f61859bf82cb |
| Bhīmasena Shrine | PNT0170 | https://danam.cats.uni-heidelberg.de/report/32270c02-f3ba-4f53-9930-621694f62a06 |
| Bhīmasena Shrine | NWK0340 | https://danam.cats.uni-heidelberg.de/report/ac5635e0-48da-4c10-b379-55e0a99e932b |
| Brahmāyaṇī Dyaḥchẽ | PNT0210 | https://danam.cats.uni-heidelberg.de/report/406cfc7f-eec3-40b4-988c-d82c522f48c5 |
| Brahmāyaṇī Pīṭha | SKH0123 | https://danam.cats.uni-heidelberg.de/report/448859a2-1768-40eb-82af-c2858e756332 |
| Brahmāyaṇī Pīṭha | BKT0250 | https://danam.cats.uni-heidelberg.de/report/52125686-c4a3-4de0-8eae-5d169c02bdc1 |
| Buddha Shrine | PPK0710 | https://danam.cats.uni-heidelberg.de/report/283e3155-3597-472e-afcd-e125391bebfc |
| Bulu Bhairava Mandira ( early 20th century) | BUL0010 | https://danam.cats.uni-heidelberg.de/report/64a2bcf3-96b8-4af7-9a2e-64be0fe4ca39 |
| Bābiro Māru | JUM0161 | https://danam.cats.uni-heidelberg.de/report/fffd6d54-efad-42e5-bbfd-3196ec129bb8 |
| Bālakumārī (ca. 18th cent) | SUN0230 | https://danam.cats.uni-heidelberg.de/report/6e03bbf6-0522-11ea-8f3c-0242ac130002 |
| Bālakumārī Dyaḥchẽ | LAL2140 | https://danam.cats.uni-heidelberg.de/report/781d9148-efea-47f6-bfee-3aa004bf0e43 |
| Bālāgāũ Mahālakṣmī Pīṭha | BLG0030 | https://danam.cats.uni-heidelberg.de/report/390ac54b-f92b-4666-82fc-82543f77755e |
| Calākhu Gaṇeśa | SKH0180 | https://danam.cats.uni-heidelberg.de/report/d1fe9550-9469-487a-b0b1-6aa5b6513dd0 |
| Caṇḍeśvarī Dyaḥchẽ | TOK0090 | https://danam.cats.uni-heidelberg.de/report/a0c8744f-2928-4961-b072-638c22e48522 |
| Chumā Gaṇeśa Dyaḥchẽ | BKT0152 | https://danam.cats.uni-heidelberg.de/report/e3f05128-990f-4936-a54b-8dc13ac4822b |
| Chvāsakāminī | LAL0580 | https://danam.cats.uni-heidelberg.de/report/51d9d5da-4ceb-11ea-8083-0242ac130006 |
| Cimṭeśvara Shrine (ca. 1743-1951 CE) | NWK0250 | https://danam.cats.uni-heidelberg.de/report/53551db6-eafd-43fe-bad2-2f298587bdb7 |
| Cunikhela Bhadrakālī Dyaḥchẽ | KAT3500 | https://danam.cats.uni-heidelberg.de/report/9fd3dca8-39d8-40ad-a48f-02fd56e43b83 |
| Dabū and temporary shrine | BUN0003 | https://danam.cats.uni-heidelberg.de/report/8fe3c368-1cbc-11ea-b74e-0242ac130002 |
| Dakṣiṇakālī Dyaḥchẽ | PRN0130 | https://danam.cats.uni-heidelberg.de/report/6435dbc3-4939-4a8d-b1ba-32d60e416984 |
| Debali Buddha Shrine | BKT0222 | https://danam.cats.uni-heidelberg.de/report/7de16804-8f8d-4613-bb41-e06138214610 |
| Devanani Lokeśvara Mandira | LAL2650 | https://danam.cats.uni-heidelberg.de/report/0274d17a-ceb6-4480-bcbd-8d893d078724 |
| Dharma Gaddi statues and stone memorial pillar | DLK0200 | https://danam.cats.uni-heidelberg.de/report/9585e306-2c44-4079-881d-906961510351 |
| Dharmasthalī Cāmuṇḍā Dyaḥchẽ | KAT3410 | https://danam.cats.uni-heidelberg.de/report/eeddb051-7d29-4453-b290-7ae1d3737ac4 |
| Dharmasthalī Cāmuṇḍā Pīṭha | KAT3412 | https://danam.cats.uni-heidelberg.de/report/e9be12a4-26f5-4071-b154-c0fac1598712 |
| Dhaṃtila Vārāhī | LAL2960 | https://danam.cats.uni-heidelberg.de/report/e277eff9-5f7a-405c-908b-e3d13cda743e |
| Dhuleśvara Jvālā Ghar | DLK0331 | https://danam.cats.uni-heidelberg.de/report/0c4603b9-882a-4c07-bc3a-5d5e6bd364cf |
| Dhuleśvara Śivaji Mahādev Mandir | DLK0330 | https://danam.cats.uni-heidelberg.de/report/2b74cf06-76ad-4bd8-a1c8-5bfa3730b9f3 |
| Dhũllā Gaṇeśa Shrine | SKH0050 | https://danam.cats.uni-heidelberg.de/report/bb21b677-3f21-4f9d-abc1-fe269c816609 |
| Dhāmī Ghara (1792 CE) | NWK0020 | https://danam.cats.uni-heidelberg.de/report/ba4a96ce-5b25-4ede-9c17-7bf5f88b5534 |
| Dhūmāvatī Shrine | LAL2940 | https://danam.cats.uni-heidelberg.de/report/283342f3-8585-4e60-a605-56189e73bea1 |
| Digi Chẽ | LAL0068 | https://danam.cats.uni-heidelberg.de/report/cdf9d48b-aebf-4118-b2b8-268e50db4c30 |
| Digichẽ  at Ī Bahī (rebuilt in ca. 1936 CE) | LAL1481 | https://danam.cats.uni-heidelberg.de/report/26daa57e-e6ae-11e9-8bc4-0242ac130002 |
| Dolakhādevī Mandira | NWK0830 | https://danam.cats.uni-heidelberg.de/report/dc757cea-d270-4a77-a3e0-914fb99386f5 |
| Dolã Māju | LAL2820 | https://danam.cats.uni-heidelberg.de/report/ef7069e0-9e23-4cb6-8af4-b5220d7197b0 |
| Dugāḥ Hiti Gaṇeśa | SKH0190 | https://danam.cats.uni-heidelberg.de/report/9b7966f5-3810-403b-ac6d-29dc76d720f9 |
| Duimāju Shrine (first established in 1588 CE) | LAL1223 | https://danam.cats.uni-heidelberg.de/report/5aa92f9a-d874-4b89-89b8-adf291c884c8 |
| Gaṇeśa Cuka | KAT0452 | https://danam.cats.uni-heidelberg.de/report/bb024f91-1f2f-44ee-8cc9-8e0360c40c92 |
| Gaṇeśa Mandira | KAT0540 | https://danam.cats.uni-heidelberg.de/report/8f950bba-35d6-4c31-b433-998dd962ec8b |
| Garuḍanārāyaṇa Shrine | NWK0350 | https://danam.cats.uni-heidelberg.de/report/a67dbf5c-6526-4333-8e6b-0788723f9f20 |
| Gaṇeśa Shrine (c. mid- 17th cent. CE) | BUN0023 | https://danam.cats.uni-heidelberg.de/report/990ceb20-1c32-11ea-b9b1-0242ac130002 |
| Ghana Bāhāḥ (ca. 1840 CE) | LAL2330 | https://danam.cats.uni-heidelberg.de/report/f17e763a-e815-11e9-b125-0242ac130002 |
| Gorakhanātha Shrine | KAT1551 | https://danam.cats.uni-heidelberg.de/report/93e89fd3-3217-499f-90fb-4aa7ec3c7efa |
| Gorakhanātha Pīṭha (1667 CE) | KIR0050 | https://danam.cats.uni-heidelberg.de/report/4a48d563-85d1-4e51-8f78-2254393f85e2 |
| Guru Nānaka Ghara | KAT2830 | https://danam.cats.uni-heidelberg.de/report/95ae1a0f-e0e0-42bf-8101-4507d5462b17 |
| Hanumān Pillar (established in1672 CE) | KAT1730 | https://danam.cats.uni-heidelberg.de/report/2dc687d3-753b-421c-802c-e9f74a427496 |
| Hanumān Shrine | PPK1709 | https://danam.cats.uni-heidelberg.de/report/d0dd5bdf-90e7-4217-a90c-83504c9ea90b |
| Hanumānthāna (1814 CE) | LAL2851 | https://danam.cats.uni-heidelberg.de/report/60d8283f-d7d3-4f40-a552-d9e2843a56b6 |
| Haugaḥ Ganedyaḥ Phalcā (ca. mid-17th century CE) | LAL4122 | https://danam.cats.uni-heidelberg.de/report/2070b496-e729-11e9-8bc4-0242ac130002 |
| Haugaḥ Hāratī Shrine | LAL3020 | https://danam.cats.uni-heidelberg.de/report/f771b0b6-0d77-4d03-9578-ddef947a93f6 |
| Hāṭa Gāũ (c. 14th-15th cent.) | DDL0030 | https://danam.cats.uni-heidelberg.de/report/24779526-7b25-4512-ac56-5d503d43020a |
| Indreśvara Mandira | PPK1215 | https://danam.cats.uni-heidelberg.de/report/643839ec-b5bf-482f-a357-7ffe0d8617ba |
| Indrāyaṇī Dyaḥchẽ (c. 1778 CE) | KIR0058 | https://danam.cats.uni-heidelberg.de/report/8ef7a2bb-be68-438f-9902-2914c6ebc9f1 |
| Indrāyaṇī Ghāṭa | NWK0700 | https://danam.cats.uni-heidelberg.de/report/f9bfb983-9500-4d2c-b612-7bd0bfc0b189 |
| Indrāyaṇī Mandira | NWK0110 | https://danam.cats.uni-heidelberg.de/report/696107df-1146-4ab2-a156-5f2bd7774c24 |
| Indrāyaṇī Pīṭha | BKT0050 | https://danam.cats.uni-heidelberg.de/report/337c6d44-c619-4816-b823-c10f18d802b4 |
| Ipātvāḥ Gaṇeśa Mandira | SKH0270 | https://danam.cats.uni-heidelberg.de/report/fffd4e1d-aa4c-46b3-bcbb-f181030c0f27 |
| Ipātvāḥ Nāsaḥdyaḥ | SKH0280 | https://danam.cats.uni-heidelberg.de/report/de6a819f-a310-4927-bde7-c361d96741d1 |
| Ituṃ Bāhāḥ Nani (before 1641 CE) | KAT1200 | https://danam.cats.uni-heidelberg.de/report/ae46da6b-090a-4862-9c95-cdacce669242 |
| Jayabali Dyaḥ | SKH0230 | https://danam.cats.uni-heidelberg.de/report/00bc99b7-02d7-48d4-948b-5d0ef1f84146 |
| Jhilṭuṅga Kāmarūdevī Mandira | NWK0570 | https://danam.cats.uni-heidelberg.de/report/57d7a521-5b29-4109-94c1-f2c1831b9b98 |
| Jitāpura Gaṃcā (1758 CE) | KHO0030 | https://danam.cats.uni-heidelberg.de/report/57c22b4c-559d-43bf-b9c6-417f669f4127 |
| Jom Bāhāḥ | LAL2680 | https://danam.cats.uni-heidelberg.de/report/63d66002-8bc5-48b3-af42-cf40b44b38d1 |
| Jyāthā Sarasvatī Shrine | KAT0030 | https://danam.cats.uni-heidelberg.de/report/ac18b25b-3750-43c5-b210-30375b978271 |
| Jālapādevī Pīṭha | NWK0740 | https://danam.cats.uni-heidelberg.de/report/25a85733-d299-46ba-b9b2-fa0ec5553d37 |
| Kalmochanaghāta | KAT2780 | https://danam.cats.uni-heidelberg.de/report/316e30ee-9dfd-4deb-a3bb-1cadf3b24876 |
| Kamalādī Gaṇeśa Dyaḥchẽ | KAT0041 | https://danam.cats.uni-heidelberg.de/report/b1f40172-f009-4f19-b738-5b47e1f412f9 |
| Kanakāsundarī Mandira | JUM0430 | https://danam.cats.uni-heidelberg.de/report/9d98c866-edfe-4172-9754-b538421ac2a1 |
| Karuṇāmaya Pīṭha | KIR0046 | https://danam.cats.uni-heidelberg.de/report/1456e045-3a8c-4c89-aace-573cfbd2ea87 |
| Kaumārī Pīṭha | BKT0630 | https://danam.cats.uni-heidelberg.de/report/3613a56a-48bc-4de1-ba52-1d7fcda2127f |
| Kirāteśvara Mandira | PPK1717 | https://danam.cats.uni-heidelberg.de/report/97bdacd9-8de4-4c7d-bbc0-ca2259cc2a1d |
| Kolkhu Ajimā Shrine | KAT0851 | https://danam.cats.uni-heidelberg.de/report/d4647012-a10e-4bba-b9c3-487dffc969ca |
| Kota Pāṭī  (18th cent.) | LAL4126 | https://danam.cats.uni-heidelberg.de/report/6206f79c-e5dc-11e9-8bc4-0242ac130002 |
| Koṭilā Koṭeśvara Mahādeva Mandira | DLK0430 | https://danam.cats.uni-heidelberg.de/report/4f1b6bc1-18b0-4112-b7c5-6b8d0302ae61 |
| Kulabhakteśvara Mandira (1795 CE) | NWK0760 | https://danam.cats.uni-heidelberg.de/report/d4b910cb-6665-466f-8211-9f1525a07057 |
| Kulle Koṭa | BTD0050 | https://danam.cats.uni-heidelberg.de/report/69280807-eee5-40af-a285-7fc9cb500ad6 |
| Kumārī Dyaḥchẽ | KAT2050 | https://danam.cats.uni-heidelberg.de/report/5a586e84-f249-40e3-ae4d-279a357ed75a |
| Kvaynā Gaṇeśa Dyaḥchẽ | LAL2970 | https://danam.cats.uni-heidelberg.de/report/b4d596ce-e31d-45d7-a9af-40f7cc1b568b |
| Kāgeśvara | PPK1311 | https://danam.cats.uni-heidelberg.de/report/c0b8c7bc-2482-4ace-9a4a-044aba344271 |
| Kālabhairava Shrine | KAT1770 | https://danam.cats.uni-heidelberg.de/report/158d3469-134c-4662-a1a9-9fbb1eb5444d |
| Kālabhairava Shrine (1631 CE) | NWK0360 | https://danam.cats.uni-heidelberg.de/report/5394724d-7746-4a10-be2a-d8ea3c79bc18 |
| Kāleśvara Mahādeva | PYG0010 | https://danam.cats.uni-heidelberg.de/report/20b36bbb-2e66-448f-b755-df44dc8ecd81 |
| Kālikā Mandira (late 20th century) | KAT1500 | https://danam.cats.uni-heidelberg.de/report/d6327d2c-6457-4406-89aa-4ea448ce22e3 |
| Lalāṭa Mandira (approx. 14th century) | DLK0140 | https://danam.cats.uni-heidelberg.de/report/300c3586-2b3b-4e52-8b7a-4637bcd3691d |
| Lekhpur Lāmā Banthān | JUM0540 | https://danam.cats.uni-heidelberg.de/report/68a341b0-d815-480f-8a03-89fa7b4d53a2 |
| Lokeśvara Dyaḥchẽ (renovated in 1730 CE) | LAL2180 | https://danam.cats.uni-heidelberg.de/report/cdc824f7-fbb4-4aa3-b164-441876d29ed8 |
| Lucubhulu Ajimā Dyaḥchẽ (built ca. 17th Cent.) | KAT0570 | https://danam.cats.uni-heidelberg.de/report/5f7c8a35-417f-41e7-8fbc-54e21cebc30e |
| Lũmadhi Ajimā Dyaḥchẽ | KAT1390 | https://danam.cats.uni-heidelberg.de/report/051a3dc8-3787-4227-b269-4014a16805fe |
| Mahākāla Shrine (ca. early 20th cent. CE) | SUN0200 | https://danam.cats.uni-heidelberg.de/report/5a2b953a-01f9-11ea-8f3c-0242ac130002 |
| Mahālakṣmī Shrine (built before 1692 CE) | SKH0160 | https://danam.cats.uni-heidelberg.de/report/e5c51d19-b453-4aaa-bbae-8a2859f5dfb7 |
| Mahādeva Mandira | NWK0080 | https://danam.cats.uni-heidelberg.de/report/f9f53336-9e6d-49f9-a522-f68ce6b90f1b |
| Mahākāla Shrine | SKH0600 | https://danam.cats.uni-heidelberg.de/report/959482f1-8473-456a-ba8a-37ee44b9ba7f |
| Mahākālī Dyaḥchẽ | BKT0160 | https://danam.cats.uni-heidelberg.de/report/3e97265e-b2b4-4a68-862a-7c76dee0bacc |
| Manamāneśvarī | KAT3050 | https://danam.cats.uni-heidelberg.de/report/34d3a0bc-bf6d-489e-b2a4-9bf09d771740 |
| Mañjuśrī Devala | KAT2070 | https://danam.cats.uni-heidelberg.de/report/ac3bfb78-41ac-4f2c-b538-4e30ff98c4ff |
| Mañjuśrī and Nāsaḥdyaḥ Dyaḥchẽ | KAT1380 | https://danam.cats.uni-heidelberg.de/report/227169da-a4d2-4266-bbbd-1a3f4a1dd5eb |
| Maru Gaṇeśa Dyaḥchẽ | KAT1950 | https://danam.cats.uni-heidelberg.de/report/89c68953-0d12-428c-86ef-5e6ddc36a313 |
| Mādhavanārāyaṇa Dyaḥchẽ | SKH0100 | https://danam.cats.uni-heidelberg.de/report/8615d9f8-6a73-4cba-b143-c4e086ea5f1b |
| Mhāsukhvāḥmāju Dyaḥchẽ | SKH0550 | https://danam.cats.uni-heidelberg.de/report/7f65c791-011e-43e9-8249-60d1c8614c2f |
| Mucalinda Buddha | NWK0840 | https://danam.cats.uni-heidelberg.de/report/5c95d1fa-c72a-4863-a1e8-021bdf603a4a |
| Mūla Coka (1666 CE) | LAL1260 | https://danam.cats.uni-heidelberg.de/report/39bb2040-e9fd-11e9-8bc4-0242ac130002 |
| Māhādyaḥ Nani Āgama | LAL0340 | https://danam.cats.uni-heidelberg.de/report/12d828f2-e4f7-11e9-8bc4-0242ac130002 |
| Mātaṅgī Shrine | LAL2930 | https://danam.cats.uni-heidelberg.de/report/ecff7ce1-747e-44bf-a543-529323af1d8f |
| Mūchẽ Āgama (ca. early 15th cent. CE) | LAL1372 | https://danam.cats.uni-heidelberg.de/report/409cfb82-e6c3-11e9-b125-0242ac130002 |
| Namarā Dyaḥchẽ | PNT0190 | https://danam.cats.uni-heidelberg.de/report/5555bd20-c739-469e-918b-6350ae42c654 |
| Navadurgā Mandira | KAT1370 | https://danam.cats.uni-heidelberg.de/report/6ab370ab-d00c-4748-9b02-a8f045cde7ae |
| Nārāyaṇa Mandira | SKH0154 | https://danam.cats.uni-heidelberg.de/report/554794d4-162a-4653-b06e-9b0cd0fc3209 |
| Nārāyaṇa Shrine | NWK0510 | https://danam.cats.uni-heidelberg.de/report/5f753c8c-ee22-49c1-a913-42aea8730977 |
| Nāsaḥ Chẽ |  | https://danam.cats.uni-heidelberg.de/report/21b56e2d-d3ff-4ce6-94cc-d5b85fb8a31e |
| Nāsaḥtvāḥ Gaṇeśa | PPK0907 | https://danam.cats.uni-heidelberg.de/report/60735091-b54f-4c9e-89cc-a6bbff1cd289 |
| Nātheśvara Śivaliṅga | PPK0328 | https://danam.cats.uni-heidelberg.de/report/b591fd8e-c93c-4ddc-929d-f8ae35c530a0 |
| Nīlvārāhī Temple Complex | BOD0050 | https://danam.cats.uni-heidelberg.de/report/42618ed6-aa6a-4248-99a1-e48996c49102 |
| Nṛtyeśvara Degaḥ (1688 CE) | LAL2710 | https://danam.cats.uni-heidelberg.de/report/d8d8d8e4-76ea-4db0-a222-6527d4e0eda3 |
| Panautī Nāsaḥdyaḥ | PNT0220 | https://danam.cats.uni-heidelberg.de/report/529d8d9b-db8c-4792-9163-2c04810b6442 |
| Piṅgalāmāī Shrine | PPK1410 | https://danam.cats.uni-heidelberg.de/report/fde1a7e2-5e0d-4dd6-bdeb-12b861aec8d6 |
| Porpā Ajimā Pīṭha | KAT3400 | https://danam.cats.uni-heidelberg.de/report/d11caed6-72b9-48a6-806f-41d78339129d |
| Pācāgaṇeśa Shrine | PPK1306 | https://danam.cats.uni-heidelberg.de/report/477a5dd0-d275-45c4-bba4-a48cf3f237a6 |
| Pādukāsthān Guntighar | DLK0273 | https://danam.cats.uni-heidelberg.de/report/e03065fa-ed14-4047-a1f9-1469df62747f |
| Pādukāsthān Siddha Guphā | DLK0271 | https://danam.cats.uni-heidelberg.de/report/1a53e635-cc47-4f38-b131-c990e76b8655 |
| Pīgaṃdyaḥ (Indrāyaṇī Pīṭha) | KIR0007 | https://danam.cats.uni-heidelberg.de/report/d62e32fe-b78c-43af-817c-edb16e6d7ae8 |
| Pīgaṃdyaḥ Pīṭha |  | https://danam.cats.uni-heidelberg.de/report/2da0a89a-f458-4203-99cf-d119819a48bd |
| Rasipatan temple and stone memorial pillar | JUM0530 | https://danam.cats.uni-heidelberg.de/report/00b7965f-0803-49e0-989f-62e679535c0c |
| Ratneśvara | PPK1310 | https://danam.cats.uni-heidelberg.de/report/ef3c4df6-7764-4432-91a4-abd290cf4b45 |
| Rudrāyaṇī Pīṭha | NWK0230 | https://danam.cats.uni-heidelberg.de/report/34697056-9775-466d-b46d-c83f874b93d3 |
| Rugā Maṣṭā Temple | MUG0020 | https://danam.cats.uni-heidelberg.de/report/1ea6cab2-5d1b-47be-be85-8bbe22658104 |
| Rāma Bāhāḥ | KAT0070 | https://danam.cats.uni-heidelberg.de/report/f7ee7e3d-05d2-4664-be56-f83a281613af |
| Rārā Mahādeva Mandira | MUG0110 | https://danam.cats.uni-heidelberg.de/report/7605825a-b679-4eb0-a1c0-8365e6493bfa |
| Sanepa Sataḥ | LAL4340 | https://danam.cats.uni-heidelberg.de/report/a3394b46-8421-4260-9385-6a5379527e60 |
| Sarasvatī Phalcā (ca. mid/late 17th cent) | KAT1820 | https://danam.cats.uni-heidelberg.de/report/75693640-0085-450b-89e5-cfbc02ff7a7d |
| Sarasvatī Shrine | SKH0040 | https://danam.cats.uni-heidelberg.de/report/9c28ca02-16e9-4137-9c29-2c67e46422af |
| Saṅkaṭā Ilānani | LAL1090 | https://danam.cats.uni-heidelberg.de/report/04e62546-0b04-41d7-9651-12189c45e5c6 |
| Siddhigaṇeśa Dyaḥchẽ | NAG0020 | https://danam.cats.uni-heidelberg.de/report/57afa28f-e522-4a0a-bbb3-1d9348b5bdb7 |
| Simākva Nārāyaṇa | SKH0300 | https://danam.cats.uni-heidelberg.de/report/20c7052d-2611-47b2-836d-b7f92638a1ee |
| Sulīma Āgama (10th cent. CE) | LAL0790 | https://danam.cats.uni-heidelberg.de/report/2c4ddb84-f419-11e9-a3c8-0242ac130002 |
| Sundargāũ Sundar Mani Malika Mandira, western temple | JUM0350 | https://danam.cats.uni-heidelberg.de/report/641c52bd-12fc-4a46-bc6c-7559e53cb8e0 |
| Suntvāḥ Gaṇeśa Mandira | SKH0220 | https://danam.cats.uni-heidelberg.de/report/15789ea0-899a-4991-a397-d59841f4cffe |
| Svasthānī Mahādeva | NWK0100 | https://danam.cats.uni-heidelberg.de/report/6f529817-41e9-4369-be8e-a371bc422777 |
| Sweta Bhairava | KAT1800 | https://danam.cats.uni-heidelberg.de/report/65567836-d1e0-4ded-ac1d-c8dd871dc08c |
| Sālkhā Gaṇeśa Shrine | SKH0120 | https://danam.cats.uni-heidelberg.de/report/dd27f3f4-f29d-430c-8667-ba4127543bc2 |
| Sūryavināyaka Mandira (1713 CE) | LAL0251 | https://danam.cats.uni-heidelberg.de/report/eb386850-e4f3-11e9-b125-0242ac130002 |
| Taleju Kvātha Chẽ | SKH0250 | https://danam.cats.uni-heidelberg.de/report/a2680407-903e-42bc-b4ae-a07ab0ee7155 |
| Taḥdhaṃ Mahādeva (1712 CE) | BKT0640 | https://danam.cats.uni-heidelberg.de/report/3ed04679-24b4-4e87-8ea5-344939168a6b |
| Thecva Pīgaṃ (before 1617 CE) | THC0110 | https://danam.cats.uni-heidelberg.de/report/80471874-5995-4cc3-bc95-d6f16189c4b0 |
| Thimi Taleju | THI0090 | https://danam.cats.uni-heidelberg.de/report/bb6f90d7-89de-4d1a-8caa-c322a295844a |
| Tichũgalli Gaṇeśa Mandira | LAL2690 | https://danam.cats.uni-heidelberg.de/report/445549f9-57cf-4664-bd5b-1da8562e7d4e |
| Tokhā Taleju | TOK0070 | https://danam.cats.uni-heidelberg.de/report/675f39f1-3142-4ddf-b7d0-dca85bde0a61 |
| Tripurasundarī Pīṭha | BKT0140 | https://danam.cats.uni-heidelberg.de/report/d9982f54-17e0-407d-8fe5-fdffe0413cac |
| Tulasī Maṭha (~17th cent.) | NWK0200 | https://danam.cats.uni-heidelberg.de/report/cbb04376-e0c4-40df-a2fb-3e734bb02f3a |
| Tuṃjhvaḥ Phalcā (1703 CE) | KIR4002 | https://danam.cats.uni-heidelberg.de/report/6a263bd4-6022-48bd-ba52-b730dd67710c |
| Tyaṅghaḥ Gaṇeśa Mandira (constructed in 1679 CE?) | KAT0320 | https://danam.cats.uni-heidelberg.de/report/f535f8f0-7c8b-40fc-8bdb-0fae2615bba4 |
| Tyāṅgā Bhairava | LEL0030 | https://danam.cats.uni-heidelberg.de/report/0a7b6845-c4cc-4fb5-b4ce-3b58837251e9 |
| Ugratārā Mandira (c. 13-th-15th cent.) | DDL0010 | https://danam.cats.uni-heidelberg.de/report/6a68f8a4-ad2d-4c82-97df-70095bf3dd7c |
| Vajra Gaṇeśa |  | https://danam.cats.uni-heidelberg.de/report/154297b7-c1ca-4eca-813e-774c28a7f805 |
| Vajrayoginī Shrine (before 1893 CE) | KAT2300 | https://danam.cats.uni-heidelberg.de/report/9a66be05-ea61-4fe9-a286-724147fbf7b8 |
| Vanakālī Mandira | PPK2101 | https://danam.cats.uni-heidelberg.de/report/1676ae2c-b3a4-4104-a36b-7dc9e98e7f22 |
| Vāphale Gaṇeśa Shrine | SKH0110 | https://danam.cats.uni-heidelberg.de/report/d6342a6e-98c7-4b4a-8923-773209670ced |
| Vidyāpīṭha | BKT0141 | https://danam.cats.uni-heidelberg.de/report/8ea5056f-dcf1-4cfe-a1c4-2f7db746c490 |
| Vināyaka Pañcadevala Kālikā Devī Mandira (built in the second half of the 20th cent.) | ACH0073 | https://danam.cats.uni-heidelberg.de/report/ae51c727-28ce-4062-896a-a84a2655ecdd |
| Viśvakarmā Devala (built in 1986 CE) | KIR0063 | https://danam.cats.uni-heidelberg.de/report/59e912ca-06a7-412a-a9b1-60d5d0fc0a6a |
| Viśveśvara Mahādeva (1676 CE) | NWK0280 | https://danam.cats.uni-heidelberg.de/report/0235b8e3-1d04-4ce5-9e05-242a3e58fc9d |
| Viṣṇu Devala | BNP0020 | https://danam.cats.uni-heidelberg.de/report/3d3baa81-be74-4fd9-b3c8-0a7d9ad4c2e1 |
| Viṣṇudevī Dyaḥcheñ (ca. 17th-18th cent.) | PNG0020 | https://danam.cats.uni-heidelberg.de/report/56b69e9c-789f-44ba-8171-7357c8ecbc3c |
| Viṣṇuvikrānta Mandira | SKH0150 | https://danam.cats.uni-heidelberg.de/report/4866412c-db26-4c5c-9a7b-2fba0dff932d |
| Viṣṇuvikrānta Shrine | PPK0430 | https://danam.cats.uni-heidelberg.de/report/b3998110-1199-4200-a785-b06a94d0d8f2 |
| Vīrāṭeśvara Mahādeva |  | https://danam.cats.uni-heidelberg.de/report/d359bd78-0698-4c4a-846e-23d6d3cfbdab |
| Yatkhā Bāhāḥ | KAT1050 | https://danam.cats.uni-heidelberg.de/report/143b3eaf-9561-4dbe-8f57-5b84756b8865 |
| Āḥjudyaḥ Bāhāḥ | BKT0210 | https://danam.cats.uni-heidelberg.de/report/c5819d99-b25f-46a9-93d5-6ade84d2cc16 |
| Śleṣmāntakeśvara | PPK0343 | https://danam.cats.uni-heidelberg.de/report/725afb79-c42e-4f63-9427-1860d20907f7 |
| Śveta Vārāhī Pīṭha | BDG0060 | https://danam.cats.uni-heidelberg.de/report/9ec6f192-10f6-4ba5-bd26-3bce660360b1 |
| Śākyamuni Buddha Shrine (consecrated in 1957 CE) |  | https://danam.cats.uni-heidelberg.de/report/222a5a4a-e1ef-4af0-afc9-bae7bd03d3ce |
| Śākyamuni Buddha Shrine (installation of the statue in 1683 CE) | SAT0023 | https://danam.cats.uni-heidelberg.de/report/7b5e6e49-2893-4f60-9e2d-d489a6cc2369 |
| Śālīnadī Bhīmasena Shrine (built in 1679 CE) | SKH0400 | https://danam.cats.uni-heidelberg.de/report/de57b03f-7d32-40a7-9b6d-088e74bbf643 |
| Ṣaḍakṣarī Lokeśvara Dyaḥchẽ | BDG0030 | https://danam.cats.uni-heidelberg.de/report/97276b3d-0f4d-4844-8d79-08aa48295358 |
| Ṭũḍikhela Gaṇeśa Mandira | NWK0310 | https://danam.cats.uni-heidelberg.de/report/73366095-3dfc-48c7-9aee-0d8b5ddc2bba |

</details>

## E1: hg:BuddhistMonument → hgn:BuddhistMonument (rdfs:subClassOf hg:ReligiousStructure)

- Test: `tests/test_sync.py::test_e1_buddhist_monument_is_extension_class`.
- Triples: 229,968 → **229,968**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 17 → **16** (0 classes, 16 properties, 0 IRI values).
- Extension terms used: 5.
- Queries (rows without LIMIT): unchanged.
- The builder does not add hg:ReligiousStructure as an extra type (the subclass axiom states it), so no new shapes apply.

## E2: hg:hasMainDeity → hgn:hasMainDeity

- Test: `tests/test_sync.py::test_e2_main_deity_is_extension_property`.
- Triples: 229,968 → **229,968**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 16 → **15** (0 classes, 15 properties, 0 IRI values).
- Extension terms used: 6.
- Queries (rows without LIMIT): unchanged.
- Checked first: the ontology's deity properties (hg:enshrinedDeity, hg:invokesDeity: sub-properties of crm:P12 for events; hg:isAboutDeity: crm:P62 for murtis; hg:embodiedDeity: roles) do not link a structure to its deity. Query 07 switched.

## E3: hg:danamCode → crm:E42_Identifier of kind hgn:DanamCode (no new property)

- Test: `tests/test_sync.py::test_e3_danam_code_is_an_identifier`.
- Triples: 229,968 → **234,846**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 15 → **14** (0 classes, 14 properties, 0 IRI values).
- Extension terms used: 7.
- Queries (rows without LIMIT): unchanged.
- An existing term does the job: the C1b identifier pattern with a third identifier kind, instead of a new property. Query 01 reads the code from the identifier node.
- Two monument records share the DANAM code `NWK0410` (both "Pā̃ḍe Pāṭī": https://danam.cats.uni-heidelberg.de/report/5d2c3e2e-485f-4a4a-be9f-4e2a27a5882e and https://danam.cats.uni-heidelberg.de/report/d3deb842-8858-4cf9-b277-af46111534d9), so 1,627 monuments have 1,626 code nodes. **Not changed here (outside the sync):** the builder's existing `owl:sameAs` between each monument and `res:monument/<code>` makes these two records one individual under OWL reasoning.

## E4: drop hg:eventIndex and hg:extractionMethod (pipeline bookkeeping)

- Test: `tests/test_sync.py::test_e4_no_pipeline_bookkeeping_on_events`.
- Triples: 234,846 → **224,650**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 14 → **12** (0 classes, 12 properties, 0 IRI values).
- Extension terms used: 7.
- Queries (rows without LIMIT): unchanged.
- Dropped rather than moved: the events export has no extraction_method column, so every event carried the builder's default 'source_table' (not source data); the event index stays in the event IRI (event/<resource_id>_<index>).

## E5: remove hg:skill

- Test: `tests/test_sync.py::test_e5_no_skill_property`.
- Triples: 224,650 → **224,649**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 12 → **11** (0 classes, 11 properties, 0 IRI values).
- Extension terms used: 7.
- Queries (rows without LIMIT): unchanged.
- The agent keeps schema:softwareRequirements naming the skill. Query 05 no longer selects ?skillName. (The AI-agent attribution itself is out of scope.)

## E6: hg:numStoreys / hg:numRoofs → hgn:numberOfStoreys / hgn:numberOfRoofs

- Test: `tests/test_sync.py::test_e6_storeys_and_roofs_are_extension_properties`.
- Triples: 224,649 → **224,649**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 11 → **9** (0 classes, 9 properties, 0 IRI values).
- Extension terms used: 9.
- Queries (rows without LIMIT): unchanged.
- Behaviour unchanged: as before, only whole numbers are written, so the 24 half-storey values in DANAM (1.5, 2.5, 4.5) are still left out. That is not a sync matter; noted for later.

## E7: hg:roofType / hg:monumentShape / hg:brickType → crm:P2_has_type with crm:E55_Type concepts (no new terms)

- Test: `tests/test_sync.py::test_e7_building_categories_are_e55_types`.
- Triples: 224,649 → **225,156**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 9 → **6** (0 classes, 6 properties, 0 IRI values).
- Extension terms used: 9.
- Queries (rows without LIMIT): unchanged.
- An existing term does the job (as instructed): one crm:E55_Type / skos:Concept per value DANAM lists, labelled as written, in three concept schemes res:scheme/roof-type (10 concepts), res:scheme/shape (5), res:scheme/brick-type (10). Multi-value cells are split on commas outside parentheses, so a monument with 'Hip roof, Gable roof' gets both types. Before, the whole cell was one literal.

## E8: place attributes hg:province/district/municipality/tola → crm:E53_Place hierarchy (crm:P89_falls_within, hg:placeType)

- Test: `tests/test_sync.py::test_e8_places_are_a_p89_hierarchy`.
- Triples: 225,156 → **224,853**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 6 → **2** (0 classes, 2 properties, 0 IRI values).
- Extension terms used: 9.
- Queries (rows without LIMIT): unchanged.
- An existing term does the job: one crm:E53_Place per level the record states, labelled as written (province number N as 'Province N'), hg:placeType from the ontology (free text: province / district / municipality / tola), each place crm:P89_falls_within the next level up the record gives; the monument's crm:P55 is its lowest level. Place IRIs carry the level and the chain (place/province-3/district-kathmandu/municipality-…/tola-…). Names are not normalised (e.g. 'Lalitpur' and 'Lalitpur Metropolitan City' stay separate), and a level missing from a record is skipped, so records that differ only in a missing level give separate nodes, as before. The one record with only a province now gets a location (crm:P55 1,631 → 1,632; tests A4/A7 updated). Query 03 reads the levels through crm:P89_falls_within*.

## E9: hg:conditionStatus / hg:identifiedThreats → hgn:conditionStatus / hgn:identifiedThreats

- Test: `tests/test_sync.py::test_e9_condition_text_and_threats_are_extension_properties`.
- Triples: 224,853 → **224,853**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 2 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 11.
- Queries (rows without LIMIT): unchanged.
- hgn:identifiedThreats is a sub-property of crm:P3_has_note rather than P3 itself, because the shapes allow one P3_has_note (xsd:string) and assessments already carry the assessment text there. Query 06 switched. Test B4 updated to read hgn:conditionStatus.

## S1: release statistics (publish_release.py) count the classes the builder now writes

- Test: `tests/test_sync.py::test_s1_release_statistics_follow_changed_terms`.
- Triples: 224,853 → **224,853**.
- SHACL results: 4,012 → **4,012** (3 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 11.
- Queries (rows without LIMIT): unchanged.
- publish_release.py counted hg:Production, hg:Place, hg:HumanMadeObject … for metadata.json, which would now be 0. It now counts the IRI the builder writes (the builder's CRM_CLASS_FOR map), and plain objects as objects with no more specific class. Other metadata.json issues (object total counting monuments too, checksum) are out of scope and unchanged.

## B5: religious traditions as concepts typed hg:ReligiousTradition (nine hgn: concepts); 'Unspecified' gives no tradition

- Test: `tests/test_sync.py::test_b5_religious_traditions_are_concepts`.
- Triples: 224,853 → **224,782**.
- SHACL results: 4,012 → **200** (1 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 21.
- Queries (rows without LIMIT): unchanged.
- Checked first: no shape has sh:minCount on hg:hasReligiousTradition (6 shapes: sh:class hg:ReligiousTradition, sh:nodeKind sh:IRI). Decision (user, 2026-11-01): 'Unspecified' (361 monuments, 15 more in combinations) gives no tradition and has no concept; in combinations the other values are kept. The nine other values map as listed under 'B5' above; values are split on commas. Query 07 now joins a monument's traditions (concept labels) in one cell, so it keeps one row per monument and deity; for monuments with 'Unspecified' alone the cell is empty instead of 'Unspecified'. Unchanged behaviour, noted for later: a deity takes the tradition(s) of the first monument that names it. Also test test_b5_unspecified_gives_no_tradition_and_combinations_keep_the_rest.

## Decisions (2026-11-01)

- **Ontology stays at 1.0.1.** Ontology 1.1.0 (style value "Not recorded") is not released or vendored. The 200 temples
  for which DANAM records no style stay without one: **200 SHACL results remain**, all `hg:hasArchitecturalStyle`
  minCount on `hg:Temple` (listed under C1c above). Final state: 200 SHACL results, 0 undeclared terms.
- **NWK0410:** `owl:sameAs` kept; record A is an empty duplicate of record B (see `SOURCE_ISSUES.md`).
- **Deity traditions:** a deity takes the tradition(s) of the first monument that names it. Not changed; listed for later
  in `SYNC_PLAN.md` ("Not part of the sync").

## F1: provenance: AI-agent attribution removed; DANAM pages attributed to DANAM; construction by the pipeline software on behalf of CAIR-Nepal

- Test: `tests/test_fixes.py::test_f1_provenance_danam_source_and_pipeline_software`.
- Triples: 224,782 → **226,436**.
- SHACL results: 200 → **200** (1 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 21.
- Queries (rows without LIMIT): unchanged.
- Removed the 'Antigravity AI Agent (DeepMind)' agent and its 12,259 prov:wasAttributedTo statements (5,098 events, 7,160 objects, the dataset). Each DANAM report page (and the DANAM site) is a prov:Entity prov:wasAttributedTo DANAM, a prov:Organization labelled as the site names itself ('Digital Archive of Nepalese Arts and Monuments (DANAM)'; comment: database of the Nepal Heritage Documentation Project, Heidelberg). Monuments, events and objects are prov:wasDerivedFrom their monument's page (events and objects newly). The construction activity prov:wasAssociatedWith a prov:SoftwareAgent (schema:codeRepository the GitHub repo, schema:softwareVersion the git commit of the build, '-dirty' if tracked files are modified), which prov:actedOnBehalfOf CAIR-Nepal. The dataset is attributed to CAIR-Nepal only.

## F3: crm:P44_has_condition points to the crm:E3_Condition_State, not the crm:E14_Condition_Assessment

- Test: `tests/test_fixes.py::test_f3_p44_points_to_the_condition_state`.
- Triples: 226,436 → **226,436**.
- SHACL results: 200 → **200** (1 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 21.
- Queries (rows without LIMIT): unchanged.
- 1,577 statements retargeted from assessment/<id> to condition_state/<id> (P44 has range crm:E3_Condition_State). The monument keeps crm:P34i_was_assessed_by the assessment, and the assessment crm:P35_has_identified the same state.

## F4: deities get no religious tradition from monuments

- Test: `tests/test_fixes.py::test_f4_deities_get_no_tradition_from_monuments`.
- Triples: 226,436 → **226,055**.
- SHACL results: 200 → **200** (1 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 21.
- Queries (rows without LIMIT): unchanged.
- Removes 381 hg:hasReligiousTradition statements on 355 deities. They came from the first monument naming the deity, so 43 deities named by monuments of different traditions got whichever came first. DANAM states traditions per monument only, so no deity gets one. Monuments keep theirs (1,162 monuments, 1,373 statements). Resolves the open item 'Deity traditions' in Decisions (2026-11-01) and SYNC_PLAN.md.

## F5: monument descriptions as dcterms:description @en / @ne, unchanged from DANAM

- Test: `tests/test_fixes.py::test_f5_monument_descriptions_unchanged_from_danam`.
- Triples: 226,055 → **229,102**.
- SHACL results: 200 → **200** (1 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 21.
- Queries (rows without LIMIT): unchanged.
- Adds 1,576 English and 1,471 Nepali descriptions (3,047 statements). The text is written exactly as in DANAM's record (staging/monuments.csv is identical to the raw JSON for both columns; checked for all 1,652 monuments); empty cells give nothing. No shape constrains dcterms:description.

## F6: source funnel: no ID is missing; 3 blank rows in resourceids.csv; 7 failed fetches

- Test: `tests/test_fixes.py::test_f6_every_listed_id_has_a_raw_file_and_seven_fetches_failed`.
- Triples: 229,102 → **229,102**.
- SHACL results: 200 → **200** (1 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 21.
- Queries (rows without LIMIT): unchanged.
- No graph change. resourceids.csv has 1,947 rows; rows 13-15 (file lines 14-16) are empty (""), so there are 1,944 distinct IDs, not 1,945 (the paper-facts script counted the blank as an ID). All 1,944 IDs have a raw JSON file. 7 of them record a failed fetch on 2026-03-16 (status 'error'; 4 page-load timeouts of 30 s, 3 connection resets; also in data_collection/scraper.log) and were not retried, which gives the 1,937 parsed records. Not re-crawled. tools/paper/stats.py reports the blank rows, IDs without a raw file (0) and the failed fetches in the funnel.

## F7: metadata.json: objects = distinct object nodes; checksums verified after writing

- Test: `tests/test_fixes.py::test_f7_metadata_counts_distinct_objects_and_checksums_match`.
- Triples: 229,102 → **229,102**.
- SHACL results: 200 → **200** (1 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 21.
- Queries (rows without LIMIT): unchanged.
- No graph change. publish_release.py counted every crm:E22_Human-Made_Object as an object, which includes the 1,652 monuments (v1.0.0: 8,806 = 7,154 + 1,652). It now counts the nodes linked to a monument (hgn:isObjectOf or crm:P46i_forms_part_of): 7,160 (7,154 DANAM object numbers; 6 numbers are used for two different objects and each row has its own node, R1). After writing checksums.sha256 the release step re-hashes every file and stops if one differs. Checked with a scratch release (test, tmp directory). The published v1.0.0 files in releases/v1.0.0/ and latest/ are not regenerated (never overwritten): their metadata.json still fails its checksum (the file was edited after the checksum was written; the three data files match) and still reports 8,806. Licence left alone (decision pending): graph dcterms:license CC BY-SA 4.0, metadata.json CC BY 4.0.

## F2: event typing: destruction and modification by the event name (crm:E11_Modification); rules in event_typing.py

- Test: `tests/test_fixes.py::test_f2_event_typing_rules_on_real_events, tests/test_fixes.py::test_f2_destruction_only_when_the_name_says_so`.
- Triples: 229,102 → **229,145**.
- SHACL results: 200 → **200** (1 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 21.
- Queries (rows without LIMIT): **changed:** `02_historical_timeline.rq` 5313 → 5356
- Query rows changed, accepted: query 02 lists one row per event and class: the 43 events with two classes (27 destruction + modification, 16 modification + transfer) add one row each (5,313 -> 5,356)
- All event-typing rules moved to event_typing.py (13 rules, documented there; the builder and its skill copy import it). Destruction only when the event name has a damage word; renovation/restoration/rebuilding/repair in the name -> crm:E11_Modification (ontology 1.0.1 has no renovation class; crm:E11 is the CIDOC-CRM superclass of crm:E12_Production); names with both -> both classes (27); names with a repair word and an endowment/donation word -> crm:E11 and crm:E10 (16); ritual/worship/pūjā in the name -> ritual event, after a name check for endowment words. A repair word only in the description keeps the earlier result (production), so those 128 events keep their class unless another F2 decision applies. Per class (before -> after; two-class events count in both): E6 695 -> 265, E11 0 -> 1,280, E12 1,808 -> 1,074, E10 284 -> 272, ritual 85 -> 100, condition assessment 15 -> 18, historical 1,996 -> 1,917, consecration 128 and enshrinement 87 unchanged. 1,435 of 5,098 events change. Listed, not changed: 'grant' matches 'granthakūṭa' (a temple style), so 'Installing door to build new temple' is a transfer of custody; 'grant' occurs in 47 events and types 40 as transfers. Pre-change list: docs/fixes/F2_destruction_events_before.md. publish_release.py counts Modification; tests A2, A3, A5, A6 and S1 updated to the new counts.

## F8: release script refuses to build from a working tree with uncommitted changes

- Test: `tests/test_fixes.py::test_release_refuses_a_dirty_working_tree`.
- Triples: 229,145 → **229,145**.
- SHACL results: 200 → **200** (1 groups).
- Undeclared terms: 0 → **0** (0 classes, 0 properties, 0 IRI values).
- Extension terms used: 21.
- Queries (rows without LIMIT): unchanged.
- No graph change. publish_release.create_release (used by publish_release.py and build_kg.py --release) first runs git status on tracked files and stops with an error, before writing anything, if any tracked file has uncommitted changes; untracked files (e.g. the paper draft) do not count. The release's pipeline commit (F1) therefore always names code that exists. The F7 test stubs the check, since tests run on uncommitted work.
