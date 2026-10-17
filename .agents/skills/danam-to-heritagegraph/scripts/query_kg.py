#!/usr/bin/env python3
"""Execute SPARQL queries against the CAIR-Nepal HeritageGraph RDF dataset.

Supports running inline SPARQL strings, individual .rq query files, or the full
test suite in `queries/`, outputting formatted tables, CSV, or JSON.

Usage:
    uv run --with rdflib python query_kg.py --all
    uv run --with rdflib python query_kg.py --query queries/01_monuments_by_aat_style.rq
    uv run --with rdflib python query_kg.py --sparql "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime

import rdflib

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def format_cell(val, max_len=45) -> str:
    """Format an RDF term for display in console table."""
    if val is None:
        return ""
    text = str(val)
    # Simplify long URIs
    prefixes = {
        "https://data.cairnepal.org/heritage/resource/": "res:",
        "https://w3id.org/cair/heritagegraph/": "hg:",
        "http://www.cidoc-crm.org/cidoc-crm/": "crm:",
        "http://vocab.getty.edu/aat/": "aat:",
        "http://www.w3.org/2003/01/geo/wgs84_pos#": "geo:",
        "http://www.opengis.net/ont/geosparql#": "geosparql:",
        "http://purl.org/dc/terms/": "dcterms:",
        "http://www.w3.org/ns/prov#": "prov:",
    }
    for full_uri, pfx in prefixes.items():
        if text.startswith(full_uri):
            text = text.replace(full_uri, pfx)
            break
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def print_table(results, headers):
    """Print an ASCII table of SPARQL results."""
    if not results:
        print("  (0 results returned)")
        return

    cols = headers
    col_widths = {c: len(c) for c in cols}
    formatted_rows = []

    for r in results:
        row_dict = {}
        for c in cols:
            val_str = format_cell(r.get(c))
            row_dict[c] = val_str
            col_widths[c] = max(col_widths[c], len(val_str))
        formatted_rows.append(row_dict)

    # Header line
    sep_line = "+-" + "-+-".join("-" * col_widths[c] for c in cols) + "-+"
    hdr_line = "| " + " | ".join(c.ljust(col_widths[c]) for c in cols) + " |"

    print(sep_line)
    print(hdr_line)
    print(sep_line)
    for r in formatted_rows:
        print("| " + " | ".join(r[c].ljust(col_widths[c]) for c in cols) + " |")
    print(sep_line)
    print(f"Total rows: {len(formatted_rows)}\n")


def execute_sparql(graph: rdflib.Graph, query_str: str) -> tuple[list[dict], list[str]]:
    """Execute a SPARQL query on the RDF graph and return rows and column headers."""
    q_res = graph.query(query_str)
    headers = [str(v) for v in q_res.vars] if q_res.vars else []
    rows = []
    for row in q_res:
        row_dict = {}
        for var in q_res.vars:
            val = row[var]
            row_dict[str(var)] = val
        rows.append(row_dict)
    return rows, headers


def main():
    parser = argparse.ArgumentParser(description="Execute SPARQL queries on HeritageGraph RDF dataset")
    parser.add_argument("--graph", default="lod_export/heritage_graph.ttl", help="Path to RDF graph (.ttl or .nt)")
    parser.add_argument("--query", help="Path to .rq SPARQL query file")
    parser.add_argument("--sparql", help="Inline SPARQL query string")
    parser.add_argument("--all", action="store_true", help="Execute all standard queries in queries/*.rq")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Output format")
    args = parser.parse_args()

    if not os.path.exists(args.graph):
        print(f"[!] Error: RDF graph file not found at '{args.graph}'.")
        print("    Please run `python build_kg.py` first to generate the dataset.")
        sys.exit(1)

    print(f"[*] Loading RDF graph from '{args.graph}'...")
    load_start = datetime.now()
    graph = rdflib.Graph()
    fmt = "nt" if args.graph.endswith(".nt") else "turtle"
    graph.parse(args.graph, format=fmt)
    load_time = (datetime.now() - load_start).total_seconds()
    print(f"[+] Loaded {len(graph):,} triples in {load_time:.2f} seconds.\n")

    if args.all:
        # Check current working directory, then script directory, then parent directories
        potential_dirs = [
            "queries",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "queries"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "queries"),
        ]
        query_dir = None
        for pd in potential_dirs:
            if os.path.isdir(pd) and glob.glob(os.path.join(pd, "*.rq")):
                query_dir = pd
                break

        if not query_dir:
            print("[!] Error: No query files found in queries/ directory.", file=sys.stderr)
            return

        query_files = sorted(glob.glob(os.path.join(query_dir, "*.rq")))
        print(f"[*] Executing {len(query_files)} standard SPARQL queries from '{query_dir}'...\n")
        for q_path in query_files:
            q_name = os.path.basename(q_path)
            with open(q_path, encoding="utf-8") as f:
                q_text = f.read()

            print(f"============================================================")
            print(f" SPARQL Query: {q_name}")
            print(f"============================================================")
            q_start = datetime.now()
            results, headers = execute_sparql(graph, q_text)
            q_elapsed = (datetime.now() - q_start).total_seconds()
            print(f"Executed in {q_elapsed:.3f}s:")
            print_table(results, headers)

    elif args.query:
        if not os.path.exists(args.query):
            print(f"[!] Error: Query file not found at '{args.query}'")
            sys.exit(1)
        with open(args.query, encoding="utf-8") as f:
            q_text = f.read()

        results, headers = execute_sparql(graph, q_text)
        if args.format == "table":
            print_table(results, headers)
        elif args.format == "json":
            serializable = [{k: str(v) if v is not None else None for k, v in r.items()} for r in results]
            print(json.dumps(serializable, indent=2, ensure_ascii=False))
        elif args.format == "csv":
            import csv as py_csv
            writer = py_csv.DictWriter(sys.stdout, fieldnames=headers)
            writer.writeheader()
            for r in results:
                writer.writerow({k: str(v) if v is not None else "" for k, v in r.items()})

    elif args.sparql:
        results, headers = execute_sparql(graph, args.sparql)
        print_table(results, headers)
    else:
        print("[!] Please provide --query <file.rq>, --sparql '<query>', or --all")


if __name__ == "__main__":
    main()
