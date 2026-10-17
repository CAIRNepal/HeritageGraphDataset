# AGENTS.md — Guidelines for HeritageGraphDataset

This document provides system instructions, architectural context, and operational guidelines for AI agents working within the `HeritageGraphDataset` repository.

---

## 1. Project Overview & Mission

`HeritageGraphDataset` is an initiative under **CAIR-Nepal** to create a structured, provenance-preserving cultural heritage dataset for Nepal. The repository ingests monument reports scraped from the **Digital Archive of Nepalese Arts and Monuments (DANAM)** (hosted at `danam.cats.uni-heidelberg.de`) and transforms them into high-quality, event-centric staging datasets aligned with the **CAIR-Nepal HeritageGraph Ontology (v1.0.0)** (CIDOC-CRM and PROV-O aligned).

---

## 2. Directory Structure

```text
HeritageGraphDataset/
├── ontology/                            # Official CAIR-Nepal HeritageGraph Ontology
│   └── HeritageGraph.ttl                # Authoritative LinkML/OWL RDF definition (v1.0.0)
├── latest/                              # Rolling mirror of latest stable release
│   ├── heritagegraph-nepal.ttl          # Human-readable Turtle serialization (221,364 triples)
│   ├── heritagegraph-nepal.jsonld       # JSON-LD serialization
│   ├── heritagegraph-nepal.nt.gz        # Gzipped N-Triples for triplestores
│   ├── metadata.json                    # DCAT / Schema.org dataset metadata
│   └── checksums.sha256                 # Cryptographic SHA-256 manifest
├── releases/                            # Archival immutable releases
│   ├── v1.0.0/                          # Release v1.0.0
│   └── v1.1.0/                          # Future release (Roadmap)
├── data_collection/                     # Scraper codebase & collected data
│   ├── danam_scraper_v2.py              # Main scraper implementation
│   ├── shard_scrape.py                  # Distributed / sharded scraper utility
│   ├── resourceids.csv                  # Catalog of DANAM monument IDs
│   └── data/
│       ├── raw/                         # Scraped raw JSON records per monument
│       └── exports/                     # Exported raw CSV dumps (monuments.csv, events.csv, objects.csv)
├── queries/                             # Standard SPARQL benchmark queries (*.rq)
│   ├── 01_monuments_by_aat_style.rq     # Getty AAT architectural style query
│   ├── 02_historical_timeline.rq        # Chronological event timeline
│   ├── 03_spatial_geosparql.rq          # GeoSPARQL & WGS84 spatial distribution
│   ├── 04_monument_sacred_objects.rq    # Sacred objects, murtis, and architectural elements
│   ├── 05_provenance_audit.rq           # W3C PROV-O provenance & source audit
│   ├── 06_condition_threats.rq          # Condition assessments & preservation threats
│   └── 07_deities_traditions.rq         # Deities & religious traditions
├── build_kg.py                          # Root runner for Knowledge Graph construction
├── publish_release.py                   # Root runner for publishing versioned releases
├── query_kg.py                          # Root runner for executing SPARQL queries
├── RELEASES.md                          # Release management, versioning & roadmap
├── skill/
│   └── danam-to-heritagegraph.skill     # Original packaged skill archive
├── AGENTS.md                            # Repository rules and guidance (this file)
└── README.md
```

---

## 3. Core Principles & Provenance Rules

Every agent operating in this repository **must** uphold the following rules:

### A. Provenance is Paramount
* Every event and object row extracted from DANAM monument narratives must explicitly trace back to:
  * The monument's `resource_id` and verbatim `monument_name`.
  * The verbatim citation from the text in `sources`.
  * The **verbatim sentence** from `description_en` in `evidence_text`.
* `validate.py` strictly enforces that `evidence_text` is an exact substring of `description_en`. Non-verbatim paraphrasing in `evidence_text` will fail validation.

