#!/usr/bin/env python3
"""Step 1: DANAM scrape CSV -> monuments.csv + candidate files for events/objects.

Usage:
  python scripts/prepare.py --input <danam_export.csv> --outdir <staging_dir>

Writes:
  monuments.csv           all original columns verbatim + derived ontology columns
  skipped_rows.csv        rows with no usable record (e.g. status ok but empty fields)
  event_candidates.jsonl  candidate sentences with dates, citations, and event cues
  object_candidates.jsonl candidate object-ID mentions with sentence context
"""
import argparse
import csv
import json
import os
import re
import sys

# Reconfigure Windows console to handle UTF-8 / IAST diacritics
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(__file__))
from heritage_dates import find_dates

csv.field_size_limit(10**9)

OBJ_ID_RE = re.compile(r"\b([A-Z]{3}\d{4}-\d{3})\b")
MON_CODE_RE = re.compile(r"\b([A-Z]{3}\d{4})\b(?!-)")
ERA_PAREN_RE = re.compile(r"^\s*(NS|VS|BS|ŚS|SS|MS|i\.e\.|\d{1,4}\s*(CE|BCE))")
EVENT_WORDS = re.compile(
    r"(renovat|reconstruct|rebuil|built|build|construct|install|donat|collaps|earthquake|stolen|theft|"
    r"consecrat|establish|dismantl|restor|replac|repair|founded|erected|inscri|endow|guṭhi|guthi|"
    r"destroy|fire|flood|damag|moved|relocat|added|offered|commission|allocated|grant)", re.I)

# monument_type keyword -> (ontology class, AAT style id or "")
TYPE_MAP = [
    ("stupa", "Stupa", "aat:300007576"),
    ("caitya", "Chaitya", "aat:300007562"), ("chaitya", "Chaitya", "aat:300007562"),
    ("monastic", "BuddhistMonument", ""),
    ("tiered", "Temple", "aat:300004829"), ("pagoda", "Temple", "aat:300004829"),
    ("bell-shaped", "Temple", "aat:300446671"), ("śikhara", "Temple", "aat:300446671"), ("shikhara", "Temple", "aat:300446671"),
    ("dome", "Temple", "aat:300001285"),
    ("temple", "Temple", ""), ("shrine", "Temple", ""),
    ("sataḥ", "Sattal", ""), ("sattal", "Sattal", ""),
    ("phalcā", "Pati", ""), ("phalca", "Pati", ""), ("pati", "Pati", ""),
    ("dharmaśālā", "Dharmashala", ""), ("dharmasala", "Dharmashala", ""),
    ("hiti", "DhungeDhara", ""), ("dhārā", "DhungeDhara", ""), ("dhunge", "DhungeDhara", ""),
    ("pokhari", "Pokhari", ""),
    ("pillar", "ArchitecturalStructure", ""),
    ("freestanding", "ArchitecturalStructure", ""),
]
STYLE_NOTE = {"aat:300446671": "Bell-shaped (ghaṇṭa) mapped to Shikhara as closest enum value; review"}


def map_type(mtype):
    classes, styles, notes = [], [], []
    for part in [p.strip().lower() for p in re.split(r",(?![^()]*\))", mtype or "") if p.strip()]:
        for kw, cls, style in TYPE_MAP:
            if kw in part:
                if cls not in classes: classes.append(cls)
                if style and style not in styles:
                    styles.append(style)
                    if style in STYLE_NOTE: notes.append(STYLE_NOTE[style])
                break
    return "|".join(classes), "|".join(styles), "; ".join(notes)


def condition_types(assess):
    if not assess:
        return ""
    flat = re.sub(r"\([^)]*\)", "", assess)
    out = []
    for tok in [t.strip() for t in flat.split(",") if t.strip()]:
        low = tok.lower()
        if low.startswith("good"): v = "Good"
        elif low.startswith(("restored", "repaired", "rebuilt")): v = "Restored"
        elif low.startswith("heavily"): v = "Ruined"
        elif low.startswith(("slightly", "surface", "moderately", "partly")): v = "Damaged"
        else: continue
        if v not in out: out.append(v)
    return "|".join(out)


def split_sentences(text):
    """Split on full stops, but not after initials ('D. Sharma') or 'p.'; DANAM text often lacks a space after '.'"""
    out, start = [], 0
    for m in re.finditer(r"\.(?=\s+[A-Z\[]|[A-Z\[])", text):
        chunk = text[start:m.start()]
        if chunk.count("(") > chunk.count(")"):      # inside a parenthetical citation: never split
            continue
        before = chunk.split()
        last = re.sub(r"^\W+", "", before[-1]) if before else ""
        if re.fullmatch(r"[A-Z]", last) or last.lower() in ("p", "pp", "ca", "c", "no", "vs", "ed", "i.e", "e.g"):
            continue
        out.append(text[start:m.end()].strip()); start = m.end()
    if text[start:].strip():
        out.append(text[start:].strip())
    return out


