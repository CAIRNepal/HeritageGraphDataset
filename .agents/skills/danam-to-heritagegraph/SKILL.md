---
name: danam-to-heritagegraph
description: >-
  Transform scraped DANAM (Digital Archive of Nepalese Arts and Monuments, danam.cats.uni-heidelberg.de)
  monument CSV exports into provenance-preserving, ontology-aligned staging datasets (monuments.csv,
  events.csv, objects.csv) and build Linked Open Data (LOD) RDF Knowledge Graphs aligned with CIDOC-CRM,
  W3C PROV-O, and the CAIR-Nepal CulturalHeritageOntology. Use this skill whenever ingesting DANAM monument
  reports, extracting historical event timelines and sacred objects from narrative prose, resolving inscriptional
  dates (NS/VS/ŚS/MS), validating staging tables, or building and querying the RDF Knowledge Graph with SPARQL.
---

# DANAM → HeritageGraph Staging & Knowledge Graph Pipeline

This skill provides an end-to-end, standard operating procedure for transforming wide, semi-structured DANAM
monument reports into a structured, provenance-preserving staging dataset and generating Linked Open Data (LOD)
RDF Knowledge Graphs.

---

## 1. Core Principles & Provenance Invariants

Every agent and human operator executing this workflow must uphold four fundamental rules:

1. **Unbroken Provenance (`evidence_text`)**:
   Every row in `events.csv` and `objects.csv` derived from narrative text must preserve:
   - The monument's `resource_id` and verbatim `monument_name`.
   - The verbatim source citation in `sources` (e.g. `(T. Siṃha1136, p. 15, folio 23A)`).
   - The **verbatim sentence** from `description_en` in `evidence_text`. The validator strictly enforces that
     `evidence_text` is an exact substring of `description_en`.
2. **Truthful Data Over Completeness ("Blank Beats Guessed")**:
   - If the narrative prose is silent regarding a date, deity, material, actor, or architecture, leave the cell completely blank. Never hallucinate or extrapolate.
   - Do not pad rows to artificially match page counters (`event_count`, `object_count`). DANAM counters reflect database tables, whereas narrative prose typically details only a subset.
3. **Preserve Era Inscriptions As Written**:
   - Record eras exactly as printed (`NS 809`, `VS 2065`, `ŚS 1422`, `MS 32`).
   - Never back-calculate an era year that the source did not state.
   - If a source contains an internal contradiction (e.g. `ŚS 1422 (i.e., 500 CE)`), keep the written values as-is, detail the contradiction in `event_description`, and assign appropriate confidence.
4. **Language Precedence**:
   - Primary extraction must be performed from `description_en`.
   - Only fall back to `description_ne` if the English description is absent, explicitly marking `extraction_method` as `llm_from_description_ne`.

---

## 2. Directory & Component Layout

```text
danam-to-heritagegraph/
├── SKILL.md                          # Standard workflow runbook (this file)
├── references/                       # Authoritative mapping specifications
│   ├── column_spec.md                # Strict column definitions & formatting rules
│   ├── ontology_mapping.md           # Monument typology & event/object class taxonomy
│   └── worked_example.md             # Ground-truth worked example (Jogeśvara Mandira)
└── scripts/                          # Automated execution utilities
    ├── prepare.py                    # Step 1: Prepares candidate JSONLs and monuments.csv
    ├── heritage_dates.py             # Step 2: Date, era (NS, VS, ŚS, MS), & calendar parser
    ├── validate.py                   # Step 3: Strict staging CSV validator
    ├── build_kg.py                   # Step 4: RDF Knowledge Graph builder & LOD exporter
    ├── publish_release.py            # Step 5: Versioned release publisher & checksum manifest
    └── query_kg.py                   # Step 6: SPARQL query execution runner
```

---

## 3. Step-by-Step Execution Workflow

### Step 1: Ingestion & Candidate Preparation
Run [prepare.py](./scripts/prepare.py) on the raw DANAM CSV export:
```bash
python .agents/skills/danam-to-heritagegraph/scripts/prepare.py --input data_collection/data/exports/monuments.csv --outdir staging
```
**Outputs generated in `--outdir`:**
- `monuments.csv`: Verbatim input columns plus derived ontology columns (`danam_code`, `name_ne`, `ontology_class`, `aat_style`, `condition_types`, `mapping_notes`).
- `skipped_rows.csv`: Catalog of dead or empty pages.
- `event_candidates.jsonl`: Sentences containing event verbs, parsed dates, and citations.
- `object_candidates.jsonl`: Sentences containing object identifiers (`AAA0000-000`) and context.

