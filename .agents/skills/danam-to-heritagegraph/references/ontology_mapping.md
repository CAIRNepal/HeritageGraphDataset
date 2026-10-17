# Mapping DANAM rows to the CulturalHeritageOntology (heritageGraph, v0.1.0-alpha.2)

Read this when you assign `ontology_class` in events.csv / objects.csv or review the derived
columns that `prepare.py` adds to monuments.csv. The CSVs are a flat staging layer; the class names
below are the ontology classes a later CSV→RDF/LinkML step will instantiate. Use class names exactly as
written (no prefix).

## monuments.csv → structures
| DANAM `monument_type` keyword | `ontology_class` | Style (AAT, `has_architectural_style`) |
|---|---|---|
| Tiered temple / pagoda | Temple | aat:300004829 Pagoda |
| Bell-shaped, Śikhara | Temple | aat:300446671 Shikhara (bell-shaped is only the *closest* enum value → keep the mapping note) |
| Dome | Temple | aat:300001285 Dome |
| Shrine, Temple (no style stated) | Temple | blank — Temple requires a style, so leave it for a human, don't guess |
| Caitya / Chaitya | Chaitya | aat:300007562 |
| Stupa | Stupa | aat:300007576 |
| Monastic building (bāhāḥ) | BuddhistMonument (+ Temple when also listed) | — |
| Phalcā, Pati | Pati (subclass of RestHouse) | — |
| Sataḥ, Sattal | Sattal | — |
| Dharmaśālā | Dharmashala | — |
| Hiti, Dhārā | DhungeDhara | — |
| Pokhari | Pokhari | — |
| Pillar, other freestanding | ArchitecturalStructure | — |

Multi-valued results are `|`-joined in source order. Other columns: `main_deity` → Deity (+ `has_religious_tradition` from
`religion`); municipality/district/tola → Place (`has_current_location`); `monument_assessment` → ConditionAssessment with
`condition_types` ∈ Good | Damaged | Ruined | Restored (Heavily damaged→Ruined, Slightly damaged/Surface damages→Damaged,
Restored/Repaired/Rebuilt→Restored, "Good (…)" →Good; parenthetical explanations are dropped).

## events.csv → event classes (`ontology_class`)
Pick the most specific class that fits what the sentence says happened, not what it implies.

| What the text says | Class |
|---|---|
| built, constructed, rebuilt, renovated, installed a finial/toraṇa/roof, added a component | Production |
| dismantled, collapsed, burnt, demolished, damaged by earthquake/flood/fire | DestructionEvent |
| prāṇapratiṣṭhā, consecration of a murti | Consecration |
| a deity image/caitya installed in a sanctum | Enshrinement |
| land endowed to a guṭhi, handed to a committee/department, custody changes | TransferOfCustody |
| special puja, jātrā, bhajan, procession, purification after an omen | RitualEvent (Festival for a named jātrā) |
| assessment / survey / documentation | ConditionAssessment or DocumentationActivity |
| theft, omens (blood on a caitya), grant recorded in an inscription, anything else dated | HistoricalEvent |

## objects.csv → object classes
| Object | Class |
|---|---|
| statue / image of a deity | Murti (IconographicObject if only depicted, e.g. relief) |
| paubha / painting | Paubha |
| toraṇa, gajūra, door, window, strut, pillar *as part of a structure* | ArchitecturalElement |
| stone lions, dhvajas, lamps, other movable sacred items | IconographicObject (or HumanMadeObject when not iconographic) |
| inscription | HumanMadeObject (+ an inscription ID such as `JUM0453_I_001` goes in `object_id` only if it follows the DANAM pattern; otherwise use the text's own ID) |