def citations(sentence):
    out = []
    for m in re.finditer(r"\(([^()]*)\)", sentence):
        body = m.group(1)
        if ERA_PAREN_RE.match(body):
            continue
        rest = re.sub(r"[A-Z]{3}\d{4}(-\d{3})?", "", body)      # drop monument / object codes
        if re.search(r"\d{4}|local resident|\bp\. ?\d|folio", rest):
            out.append(m.group(0))
    return out


def main():
    parser = argparse.ArgumentParser(
        description="DANAM Ingestion & Staging Candidate Preparation Utility",
        epilog="Examples:\n"
               "  python prepare.py --input data_collection/data/exports/monuments.csv --outdir staging\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to input DANAM scrape export CSV")
    parser.add_argument("--outdir", "-o", default="staging", help="Output directory for staging files (default: 'staging')")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[!] Error: Input file '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.outdir, exist_ok=True)
    print(f"[*] Reading DANAM records from '{args.input}'...")

    try:
        with open(args.input, newline="", encoding="utf-8-sig") as f:
            rd = csv.DictReader(f)
            rows = list(rd)
            cols = rd.fieldnames or []
    except Exception as e:
        print(f"[!] Error reading CSV '{args.input}': {e}", file=sys.stderr)
        sys.exit(1)

    if not cols:
        print(f"[!] Error: CSV file '{args.input}' contains no header or is empty.", file=sys.stderr)
        sys.exit(1)

    derived = ["danam_code", "name_ne", "ontology_class", "aat_style", "condition_types", "mapping_notes"]
    skipped, kept, ev_c, ob_c = [], [], [], []

    print(f"[*] Processing {len(rows)} records for ontology classification & candidate extraction...")
    for r in rows:
        if not (r.get("monument_name") or "").strip() and not (r.get("description_en") or "").strip():
            skipped.append({
                "resource_id": r.get("resource_id"),
                "url": r.get("url"),
                "scraped_at": r.get("scraped_at"),
                "status": r.get("status"),
                "reason": "no monument_name and no description_en (empty record)"
            })
            continue

        ne = r.get("name_devanagari") or ""
        code_m = re.search(r"([A-Z]{3}\d{4})\s*$", ne.strip())
        code = code_m.group(1) if code_m else ""
        name_ne = re.sub(r"\s*(\|\||।।)\s*[A-Z]{3}\d{4}\s*$", "", ne).strip()
        cls, style, note = map_type(r.get("monument_type"))
        d = dict(r)
        d.update(
            danam_code=code,
            name_ne=name_ne,
            ontology_class=cls,
            aat_style=style,
            condition_types=condition_types(r.get("monument_assessment")),
            mapping_notes=note
        )
        kept.append(d)

        desc = r.get("description_en") or ""
        base = {"resource_id": r["resource_id"], "monument_name": r["monument_name"], "danam_code": code}
        for i, s in enumerate(split_sentences(desc)):
            dates = find_dates(s)
            ids = OBJ_ID_RE.findall(s)
            if dates or EVENT_WORDS.search(s):
                ev_c.append({
                    **base,
                    "sentence_index": i,
                    "text": s,
                    "dates": dates,
                    "citations": citations(s),
                    "object_ids": ids,
                    "other_monument_codes": [c for c in MON_CODE_RE.findall(s) if c != code]
                })
            for oid in ids:
                ob_c.append({
                    **base,
                    "sentence_index": i,
                    "object_id": oid,
                    "belongs_to_this_monument": oid.startswith(code + "-") if code else None,
                    "context": s,
                    "dates": dates,
                    "citations": citations(s)
                })

    monuments_out = os.path.join(args.outdir, "monuments.csv")
    with open(monuments_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols + derived)
        w.writeheader()
        w.writerows(kept)

    skipped_out = os.path.join(args.outdir, "skipped_rows.csv")
    with open(skipped_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["resource_id", "url", "scraped_at", "status", "reason"])
        w.writeheader()
        w.writerows(skipped)

    for name, data in (("event_candidates.jsonl", ev_c), ("object_candidates.jsonl", ob_c)):
        out_path = os.path.join(args.outdir, name)
        with open(out_path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\n[+] Staging preparation complete in '{args.outdir}':")
    print(f"    - Monuments Kept:        {len(kept):,}")
    print(f"    - Dead/Empty Skipped:    {len(skipped):,}")
    print(f"    - Event Candidates:      {len(ev_c):,}")
    print(f"    - Object Candidates:     {len(ob_c):,}")


if __name__ == "__main__":
    main()
