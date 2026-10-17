#!/usr/bin/env python3
"""Step 3: Validate monuments.csv / events.csv / objects.csv.

Usage:
  python scripts/validate.py --dir <staging_dir>

Exit code:
  0: All critical checks passed (warnings/info may be present)
  1: One or more ERROR conditions detected
"""
import argparse
import csv
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
from heritage_dates import ERA_RE, CE_RE, era_to_ce, MONTHS

csv.field_size_limit(10**9)
EVENT_COLS = ["resource_id", "monument_name", "event_index", "event_name", "event_description",
              "date_bce_ce", "period", "year_ss_ns_vs", "nepali_month", "paksha", "tithi", "sources"]
EVENT_EXTRA = ["ontology_class", "evidence_text", "extraction_method", "confidence"]
OBJECT_COLS = ["resource_id", "monument_name", "object_index", "object_id", "object_name", "object_type",
               "object_material", "object_location", "date_bce_ce", "date_vs_ns"]
OBJECT_EXTRA = ["ontology_class", "evidence_text", "extraction_method", "confidence"]
PAKSHA = {"", "Śukla", "Kṛṣṇa"}
norm = lambda s: re.sub(r"\s+", " ", s or "").strip()


def read(path):
    if not os.path.exists(path):
        return [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        return rd.fieldnames or [], list(rd)


def main():
    parser = argparse.ArgumentParser(
        description="HeritageGraph Staging CSV Strict Validator",
        epilog="Examples:\n"
               "  python validate.py --dir staging\n"
               "  python validate.py --dir data_collection/data/exports\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dir", "-d", default="staging", help="Directory containing monuments.csv, events.csv, objects.csv (default: 'staging')")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"[!] Error: Staging directory '{args.dir}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Validating staging CSVs in '{args.dir}'...")
    issues = []
    add = lambda lvl, where, msg: issues.append((lvl, where, msg))

    mon_path = os.path.join(args.dir, "monuments.csv")
    if not os.path.exists(mon_path):
        add("ERROR", "monuments.csv", f"File missing in '{args.dir}'")
        mh, mons = [], []
        M = {}
    else:
        mh, mons = read(mon_path)
        M = {m["resource_id"]: m for m in mons}
        if len(M) != len(mons):
            add("ERROR", "monuments.csv", "duplicate resource_id found")

    for fname, req, extra, idx in (("events.csv", EVENT_COLS, EVENT_EXTRA, "event_index"),
                                   ("objects.csv", OBJECT_COLS, OBJECT_EXTRA, "object_index")):
        p = os.path.join(args.dir, fname)
        if not os.path.exists(p):
            add("ERROR", fname, f"File missing in '{args.dir}'")
            continue
        hdr, rows = read(p)
        if hdr[:len(req)] != req:
            add("ERROR", fname, f"first columns must be exactly {req}")
        for c in extra:
            if c not in hdr: add("WARN", fname, f"provenance column '{c}' missing")
        seen = {}
        for n, r in enumerate(rows, start=2):
            w = f"{fname}:{n}"
            m = M.get(r["resource_id"])
            if not m:
                add("ERROR", w, f"resource_id {r['resource_id']} not in monuments.csv"); continue
            if r["monument_name"] != m["monument_name"]:
                add("ERROR", w, "monument_name differs from monuments.csv (must be copied verbatim)")
            seen.setdefault(r["resource_id"], []).append(r[idx])
            ev = norm(r.get("evidence_text"))
            if ev:
                hay = norm(m.get("description_en"))
                if ev not in hay:
                    add("ERROR", w, "evidence_text is not a verbatim substring of description_en")
            elif r.get("extraction_method", "") not in ("source_table",):
                add("WARN", w, "no evidence_text (every inferred row needs one)")
            if fname == "events.csv":
                if not r["event_name"].strip(): add("ERROR", w, "empty event_name")
                if r["paksha"] not in PAKSHA: add("ERROR", w, f"paksha '{r['paksha']}' not in {sorted(PAKSHA)}")
                if r["nepali_month"] and r["nepali_month"] not in set(MONTHS.values()):
                    add("ERROR", w, f"nepali_month '{r['nepali_month']}' not canonical")
                if r["tithi"] and not (r["tithi"].isdigit() and 1 <= int(r["tithi"]) <= 15):
                    add("ERROR", w, "tithi must be 1-15 (use paksha for fortnight)")
                if r["tithi"] and not r["paksha"]: add("WARN", w, "tithi without paksha")
                era = ERA_RE.fullmatch(r["year_ss_ns_vs"].strip()) if r["year_ss_ns_vs"].strip() else None
                if r["year_ss_ns_vs"].strip() and not era:
                    add("ERROR", w, f"year_ss_ns_vs '{r['year_ss_ns_vs']}' must look like 'NS 809'")
                ce = CE_RE.fullmatch(r["date_bce_ce"].strip()) if r["date_bce_ce"].strip() else None
                if r["date_bce_ce"].strip() and not ce:
                    add("ERROR", w, f"date_bce_ce '{r['date_bce_ce']}' must look like '1689 CE' or '1300 BCE'")
                if era and ce:
                    cy = int(ce.group(1)) * (-1 if ce.group(2).upper().startswith("B") else 1)
                    month = r["nepali_month"] or None
                    exp, _ = era_to_ce(era.group(1), int(era.group(2)), month)
                    if exp is not None and abs(exp - cy) > 1:
                        add("WARN", w, f"era/CE disagree: {r['year_ss_ns_vs']} implies {exp}, row says {cy} (keep source value, make sure the mismatch is noted in event_description)")
            else:
                oid = r["object_id"]
                if not re.fullmatch(r"[A-Z]{3}\d{4}-\d{3}", oid):
                    add("ERROR", w, f"object_id '{oid}' malformed")
                elif m.get("danam_code") and not oid.startswith(m["danam_code"] + "-"):
                    add("WARN", w, f"object_id {oid} belongs to a different monument than {m['danam_code']}")
        for rid, ids in seen.items():
            if [int(i) for i in ids] != list(range(len(ids))):
                add("ERROR", fname, f"{rid}: {idx} must run 0..n-1 without gaps, got {ids}")
            declared = M[rid].get("event_count" if fname == "events.csv" else "object_count", "")
            if declared.isdigit() and int(declared) != len(ids):
                add("INFO", fname, f"{rid}: extracted {len(ids)} vs {declared} declared on the DANAM page (description text is only a subset)")

    for lvl in ("ERROR", "WARN", "INFO"):
        for l, where, msg in issues:
            if l == lvl: print(f"[{l}] {where}: {msg}")
    errs = sum(1 for i in issues if i[0] == "ERROR")
    print(f"\n{errs} error(s), {sum(1 for i in issues if i[0]=='WARN')} warning(s), {sum(1 for i in issues if i[0]=='INFO')} info")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
