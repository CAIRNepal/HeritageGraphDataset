"""Build into a scratch directory, check alignment and query answers, and log the step in docs/sync/SYNC_LOG.md.

Usage:
  python tools/sync/step_check.py --item A1 --title "drop hg:HumanMadeObject" --test tests/test_sync.py::test_a1 [--note "..."]
  python tools/sync/step_check.py --item S0 --title baseline --baseline     # first entry: records the starting point

The build uses the same inputs as release v1.0.0 (tests/conftest.py) and writes build/sync/graph.nt (never releases/ or
latest/). Alignment: tools/sync/check_alignment.py. Queries: every queries/*.rq run without its LIMIT; the row count is
compared with the previous step's (docs/sync/state.json). If a query's row count changed, nothing is recorded (exit 1).
"""
import argparse, glob, json, os, re, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "tests"))
OUT = os.path.join(REPO, "build", "sync")
STATE = os.path.join(REPO, "docs", "sync", "state.json")
LOG = os.path.join(REPO, "docs", "sync", "SYNC_LOG.md")


def query_counts(g):
    out = {}
    for p in sorted(glob.glob(os.path.join(REPO, "queries", "*.rq"))):
        text = re.sub(r"(?im)^\s*LIMIT\s+\d+\s*$", "", open(p, encoding="utf-8").read())
        out[os.path.basename(p)] = len(list(g.query(text)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--item", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--test", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--accept", default="", help="record despite changed query rows; the reason goes in the log")
    a = ap.parse_args()
    import build_kg
    from conftest import EVENTS, MONUMENTS, OBJECTS
    t = time.time()
    g, stats = build_kg.build_knowledge_graph(MONUMENTS, EVENTS, OBJECTS)
    os.makedirs(OUT, exist_ok=True)
    nt = os.path.join(OUT, "graph.nt")
    g.serialize(nt, format="nt", encoding="utf-8")
    rep = os.path.join(OUT, f"alignment_{a.item}")
    r = subprocess.run([sys.executable, os.path.join(REPO, "tools", "sync", "check_alignment.py"), "--graph", nt, "--out", rep],
                       capture_output=True, text=True, check=True)
    summ = json.loads(r.stdout.strip().splitlines()[-1])
    qc = query_counts(g)
    prev = json.load(open(STATE)) if os.path.exists(STATE) and not a.baseline else None
    changed = {q: (prev["queries"].get(q), n) for q, n in qc.items() if prev and prev["queries"].get(q) != n}
    undeclared = summ["undeclared_classes"] + summ["undeclared_properties"] + summ["undeclared_iri_values"]
    state = {"item": a.item, "triples": len(g), "shacl_results": summ["shacl_results"], "shacl_groups": summ["shacl_groups"],
             "undeclared": undeclared, "undeclared_detail": {k: summ[k] for k in ("undeclared_classes", "undeclared_properties", "undeclared_iri_values")},
             "extension_terms": summ.get("extension_terms"), "queries": qc}
    if changed and not a.accept:  # nothing is recorded: fix the query (or the change) and rerun
        print("NOT RECORDED. queries changed:", changed)
        sys.exit(1)
    if not os.path.exists(LOG):
        open(LOG, "w", encoding="utf-8").write(
            "# Sync log\n\nOne entry per change, newest last. Each entry: what changed, the test that fails before and passes "
            "after, and the counts before/after from `tools/sync/step_check.py` (scratch build in `build/sync/`, alignment by "
            "`tools/sync/check_alignment.py`, query rows without LIMIT).\n")
    def fmt(k):
        return f"{prev[k]:,} → **{state[k]:,}**" if prev else f"**{state[k]:,}**"
    lines = [f"\n## {a.item}: {a.title}\n"]
    if a.test:
        lines.append(f"- Test: `{a.test}`.")
    lines += [f"- Triples: {fmt('triples')}.", f"- SHACL results: {fmt('shacl_results')} ({state['shacl_groups']} groups).",
              f"- Undeclared terms: {fmt('undeclared')} ({state['undeclared_detail']['undeclared_classes']} classes, "
              f"{state['undeclared_detail']['undeclared_properties']} properties, {state['undeclared_detail']['undeclared_iri_values']} IRI values)."]
    if state["extension_terms"] is not None:
        lines.append(f"- Extension terms used: {state['extension_terms']}.")
    lines.append("- Queries (rows without LIMIT): " + ("unchanged." if prev and not changed else
                 (", ".join(f"`{q}` {n:,}" for q, n in qc.items()) if not prev else
                  "**changed:** " + ", ".join(f"`{q}` {b} → {n}" for q, (b, n) in changed.items()))))
    if changed and a.accept:
        lines.append(f"- Query rows changed, accepted: {a.accept}")
    if a.note:
        lines.append(f"- {a.note}")
    open(LOG, "a", encoding="utf-8").write("\n".join(lines) + "\n")
    json.dump(state, open(STATE, "w"), indent=1)
    print(json.dumps({k: state[k] for k in ("item", "triples", "shacl_results", "undeclared")}), "queries changed:", changed or "none",
          f"({time.time() - t:.0f}s)")
    sys.exit(1 if changed and not a.accept else 0)


if __name__ == "__main__":
    main()