### Step 2: Date Parsing & Era Verification
Use [heritage_dates.py](./scripts/heritage_dates.py) to resolve dates, eras, and lunisolar calendars:
```bash
# Test inline text
python .agents/skills/danam-to-heritagegraph/scripts/heritage_dates.py "On the 13th of the bright fortnight of Phālguna in 1689 CE (NS 809)"

# Run self-test suite
python .agents/skills/danam-to-heritagegraph/scripts/heritage_dates.py --test
```
**Era Conversion Reference Offsets:**
- **Nepāla Saṃvat (NS)**: +879/880 to CE (month-aware: Kārtika–Pauṣa = +879; other months = +880).
- **Vikrama Saṃvat (VS)**: -56/57 to CE (month-aware: Māgha–Caitra = -56; other months = -57).
- **Śaka Saṃvat (ŚS)**: +78 to CE.
- **Mānadeva Saṃvat (MS)**: +576 to CE.

### Step 3: Event & Object Extraction
1. Consult [references/column_spec.md](./references/column_spec.md) for required column schemas and strict ordering.
2. Consult [references/ontology_mapping.md](./references/ontology_mapping.md) for class assignments:
   - **Events**: `Production`, `DestructionEvent`, `Consecration`, `Enshrinement`, `TransferOfCustody`, `RitualEvent`, `ConditionAssessment`, `HistoricalEvent`.
   - **Objects**: `Murti`, `Paubha`, `ArchitecturalElement`, `IconographicObject`, `HumanMadeObject`.
3. Process candidates monument by monument, utilizing the full narrative context of `description_en`.
4. Ensure `event_index` and `object_index` are 0-based and contiguous per monument.

### Step 4: Strict Quality Validation
Run [validate.py](./scripts/validate.py) against the staging directory:
```bash
python .agents/skills/danam-to-heritagegraph/scripts/validate.py --dir staging
```
**Verification Rules:**
- The process must exit with status code `0` (`0 error(s)`).
- Critical errors (`ERROR`) must be resolved immediately:
  - Missing foreign keys in `monuments.csv`.
  - Non-verbatim `evidence_text` that is not an exact substring of `description_en`.
  - Gaps or duplicates in `event_index` or `object_index`.
  - Invalid calendar fields (`paksha`, `nepali_month`, `tithi`).
- Warnings (`WARN`) must be audited (e.g. noted era/CE disagreements).

### Step 5: Knowledge Graph Construction & Release Publishing
Generate standards-compliant RDF Linked Open Data and publish releases:
```bash
# Publish a standardized versioned release (e.g., v1.0.0, v1.1.0) and update latest/:
python publish_release.py --version v1.0.0

# Or rebuild from staging CSVs and publish:
python publish_release.py --version v1.1.0 --rebuild --dir staging

# Or using build_kg.py with --release flag:
uv run --with rdflib python build_kg.py --dir staging --release v1.0.0
```
**Release Outputs produced in `releases/<version>/` and mirrored to `latest/`:**
- `heritagegraph-nepal.ttl`: Turtle syntax with human-readable prefixes (`hg:`, `crm:`, `prov:`, `aat:`, `geo:`, `geosparql:`, `schema:`, `void:`, `res:`).
- `heritagegraph-nepal.jsonld`: JSON-LD serialization for web platforms and Schema.org ingestion.
- `heritagegraph-nepal.nt.gz`: Gzipped N-Triples for streaming bulk ingestion into triplestores (GraphDB, Virtuoso, Jena Fuseki, Blazegraph).
- `metadata.json`: Machine-readable W3C DCAT & Schema.org dataset metadata and entity statistics.
- `checksums.sha256`: Cryptographic SHA-256 integrity manifest.

### Step 6: SPARQL Querying & Verification
Query the generated RDF Knowledge Graph using [query_kg.py](./scripts/query_kg.py):
```bash
# Execute all standard benchmark queries (queries/01 through 07)
uv run --with rdflib python query_kg.py --all

# Execute a specific benchmark query
uv run --with rdflib python query_kg.py --query queries/01_monuments_by_aat_style.rq

# Execute an ad-hoc SPARQL query
uv run --with rdflib python query_kg.py --sparql "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
```

---

## 4. Troubleshooting & Common Pitfalls

| Issue | Cause | Resolution |
|---|---|---|
| `[ERROR] evidence_text is not a verbatim substring` | Text was rephrased, truncated, or normalized incorrectly | Copy the exact sentence directly from `description_en` without alteration |
| `[ERROR] duplicate resource_id` | Duplicate entries in `monuments.csv` | Deduplicate by `resource_id` prior to validation |
| `[ERROR] event_index must run 0..n-1 without gaps` | Non-sequential indexing | Re-index events starting at 0 for each monument |
| `UnicodeEncodeError: 'charmap'` | Windows console codepage mismatch | All scripts reconfigure UTF-8 streams automatically. Ensure Python 3.11+ is used |
| `era_ce_mismatch` Warning | Source text has inconsistent dates | Keep the source text as written, document the variance in `event_description` |