### B. Truthful Data over Completeness ("Blank Beats Guessed")
* **Never fabricate or pad data**: If the prose is silent on an attribute (e.g. date, deity, material, actor), leave the cell completely blank.
* **Do not artificially match page counters**: DANAM monument pages declare `event_count` and `object_count` from database tables, but narrative prose often only covers a fraction of them. Extract only what is supported by the prose.
* **Keep era labels as written**: Record era strings as printed (`NS 809`, `VS 2065`, `ŚS 1422`, `MS 32`). **Never back-compute** an era year that the source did not state.
* **Document contradictions without altering sources**: If a source presents an obvious date mismatch (e.g. `ŚS 1422 (i.e., 500 CE)`), keep the written values as-is, detail the contradiction in `event_description`, and flag it rather than silently fixing it.

### C. Language Precedence
* `description_en` is the primary source for event and object extraction.
* Do not extract from `description_ne` unless the English description is absent. If Nepali text is used, set `extraction_method` to `llm_from_description_ne`.

---

## 4. Staging Data Specifications

The transformation produces three linked staging CSVs:

### 1. `monuments.csv`
* Retains all 46 original DANAM input columns unmodified.
* Appends derived ontology columns:
  * `danam_code`: e.g. `SKH0510` (extracted from `name_devanagari` after `||`).
  * `name_ne`: Devanagari name without the DANAM code.
  * `ontology_class`: e.g. `Temple`, `Chaitya`, `Stupa`, `Pati`, `Sattal`, `Dharmashala`, `DhungeDhara`, `Pokhari`.
  * `aat_style`: Getty AAT architectural style identifier (e.g. `aat:300004829 Pagoda`).
  * `condition_types`: Normalized status (`Good` | `Damaged` | `Ruined` | `Restored`).
  * `mapping_notes`: Unresolved mapping details or ambiguities.
* Empty/dead page records are sent to `skipped_rows.csv`.

### 2. `events.csv`
Columns (in order):
1. `resource_id`
2. `monument_name`
3. `event_index` (0-based contiguous per monument, chronological as presented in text)
4. `event_name` (Short noun phrase, sentence case, e.g. "Renovation of the temple")
5. `event_description` (Concise summary faithful to source)
6. `date_bce_ce` (e.g. `1689 CE`, `1300 BCE`, or blank)
7. `period` (`Licchavi`, `Early medieval`, `Malla`, `Śāha`, `Rāṇā`, `Post-Rāṇā`)
8. `year_ss_ns_vs` (`NS 809`, `VS 2065`, `ŚS 1422`, `MS 32`, or blank)
9. `nepali_month` (Canonical name: `Phālguna`, `Māgha`, `Āśvina`, etc.)
10. `paksha` (`Śukla` or `Kṛṣṇa`)
11. `tithi` (Integer `1`–`15`)
12. `sources` (Exact citation, `; `-separated)
13. `ontology_class` (`Production`, `DestructionEvent`, `Consecration`, `Enshrinement`, `TransferOfCustody`, `RitualEvent`, `ConditionAssessment`, `HistoricalEvent`)
14. `evidence_text` (Verbatim sentence from `description_en`)
15. `extraction_method` (`llm_from_description` or `source_table`)
16. `confidence` (`high`, `medium`, `low`)

### 3. `objects.csv`
Columns (in order):
1. `resource_id`
2. `monument_name`
3. `object_index` (0-based contiguous per monument)
4. `object_id` (DANAM identifier matching `AAA0000-000`)
5. `object_name` (Name of object)
6. `object_type` (e.g. `Toraṇa`, `Statue`, `Pillar`, `Stone lion`)
7. `object_material` (e.g. `stone`, `silver`, `gilded copper` if stated)
8. `object_location` (Position stated in text, e.g. `sanctum`, `north of the temple`)
9. `date_bce_ce`
10. `date_vs_ns`
11. `ontology_class` (`Murti`, `Paubha`, `ArchitecturalElement`, `IconographicObject`, `HumanMadeObject`)
12. `evidence_text` (Verbatim sentence from `description_en`)
13. `extraction_method`
14. `confidence`

---

## 5. Workflow & Tool Execution Runbook

When performing a dataset preparation or extraction:

