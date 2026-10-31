# Source issues in the DANAM records

Problems found in the DANAM monument records (as collected on 16 March 2026) while building the graph. They are reported
here, not corrected in the data: the graph keeps what DANAM states. Each entry gives the DANAM page.

## 1. Object numbers used for two objects

DANAM numbers each object within a monument record (usually `AAA0000-000`). Six numbers are each given to two objects.
The graph keeps every object as its own node (`res:object/<number>_1`, `_2`, in file order); both keep the DANAM number
as their identifier (sync log item R1).

| number | object 1 | object 2 | monument | DANAM page |
|---|---|---|---|---|
| LAL2570-001 | Śikharakūṭa Caitya | Statue of Donor | Jothā Bāhāḥ | https://danam.cats.uni-heidelberg.de/report/1798db32-ecce-11e9-8bc4-0242ac130002 |
| KAT2130-003 | Lion | lion | Jora Gaṇeśa Mandira | https://danam.cats.uni-heidelberg.de/report/41dddca9-4465-44d7-9e66-330391c7f252 |
| LAL0841-006 | Viṣṇu | Licchavi Caitya | two monuments: Tāpā Hiti East (object 1), Tāpā Hiti West (object 2) | https://danam.cats.uni-heidelberg.de/report/5d44f5b8-70f8-11ea-966a-0242ac130006 and https://danam.cats.uni-heidelberg.de/report/5f27520c-348e-43da-8160-a2e2729a37c7 |
| KAT1150-014 | Garuḍanārāyaṇa | Gaṇeśa (B) | Bhulukā Degaḥ (Santāneśvara Mahādeva) | https://danam.cats.uni-heidelberg.de/report/7171bc5b-58ee-4d5d-9808-c118c20022de |
| SUN0010-004 | Statue of Jalaśayana Viṣṇu on the southern side of the entrance | Jalaśayana Viṣṇu | Mahādyaḥ Gāḥcā | https://danam.cats.uni-heidelberg.de/report/872e0e8c-f0ba-11e9-a3c8-0242ac130002 |
| TOK0090-001 | Umāmaheśvara | Bell | Caṇḍeśvarī Dyaḥchẽ | https://danam.cats.uni-heidelberg.de/report/a0c8744f-2928-4961-b072-638c22e48522 |

Notes:
- **SUN0010-004** is probably one statue listed twice (the second entry repeats the first without the position). Kept as
  two nodes, as for the others; DANAM should confirm.
- **KAT2130-003** may be a pair of lions given one number, or one lion listed twice.
- **LAL0841-006** is used in two different monument records.

## 2. Two records with the DANAM code NWK0410

Both records are named Pā̃ḍe Pāṭī and carry the code NWK0410.

| | record A | record B |
|---|---|---|
| DANAM page | https://danam.cats.uni-heidelberg.de/report/5d2c3e2e-485f-4a4a-be9f-4e2a27a5882e | https://danam.cats.uni-heidelberg.de/report/d3deb842-8858-4cf9-b277-af46111534d9 |
| content | name and code only: no description, location, coordinates, measurements, condition or events | full record: phalcā (arcaded platform) in Sītāpokharī, Bidur Municipality, Nuwakot (Province 3); coordinates; measurements; description (English and Nepali); condition "Ruined"; one event; an inscription of ŚS 1700 |
| code separator in the Devanagari name | `ll` (two Latin letters) | `||` |

Record A looks like an empty duplicate of record B. Because of the `ll`, staging did not separate the code from A's
Nepali name (`name_ne` = "पाँडे पाटी ll NWK0410").

**Not yet changed:** the builder links each monument to `res:monument/<code>` with `owl:sameAs`, so under OWL reasoning
the two records become one individual.
