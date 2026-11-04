#!/usr/bin/env python3
"""Fetch the raw OSM and Wikidata responses for one pilot district into docs/pilot/<district>/raw/.

One Overpass request per district (the Lalitpur query, with the district's boundary relation), then one Wikidata
request (the Lalitpur query, with the bounding box of the district's OSM boundary, widened by 0.01 degrees). Each
request carries an identifying User-Agent; the query, the response and the retrieval time (UTC) are saved. A failed
request is reported and not retried automatically.

Usage:  python3 tools/pilot/fetch.py chitwan
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from districts import DISTRICTS, PILOT  # noqa: E402

UA = "HeritageGraphDataset-pilot/0.1 (CAIR-Nepal research; https://github.com/CAIRNepal/HeritageGraphDataset)"
OVERPASS = "https://overpass-api.de/api/interpreter"
WDQS = "https://query.wikidata.org/sparql"

OVERPASS_QUERY = """/* OSM heritage features inside {label} District (relation {rel}, admin_level 6, wikidata {qid}).
   Same tags as the Lalitpur pilot: any historic=*, any heritage=*, amenity=place_of_worship,
   building=temple|shrine|stupa. Output: tags and a centre point for ways and relations; then the district
   boundary geometry (used to filter Wikidata items and DANAM monuments to the same area). */
[out:json][timeout:180];
area(id:{area})->.d;
(
  nwr["historic"](area.d);
  nwr["heritage"](area.d);
  nwr["amenity"="place_of_worship"](area.d);
  nwr["building"~"^(temple|shrine|stupa)$"](area.d);
);
out center tags;
rel({rel});
out geom;
"""


def wikidata_query(label, qid, box):
    w, s, e, n = box
    template = open(os.path.join(PILOT, "lalitpur", "raw", "wikidata_query.rq"), encoding="utf-8").read()
    q = template.replace("Lalitpur District (Q1108338)", f"{label} District ({qid})")
    q = q.replace("(85.21..85.43 E, 27.41..27.70 N, slightly widened)",
                  f"({w:.2f}..{e:.2f} E, {s:.2f}..{n:.2f} N: the OSM boundary's bounding box widened by 0.01)")
    q = q.replace('"Point(85.21 27.41)"', f'"Point({w:.2f} {s:.2f})"').replace('"Point(85.43 27.70)"', f'"Point({e:.2f} {n:.2f})"')
    assert f"Point({w:.2f} {s:.2f})" in q and f"Point({e:.2f} {n:.2f})" in q
    return q


def post(url, field, query, accept=None):
    """POST the query with curl (uses the system's certificates); raises on an HTTP error, which is not retried."""
    import subprocess
    cmd = ["curl", "-sS", "-m", "300", "-A", UA, "--fail-with-body", "--data-urlencode", f"{field}@-", url]
    if accept:
        cmd[1:1] = ["-H", f"Accept: {accept}"]
    r = subprocess.run(cmd, input=query.encode(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"{url}: curl exit {r.returncode}: {r.stderr.decode()[:200]} {r.stdout.decode()[:300]}")
    return r.stdout


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    slug = sys.argv[1]
    d = DISTRICTS[slug]
    raw = os.path.join(PILOT, slug, "raw")
    os.makedirs(raw, exist_ok=True)

    q = OVERPASS_QUERY.format(label=d["label"], rel=d["rel"], qid=d["qid"], area=3600000000 + d["rel"])
    open(os.path.join(raw, "overpass_query.overpassql"), "w", encoding="utf-8").write(q)
    t = now()
    body = post(OVERPASS, "data", q)
    open(os.path.join(raw, "overpass_response.json"), "wb").write(body)
    open(os.path.join(raw, "overpass_retrieved_at.txt"), "w").write(f"{t} {OVERPASS}\n")
    resp = json.loads(body)
    rel = next(e for e in resp["elements"] if e["type"] == "relation" and e["id"] == d["rel"])
    pts = [(p["lon"], p["lat"]) for m in rel["members"] if m["type"] == "way" for p in m.get("geometry", [])]
    box = (min(p[0] for p in pts) - 0.01, min(p[1] for p in pts) - 0.01, max(p[0] for p in pts) + 0.01,
           max(p[1] for p in pts) + 0.01)
    print(f"overpass: {len(resp['elements']) - 1} features; boundary {rel.get('tags', {}).get('name')} "
          f"admin_level {rel.get('tags', {}).get('admin_level')} wikidata {rel.get('tags', {}).get('wikidata')}; "
          f"box {tuple(round(x, 3) for x in box)}")

    wq = wikidata_query(d["label"], d["qid"], box)
    open(os.path.join(raw, "wikidata_query.rq"), "w", encoding="utf-8").write(wq)
    t = now()
    body = post(WDQS, "query", wq, "application/sparql-results+json")
    open(os.path.join(raw, "wikidata_response.json"), "wb").write(body)
    open(os.path.join(raw, "wikidata_retrieved_at.txt"), "w").write(f"{t} {WDQS}\n")
    print(f"wikidata: {len(json.loads(body)['results']['bindings'])} items")


if __name__ == "__main__":
    main()
