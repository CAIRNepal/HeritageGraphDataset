#!/usr/bin/env python3
"""Fetch the raw OSM and Wikidata responses for one province into data_collection/collected/raw/<province>/.

Per province: ONE Overpass request (heritage features, the province's district boundaries and the province boundary),
skipped when osm_extract.py has already selected the same features from the Geofabrik extract, and Wikidata
requests for the province boundary's bounding box in tiles. Each request carries an
identifying User-Agent and is sent only when the Overpass server reports a free slot; a failed request is reported
and not retried. The query, the response (gzipped) and the retrieval time (UTC) are saved.

Usage:  python3 tools/collect/fetch.py bagmati
        python3 tools/collect/fetch.py --no-coordinates   (national: Wikidata items without coordinates)
"""
import gzip
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from provinces import OUT, PROVINCES  # noqa: E402

UA = "HeritageGraphDataset-collect/0.1 (CAIR-Nepal research; https://github.com/CAIRNepal/HeritageGraphDataset)"
OVERPASS = "https://overpass-api.de/api/interpreter"
STATUS = "https://overpass-api.de/api/status"
WDQS = "https://query.wikidata.org/sparql"
TILE = 0.5  # degrees

# Tangible heritage in OSM. historic=*, heritage=* and ruins=* are heritage by tagging; places of worship, monasteries
# and religious buildings are collected because most Nepalese temples and monasteries carry no historic tag (build.py
# marks which is which); museums and attractions; named religious compounds; and water architecture named as such
# (stone spouts hiti / dhara, wells inar / kuwa, ponds pokhari), which is usually historic. All tags are kept.
OVERPASS_QUERY = """/* Tangible heritage in {label} Province, Nepal (relation {rel}, admin_level 4, wikidata {qid}).
   Features: historic=*, heritage=*, ruins=*, amenity=place_of_worship|monastery,
   building=temple|shrine|stupa|monastery|pagoda|palace|church|mosque|gurdwara|cathedral|chapel,
   tourism=museum|attraction, landuse=religious (named), and water architecture named hiti / dhara (drinking water),
   inar / kuwa (wells) or pokhari (ponds). Output: tags and a centre point; then the province's district boundaries
   (admin_level 6) and the province boundary, with geometry. */
[out:json][timeout:900][maxsize:2000000000];
area(id:{area})->.p;
(
  nwr["historic"](area.p);
  nwr["heritage"](area.p);
  nwr["ruins"](area.p);
  nwr["amenity"~"^(place_of_worship|monastery)$"](area.p);
  nwr["building"~"^(temple|shrine|stupa|monastery|pagoda|palace|church|mosque|gurdwara|cathedral|chapel)$"](area.p);
  nwr["tourism"~"^(museum|attraction)$"](area.p);
  nwr["landuse"="religious"]["name"](area.p);
  nwr["amenity"="drinking_water"]["name"~"hiti|hity|dhara|धारा|हिटी|हिति",i](area.p);
  nwr["man_made"="water_well"]["name"~"inar|inaar|kuwa|इनार|कुवा",i](area.p);
  nwr["natural"="water"]["name"~"pokhari|pokhri|पोखरी",i](area.p);
);
out center tags;
rel(area.p)["boundary"="administrative"]["admin_level"="6"];
out geom;
rel({rel});
out geom;
"""

