#!/usr/bin/env python3
"""Pilot: match DANAM monuments, OpenStreetMap features and Wikidata items in one district.

Reads the saved raw responses in docs/pilot/<district>/raw/ (no network access; see fetch.py) and
staging/monuments.csv, keeps what lies inside the district (its OSM boundary relation, returned with the Overpass
query; districts.py), and proposes candidate matches between every pair of sources:

  candidate  the two are less than MAX_DIST metres apart; name similarity (0-1) is reported
  likely     a candidate with name similarity >= LIKELY_SIM, or a pair the sources already link to each other
             (OSM wikidata=* tag; Wikidata's OSM node / way / relation ID), at any distance

Nothing is merged. The candidate CSVs have empty columns for a reviewer ('decision': same / different / unsure).
The report (REPORT.md) gives counts per source, overlaps by likely matches, what each source has that the others
lack, and the licence and attribution of each source.

It also writes summary.json (the numbers used by compare.py), and flags OSM features that look like recent
buildings rather than heritage (RECENT_* below; a heuristic, reported as such).

Usage:  python3 tools/pilot/match.py [lalitpur|chitwan|kanchanpur]
"""
import csv
import difflib
import json
import math
import os
import re
import unicodedata
from collections import Counter, defaultdict

import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from districts import DISTRICTS  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLUG = "lalitpur"
PILOT = RAW = None
DISTRICT_REL = None

# An OSM feature 'looks recent' (rather than heritage) if it has no historic=* or heritage=* tag and at least one of:
RECENT_RELIGIONS = {"christian"}  # in these districts, congregations founded mostly after 1990. (Not religion=bahai:
# in Lalitpur, Newar monasteries named *bahī* are tagged religion=bahai, a tagging error reported in REPORT.md.)
RECENT_NAME = re.compile(r"church|chapel|fellowship|kingdom hall|ministr|assembl|mission|satsang|sat sang|ashram|"
                         r"school|college|\bhall\b|\bbhawan\b|\bbhavan\b", re.I)  # whole words: not 'Bhawani'
RECENT_FROM_YEAR = 1950  # start_date in or after this year
MAX_DIST = 50.0      # metres
LIKELY_SIM = 0.7
EXAMPLES = 10

# Words that name the kind of building rather than the building; removed before names are compared (Latin after
# transliteration folding, and Devanagari)
GENERIC = {"mandir", "mandira", "mandiram", "temple", "shrine", "the", "of", "sri", "and", "hiti", "dhara", "dhunge",
           "bahal", "baha", "bahah", "bahi", "bahil", "vihar", "vihara", "mahavihar", "mahavihara", "mahabihar", "bihar",
           "phalca", "phalcha", "pati", "sattal", "satah", "sata", "caitya", "chaitya", "cibhah", "stupa", "degah",
           "deval", "dega", "pokhari", "math", "matha", "pith", "pitha", "east", "west", "north", "south", "northern",
           "southern", "eastern", "western", "a", "b", "c", "d", "1", "2", "3", "4",
           "मन्दिर", "मंदिर", "हिटी", "हिति", "धारा", "बहाल", "बहाः", "बही", "विहार", "महाविहार", "पाटी", "फल्चा", "सत्तल",
           "चैत्य", "स्तूप", "स्तुप", "देगः", "पोखरी", "श्री"}
# Kind of building, from name words (and DANAM class / OSM tags); a pair whose kinds conflict is not 'likely'
KIND_WORDS = {"water": {"hiti", "dhara", "dhunge", "pokhari", "well", "हिटी", "हिति", "धारा", "पोखरी"},
              "resthouse": {"phalca", "phalcha", "pati", "sattal", "satah", "sata", "पाटी", "फल्चा", "सत्तल"},
              "buddhist": {"bahal", "baha", "bahah", "bahi", "bahil", "vihar", "vihara", "mahavihar", "mahavihara",
                           "mahabihar", "caitya", "chaitya", "stupa", "बहाल", "विहार", "महाविहार", "चैत्य", "स्तूप"},
              "temple": {"mandir", "mandira", "temple", "degah", "deval", "मन्दिर", "मंदिर"}}