### Step 1: Candidate Generation
Run `prepare.py` on the raw DANAM CSV:
```bash
python .agents/skills/danam-to-heritagegraph/scripts/prepare.py --input <danam_export.csv> --outdir <staging_dir>
```
This generates:
- `<staging_dir>/monuments.csv`
- `<staging_dir>/skipped_rows.csv`
- `<staging_dir>/event_candidates.jsonl`
- `<staging_dir>/object_candidates.jsonl`

### Step 2: Date Parsing & Era Verification
Use `heritage_dates.py` for text-based date parsing and calendar validation:
```bash
python .agents/skills/danam-to-heritagegraph/scripts/heritage_dates.py "<free_text>"
```
Era offsets reference:
- Nepāla Saṃvat (NS): +879/880 to CE
- Vikrama Saṃvat (VS): -56/57 to CE
- Śaka Saṃvat (ŚS): +78 to CE
- Mānadeva Saṃvat (MS): +576 to CE

### Step 3: Event & Object Extraction
- Process monument records using the candidates alongside full narrative context.
- Assign `ontology_class` referencing `.agents/skills/danam-to-heritagegraph/references/ontology_mapping.md`.
- Follow column formatting rules in `.agents/skills/danam-to-heritagegraph/references/column_spec.md`.

### Step 4: Strict Validation
Always validate the resulting staging directory:
```bash
python .agents/skills/danam-to-heritagegraph/scripts/validate.py --dir <staging_dir>
```
* The script must exit with status `0` (`ALL CHECKS PASSED`).
* Fix any reported `ERROR` issues immediately (FK mismatches, non-verbatim `evidence_text`, indexing gaps).

### Step 5: Knowledge Graph (KG) Construction & Release Publishing
Construct the RDF Knowledge Graph from staging CSVs and publish releases:
```bash
# Build knowledge graph and publish a versioned release (e.g., v1.0.0, v1.1.0):
python publish_release.py --version v1.0.0

# Rebuild from staging and publish directly:
python publish_release.py --version v1.1.0 --rebuild --dir staging

# Or using build_kg.py with release flag:
python build_kg.py --dir staging --release v1.0.0
```
This generates the release artifacts in `releases/<version>/` and synchronizes `latest/`:
- `heritagegraph-nepal.ttl`: Human-readable Turtle serialization with standard prefixes (`hg:`, `crm:`, `prov:`, `aat:`, `geo:`, `geosparql:`, `schema:`, `void:`, `res:`).
- `heritagegraph-nepal.jsonld`: JSON-LD serialization for web / schema.org integrations.
- `heritagegraph-nepal.nt.gz`: Streaming compressed N-Triples for triplestores (Blazegraph, Jena Fuseki, GraphDB, Virtuoso).
- `metadata.json`: Machine-readable W3C DCAT / Schema.org dataset metadata and statistics.
- `checksums.sha256`: Cryptographic SHA-256 integrity manifest.

### Step 6: SPARQL Querying & Verification
Verify and query the generated Knowledge Graph (defaults to `latest/heritagegraph-nepal.ttl`):
```bash
# Run all standard benchmark queries in queries/*.rq
python query_kg.py --all

# Run a specific query
python query_kg.py --query queries/01_monuments_by_aat_style.rq

# Run against a specific pinned release
python query_kg.py --graph releases/v1.0.0/heritagegraph-nepal.ttl --query queries/02_historical_timeline.rq

# Run an ad-hoc inline SPARQL query
python query_kg.py --sparql "SELECT ?monument ?label WHERE { ?monument a hg:Temple ; rdfs:label ?label } LIMIT 10"
```

---

## 6. Environment & Tooling

* **Python**: Python 3.11+ managed via `uv` or system Python.
* **Encoding**: All text operations must use UTF-8 explicitly.
* **Dependencies**: Scraper dependencies are declared in `data_collection/pyproject.toml`. Staging and date parsing scripts use the Python Standard Library. RDF graph construction and SPARQL execution utilize `rdflib` via `uv run --with rdflib`.

