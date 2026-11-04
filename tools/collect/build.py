#!/usr/bin/env python3
"""Build the district-wise collection from the saved raw responses (no network access).

For each province (data_collection/collected/raw/<province>/, see fetch.py): the province's districts come from the OSM
district boundaries (admin_level 6) in the same response; every OSM feature, Wikidata item and DANAM monument is
assigned to the district whose boundary contains it. Quality checks are recorded per row in `quality_flags`; nothing
is corrected or merged. Output:

  data_collection/collected/<province>/<district>/osm.csv, wikidata.csv, danam.csv
  data_collection/collected/index.csv        one row per district: counts per source and category
  data_collection/collected/QUALITY.md       what was collected, the checks and their results, licences

Usage:  python3 tools/collect/build.py
"""
import csv
import glob
import gzip
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "pilot")]
from geo import inside  # noqa: E402
from match import fold, haversine, norm, recent_signals, rings_from_relation  # noqa: E402  (tools/pilot)
from provinces import OUT, PROVINCES, REPO  # noqa: E402

KNOWN_RELIGIONS = {"hindu", "buddhist", "christian", "muslim", "sikh", "jain", "bahai", "kirant", "kirat", "bon",
                   "animist", "multifaith", "hindu;buddhist", "buddhist;hindu"}
DUP_DIST = 30.0  # metres: a node and a way with the same name this close are probably one feature mapped twice

OSM_COLS = ["osm_id", "url", "name", "name_en", "name_ne", "lat", "lon", "category", "heritage_tagged", "historic",
            "heritage", "amenity", "building", "religion", "denomination", "tourism", "wikidata", "start_date",
            "recent_looking", "recent_signals", "duplicate_group", "quality_flags", "tags_json"]
WD_COLS = ["qid", "url", "label_en", "label_ne", "description", "lat", "lon", "classes", "heritage_designation",
           "inception", "religion", "architectural_style", "dedicated_to", "material", "height_m", "image",
           "commons_category", "wikipedia_en", "wikipedia_ne", "geonames_id", "osm_ids", "sitelinks", "p131",
           "quality_flags"]
GN_COLS = ["geonameid", "url", "name", "asciiname", "alternatenames", "lat", "lon", "feature_code", "feature_meaning",
           "elevation", "modification_date", "quality_flags"]
# GeoNames feature codes kept (class S): heritage and religious sites
FEATURE_CODES = {"TMPL": "temple", "PGDA": "pagoda", "MSTY": "monastery", "SHRN": "shrine", "CH": "church",
                 "MSQE": "mosque", "RLG": "religious site", "CTRR": "religious center", "MNMT": "monument",
                 "RUIN": "ruin", "HSTS": "historical site", "ANS": "archaeological/prehistoric site", "CSTL": "castle",
                 "FT": "fort", "PAL": "palace", "MUS": "museum", "TMB": "tomb", "WALLA": "ancient wall"}
DN_COLS = ["resource_id", "danam_code", "url", "monument_name", "anglicized_name", "name_ne", "ontology_class",
           "monument_type", "religion", "main_deity", "condition_types", "events", "objects", "lat", "lon",
           "danam_province", "danam_district", "danam_municipality", "quality_flags"]