DANAM_KIND = {"DhungeDhara": "water", "Pokhari": "water", "Pati": "resthouse", "Sattal": "resthouse",
              "BuddhistMonument": "buddhist", "Chaitya": "buddhist", "Stupa": "buddhist", "Temple": "temple"}


# ── geometry ──────────────────────────────────────────────────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    r = 6371008.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def rings_from_relation(rel):
    """Closed outer rings ([(lon, lat), ...]) stitched from the relation's outer ways."""
    segs = [[(p["lon"], p["lat"]) for p in m["geometry"]] for m in rel["members"]
            if m["type"] == "way" and m.get("role") in ("outer", "") and m.get("geometry")]
    rings = []
    while segs:
        ring = segs.pop(0)
        while ring[0] != ring[-1]:
            for i, s in enumerate(segs):
                if s[0] == ring[-1]:
                    ring += s[1:]
                elif s[-1] == ring[-1]:
                    ring += s[::-1][1:]
                elif s[-1] == ring[0]:
                    ring = s[:-1] + ring
                elif s[0] == ring[0]:
                    ring = s[::-1][:-1] + ring
                else:
                    continue
                segs.pop(i)
                break
            else:
                raise ValueError("boundary ways do not close into a ring")
        rings.append(ring)
    return rings


def inside(lon, lat, rings):
    """Even-odd rule over all rings."""
    hit = False
    for ring in rings:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
            if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
                hit = not hit
    return hit


# ── names ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def fold(name):
    """Lower case, no bracketed notes, no diacritics (Latin only; Devanagari keeps its vowel signs), common
    transliteration variants folded (sh/ś -> s, chh/ch -> c, w -> v, doubled vowels -> single)."""
    s = re.sub(r"\([^)]*\)", " ", name or "").lower()
    s = "".join(c for c in unicodedata.normalize("NFKD", s)
                if not (unicodedata.combining(c) and not "\u0900" <= c <= "\u097f"))
    s = unicodedata.normalize("NFC", s)
    for a, b in (("chh", "c"), ("ch", "c"), ("sh", "s"), ("w", "v"), ("aa", "a"), ("ee", "i"), ("oo", "u")):
        s = s.replace(a, b)
    return re.sub(r"[^\w\s]", " ", s)


def norm(name):
    """Folded name without generic words."""
    return " ".join(w for w in fold(name).split() if w not in GENERIC)


def kinds(names, extra=()):
    words = {w for n in names if n for w in fold(n).split()}
    return {k for k, ws in KIND_WORDS.items() if words & ws} | set(extra)


def kinds_conflict(ka, kb):
    """Both known and no kind in common; temple vs Buddhist building is not a conflict (bāhāḥs have shrines)."""
    if not ka or not kb or ka & kb:
        return False
    return not ({"temple", "buddhist"} >= (ka | kb))


def similarity(names_a, names_b):
    """Best similarity over all name pairs: max of character-sequence ratio and token overlap (0-1)."""
    best = 0.0
    for a in filter(None, map(norm, names_a)):
        for b in filter(None, map(norm, names_b)):
            seq = difflib.SequenceMatcher(None, a.replace(" ", ""), b.replace(" ", "")).ratio()
            ta, tb = set(a.split()), set(b.split())
            tok = len(ta & tb) / min(len(ta), len(tb)) if ta and tb else 0.0
            best = max(best, seq, tok)
    return round(best, 2)