WIKIDATA_QUERY = """# Tangible heritage in {label} Province, Nepal ({qid}): items with coordinates in the province boundary's bounding
# box, one tile of it ({w:.2f}..{e:.2f} E, {s:.2f}..{n:.2f} N); the polygon is applied in build.py.
# Kept if the item is (via P31/P279*) a temple Q44539, stupa Q180987, monument Q4989906, heritage site Q358, Buddhist
# monastery Q160742, archaeological site Q839954, fort Q57821, palace Q16560, museum Q33506, place of worship Q1370598,
# religious building Q24398318, shrine Q697295 or ruins Q109607, or has any heritage designation (P1435).
# Fields: labels (en, ne), description, classes, heritage designation, religion P140, architectural style P149,
# dedicated to P825, material P186, height P2048, inception P571, image P18, Commons category P373, GeoNames ID P1566,
# OSM node/way/relation IDs, located in P131, English and Nepali Wikipedia articles, number of sitelinks.
SELECT ?item ?itemLabel ?label_ne ?description ?coord
       (GROUP_CONCAT(DISTINCT ?clsLabel; separator="; ") AS ?classes)
       (GROUP_CONCAT(DISTINCT ?heritageLabel; separator="; ") AS ?heritage)
       (SAMPLE(?p131) AS ?p131) (SAMPLE(?image) AS ?image) (SAMPLE(?inception) AS ?inception)
       (SAMPLE(?commons) AS ?commons) (SAMPLE(?osmNode) AS ?osmNode) (SAMPLE(?osmWay) AS ?osmWay)
       (SAMPLE(?osmRel) AS ?osmRel) (SAMPLE(?sitelinks) AS ?sitelinks)
       (GROUP_CONCAT(DISTINCT ?religionLabel; separator="; ") AS ?religion)
       (GROUP_CONCAT(DISTINCT ?styleLabel; separator="; ") AS ?style)
       (GROUP_CONCAT(DISTINCT ?dedicatedLabel; separator="; ") AS ?dedicated_to)
       (GROUP_CONCAT(DISTINCT ?materialLabel; separator="; ") AS ?material)
       (SAMPLE(?height) AS ?height) (SAMPLE(?geonames) AS ?geonames) (SAMPLE(?enwiki) AS ?enwiki) (SAMPLE(?newiki) AS ?newiki)
WHERE {{
  SERVICE wikibase:box {{
    ?item wdt:P625 ?coord .
    bd:serviceParam wikibase:cornerSouthWest "Point({w:.2f} {s:.2f})"^^geo:wktLiteral .
    bd:serviceParam wikibase:cornerNorthEast "Point({e:.2f} {n:.2f})"^^geo:wktLiteral .
  }}
  FILTER (EXISTS {{ ?item wdt:P31/wdt:P279* ?cls .
                    VALUES ?cls {{ wd:Q44539 wd:Q180987 wd:Q4989906 wd:Q358 wd:Q160742 wd:Q839954 wd:Q57821 wd:Q16560
                                  wd:Q33506 wd:Q1370598 wd:Q24398318 wd:Q697295 wd:Q109607 }} }}
          || EXISTS {{ ?item wdt:P1435 ?anyDesignation }})
  OPTIONAL {{ ?item wdt:P31 ?c31 . ?c31 rdfs:label ?clsLabel FILTER(LANG(?clsLabel) = "en") }}
  OPTIONAL {{ ?item rdfs:label ?itemLabel FILTER(LANG(?itemLabel) = "en") }}
  OPTIONAL {{ ?item rdfs:label ?label_ne FILTER(LANG(?label_ne) = "ne") }}
  OPTIONAL {{ ?item schema:description ?description FILTER(LANG(?description) = "en") }}
  OPTIONAL {{ ?item wdt:P131 ?p131 }}
  OPTIONAL {{ ?item wdt:P18 ?image }}
  OPTIONAL {{ ?item wdt:P1435 ?h . ?h rdfs:label ?heritageLabel FILTER(LANG(?heritageLabel) = "en") }}
  OPTIONAL {{ ?item wdt:P571 ?inception }}
  OPTIONAL {{ ?item wdt:P373 ?commons }}
  OPTIONAL {{ ?item wdt:P11693 ?osmNode }}
  OPTIONAL {{ ?item wdt:P10689 ?osmWay }}
  OPTIONAL {{ ?item wdt:P402 ?osmRel }}
  OPTIONAL {{ ?item wikibase:sitelinks ?sitelinks }}
  OPTIONAL {{ ?item wdt:P140 ?rl . ?rl rdfs:label ?religionLabel FILTER(LANG(?religionLabel) = "en") }}
  OPTIONAL {{ ?item wdt:P149 ?st . ?st rdfs:label ?styleLabel FILTER(LANG(?styleLabel) = "en") }}
  OPTIONAL {{ ?item wdt:P825 ?dd . ?dd rdfs:label ?dedicatedLabel FILTER(LANG(?dedicatedLabel) = "en") }}
  OPTIONAL {{ ?item wdt:P186 ?mt . ?mt rdfs:label ?materialLabel FILTER(LANG(?materialLabel) = "en") }}
  OPTIONAL {{ ?item wdt:P2048 ?height }}
  OPTIONAL {{ ?item wdt:P1566 ?geonames }}
  OPTIONAL {{ ?enwiki schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> }}
  OPTIONAL {{ ?newiki schema:about ?item ; schema:isPartOf <https://ne.wikipedia.org/> }}
}}
GROUP BY ?item ?itemLabel ?label_ne ?description ?coord
"""


def no_coordinates_query():
    """Items of the same classes with country Nepal (P17) and no coordinates, which no box query returns; their P131
    chain (located in, transitively) lets build.py place them in a district where the chain reaches one."""
    q = WIKIDATA_QUERY.format(label="", qid="", w=0, s=0, e=0, n=0)
    q = q[q.index("# Kept if"):]
    box = q[q.index("  SERVICE wikibase:box {"):q.index("  FILTER (EXISTS")]
    q = q.replace(box, "  ?item wdt:P17 wd:Q837 .\n  FILTER NOT EXISTS { ?item wdt:P625 [] }\n"
                       "  OPTIONAL { ?item wdt:P131+ ?anc }\n")
    q = q.replace("SELECT ?item ?itemLabel ?label_ne ?description ?coord",
                  "SELECT ?item ?itemLabel ?label_ne ?description ?coord\n"
                  "       (GROUP_CONCAT(DISTINCT ?anc; separator=\" \") AS ?p131_chain)")
    return ("# Tangible heritage in Nepal without coordinates: items with country Nepal (Q837) and no P625, with their\n"
            "# P131 chain (transitive 'located in').\n" + q)