def slug(s):
    """Folder name: the district name as written, lower case, ASCII letters only (not match.py's fold, which merges
    transliteration variants such as ch/c)."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "unknown"


def district_name(t):
    n = t.get("name:en") or t.get("name") or ""
    n = re.sub(r"\s*\(nepal\)$", "", n, flags=re.I)
    return re.sub(r"\s+district$", "", n, flags=re.I).strip()


def centroid(rings):
    pts = [p for r in rings for p in r]
    return sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts)


CATEGORIES = ["historic", "museum", "monastery", "place_of_worship", "religious_building", "religious_compound",
              "water_spout", "well", "pond", "attraction"]


def category(t):
    """One category per OSM feature, first match: heritage by tagging, then what the feature is."""
    if "historic" in t or "heritage" in t or "ruins" in t:
        return "historic"
    if t.get("tourism") == "museum":
        return "museum"
    if t.get("amenity") == "monastery" or t.get("building") == "monastery":
        return "monastery"
    if t.get("amenity") == "place_of_worship":
        return "place_of_worship"
    if t.get("building") in ("temple", "shrine", "stupa", "pagoda", "palace", "church", "mosque", "gurdwara",
                             "cathedral", "chapel"):
        return "religious_building"
    if t.get("landuse") == "religious":
        return "religious_compound"
    if t.get("amenity") == "drinking_water":
        return "water_spout"
    if t.get("man_made") == "water_well":
        return "well"
    if t.get("natural") == "water":
        return "pond"
    return "attraction"


def write(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def wd_row(v, lat, lon, fl):
    """One wikidata.csv row from a query result binding."""
    qid = v["item"].rsplit("/", 1)[-1]
    osm_ids = "; ".join(x for x in (f"node/{v['osmNode']}" if v.get("osmNode") else "",
                                    f"way/{v['osmWay']}" if v.get("osmWay") else "",
                                    f"relation/{v['osmRel']}" if v.get("osmRel") else "") if x)
    return {"qid": qid, "url": v["item"], "label_en": v.get("itemLabel", ""),
                       "label_ne": v.get("label_ne", ""), "description": v.get("description", ""), "lat": lat,
                       "lon": lon, "classes": v.get("classes", ""), "heritage_designation": v.get("heritage", ""),
                       "inception": v.get("inception", "")[:10], "image": v.get("image", ""),
                       "commons_category": v.get("commons", ""), "osm_ids": osm_ids,
                       "sitelinks": v.get("sitelinks", ""), "p131": v.get("p131", "").rsplit("/", 1)[-1],
                       "religion": v.get("religion", ""), "architectural_style": v.get("style", ""),
                       "dedicated_to": v.get("dedicated_to", ""), "material": v.get("material", ""),
                       "height_m": v.get("height", ""), "geonames_id": v.get("geonames", ""),
                       "wikipedia_en": v.get("enwiki", ""), "wikipedia_ne": v.get("newiki", ""),
                       "quality_flags": "; ".join(fl)}


def main():
    danam = [r for r in csv.DictReader(open(os.path.join(REPO, "staging", "monuments.csv"), encoding="utf-8-sig"))
             if r["coordinates_lat"].strip()]
    danam_seen = set()
    import zipfile
    gpath = os.path.join(OUT, "raw", "geonames", "NP.zip")
    geonames = []
    if os.path.exists(gpath):
        for line in zipfile.ZipFile(gpath).read("NP.txt").decode("utf-8").splitlines():
            r = line.split("\t")
            if r[6] == "S" and r[7] in FEATURE_CODES:
                geonames.append(r)
    gn_seen = set()
    exports = os.path.join(REPO, "data_collection", "data", "exports")
    n_events = Counter(r["resource_id"] for r in csv.DictReader(open(os.path.join(exports, "events.csv"), encoding="utf-8-sig")))
    n_objects = Counter(r["resource_id"] for r in csv.DictReader(open(os.path.join(exports, "objects.csv"), encoding="utf-8-sig")))
    index, folders, flags_total, notes = [], [], Counter(), []
    per_province = {}
    retrieved = {}

    # Wikidata items without coordinates (fetch.py --no-coordinates), placed by the district QIDs in their P131 chain
    nc_path = os.path.join(OUT, "raw", "wikidata_no_coordinates", "response.json.gz")
    nocoord = ([{k: x["value"] for k, x in b.items()} for b in json.load(gzip.open(nc_path))["results"]["bindings"]]
               if os.path.exists(nc_path) else [])
    nc_placed = set()

    for pslug, p in PROVINCES.items():
        raw = os.path.join(OUT, "raw", pslug)
        # OSM: the Geofabrik-extract selection (osm_extract.py) if present, else an Overpass response (fetch.py)
        osm_src = next((k for k in ("osm", "overpass") if os.path.exists(os.path.join(raw, f"{k}_response.json.gz"))), None)
        if not osm_src:
            notes.append(f"{p['label']}: no OSM response yet; skipped")
            continue
        retrieved[pslug] = {k: open(os.path.join(raw, f"{k}_retrieved_at.txt")).read().split()[0]
                            for k in (osm_src, "wikidata") if os.path.exists(os.path.join(raw, f"{k}_retrieved_at.txt"))}
        retrieved[pslug]["overpass"] = retrieved[pslug].pop(osm_src, "")
        wt = sorted(open(f).read().split()[0] for f in glob.glob(os.path.join(raw, "wikidata_tile*_retrieved_at.txt")))
        if wt:
            retrieved[pslug]["wikidata"] = wt[0] if wt[0][:10] == wt[-1][:10] else f"{wt[0]}..{wt[-1]}"
        resp = json.load(gzip.open(os.path.join(raw, f"{osm_src}_response.json.gz")))
        prov_rel = next(e for e in resp["elements"] if e["type"] == "relation" and e["id"] == p["rel"])
        prov_rings = rings_from_relation(prov_rel)
        districts = {}
        for e in resp["elements"]:
            if e["type"] != "relation" or e.get("tags", {}).get("admin_level") != "6" or "members" not in e:
                continue
            try:
                rings = rings_from_relation(e)
            except ValueError:
                notes.append(f"{p['label']}: district relation {e['id']} ({district_name(e['tags'])}) has an open "
                             "boundary; skipped")
                continue
            if inside(*centroid(rings), prov_rings):  # neighbours touching the province are returned too
                districts[e["id"]] = {"name": district_name(e["tags"]), "name_ne": e["tags"].get("name", ""),
                                      "wikidata": e["tags"].get("wikidata", ""), "rings": rings}
        osm_by = defaultdict(list)
        feats = [e for e in resp["elements"] if not (e["type"] == "relation" and "members" in e
                                                       and e.get("tags", {}).get("boundary") == "administrative")]

        def district_of(lon, lat):
            return next((rid for rid, d in districts.items() if inside(lon, lat, d["rings"])), None)

        rows = []
        for e in feats:
            t = e.get("tags", {})
            lat, lon = (e["lat"], e["lon"]) if e["type"] == "node" else (e["center"]["lat"], e["center"]["lon"])
            fl = []
            name = t.get("name", "")
            if not (name or t.get("name:en") or t.get("name:ne")):
                fl.append("no_name")
            rel_v = t.get("religion", "")
            if rel_v and rel_v not in KNOWN_RELIGIONS:
                fl.append(f"unusual_religion:{rel_v}")
            if rel_v == "bahai" and re.search(r"bah[aāi]|बहा", " ".join(t.get(k, "") for k in ("name", "name:en")), re.I):
                fl.append("bahai_probably_bahi_monastery")
            did = district_of(lon, lat)
            if did is None:
                fl.append("no_district")
            rs = recent_signals({"tags": t})
            rows.append({"_did": did, "_e": e, "osm_id": f"{e['type']}/{e['id']}",
                         "url": f"https://www.openstreetmap.org/{e['type']}/{e['id']}", "name": name,
                         "name_en": t.get("name:en", ""), "name_ne": t.get("name:ne", ""), "lat": lat, "lon": lon,
                         "category": category(t), "heritage_tagged": "yes" if ("historic" in t or "heritage" in t or "ruins" in t) else "",
                         "historic": t.get("historic", ""), "heritage": t.get("heritage", ""), "amenity": t.get("amenity", ""),
                         "building": t.get("building", ""), "religion": rel_v, "denomination": t.get("denomination", ""),
                         "tourism": t.get("tourism", ""), "wikidata": t.get("wikidata", ""), "start_date": t.get("start_date", ""),
                         "recent_looking": "yes" if rs else "", "recent_signals": "; ".join(rs), "duplicate_group": "",
                         "_fl": fl, "tags_json": json.dumps(t, ensure_ascii=False, sort_keys=True)})
        # possible duplicates: same normalised name, within DUP_DIST, different elements
        by_name = defaultdict(list)
        for r in rows:
            k = norm(r["name_en"] or r["name"]) or None
            if k:
                by_name[k].append(r)
        g = 0
        for k, rs in by_name.items():
            if len(rs) < 2:
                continue
            for i, a in enumerate(rs):
                for b in rs[i + 1:]:
                    if haversine(a["lat"], a["lon"], b["lat"], b["lon"]) <= DUP_DIST:
                        grp = a["duplicate_group"] or b["duplicate_group"]
                        if not grp:
                            g += 1
                            grp = f"{pslug}-{g}"
                        a["duplicate_group"] = b["duplicate_group"] = grp
        for r in rows:
            if r["duplicate_group"]:
                r["_fl"].append("possible_duplicate")
            r["quality_flags"] = "; ".join(r["_fl"])
            flags_total.update(f.split(":")[0] for f in r["_fl"])
            osm_by[r["_did"]].append(r)

        # Wikidata
        wd_by = defaultdict(list)
        wd_outside, wd_seen = 0, set()
        for wpath in sorted(glob.glob(os.path.join(raw, "wikidata_tile*_response.json.gz"))):
            for b in json.load(gzip.open(wpath))["results"]["bindings"]:
                v = {k: x["value"] for k, x in b.items()}
                m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", v.get("coord", ""))
                if not m:
                    continue
                lon, lat = float(m.group(1)), float(m.group(2))
                if v["item"] in wd_seen:  # an item on a tile edge is returned twice
                    continue
                wd_seen.add(v["item"])
                if not inside(lon, lat, prov_rings):
                    wd_outside += 1
                    continue
                fl = []
                if not v.get("itemLabel"):
                    fl.append("no_english_label")
                if not v.get("classes"):
                    fl.append("no_class")
                if (re.search(r"\b(city|town|village|municipality|district|rural municipality|metropolitan)\b",
                              v.get("classes", ""), re.I)
                        and not re.search(r"archaeological|ruins", v.get("classes", ""), re.I)):
                    fl.append("settlement_not_a_structure")
                did = district_of(lon, lat)
                if did is None:
                    fl.append("no_district")
                flags_total.update(fl)
                wd_by[did].append(wd_row(v, lat, lon, fl))

        by_qid = {d["wikidata"]: rid for rid, d in districts.items() if d["wikidata"]}
        for v in nocoord:
            hits = {by_qid[q.rsplit("/", 1)[-1]] for q in v.get("p131_chain", "").split() if q.rsplit("/", 1)[-1] in by_qid}
            if len(hits) == 1 and v["item"] not in nc_placed:
                nc_placed.add(v["item"])
                fl = ["no_coordinates_district_from_p131"] + ([] if v.get("itemLabel") else ["no_english_label"])
                flags_total.update(fl)
                wd_by[hits.pop()].append(wd_row(v, "", "", fl))

        # DANAM (existing crawl, staging/monuments.csv; not re-collected)
        dn_by = defaultdict(list)
        for r in danam:
            lat, lon = float(r["coordinates_lat"]), float(r["coordinates_lon"])
            if r["resource_id"] in danam_seen or not inside(lon, lat, prov_rings):
                continue
            danam_seen.add(r["resource_id"])
            did = district_of(lon, lat)
            fl = []
            if did is None:
                fl.append("no_district")
            elif r["district"].strip() and fold(r["district"]).split()[0] not in fold(districts[did]["name"]):
                fl.append(f"danam_district_differs:{r['district'].strip()}")
            flags_total.update(f.split(":")[0] for f in fl)
            dn_by[did].append({"resource_id": r["resource_id"], "danam_code": r["danam_code"], "url": r["url"],
                               "monument_name": r["monument_name"], "anglicized_name": r["anglicized_name"],
                               "name_ne": r["name_ne"], "ontology_class": r["ontology_class"],
                               "monument_type": r["monument_type"], "religion": r["religion"],
                               "main_deity": r["main_deity"], "condition_types": r["condition_types"],
                               "events": n_events[r["resource_id"]], "objects": n_objects[r["resource_id"]], "lat": lat,
                               "lon": lon, "danam_province": r["province"], "danam_district": r["district"],
                               "danam_municipality": r["municipality"], "quality_flags": "; ".join(fl)})

        # GeoNames (Nepal file, heritage and religious feature codes)
        gn_by = defaultdict(list)
        for r in geonames:
            lat, lon = float(r[4]), float(r[5])
            if r[0] in gn_seen or not inside(lon, lat, prov_rings):
                continue
            gn_seen.add(r[0])
            did = district_of(lon, lat)
            fl = ["no_district"] if did is None else []
            flags_total.update(fl)
            gn_by[did].append({"geonameid": r[0], "url": f"https://www.geonames.org/{r[0]}", "name": r[1],
                               "asciiname": r[2], "alternatenames": r[3], "lat": lat, "lon": lon, "feature_code": r[7],
                               "feature_meaning": FEATURE_CODES[r[7]], "elevation": r[15] or r[16],
                               "modification_date": r[18], "quality_flags": "; ".join(fl)})

        # write per district (and a folder for features outside every district boundary, if any)
        prov_counts = Counter()
        for did in sorted(set(districts) | set(osm_by) | set(wd_by) | set(dn_by) | set(gn_by),
                          key=lambda d: districts[d]["name"] if d in districts else "~"):
            dname = districts[did]["name"] if did in districts else "_no_district"
            folder = os.path.join(OUT, pslug, slug(dname) if did in districts else "_no_district")
            o, w_, d_, g_ = osm_by.get(did, []), wd_by.get(did, []), dn_by.get(did, []), gn_by.get(did, [])
            write(os.path.join(folder, "osm.csv"), OSM_COLS, [{k: r[k] for k in OSM_COLS} for r in o])
            write(os.path.join(folder, "wikidata.csv"), WD_COLS, w_)
            write(os.path.join(folder, "danam.csv"), DN_COLS, d_)
            write(os.path.join(folder, "geonames.csv"), GN_COLS, g_)
            folders.append((p["label"], dname, folder))
            cats = Counter(r["category"] for r in o)
            index.append({"province": p["label"], "district": dname, "district_osm_relation": did or "",
                          "district_wikidata": districts[did]["wikidata"] if did in districts else "",
                          "osm_total": len(o), **{f"osm_{c}": cats[c] for c in CATEGORIES},
                          "osm_recent_looking": sum(1 for r in o if r["recent_looking"]),
                          "osm_possible_duplicates": sum(1 for r in o if r["duplicate_group"]),
                          "wikidata": len(w_), "geonames": len(g_), "danam": len(d_)})
            prov_counts.update({"districts": 1 if did in districts else 0, "osm": len(o), "wikidata": len(w_),
                                "geonames": len(g_),
                                "danam": len(d_), "historic": cats["historic"], "recent": index[-1]["osm_recent_looking"]})
        prov_counts["wikidata_outside"] = wd_outside
        per_province[pslug] = prov_counts

    rest = [wd_row(v, "", "", ["no_coordinates_no_district"] + ([] if v.get("itemLabel") else ["no_english_label"]))
            for v in nocoord if v["item"] not in nc_placed]
    flags_total.update(f for r in rest for f in r["quality_flags"].split("; "))
    write(os.path.join(OUT, "_no_coordinates", "wikidata.csv"), WD_COLS, rest)

    write(os.path.join(OUT, "index.csv"), list(index[0]) if index else ["province"], index)

    # national files (one per source) for convenience
    for name, cols in (("osm", OSM_COLS), ("wikidata", WD_COLS), ("geonames", GN_COLS), ("danam", DN_COLS)):
        allrows = []
        for prov, dname, folder in folders:
            for r in csv.DictReader(open(os.path.join(folder, f"{name}.csv"), encoding="utf-8")):
                allrows.append({"province": prov, "district": dname, **r})
        write(os.path.join(OUT, f"all_{name}.csv"), ["province", "district"] + cols, allrows)

    # report
    sp = os.path.join(OUT, "raw", "osm", "retrieved_at.txt")
    OSM_SOURCE = open(sp, encoding="utf-8").read().strip() if os.path.exists(sp) else "Overpass API"
    L = ["# Collected heritage data, by province and district", "",
         "Generated by `tools/collect/build.py` from the raw files in `raw/`: OSM selected from the Geofabrik Nepal extract "
         f"(`tools/collect/osm_extract.py`; {OSM_SOURCE}), Wikidata queried per province in tiles "
         "(`tools/collect/fetch.py`), the GeoNames Nepal file (`tools/collect/geonames.py`) and DANAM from the existing "
         "crawl. Nothing is corrected or merged; each row keeps its source's values and a list of quality flags.", "",
         "## Per province", "",
         "| province | districts | OSM features | of which historic/heritage-tagged | recent-looking | Wikidata items | GeoNames places | DANAM monuments | OSM retrieved | Wikidata retrieved |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for pslug, c in per_province.items():
        r_ = retrieved.get(pslug, {})
        L.append(f"| {PROVINCES[pslug]['label']} | {c['districts']} | {c['osm']:,} | {c['historic']:,} | {c['recent']:,} | "
                 f"{c['wikidata']:,} | {c['geonames']:,} | {c['danam']:,} | {r_.get('overpass', '')} | {r_.get('wikidata', '')} |")
    tot = Counter()
    for c in per_province.values():
        tot.update(c)
    L.append(f"| **all** | {tot['districts']} | {tot['osm']:,} | {tot['historic']:,} | {tot['recent']:,} | "
             f"{tot['wikidata']:,} | {tot['geonames']:,} | {tot['danam']:,} | | |")
    L += ["", f"DANAM monuments with coordinates: {len(danam):,}; placed in a province: {len(danam_seen):,}.", "",
          f"GeoNames places with a heritage or religious feature code: {len(geonames):,}; placed in a province: {len(gn_seen):,}.", "",
          "Per district: `index.csv`. Rows: `<province>/<district>/{osm,wikidata,geonames,danam}.csv` and `all_*.csv`.", "",
          "## Quality checks (column `quality_flags`)", "",
          "| flag | meaning | rows |", "|---|---|---:|"]
    meaning = {"no_district": "inside the province but in no district boundary (boundary gap); kept in `_no_district/`",
               "no_name": "OSM feature without any name", "unusual_religion": "OSM `religion` value outside the usual list",
               "bahai_probably_bahi_monastery": "`religion=bahai` on a feature named *bahā/bahī* (Newar monastery): likely a tagging error",
               "possible_duplicate": f"same name as another OSM feature within {DUP_DIST:.0f} m (e.g. a node and a building outline)",
               "no_english_label": "Wikidata item without an English label", "no_class": "Wikidata item kept only for its heritage designation",
               "danam_district_differs": "DANAM's own district field differs from the district boundary that contains the point",
               "no_coordinates_district_from_p131": "Wikidata item without coordinates, placed by the one district in its P131 chain",
               "no_coordinates_no_district": "Wikidata item without coordinates whose P131 chain names no single district; in `_no_coordinates/wikidata.csv`",
               "settlement_not_a_structure": "Wikidata item is a town or municipality (kept for its heritage designation)"}
    for k, v in meaning.items():
        L.append(f"| `{k}` | {v} | {flags_total[k]:,} |")
    L += ["", "Other columns that help judge quality: `heritage_tagged` (OSM `historic=*` or `heritage=*`), `category`, "
          "`recent_looking` and `recent_signals` (no heritage tag and religion Christian, a modern-sounding name, or a "
          "start_date from 1950: a heuristic), `duplicate_group`.", "",
          "**Coverage caveat.** Most OSM features are current places of worship without a heritage tag; only the "
          "`historic` category is heritage by tagging. Their age cannot be read from OSM.", ""]
    if notes:
        L += ["## Notes", ""] + [f"- {n}" for n in notes] + [""]
    L += ["## Licences and attribution", "",
          "- **OpenStreetMap** features and boundaries: © OpenStreetMap contributors, Open Database License 1.0 "
          "(<https://www.openstreetmap.org/copyright>). Tables built from them are ODbL as well.",
          "- **Wikidata**: CC0 1.0. Linked images (Wikimedia Commons) keep their own licences.",
          "- **GeoNames**: CC BY 4.0, attribution “GeoNames” (<https://www.geonames.org/>); Nepal file `NP.zip`.",
          "- **DANAM**: from the existing crawl (`staging/monuments.csv`); not re-collected. Licence not yet settled.",
          "- Not used: CHIMS (unreachable, login-only when last seen; `docs/sources/chims_recon.md`), Google Maps or any "
          "source whose terms forbid reuse.", ""]
    open(os.path.join(OUT, "QUALITY.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[5:15]))


if __name__ == "__main__":
    main()