# ── sources ───────────────────────────────────────────────────────────────────────────────────────────────────────
def load_osm():
    d = json.load(open(os.path.join(RAW, "overpass_response.json"), encoding="utf-8"))
    rel = next(e for e in d["elements"] if e["type"] == "relation" and e["id"] == DISTRICT_REL and "members" in e)
    rings = rings_from_relation(rel)
    out = []
    for e in d["elements"]:
        if e["type"] == "relation" and e["id"] == DISTRICT_REL:
            continue
        t = e.get("tags", {})
        lat, lon = (e["lat"], e["lon"]) if e["type"] == "node" else (e["center"]["lat"], e["center"]["lon"])
        out.append({
            "source": "osm", "id": f"{e['type']}/{e['id']}", "url": f"https://www.openstreetmap.org/{e['type']}/{e['id']}",
            "lat": lat, "lon": lon, "name": t.get("name:en") or t.get("name", ""),
            "names": [t.get(k) for k in ("name", "name:en", "name:ne", "name:new", "alt_name", "old_name") if t.get(k)],
            "kind": "; ".join(f"{k}={t[k]}" for k in ("historic", "heritage", "amenity", "building", "religion") if k in t),
            "wikidata": t.get("wikidata", ""), "tags": t,
            "kinds": kinds([t.get(k) for k in ("name", "name:en", "name:ne")],
                           ["buddhist"] if t.get("building") == "stupa" else ["temple"] if t.get("building") == "temple" else []),
        })
    return out, rings, d.get("osm3s", {}).get("timestamp_osm_base", "")


def load_wikidata(rings):
    d = json.load(open(os.path.join(RAW, "wikidata_response.json"), encoding="utf-8"))
    out, outside = [], 0
    for b in d["results"]["bindings"]:
        v = {k: x["value"] for k, x in b.items()}
        lon, lat = map(float, re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", v["coord"]).groups())
        if not inside(lon, lat, rings):
            outside += 1
            continue
        qid = v["item"].rsplit("/", 1)[-1]
        osm = [f"node/{v['osmNode']}" if v.get("osmNode") else "", f"way/{v['osmWay']}" if v.get("osmWay") else "",
               f"relation/{v['osmRel']}" if v.get("osmRel") else ""]
        out.append({
            "source": "wikidata", "id": qid, "url": v["item"], "lat": lat, "lon": lon, "name": v.get("itemLabel", qid),
            "names": [v.get("itemLabel"), v.get("label_ne")], "kind": v.get("classes", ""),
            "osm": [o for o in osm if o], "image": v.get("image", ""), "heritage": v.get("heritage", ""),
            "inception": v.get("inception", ""), "commons": v.get("commons", ""), "sitelinks": int(v.get("sitelinks", 0) or 0),
            "kinds": kinds([v.get("itemLabel"), v.get("label_ne")]),
        })
    return out, outside


def load_danam(rings):
    out, district_field = [], 0
    for r in csv.DictReader(open(os.path.join(REPO, "staging", "monuments.csv"), encoding="utf-8-sig")):
        if not r["coordinates_lat"].strip():
            continue
        lat, lon = float(r["coordinates_lat"]), float(r["coordinates_lon"])
        if not inside(lon, lat, rings):
            continue
        district_field += r["district"].strip().lower().startswith("lalitpur")
        out.append({
            "source": "danam", "id": r["danam_code"] or r["resource_id"], "url": r["url"], "lat": lat, "lon": lon,
            "name": r["monument_name"], "names": [r["monument_name"], r["anglicized_name"], r["name_ne"]],
            "kind": r["ontology_class"] or r["monument_type"], "row": r,
            "kinds": kinds([r["monument_name"], r["anglicized_name"], r["name_ne"]],
                           {DANAM_KIND[c] for c in r["ontology_class"].split("|") if c in DANAM_KIND}),
        })
    return out, district_field


def recent_signals(e):
    """Why an OSM feature looks like a recent building rather than heritage ([] if it does not)."""
    t = e["tags"]
    if "historic" in t or "heritage" in t:
        return []
    why = []
    if t.get("religion") in RECENT_RELIGIONS:
        why.append(f"religion={t['religion']}")
    name = " ".join(t.get(k, "") for k in ("name", "name:en"))
    m = RECENT_NAME.search(name)
    if m:
        why.append(f"name: {m.group(0).lower()}")
    y = re.match(r"\s*(\d{4})", t.get("start_date", ""))
    if y and int(y.group(1)) >= RECENT_FROM_YEAR:
        why.append(f"start_date={t['start_date']}")
    return why


# ── matching ──────────────────────────────────────────────────────────────────────────────────────────────────────
def explicit_link(a, b):
    pair = {a["source"], b["source"]}
    if pair == {"osm", "wikidata"}:
        o, w = (a, b) if a["source"] == "osm" else (b, a)
        return o["wikidata"] == w["id"] or o["id"] in w["osm"]
    return False


def candidates(A, B):
    rows = []
    for a in A:
        for b in B:
            link = explicit_link(a, b)
            dlat = abs(a["lat"] - b["lat"]) * 111_000
            if dlat > MAX_DIST and not link:
                continue
            d = haversine(a["lat"], a["lon"], b["lat"], b["lon"])
            if d > MAX_DIST and not link:
                continue
            sim = similarity(a["names"], b["names"])
            conflict = kinds_conflict(a["kinds"], b["kinds"])
            rows.append({"a": a, "b": b, "dist": round(d, 1), "sim": sim, "link": link, "conflict": conflict,
                         "likely": link or (sim >= LIKELY_SIM and not conflict)})
    rows.sort(key=lambda r: (not r["likely"], -r["sim"], r["dist"]))
    return rows


def write_candidates(path, rows, la, lb):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pair_no", "likely", "distance_m", "name_similarity", "linked_by_source", "kinds_conflict",
                    f"{la}_id", f"{la}_name", f"{la}_kind", f"{la}_url",
                    f"{lb}_id", f"{lb}_name", f"{lb}_kind", f"{lb}_url", "decision (same/different/unsure)", "note"])
        for i, r in enumerate(rows, 1):
            a, b = r["a"], r["b"]
            w.writerow([i, "yes" if r["likely"] else "", r["dist"], r["sim"], "yes" if r["link"] else "",
                        "yes" if r["conflict"] else "",
                        a["id"], a["name"], a["kind"], a["url"], b["id"], b["name"], b["kind"], b["url"], "", ""])


