#!/usr/bin/env python3
"""Publish and manage versioned releases and 'latest' for HeritageGraphDataset.

Generates the standardized release layout:
HeritageGraphDataset/
├── latest/
│   ├── heritagegraph-nepal.ttl
│   ├── heritagegraph-nepal.jsonld
│   ├── heritagegraph-nepal.nt.gz
│   ├── metadata.json
│   └── checksums.sha256
└── releases/
    └── <version>/
        ├── heritagegraph-nepal.ttl
        ├── heritagegraph-nepal.jsonld
        ├── heritagegraph-nepal.nt.gz
        ├── metadata.json
        └── checksums.sha256

Usage:
    python publish_release.py --version v1.0.0
    python publish_release.py --version v1.0.0 --from-existing-ttl lod_export/heritage_graph.ttl --from-existing-nt lod_export/heritage_graph.nt
    python publish_release.py --version v1.1.0 --rebuild --dir staging
"""

import argparse
import gzip
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone

# Reconfigure Windows console to handle UTF-8 / IAST diacritics
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import rdflib
from rdflib import RDF, URIRef

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_kg import CRM_CLASS_FOR as CLASS_WRITTEN_AS  # noqa: E402  hg class name -> IRI the builder writes


def compute_sha256(filepath: str) -> str:
    """Compute hex SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def dirty_files(repo_dir: str | None = None) -> list[str]:
    """Tracked files with uncommitted changes in the git checkout that holds this script (untracked files do not count).
    A release must be reproducible from a commit, so create_release refuses to run while this list is not empty."""
    import subprocess
    repo_dir = repo_dir or os.path.dirname(os.path.abspath(__file__))
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo_dir,
                         capture_output=True, text=True, check=True).stdout
    return [line[3:] for line in out.splitlines() if line.strip()]


def verify_checksums(release_dir: str) -> list[str]:
    """Files in release_dir whose SHA-256 differs from checksums.sha256 (empty list: all match)."""
    bad = []
    for line in open(os.path.join(release_dir, "checksums.sha256"), encoding="utf-8"):
        if line.strip():
            digest, name = line.split(None, 1)
            if compute_sha256(os.path.join(release_dir, name.strip())) != digest:
                bad.append(name.strip())
    return bad


def compute_graph_stats(g: rdflib.Graph) -> dict:
    """Compute detailed dataset and entity statistics from the RDF graph."""
    print("[*] Computing graph statistics...")
    total_triples = len(g)

    # Key ontology classes
    hg_ns = "https://cair-nepal.org/heritagegraph/"
    crm_ns = "http://www.cidoc-crm.org/cidoc-crm/"

    def count_class(uri_str: str) -> int:
        # Classes the builder writes under another IRI (CIDOC-CRM, or the extension vocabulary) are counted there.
        local = uri_str[len(hg_ns):] if uri_str.startswith(hg_ns) else None
        if local in CLASS_WRITTEN_AS:
            uri_str = str(CLASS_WRITTEN_AS[local])
        return len(set(g.subjects(RDF.type, URIRef(uri_str))))

    # Objects: the nodes linked to a monument (housed in it, or part of it). Monuments are crm:E22_Human-Made_Object
    # too, so counting that class would include them.
    objs = set(g.subjects(URIRef("https://w3id.org/heritagegraph-nepal/vocab#isObjectOf"), None)) | \
           set(g.subjects(URIRef(f"{crm_ns}P46i_forms_part_of"), None))

    def count_plain_objects() -> int:
        """Objects with no class more specific than crm:E22_Human-Made_Object (ontology_class HumanMadeObject)."""
        specific = {URIRef(hg_ns + c) for c in ("Murti", "IconographicObject", "ArchitecturalElement", "Paubha")}
        return sum(1 for o in objs if not specific & set(g.objects(o, RDF.type)))

    monuments_count = count_class(f"{hg_ns}ArchitecturalStructure")
    events_count = count_class(f"{crm_ns}E5_Event")
    objects_count = len(objs)
    places_count = count_class(f"{hg_ns}Place") or count_class("https://schema.org/Place")  # crm:E53_Place
    deities_count = count_class(f"{hg_ns}Deity")
    geometries_count = count_class("http://www.opengis.net/ont/geosparql#Geometry")

    # Specific event types
    event_breakdown = {
        "Production": count_class(f"{hg_ns}Production"),
        "HistoricalEvent": count_class(f"{hg_ns}HistoricalEvent"),
        "ConditionAssessment": count_class(f"{hg_ns}ConditionAssessment"),
        "DestructionEvent": count_class(f"{hg_ns}DestructionEvent"),
        "Modification": count_class(f"{hg_ns}Modification"),  # crm:E11_Modification (renovation, repair …)
        "TransferOfCustody": count_class(f"{hg_ns}TransferOfCustody"),
        "Consecration": count_class(f"{hg_ns}Consecration"),
        "Enshrinement": count_class(f"{hg_ns}Enshrinement"),
        "RitualEvent": count_class(f"{hg_ns}RitualEvent"),
    }

    # Specific object types
    object_breakdown = {
        "Murti": count_class(f"{hg_ns}Murti"),
        "IconographicObject": count_class(f"{hg_ns}IconographicObject"),
        "ArchitecturalElement": count_class(f"{hg_ns}ArchitecturalElement"),
        "HumanMadeObject": count_plain_objects(),
        "Paubha": count_class(f"{hg_ns}Paubha"),
    }

    # Monument architectural types
    monument_breakdown = {
        "Temple": count_class(f"{hg_ns}Temple"),
        "Pati": count_class(f"{hg_ns}Pati"),
        "Sattal": count_class(f"{hg_ns}Sattal"),
        "Chaitya": count_class(f"{hg_ns}Chaitya"),
        "Stupa": count_class(f"{hg_ns}Stupa"),
        "Dharmashala": count_class(f"{hg_ns}Dharmashala"),
        "DhungeDhara": count_class(f"{hg_ns}DhungeDhara"),
        "Pokhari": count_class(f"{hg_ns}Pokhari"),
    }

    return {
        "triples": total_triples,
        "monuments": monuments_count,
        "events": events_count,
        "objects": objects_count,
        "places": places_count,
        "deities": deities_count,
        "geometries": geometries_count,
        "monumentTypes": {k: v for k, v in monument_breakdown.items() if v > 0},
        "eventTypes": {k: v for k, v in event_breakdown.items() if v > 0},
        "objectTypes": {k: v for k, v in object_breakdown.items() if v > 0},
    }


def create_release(
    version: str,
    ttl_source: str | None = None,
    nt_source: str | None = None,
    graph: rdflib.Graph | None = None,
    update_latest: bool = True,
    base_dir: str = ".",
    notes: str = "",
) -> tuple[str, str]:
    """Publish a new dataset release and update latest/. Refuses to run from a working tree with uncommitted changes."""
    dirty = dirty_files()
    if dirty:
        raise RuntimeError("refusing to build a release from a working tree with uncommitted changes "
                           f"(commit or stash them first): {', '.join(dirty)}")
    # Ensure version follows vX.Y.Z
    if not version.startswith("v"):
        version = f"v{version}"

    release_dir = os.path.join(base_dir, "releases", version)
    latest_dir = os.path.join(base_dir, "latest")
    os.makedirs(release_dir, exist_ok=True)
    if update_latest:
        os.makedirs(latest_dir, exist_ok=True)

    print(f"\n========================================================")
    print(f" Publishing HeritageGraph Nepal Release: {version}")
    print(f" Target Directory: {release_dir}")
    print(f" Update 'latest/': {update_latest}")
    print(f"========================================================\n")

    ttl_dest = os.path.join(release_dir, "heritagegraph-nepal.ttl")
    jsonld_dest = os.path.join(release_dir, "heritagegraph-nepal.jsonld")
    nt_dest_gz = os.path.join(release_dir, "heritagegraph-nepal.nt.gz")
    metadata_dest = os.path.join(release_dir, "metadata.json")
    checksums_dest = os.path.join(release_dir, "checksums.sha256")

    # Step 1: Ensure Turtle graph is loaded or copied
    if graph is None:
        graph = rdflib.Graph()
        if ttl_source and os.path.exists(ttl_source):
            print(f"[*] Parsing existing Turtle from {ttl_source}...")
            graph.parse(ttl_source, format="turtle")
            # Copy to destination if not identical
            if os.path.abspath(ttl_source) != os.path.abspath(ttl_dest):
                shutil.copy2(ttl_source, ttl_dest)
        else:
            raise FileNotFoundError(f"Turtle source '{ttl_source}' not found and graph not provided.")
    else:
        print(f"[*] Serializing Turtle to {ttl_dest}...")
        graph.serialize(destination=ttl_dest, format="turtle", encoding="utf-8")

    # Step 2: Ensure JSON-LD
    print(f"[*] Serializing JSON-LD to {jsonld_dest}...")
    graph.serialize(destination=jsonld_dest, format="json-ld", encoding="utf-8")
    print(f"[+] Serialized JSON-LD ({os.path.getsize(jsonld_dest) / (1024*1024):.2f} MB)")

    # Step 3: Ensure Gzipped N-Triples (.nt.gz)
    print(f"[*] Preparing gzipped N-Triples at {nt_dest_gz}...")
    if nt_source and os.path.exists(nt_source):
        print(f"    Compressing existing N-Triples {nt_source} -> {nt_dest_gz}...")
        with open(nt_source, "rb") as f_in, gzip.open(nt_dest_gz, "wb", compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)
    else:
        temp_nt = os.path.join(release_dir, "_temp.nt")
        print(f"    Serializing N-Triples to temporary file...")
        graph.serialize(destination=temp_nt, format="nt", encoding="utf-8")
        with open(temp_nt, "rb") as f_in, gzip.open(nt_dest_gz, "wb", compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)
        if os.path.exists(temp_nt):
            os.remove(temp_nt)
    print(f"[+] Created {nt_dest_gz} ({os.path.getsize(nt_dest_gz) / (1024*1024):.2f} MB)")

    # Step 4: Compute statistics
    stats = compute_graph_stats(graph)

    # Step 5: Compute hashes for the three distribution files
    ttl_hash = compute_sha256(ttl_dest)
    jsonld_hash = compute_sha256(jsonld_dest)
    nt_gz_hash = compute_sha256(nt_dest_gz)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_published = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    metadata = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "HeritageGraph Nepal: Event-Centric Cultural Heritage Knowledge Graph",
        "identifier": f"https://cair-nepal.org/heritagegraph/dataset/{version}",
        "version": version,
        "description": (
            "Event-centric Linked Open Data (LOD) cultural heritage Knowledge Graph of Nepal "
            "derived from DANAM (Digital Archive of Nepalese Arts and Monuments) narratives and records. "
            "Structured in accordance with CAIR-Nepal HeritageGraph Ontology (v1.0.0), "
            "CIDOC-CRM (v7.1.2), W3C PROV-O, GeoSPARQL, and Getty AAT."
        ),
        "publisher": {
            "@type": "Organization",
            "name": "CAIR-Nepal (Center for Artificial Intelligence Research Nepal)",
            "url": "https://cairnepal.org",
            "email": "contact@cairnepal.org"
        },
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "datePublished": date_published,
        "dateModified": now_iso,
        "inLanguage": ["en", "ne", "sa"],
        "keywords": [
            "Cultural Heritage",
            "Nepal",
            "Knowledge Graph",
            "Linked Open Data",
            "CIDOC-CRM",
            "PROV-O",
            "DANAM",
            "Temples",
            "Inscriptions",
            "GeoSPARQL"
        ],
        "spatialCoverage": {
            "@type": "Place",
            "name": "Nepal (Kathmandu Valley and surrounding regions)"
        },
        "releaseNotes": notes or f"Standardized release {version} of HeritageGraph Nepal Knowledge Graph.",
        "statistics": stats,
        "namespaces": {
            "hg": "https://cair-nepal.org/heritagegraph/",
            "heritageGraph": "https://cair-nepal.org/heritagegraph/",
            "crm": "http://www.cidoc-crm.org/cidoc-crm/",
            "prov": "http://www.w3.org/ns/prov#",
            "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
            "geosparql": "http://www.opengis.net/ont/geosparql#",
            "aat": "http://vocab.getty.edu/aat/",
            "schema": "https://schema.org/",
            "void": "http://rdfs.org/ns/void#",
            "dcat": "http://www.w3.org/ns/dcat#",
            "dcterms": "http://purl.org/dc/terms/",
            "res": "https://data.cairnepal.org/heritage/resource/"
        },
        "distribution": [
            {
                "@type": "DataDownload",
                "name": "Turtle Serialization",
                "fileName": "heritagegraph-nepal.ttl",
                "encodingFormat": "text/turtle",
                "contentSize": f"{os.path.getsize(ttl_dest) / (1024*1024):.2f} MB",
                "byteSize": os.path.getsize(ttl_dest),
                "sha256": ttl_hash
            },
            {
                "@type": "DataDownload",
                "name": "JSON-LD Serialization",
                "fileName": "heritagegraph-nepal.jsonld",
                "encodingFormat": "application/ld+json",
                "contentSize": f"{os.path.getsize(jsonld_dest) / (1024*1024):.2f} MB",
                "byteSize": os.path.getsize(jsonld_dest),
                "sha256": jsonld_hash
            },
            {
                "@type": "DataDownload",
                "name": "Compressed N-Triples (Bulk Ingestion)",
                "fileName": "heritagegraph-nepal.nt.gz",
                "encodingFormat": "application/gzip",
                "contentSize": f"{os.path.getsize(nt_dest_gz) / (1024*1024):.2f} MB",
                "byteSize": os.path.getsize(nt_dest_gz),
                "sha256": nt_gz_hash
            }
        ],
        "citation": (
            "CAIR-Nepal. (2026). HeritageGraph Nepal: Event-Centric Cultural Heritage Knowledge Graph (Version "
            + version
            + ") [Data set]. CAIR-Nepal. https://github.com/CAIRNepal/HeritageGraphDataset"
        )
    }

    # Step 6: Write metadata.json
    with open(metadata_dest, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"[+] Wrote dataset metadata: {metadata_dest}")

    # Compute hash of metadata.json
    meta_hash = compute_sha256(metadata_dest)

    # Step 7: Write checksums.sha256
    checksum_lines = [
        f"{ttl_hash}  heritagegraph-nepal.ttl",
        f"{jsonld_hash}  heritagegraph-nepal.jsonld",
        f"{nt_gz_hash}  heritagegraph-nepal.nt.gz",
        f"{meta_hash}  metadata.json",
    ]
    with open(checksums_dest, "w", encoding="utf-8") as f:
        f.write("\n".join(checksum_lines) + "\n")
    print(f"[+] Wrote SHA-256 checksums: {checksums_dest}")
    bad = verify_checksums(release_dir)
    if bad:
        raise RuntimeError(f"checksums.sha256 does not match: {', '.join(bad)}")

    # Step 8: Update latest/
    if update_latest:
        print(f"\n[*] Updating 'latest/' directory from {release_dir}...")
        for filename in [
            "heritagegraph-nepal.ttl",
            "heritagegraph-nepal.jsonld",
            "heritagegraph-nepal.nt.gz",
            "metadata.json",
            "checksums.sha256",
        ]:
            src = os.path.join(release_dir, filename)
            dst = os.path.join(latest_dir, filename)
            shutil.copy2(src, dst)
        print(f"[+] 'latest/' successfully synchronized with release {version}.")

    print("\n" + "=" * 60)
    print(f" HeritageGraph Nepal Release {version} Published Successfully!")
    print("=" * 60)
    print(f" Release Directory:  {release_dir}")
    print(f" Latest Directory:   {latest_dir if update_latest else 'N/A'}")
    print(f" Triples Count:      {stats['triples']:,}")
    print(f" Monuments Count:    {stats['monuments']:,}")
    print(f" Events Count:       {stats['events']:,}")
    print(f" Objects Count:      {stats['objects']:,}")
    print(" Files:")
    print(f"   - heritagegraph-nepal.ttl     ({os.path.getsize(ttl_dest)/(1024*1024):.2f} MB)")
    print(f"   - heritagegraph-nepal.jsonld  ({os.path.getsize(jsonld_dest)/(1024*1024):.2f} MB)")
    print(f"   - heritagegraph-nepal.nt.gz   ({os.path.getsize(nt_dest_gz)/(1024*1024):.2f} MB)")
    print(f"   - metadata.json               ({os.path.getsize(metadata_dest)/1024:.2f} KB)")
    print(f"   - checksums.sha256            ({os.path.getsize(checksums_dest)} bytes)")
    print("=" * 60 + "\n")

    return release_dir, latest_dir


def main():
    parser = argparse.ArgumentParser(
        description="Publish a versioned release and update 'latest/' for HeritageGraphDataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Publish v1.0.0 using existing lod_export files
  python publish_release.py --version v1.0.0 --from-existing-ttl lod_export/heritage_graph.ttl --from-existing-nt lod_export/heritage_graph.nt

  # Rebuild full graph from staging and publish as v1.1.0
  python publish_release.py --version v1.1.0 --rebuild --dir staging

  # Publish release without updating latest
  python publish_release.py --version v1.0.1 --no-latest
"""
    )
    parser.add_argument("--version", default="v1.0.0", help="Release version tag (e.g. v1.0.0, v1.1.0)")
    parser.add_argument("--from-existing-ttl", default=None, help="Path to existing Turtle graph file")
    parser.add_argument("--from-existing-nt", default=None, help="Path to existing N-Triples graph file")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild graph from staging CSVs using build_kg.py")
    parser.add_argument("--dir", default="staging", help="Base staging directory when rebuilding")
    parser.add_argument("--notes", default="", help="Optional release notes description")
    parser.add_argument("--no-latest", action="store_true", help="Do not update the latest/ directory")
    args = parser.parse_args()

    ttl_src = args.from_existing_ttl
    nt_src = args.from_existing_nt
    graph = None

    if args.rebuild:
        print("[*] Rebuilding Knowledge Graph from staging CSVs...")
        import build_kg
        mon_path = os.path.join(args.dir, "monuments.csv")
        ev_path = os.path.join(args.dir, "events.csv")
        obj_path = os.path.join(args.dir, "objects.csv")
        if not os.path.exists(ev_path):
            ev_path = "data_collection/data/exports/events.csv"
        if not os.path.exists(obj_path):
            obj_path = "data_collection/data/exports/objects.csv"

        graph, _ = build_kg.build_knowledge_graph(mon_path, ev_path, obj_path)
    else:
        # Default fallback to lod_export if nothing given
        if not ttl_src:
            for cand in ["lod_export/heritage_graph.ttl", "latest/heritagegraph-nepal.ttl"]:
                if os.path.exists(cand):
                    ttl_src = cand
                    break
        if not nt_src:
            for cand in ["lod_export/heritage_graph.nt"]:
                if os.path.exists(cand):
                    nt_src = cand
                    break

    create_release(
        version=args.version,
        ttl_source=ttl_src,
        nt_source=nt_src,
        graph=graph,
        update_latest=not args.no_latest,
        notes=args.notes,
    )


if __name__ == "__main__":
    main()