def no_coordinates():
    raw = os.path.join(OUT, "raw", "wikidata_no_coordinates")
    os.makedirs(raw, exist_ok=True)
    q = no_coordinates_query()
    open(os.path.join(raw, "query.rq"), "w", encoding="utf-8").write(q)
    t = now()
    body = post(WDQS, "query", q, "application/sparql-results+json")
    n = len(json.loads(body)["results"]["bindings"])
    with gzip.open(os.path.join(raw, "response.json.gz"), "wb") as f:
        f.write(body)
    open(os.path.join(raw, "retrieved_at.txt"), "w").write(f"{t} {WDQS}\n")
    print(f"wikidata without coordinates: {n} items")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def post(url, field, query, accept=None):
    cmd = ["curl", "-sS", "-m", "1000", "-A", UA, "--fail-with-body", "--data-urlencode", f"{field}@-", url]
    if accept:
        cmd[1:1] = ["-H", f"Accept: {accept}"]
    r = subprocess.run(cmd, input=query.encode(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"{url}: curl exit {r.returncode}: {r.stderr.decode()[:300]} {r.stdout.decode()[:300]}")
    return r.stdout


def wait_for_slot(max_wait=3600):
    t0 = time.time()
    while True:
        st = subprocess.run(["curl", "-s", "-m", "30", "-A", UA, STATUS], capture_output=True, text=True).stdout
        if "slots available now" in st:
            return
        if time.time() - t0 > max_wait:
            raise RuntimeError("no free Overpass slot within the waiting time")
        time.sleep(120)


def main():
    slug = sys.argv[1]
    if slug == "--no-coordinates":
        return no_coordinates()
    p = PROVINCES[slug]
    raw = os.path.join(OUT, "raw", slug)
    os.makedirs(raw, exist_ok=True)

    # osm_extract.py writes osm_response.json.gz from the Geofabrik extract; Overpass is then not asked
    osm = os.path.join(raw, "osm_response.json.gz")
    if not os.path.exists(osm) and not os.path.exists(os.path.join(raw, "overpass_response.json.gz")):
        q = OVERPASS_QUERY.format(label=p["label"], rel=p["rel"], qid=p["qid"], area=3600000000 + p["rel"])
        open(os.path.join(raw, "overpass_query.overpassql"), "w", encoding="utf-8").write(q)
        wait_for_slot()
        t = now()
        body = post(OVERPASS, "data", q)
        json.loads(body)  # must be valid JSON before it is saved
        with gzip.open(os.path.join(raw, "overpass_response.json.gz"), "wb") as f:
            f.write(body)
        open(os.path.join(raw, "overpass_retrieved_at.txt"), "w").write(f"{t} {OVERPASS}\n")
    resp = json.load(gzip.open(osm if os.path.exists(osm) else os.path.join(raw, "overpass_response.json.gz")))
    rel = next(e for e in resp["elements"] if e["type"] == "relation" and e["id"] == p["rel"])
    pts = [(g["lon"], g["lat"]) for m in rel["members"] if m["type"] == "way" for g in m.get("geometry", [])]
    w, s = min(x for x, _ in pts) - 0.01, min(y for _, y in pts) - 0.01
    e, n = max(x for x, _ in pts) + 0.01, max(y for _, y in pts) + 0.01
    districts = [x for x in resp["elements"] if x["type"] == "relation" and x.get("tags", {}).get("admin_level") == "6"]
    print(f"{slug}: osm {len(resp['elements']) - len(districts) - 1} features, {len(districts)} district relations")

    # Wikidata: the bounding box in tiles of TILE degrees (one province-wide query would exceed the 60 s limit),
    # one request per tile, a short pause between them; each tile's query, response and time are saved.
    import math
    tiles = [(x, y) for x in range(math.floor(w / TILE), math.ceil(e / TILE)) for y in range(math.floor(s / TILE), math.ceil(n / TILE))]
    total = 0
    for i, (tx, ty) in enumerate(tiles):
        tw, ts, te, tn = max(w, tx * TILE), max(s, ty * TILE), min(e, (tx + 1) * TILE), min(n, (ty + 1) * TILE)
        if tw >= te or ts >= tn:
            continue
        base = os.path.join(raw, f"wikidata_tile{i:02d}")
        if not os.path.exists(base + "_response.json.gz"):
            wq = WIKIDATA_QUERY.format(label=p["label"], qid=p["qid"], w=tw, s=ts, e=te, n=tn)
            open(base + "_query.rq", "w", encoding="utf-8").write(wq)
            t = now()
            body = post(WDQS, "query", wq, "application/sparql-results+json")
            json.loads(body)
            with gzip.open(base + "_response.json.gz", "wb") as f:
                f.write(body)
            open(base + "_retrieved_at.txt", "w").write(f"{t} {WDQS}\n")
            time.sleep(5)
        total += len(json.load(gzip.open(base + "_response.json.gz"))["results"]["bindings"])
    print(f"{slug}: wikidata {total} rows from {len(tiles)} tiles")

if __name__ == "__main__":
    main()