def main():
    global SLUG, PILOT, RAW, DISTRICT_REL
    SLUG = sys.argv[1] if len(sys.argv) > 1 else "lalitpur"
    cfg = DISTRICTS[SLUG]
    PILOT = os.path.join(REPO, "docs", "pilot", SLUG)
    RAW = os.path.join(PILOT, "raw")
    DISTRICT_REL = cfg["rel"]
    osm, rings, osm_base = load_osm()
    wd, wd_outside = load_wikidata(rings)
    dn, dn_district_field = load_danam(rings)
    src = {"danam": dn, "osm": osm, "wikidata": wd}
    label = {"danam": "DANAM", "osm": "OpenStreetMap", "wikidata": "Wikidata"}
    pairs = [("danam", "osm"), ("danam", "wikidata"), ("osm", "wikidata")]
    cand, likely_of = {}, defaultdict(lambda: defaultdict(set))
    for x, y in pairs:
        cand[(x, y)] = candidates(src[x], src[y])
        write_candidates(os.path.join(PILOT, f"candidates_{x}_{y}.csv"), cand[(x, y)], x, y)
        for r in cand[(x, y)]:
            if r["likely"]:
                likely_of[x][r["a"]["id"]].add(y)
                likely_of[y][r["b"]["id"]].add(x)

    L = [f"# Pilot: DANAM, OpenStreetMap and Wikidata in {cfg['label']} District", "",
         "Generated by `tools/pilot/match.py` from the saved responses in `raw/` (no merging; candidates are for manual "
         "review). Area: Lalitpur District as OSM boundary relation "
         f"[{DISTRICT_REL}](https://www.openstreetmap.org/relation/{DISTRICT_REL}) (admin_level 6, Wikidata {cfg['qid']}), "
         "applied to all three sources.", "",
         f"Candidate: less than {MAX_DIST:.0f} m apart. Likely: a candidate with name similarity ≥ {LIKELY_SIM} (0–1, best "
         "over the names each source gives, after removing diacritics, bracketed notes, common transliteration variants "
         "and words that only name the kind of building, such as *mandir*, *hiti* or *bāhāḥ*) whose kinds of building "
         "do not conflict (e.g. a water spout and a rest house), or a pair that one source already links to the other "
         "(OSM `wikidata=*`, Wikidata OSM IDs).", ""]

    # counts
    L += ["## 1. Counts per source", "", "| source | in the district | retrieved | notes |", "|---|---:|---|---|",
          f"| DANAM | {len(dn)} | staging/monuments.csv, by coordinates | DANAM's own `district` field says Lalitpur for "
          f"{dn_district_field} of them |",
          f"| OpenStreetMap | {len(osm)} | Overpass, data as of {osm_base} | " + ", ".join(
              f"{k} {v}" for k, v in Counter(e["tags"].get("amenity") == "place_of_worship" and "place of worship"
                                             or ("historic" in e["tags"] and "historic") or "other" for e in osm).most_common())
          + f"; {sum(1 for e in osm if e['tags'].get('name') or e['tags'].get('name:en'))} named |",
          f"| Wikidata | {len(wd)} | query.wikidata.org | {wd_outside} more items in the bounding box lie outside the "
          "district |", ""]
    osm_rel = Counter(e["tags"].get("religion", "not tagged") for e in osm if e["tags"].get("amenity") == "place_of_worship")
    L += ["OSM places of worship by `religion`: " + ", ".join(f"{k} {v}" for k, v in osm_rel.most_common()) + ".", ""]
    no_heritage_tag = [e for e in osm if "historic" not in e["tags"] and "heritage" not in e["tags"]]
    recent = [(e, recent_signals(e)) for e in osm]
    recent = [(e, w) for e, w in recent if w]
    why = Counter(w.split(":")[0].split("=")[0] for _, ws in recent for w in ws)
    L += [f"OSM features without a `historic=*` or `heritage=*` tag: {len(no_heritage_tag)} of {len(osm)}. Of these, "
          f"**{len(recent)} look like recent buildings** rather than heritage (heuristic: religion Christian, "
          "a name with words such as church, fellowship, satsang, ashram, school, hall or bhawan, or a start_date from "
          f"{RECENT_FROM_YEAR} on; signals: " + (", ".join(f"{k} {v}" for k, v in why.most_common()) or "none") + "). "
          "The rest cannot be dated from OSM alone.", ""]
    bahai = [e for e in osm if e["tags"].get("religion") == "bahai"]
    if bahai:
        L += [f"Possible OSM tagging errors: {len(bahai)} feature(s) tagged `religion=bahai`: "
              + "; ".join(f"{e['name'] or '(unnamed)'} ({e['id']})" for e in bahai)
              + ". Names ending in *bahī*/*bahi* are Newar Buddhist monasteries, not Bahá'í places of worship.", ""]

    # overlaps
    L += ["## 2. Overlaps", "", "| pair | candidate pairs (< 50 m) | likely pairs | already linked by a source |",
          "|---|---:|---:|---:|"]
    for x, y in pairs:
        rows = cand[(x, y)]
        L.append(f"| {label[x]} – {label[y]} | {len(rows)} | {sum(r['likely'] for r in rows)} | {sum(r['link'] for r in rows)} |")
    L += ["", "Items with a likely match (an item can have several):", "",
          "| source | items | with a likely match in … | | in both others | in neither |", "|---|---:|---|---|---:|---:|"]
    for s in ("danam", "osm", "wikidata"):
        others = [o for o in src if o != s]
        m = likely_of[s]
        per = [sum(1 for i in src[s] if o in m[i["id"]]) for o in others]
        both = sum(1 for i in src[s] if set(others) <= m[i["id"]])
        none = sum(1 for i in src[s] if not m[i["id"]])
        L.append(f"| {label[s]} | {len(src[s])} | {label[others[0]]}: {per[0]} | {label[others[1]]}: {per[1]} | {both} | {none} |")
    L += ["", "Counts of likely matches are not verified: they are what the review in the candidate files decides.", ""]

    # what each source has that the others lack
    def ex(items, fmt):
        return [f"- {fmt(i)}" for i in items[:EXAMPLES]]

    L += ["## 3. What each source has that the others lack", ""]
    dn_only = [i for i in dn if not likely_of["danam"][i["id"]]]
    osm_only = [i for i in osm if not likely_of["osm"][i["id"]] and (i["tags"].get("name") or i["tags"].get("name:en"))]
    wd_only = [i for i in wd if not likely_of["wikidata"][i["id"]]]
    ev = Counter(); ob = Counter()
    for r in csv.DictReader(open(os.path.join(REPO, "data_collection", "data", "exports", "events.csv"), encoding="utf-8-sig")):
        ev[r["resource_id"]] += 1
    for r in csv.DictReader(open(os.path.join(REPO, "data_collection", "data", "exports", "objects.csv"), encoding="utf-8-sig")):
        ob[r["resource_id"]] += 1
    dn_ev = sum(1 for i in dn if ev[i["row"]["resource_id"]]); dn_ob = sum(1 for i in dn if ob[i["row"]["resource_id"]])
    dn_cond = sum(1 for i in dn if i["row"]["condition_types"]); dn_desc = sum(1 for i in dn if i["row"]["description_en"].strip())
    L += ["### DANAM", "",
          f"Attributes the other sources do not have: historical events ({dn_ev} of {len(dn)} monuments, "
          f"{sum(ev[i['row']['resource_id']] for i in dn):,} events), objects ({dn_ob} monuments, "
          f"{sum(ob[i['row']['resource_id']] for i in dn):,} objects), a condition assessment ({dn_cond}), English "
          f"descriptions ({dn_desc}), site codes, measurements and building categories.", "",
          f"Monuments with no likely match in OSM or Wikidata: {len(dn_only)}. Examples:", ""]
    L += ex(dn_only, lambda i: f"{i['name']} ({i['id']}, {i['kind']}) – {i['url']}")
    tag_cov = {k: sum(1 for e in osm if k in e["tags"]) for k in
               ("building", "religion", "denomination", "start_date", "name:ne", "wikidata", "heritage", "opening_hours")}
    L += ["", "### OpenStreetMap", "",
          f"Attributes the others lack: building footprints (ways and relations: "
          f"{sum(1 for e in osm if not e['id'].startswith('node'))} of {len(osm)}), religion and denomination tags, "
          "current use (e.g. places of worship of all religions, including recent ones). Tag coverage: "
          + ", ".join(f"`{k}` {v}" for k, v in tag_cov.items()) + ".", "",
          f"Named features with no likely match in DANAM or Wikidata: {len(osm_only)}. Examples:", ""]
    L += ex(osm_only, lambda i: f"{i['name']} ({i['id']}, {i['kind']}) – {i['url']}")
    L += ["", "### Wikidata", "",
          f"Attributes the others lack: images ({sum(1 for i in wd if i['image'])} of {len(wd)}), Wikimedia Commons "
          f"categories ({sum(1 for i in wd if i['commons'])}), Wikipedia articles (items with sitelinks: "
          f"{sum(1 for i in wd if i['sitelinks'])}), heritage designations ({sum(1 for i in wd if i['heritage'])}), "
          f"inception dates ({sum(1 for i in wd if i['inception'])}), and stable identifiers used across the web.", "",
          f"Items with no likely match in DANAM or OSM: {len(wd_only)}. Examples:", ""]
    L += ex(wd_only, lambda i: f"{i['name']} ({i['id']}, {i['kind']}) – {i['url']}")
    L += ["", "### Likely matches (examples)", ""]
    for x, y in pairs:
        L += [f"**{label[x]} – {label[y]}**", ""]
        L += [f"- {r['a']['name']} ↔ {r['b']['name']} ({r['dist']} m, similarity {r['sim']}"
              + (", linked by the source" if r["link"] else "") + ")" for r in [r for r in cand[(x, y)] if r["likely"]][:EXAMPLES]]
        L.append("")

    L += ["## 4. Licences and attribution", "",
          "| source | licence | attribution | notes |", "|---|---|---|---|",
          "| OpenStreetMap (features and the district boundary) | Open Database License (ODbL) 1.0 | “© OpenStreetMap "
          "contributors”, with a link to <https://www.openstreetmap.org/copyright> | A database built from OSM data "
          "(e.g. published match tables with OSM IDs and attributes) must also be offered under the ODbL. Retrieved "
          "through the Overpass API (overpass-api.de), one query, within its usage policy. |",
          "| Wikidata | CC0 1.0 (public-domain dedication) | not required; credit “Wikidata” as a courtesy | Images "
          "linked from Wikidata (Wikimedia Commons) have their own licences, per file. |",
          "| DANAM | not yet settled (see the paper's rights paragraph); DANAM's heiDATA deposit is CC BY-SA 4.0 | Digital "
          "Archive of Nepalese Arts and Monuments (DANAM), Heidelberg | Permission to republish is pending. |",
          "", "Not used: Google Maps and any other source whose terms forbid reuse of its data.", ""]
    L += ["## 5. Files", "",
          "- `raw/overpass_query.overpassql`, `raw/overpass_response.json`, `raw/overpass_retrieved_at.txt`",
          "- `raw/wikidata_query.rq`, `raw/wikidata_response.json`, `raw/wikidata_retrieved_at.txt`",
          "- `candidates_danam_osm.csv`, `candidates_danam_wikidata.csv`, `candidates_osm_wikidata.csv`: one row per "
          "candidate pair, likely ones first; fill `decision` (same / different / unsure)", ""]
    open(os.path.join(PILOT, "REPORT.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    summary = {
        "district": cfg["label"], "rel": DISTRICT_REL, "qid": cfg["qid"], "osm_base": osm_base,
        "counts": {s_: len(src[s_]) for s_ in src}, "wikidata_outside": wd_outside, "danam_district_field": dn_district_field,
        "pairs": {f"{x}-{y}": {"candidates": len(cand[(x, y)]), "likely": sum(r["likely"] for r in cand[(x, y)]),
                               "linked": sum(r["link"] for r in cand[(x, y)])} for x, y in pairs},
        "with_likely_match": {s_: {o_: sum(1 for i in src[s_] if o_ in likely_of[s_][i["id"]]) for o_ in src if o_ != s_}
                              for s_ in src},
        "unique": {s_: sum(1 for i in src[s_] if not likely_of[s_][i["id"]]) for s_ in src},
        "unique_named_osm": len(osm_only),
        "osm_no_heritage_tag": len(no_heritage_tag), "osm_recent": len(recent), "osm_recent_signals": dict(why),
        "osm_recent_examples": [f"{e['name'] or '(unnamed)'} ({e['id']}; {', '.join(w)})" for e, w in recent[:EXAMPLES]],
        "osm_place_of_worship": sum(1 for e in osm if e["tags"].get("amenity") == "place_of_worship"),
        "osm_historic": sum(1 for e in osm if "historic" in e["tags"]),
    }
    json.dump(summary, open(os.path.join(PILOT, "summary.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"danam {len(dn)}, osm {len(osm)}, wikidata {len(wd)} (outside {wd_outside}); candidates "
          + ", ".join(f"{x}-{y} {len(cand[(x, y)])} ({sum(r['likely'] for r in cand[(x, y)])} likely)" for x, y in pairs))


if __name__ == "__main__":
    main()
