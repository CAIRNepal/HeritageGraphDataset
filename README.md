# CAIR-Nepal HeritageGraphDataset

[![Ontology: CAIR-Nepal CulturalHeritageOntology](https://img.shields.io/badge/Ontology-CulturalHeritageOntology%20v0.1.0--alpha.2-blue.svg)](https://w3id.org/cair/heritagegraph/)
[![Standards: CIDOC-CRM v7.1.2](https://img.shields.io/badge/Standard-CIDOC--CRM%20v7.1.2-green.svg)](http://www.cidoc-crm.org/cidoc-crm/)
[![Provenance: W3C PROV-O](https://img.shields.io/badge/Provenance-W3C%20PROV--O-orange.svg)](http://www.w3.org/ns/prov#)
[![Vocabulary: Getty AAT](https://img.shields.io/badge/Vocabulary-Getty%20AAT-purple.svg)](http://vocab.getty.edu/aat/)
[![Linked Data: RDF / SPARQL](https://img.shields.io/badge/Linked%20Data-Turtle%20%7C%20N--Triples%20%7C%20SPARQL-informational.svg)](https://www.w3.org/TR/turtle/)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)

An authoritative, provenance-preserving cultural heritage dataset and Linked Open Data (LOD) Knowledge Graph for Nepal.
This project ingests monument reports scraped from the **Digital Archive of Nepalese Arts and Monuments (DANAM)**
(`danam.cats.uni-heidelberg.de`), normalizes inscriptional calendars and architectural typologies into structured staging
tables, and synthesizes standards-compliant RDF Knowledge Graphs aligned with **CIDOC-CRM (v7.1.2)**, **W3C PROV-O**,
**Getty AAT**, and **GeoSPARQL**.

---

## Table of Contents
- [1. Architecture & Pipeline](#1-architecture--pipeline)
- [2. Repository Structure](#2-repository-structure)
- [3. Installation & Environment](#3-installation--environment)
- [4. Pipeline Stage 1: Data Collection (Scraping)](#4-pipeline-stage-1-data-collection-scraping)
- [5. Pipeline Stage 2: Staging & Provenance Transformation](#5-pipeline-stage-2-staging--provenance-transformation)
- [6. Pipeline Stage 3: Knowledge Graph (KG) Construction](#6-pipeline-stage-3-knowledge-graph-kg-construction)
- [7. Pipeline Stage 4: SPARQL Analytics & Benchmark Queries](#7-pipeline-stage-4-sparql-analytics--benchmark-queries)
- [8. Antigravity Skill (`danam-to-heritagegraph`)](#8-antigravity-skill-danam-to-heritagegraph)
- [9. Ontological Foundations & Namespaces](#9-ontological-foundations--namespaces)
- [10. Script Reference & CLI Help](#10-script-reference--cli-help)
- [11. Quality Invariants & Auditing](#11-quality-invariants--auditing)

---

## 1. Architecture & Pipeline

```mermaid
flowchart TD
    subgraph DataCollection["1. Data Collection & Scraping"]
        R[resourceids.csv] -->|Playwright Headless| Scraper[danam_scraper_v2.py / shard_scrape.py]
        Scraper -->|Raw JSON Cache| RawJSON["data/raw/{uuid}.json"]
        Scraper -->|Tabular Dumps| Exports["data/exports/ (monuments.csv, events.csv, objects.csv)"]
    end

    subgraph StagingPipeline["2. Staging & Provenance Transformation"]
        Exports -->|prepare.py| StagingPrep["staging/monuments.csv<br/>staging/skipped_rows.csv"]
        Exports -->|prepare.py + heritage_dates.py| Candidates["event_candidates.jsonl<br/>object_candidates.jsonl"]
        Candidates -->|LLM / Human Extraction| StagingEvents["staging/events.csv"]
        Candidates -->|LLM / Human Extraction| StagingObjects["staging/objects.csv"]
        StagingPrep & StagingEvents & StagingObjects -->|Strict Verification| Validator["validate.py (Exit 0)"]
    end

    subgraph KnowledgeGraph["3. Knowledge Graph & Linked Open Data"]
        Validator -->|build_kg.py| KGBuilder["RDF Graph Construction Engine"]
        KGBuilder -->|Turtle Serializer| TTL["lod_export/heritage_graph.ttl (~180,800+ triples)"]
        KGBuilder -->|N-Triples Serializer| NT["lod_export/heritage_graph.nt (Bulk Triplestores)"]
        KGBuilder -->|VoID & DCAT| LODMeta["Dataset Metadata & Provenance"]
    end

    subgraph SPARQLAnalytics["4. Semantic Queries & Benchmarks"]
        TTL & NT -->|query_kg.py| SPARQLRunner["SPARQL 1.1 Query Engine"]
        SPARQLRunner --> Q1["01_monuments_by_aat_style.rq"]
        SPARQLRunner --> Q2["02_historical_timeline.rq"]
        SPARQLRunner --> Q3["03_spatial_geosparql.rq"]
        SPARQLRunner --> Q4["04_monument_sacred_objects.rq"]
        SPARQLRunner --> Q5["05_provenance_audit.rq"]
        SPARQLRunner --> Q6["06_condition_threats.rq"]
        SPARQLRunner --> Q7["07_deities_traditions.rq"]
    end
```

---

## 2. Repository Structure

```text
HeritageGraphDataset/
├── .agents/
│   └── skills/
│       └── danam-to-heritagegraph/     # Standard Antigravity agent skill
│           ├── SKILL.md                 # Workflow runbook & agent instructions
│           ├── references/              # Specifications & ground-truth mappings
│           │   ├── column_spec.md       # Exact staging schema & column definitions
│           │   ├── ontology_mapping.md  # Class mapping rules & Getty AAT styles
│           │   └── worked_example.md    # Worked ground-truth example (Jogeśvara Mandira)
│           └── scripts/                 # Core automation tools (cross-platform, UTF-8 hardened)
│               ├── prepare.py           # Ingestion, typology mapping & candidate generator
│               ├── heritage_dates.py    # Date, era (NS, VS, ŚS, MS), & calendar parser
│               ├── validate.py          # Strict staging CSV validator
│               ├── build_kg.py          # RDF Knowledge Graph builder & LOD exporter
│               └── query_kg.py          # SPARQL query execution runner
├── data_collection/                     # Scraper subsystem
│   ├── danam_scraper_v2.py              # Main Playwright scraping & export engine
│   ├── shard_scrape.py                  # Distributed multi-process shard runner
│   ├── main.py                          # Data collection CLI dispatcher
│   ├── resourceids.csv                  # Catalog of DANAM monument IDs
│   ├── pyproject.toml                   # Scraper dependencies
│   └── data/
│       ├── raw/                         # Scraped JSON records (one per monument UUID)
│       └── exports/                     # Raw CSV exports (monuments.csv, events.csv, objects.csv)
├── queries/                             # Standard SPARQL benchmark suite (*.rq)
│   ├── 01_monuments_by_aat_style.rq     # Getty AAT architectural style classification
│   ├── 02_historical_timeline.rq        # Multi-era chronological historical event timeline
│   ├── 03_spatial_geosparql.rq          # GeoSPARQL & WGS84 spatial distribution
│   ├── 04_monument_sacred_objects.rq    # Sacred objects, murtis, and architectural elements
│   ├── 05_provenance_audit.rq           # W3C PROV-O provenance, sources, & evidence audit
│   ├── 06_condition_threats.rq          # Conservation assessments & identified threats
│   └── 07_deities_traditions.rq         # Religious traditions & primary deities
├── lod_export/                          # Generated Linked Open Data RDF graphs
│   ├── heritage_graph.ttl               # Human-readable Turtle serialization (~180,800+ triples)
│   └── heritage_graph.nt                # Bulk streaming N-Triples for triplestores
├── staging/                             # Active staging datasets and candidates
│   ├── monuments.csv                    # Ingested monuments with derived ontology columns
│   ├── skipped_rows.csv                 # Catalog of dead/empty records
│   ├── event_candidates.jsonl           # Pre-filtered candidate sentences for events
│   └── object_candidates.jsonl          # Pre-filtered candidate mentions for objects
├── build_kg.py                          # Root convenience wrapper for Knowledge Graph construction
├── query_kg.py                          # Root convenience wrapper for SPARQL query execution
├── skill/
│   └── danam-to-heritagegraph.skill     # Standard packaged ZIP distribution of the skill
├── AGENTS.md                            # Operational rules & guidelines for AI agents
└── README.md                            # Comprehensive repository documentation (this file)
```

---

## 3. Installation & Environment

### Prerequisites
- **Python**: Version 3.11 or later
- **Package Manager**: Standard `pip` or [`uv`](https://github.com/astral-sh/uv) (recommended)
- **Operating System**: Linux, macOS, or Windows (Windows console UTF-8 stream handling is built-in)

### Dependencies
Install the required packages:
```bash
# Core RDF Knowledge Graph & SPARQL dependencies:
pip install rdflib

# Scraper dependencies (if performing data collection):
pip install playwright beautifulsoup4 lxml
playwright install chromium
```

Or using `uv` without global installation:
```bash
# Run commands directly with rdflib
uv run --with rdflib python build_kg.py --help
uv run --with rdflib python query_kg.py --all
```

---

## 4. Pipeline Stage 1: Data Collection (Scraping)

The scraper retrieves JavaScript-rendered monument pages from DANAM using Playwright headless Chromium.

### Running a Test Scrape
```bash
cd data_collection
python danam_scraper_v2.py --csv resourceids.csv --out data/raw --limit 5
```

### Running Distributed Shards
To parallelize scraping across multiple terminals:
```bash
# Terminal 1: Shard 0 of 4
python shard_scrape.py --csv resourceids.csv --out data/raw --shard 0 --total-shards 4

# Terminal 2: Shard 1 of 4
python shard_scrape.py --csv resourceids.csv --out data/raw --shard 1 --total-shards 4
```
Each shard maintains an independent checkpoint file (`checkpoint_shard_N.txt`) and is fully idempotent.

### Exporting Scraped Data to CSV
Once JSON files are written to `data/raw/`:
```bash
python danam_scraper_v2.py --csv resourceids.csv --out data/raw --export-only --export-dir data/exports
```
This produces three flat tabular files:
1. `data/exports/monuments.csv` (46 raw attributes)
2. `data/exports/events.csv` (tabular historical events, FK: `resource_id`)
3. `data/exports/objects.csv` (tabular objects and elements, FK: `resource_id`)

---

## 5. Pipeline Stage 2: Staging & Provenance Transformation

### Ingestion & Candidate Preparation (`prepare.py`)
Run `prepare.py` on the raw monuments export:
```bash
python .agents/skills/danam-to-heritagegraph/scripts/prepare.py --input data_collection/data/exports/monuments.csv --outdir staging
```
**What `prepare.py` does:**
1. Preserves all 46 original DANAM columns verbatim.
2. Isolates dead pages into `skipped_rows.csv`.
3. Appends normalized ontology columns:
   - `danam_code`: e.g. `SKH0510` (extracted from `name_devanagari`).
   - `name_ne`: Devanagari monument name with the code stripped.
   - `ontology_class`: e.g. `Temple`, `Chaitya`, `Stupa`, `Pati`, `Sattal`, `DhungeDhara`.
   - `aat_style`: Getty AAT architectural style (e.g. `aat:300004829` for Pagoda, `aat:300446671` for Shikhara).
   - `condition_types`: Normalized status (`Good`, `Damaged`, `Ruined`, `Restored`).
   - `mapping_notes`: Flags for manual review.
4. Generates `event_candidates.jsonl` and `object_candidates.jsonl` containing extracted sentences, inscriptional dates, object IDs, and citations.

### Date Parsing & Lunisolar Verification (`heritage_dates.py`)
`heritage_dates.py` parses free text for Nepali era dates, months, lunar fortnights (paksha), and tithis, pairing them with CE years:
```bash
# Parse arbitrary text from CLI
python .agents/skills/danam-to-heritagegraph/scripts/heritage_dates.py "On the 13th of the bright fortnight of Phālguna in 1689 CE (NS 809)"

# Run internal test suite
python .agents/skills/danam-to-heritagegraph/scripts/heritage_dates.py --test
```
**Era Conversion Offsets:**
| Era Name | Code | Base Offset to CE | Month-Aware Boundary |
|---|---|---|---|
| Nepāla Saṃvat | `NS` | +879 / +880 | Months Kārtika, Mārgaśīrṣa, Pauṣa = +879; others = +880 |
| Vikrama Saṃvat | `VS` / `BS` | -56 / -57 | Months Māgha, Phālguna, Caitra = -56; others = -57 |
| Śaka Saṃvat | `ŚS` / `SS` | +78 | Fixed +78 |
| Mānadeva Saṃvat | `MS` | +576 | Fixed +576 (approximate) |

### Strict Quality Validation (`validate.py`)
Run `validate.py` on the staging directory before Knowledge Graph ingestion:
```bash
python .agents/skills/danam-to-heritagegraph/scripts/validate.py --dir staging
```
The validator strictly enforces:
- **Foreign Key Integrity**: Every `resource_id` and `monument_name` in `events.csv` and `objects.csv` must match `monuments.csv` verbatim.
- **Substring Provenance**: `evidence_text` must be an exact verbatim substring of the monument's `description_en`.
- **Sequential Indexing**: `event_index` and `object_index` must be 0-based and contiguous (0..n-1).
- **Calendar Conformance**: Canonical month spellings (`Phālguna`, `Māgha`, etc.), `paksha` (`Śukla` or `Kṛṣṇa`), and `tithi` (1..15).
- **Exit Code**: Exits `0` only when zero errors remain.

---

## 6. Pipeline Stage 3: Knowledge Graph (KG) Construction

The Knowledge Graph builder transforms staging CSVs into a formal RDF graph aligned with international ontology standards.

### Running Knowledge Graph Construction
```bash
# Ingest staging datasets and output Turtle + N-Triples
python build_kg.py --dir staging --outdir lod_export --formats turtle,nt

# Test on a subset of 50 monuments
python build_kg.py --dir staging --sample 50 --outdir lod_export
```

### Knowledge Graph Metrics (Full Dataset)
- **Monuments Ingested**: 1,228
- **Historical Events**: 5,090
- **Sacred Objects**: 7,160
- **Geographic Places**: 234
- **Unique Deities**: 172
- **Total RDF Triples**: **180,820+**
- **Artifacts Generated**:
  - `lod_export/heritage_graph.ttl`: 18.1 MB
  - `lod_export/heritage_graph.nt`: 42.3 MB

---

## 7. Pipeline Stage 4: SPARQL Analytics & Benchmark Queries

The repository includes 7 standard benchmark SPARQL queries located in `queries/`:

| Query File | Description | Ontological Alignment |
|---|---|---|
| `01_monuments_by_aat_style.rq` | Classifies monuments by Getty AAT architectural style (Pagoda, Shikhara, Stupa, Chaitya, Dome). | `hg:hasArchitecturalStyle`, `aat:` |
| `02_historical_timeline.rq` | Extracts chronological event timelines across Licchavi, Malla, Shah, and Rana periods. | `crm:E5_Event`, `hg:period`, `hg:inscriptionalDateEra` |
| `03_spatial_geosparql.rq` | Queries spatial coordinates (WGS84 lat/lon) and administrative locations (districts, municipalities). | `geo:lat`, `geo:long`, `geosparql:asWKT` |
| `04_monument_sacred_objects.rq` | Identifies sacred objects, murtis, toranas, bells, and architectural components per monument. | `crm:P46_is_composed_of`, `hg:Murti`, `hg:material` |
| `05_provenance_audit.rq` | Audits W3C PROV-O provenance, primary source citations, and verbatim evidence text. | `prov:wasDerivedFrom`, `prov:wasAttributedTo`, `dcterms:source` |
| `06_condition_threats.rq` | Analyzes physical condition assessments and identified threats (earthquakes, erosion, encroachment). | `crm:E14_Condition_Assessment`, `hg:conditionStatus` |
| `07_deities_traditions.rq` | Maps religious traditions (Hinduism, Buddhism, etc.) and primary enshrined deities. | `hg:Deity`, `hg:hasReligiousTradition` |

### Running Queries with `query_kg.py`
```bash
# Execute all 7 benchmark queries with formatted table output:
python query_kg.py --all

# Execute a single benchmark query:
python query_kg.py --query queries/01_monuments_by_aat_style.rq

# Export query results as JSON or CSV:
python query_kg.py --query queries/02_historical_timeline.rq --format json
python query_kg.py --query queries/03_spatial_geosparql.rq --format csv

# Execute an arbitrary inline SPARQL query:
python query_kg.py --sparql "SELECT ?m ?name WHERE { ?m a hg:Temple ; rdfs:label ?name } LIMIT 10"
```

---

## 8. Antigravity Skill (`danam-to-heritagegraph`)

This repository is equipped with an official Antigravity skill located at `.agents/skills/danam-to-heritagegraph/`.

### Structure
- **`SKILL.md`**: Main instruction runbook containing step-by-step guidance, rules, and commands.
- **`references/`**: Authoritative specifications:
  - `column_spec.md`: Column-by-column formatting rules.
  - `ontology_mapping.md`: Mapping tables from keywords to ontology classes.
  - `worked_example.md`: Complete worked example of Jogeśvara Mandira.
- **`scripts/`**: Hardened, self-contained Python scripts for date parsing, candidate extraction, validation, KG building, and querying.
- **`skill/danam-to-heritagegraph.skill`**: Pre-packaged ZIP archive for one-click installation into external Antigravity environments.

### How the Agent Uses the Skill
When an agent is asked to "transform heritage data", "extract events from descriptions", "parse NS/VS dates", or "build the knowledge graph", Antigravity automatically activates this skill and follows its standardized runbook.

---

## 9. Ontological Foundations & Namespaces

The dataset merges domain-specific cultural concepts with international standards:

```turtle
@prefix hg:        <https://w3id.org/cair/heritagegraph/> .
@prefix crm:       <http://www.cidoc-crm.org/cidoc-crm/> .
@prefix prov:      <http://www.w3.org/ns/prov#> .
@prefix aat:       <http://vocab.getty.edu/aat/> .
@prefix geo:       <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix geosparql: <http://www.opengis.net/ont/geosparql#> .
@prefix schema:    <https://schema.org/> .
@prefix void:      <http://rdfs.org/ns/void#> .
@prefix dcat:      <http://www.w3.org/ns/dcat#> .
@prefix dcterms:   <http://purl.org/dc/terms/> .
@prefix res:       <https://data.cairnepal.org/heritage/resource/> .
```

### Core Entity Class Mappings
- **Monuments**: `hg:ArchitecturalStructure` (subclasses: `hg:Temple`, `hg:Stupa`, `hg:Chaitya`, `hg:Pati`, `hg:Sattal`, `hg:Dharmashala`, `hg:DhungeDhara`, `hg:Pokhari`).
- **Events**: `crm:E5_Event` (subclasses: `hg:Production`, `hg:DestructionEvent`, `hg:Consecration`, `hg:Enshrinement`, `hg:TransferOfCustody`, `hg:RitualEvent`, `hg:ConditionAssessment`, `hg:HistoricalEvent`).
- **Objects**: `crm:E22_Human-Made_Object` (subclasses: `hg:Murti`, `hg:Paubha`, `hg:ArchitecturalElement`, `hg:IconographicObject`, `hg:HumanMadeObject`).
- **Geography**: `crm:E53_Place`, `geo:SpatialThing`, `geosparql:Geometry`.
- **Provenance**: `prov:Entity`, `prov:Activity`, `prov:Agent`.

---

## 10. Script Reference & CLI Help

Every script in this repository is hardened, cross-platform, supports `--help`, and handles Windows console UTF-8 stream re-encoding:

| Script | Location | Key Arguments | Purpose |
|---|---|---|---|
| `prepare.py` | `.agents/skills/.../scripts/` | `--input <csv>`, `--outdir <dir>` | Ingests raw CSV and prepares staging files and candidates. |
| `heritage_dates.py` | `.agents/skills/.../scripts/` | `[text]`, `--file <file>`, `--test`, `--compact` | Extracts inscriptional dates, converts eras to CE, and parses lunisolar calendar terms. |
| `validate.py` | `.agents/skills/.../scripts/` | `--dir <staging_dir>` | Strictly validates staging CSV foreign keys, indices, and verbatim evidence text. |
| `build_kg.py` | Root & `.agents/skills/.../scripts/` | `--dir <staging_dir>`, `--outdir <dir>`, `--formats <fmt>`, `--sample <n>` | Builds the RDF Knowledge Graph from staging CSVs and serializes to Turtle / N-Triples. |
| `query_kg.py` | Root & `.agents/skills/.../scripts/` | `--all`, `--query <file.rq>`, `--sparql <query>`, `--format <table\|json\|csv>` | Executes SPARQL queries against the generated Knowledge Graph. |
| `danam_scraper_v2.py`| `data_collection/` | `--csv <file>`, `--out <dir>`, `--limit <n>`, `--export-only` | Playwright scraper that extracts monument pages into JSON and exports flat CSVs. |
| `shard_scrape.py` | `data_collection/` | `--csv <file>`, `--shard <id>`, `--total-shards <n>` | Multi-process shard runner for parallelized scraping. |

---

## 11. Quality Invariants & Auditing

The following invariants are strictly enforced throughout all data pipelines:

1. **"Blank Beats Guessed"**: Never pad rows or guess values when sources are silent.
2. **Exact Verbatim Substring**: `evidence_text` must be an exact substring of `description_en`.
3. **Preserve Contradictions**: When historical sources disagree (e.g. `ŚS 1422 (i.e., 500 CE)`), keep the written values as-is and detail the discrepancy in `event_description`.
4. **No Artificial Padding**: Extracted counts need not match page counters (`event_count`, `object_count`). Page counters reflect tabular database records, whereas narrative descriptions cover only a subset.

---

## License & Attribution

This dataset and codebase are developed by **CAIR-Nepal** (Centre for Artificial Intelligence Research Nepal).
Monument reports and source materials originate from the **Digital Archive of Nepalese Arts and Monuments (DANAM)**, Heidelberg University (`danam.cats.uni-heidelberg.de`).
Distributed for academic research, cultural preservation, and natural language processing.