#!/usr/bin/env python3
"""OSM heritage features for every province from the Geofabrik Nepal extract, without the Overpass API.

The public Overpass servers turn down province-wide queries when they are busy, so the same selection as
fetch.py's OVERPASS_QUERY is applied locally to one downloaded extract (data_collection/collected/raw/osm/,
retrieved_at.txt records file, time and OSM data date). Output per province, in the shape of an Overpass
`out center tags` / `out geom` response so build.py reads it unchanged:

    raw/<province>/osm_response.json.gz   features whose centre lies inside the province boundary, the province's
                                          district relations (admin_level 6) with geometry, and the province relation
    raw/<province>/osm_retrieved_at.txt   the extract's retrieval time and source

Centres follow Overpass: a node's own position; for ways and relations the centre of the bounding box.
Check: with the Lalitpur pilot's narrower tag set, the extract gives the same 604 features as the pilot's Overpass
response of 2026-11-04 (docs/pilot/lalitpur/raw/), centres within 1e-7 degrees.

Usage:  uv run --no-project --with osmium --with-requirements tools/sync/requirements.txt python tools/collect/osm_extract.py data_collection/collected/raw/osm/nepal-261103.osm.pbf
"""
import gzip
import json
import os
import re
import sys

import osmium

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pilot"))
from geo import inside_many  # noqa: E402
from match import rings_from_relation  # noqa: E402
from provinces import OUT, PROVINCES  # noqa: E402

BUILDINGS = {"temple", "shrine", "stupa", "monastery", "pagoda", "palace", "church", "mosque", "gurdwara", "cathedral",
             "chapel"}
SPOUT = re.compile("hiti|hity|dhara|धारा|हिटी|हिति", re.I)
WELL = re.compile("inar|inaar|kuwa|इनार|कुवा", re.I)
POND = re.compile("pokhari|pokhri|पोखरी", re.I)


def selected(t):
    """The tag selection of fetch.py's OVERPASS_QUERY."""
    name = t.get("name", "")
    return bool("historic" in t or "heritage" in t or "ruins" in t
                or t.get("amenity") in ("place_of_worship", "monastery")
                or t.get("building") in BUILDINGS
                or t.get("tourism") in ("museum", "attraction")
                or (t.get("landuse") == "religious" and name)
                or (t.get("amenity") == "drinking_water" and SPOUT.search(name))
                or (t.get("man_made") == "water_well" and WELL.search(name))
                or (t.get("natural") == "water" and POND.search(name)))


def admin(t):
    return t.get("boundary") == "administrative" and t.get("admin_level") in ("4", "6")


def center(pts):
    lats, lons = [p[0] for p in pts], [p[1] for p in pts]
    return {"lat": round((min(lats) + max(lats)) / 2, 7), "lon": round((min(lons) + max(lons)) / 2, 7)}


def main():
    pbf = sys.argv[1]
    src = open(os.path.join(os.path.dirname(pbf), "retrieved_at.txt"), encoding="utf-8").read().strip()

    # pass 1: relations (features and admin boundaries) and the ways and nodes they need
    rels, need_w, need_n = {}, set(), set()
    for o in osmium.FileProcessor(pbf, osmium.osm.RELATION):
        t = {x.k: x.v for x in o.tags}
        if selected(t) or admin(t):
            rels[o.id] = {"type": "relation", "id": o.id, "tags": t,
                          "m": [(m.type, m.ref, m.role) for m in o.members]}
            need_w |= {m.ref for m in o.members if m.type == "w"}
            need_n |= {m.ref for m in o.members if m.type == "n"}

    # pass 2: nodes and ways with locations
    feats, wgeom, nloc, broken = [], {}, {}, 0
    for o in osmium.FileProcessor(pbf, osmium.osm.NODE | osmium.osm.WAY).with_locations():
        if o.is_node():
            if o.id in need_n:
                nloc[o.id] = (o.location.lat, o.location.lon)
            if len(o.tags):
                t = {x.k: x.v for x in o.tags}
                if selected(t):
                    feats.append({"type": "node", "id": o.id, "lat": o.location.lat, "lon": o.location.lon, "tags": t})
            continue
        sel = o.id not in need_w and len(o.tags) and selected({x.k: x.v for x in o.tags})
        if o.id not in need_w and not sel:
            continue
        try:
            pts = [(n.lat, n.lon) for n in o.nodes]
        except osmium.InvalidLocationError:  # node outside the extract
            broken += 1
            continue
        if o.id in need_w:
            wgeom[o.id] = pts
            sel = selected({x.k: x.v for x in o.tags})
        if sel:
            feats.append({"type": "way", "id": o.id, "center": center(pts), "tags": {x.k: x.v for x in o.tags}})

    boundaries = []
    for r in rels.values():
        if admin(r["tags"]):
            boundaries.append({"type": "relation", "id": r["id"], "tags": r["tags"], "members": [
                {"type": "way", "ref": ref, "role": role, "geometry": [{"lat": a, "lon": b} for a, b in wgeom[ref]]}
                for typ, ref, role in r["m"] if typ == "w" and ref in wgeom]})
        if selected(r["tags"]):
            pts = [p for typ, ref, _ in r["m"] if typ == "w" for p in wgeom.get(ref, [])]
            pts += [nloc[ref] for typ, ref, _ in r["m"] if typ == "n" and ref in nloc]
            if pts:
                feats.append({"type": "relation", "id": r["id"], "center": center(pts), "tags": r["tags"]})
            else:
                broken += 1
    districts = [b for b in boundaries if b["tags"]["admin_level"] == "6"]
    print(f"{len(feats):,} features, {len(districts)} district and {len(boundaries) - len(districts)} province "
          f"relations; {broken} ways/relations without complete geometry skipped")

    placed = set()
    for slug, p in PROVINCES.items():
        prov = next(b for b in boundaries if b["id"] == p["rel"])
        rings = rings_from_relation(prov)
        todo = [f for f in feats if (f["type"], f["id"]) not in placed]
        hit = inside_many([(f["lon"], f["lat"]) if f["type"] == "node" else (f["center"]["lon"], f["center"]["lat"])
                           for f in todo], rings)
        mine = [f for f, h in zip(todo, hit) if h]
        # the province's districts: closed boundaries whose centroid lies inside (the extract's buffer also holds
        # Indian and Chinese admin_level 6 units, cut open at its edge)
        dist = []
        for d in districts:
            try:
                pts = [q for r in rings_from_relation(d) for q in r]
            except ValueError:
                continue
            if inside_many([(sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))], rings)[0]:
                dist.append(d)
        placed |= {(f["type"], f["id"]) for f in mine}
        raw = os.path.join(OUT, "raw", slug)
        os.makedirs(raw, exist_ok=True)
        resp = {"generator": f"tools/collect/osm_extract.py from {os.path.basename(pbf)}",
                "osm3s": {"copyright": "The data included in this document is from www.openstreetmap.org. "
                          "The data is made available under ODbL."},
                "elements": mine + dist + [prov]}
        out = os.path.join(raw, "osm_response.json.gz")
        with gzip.open(out + ".tmp", "wt", encoding="utf-8") as fh:  # renamed when complete: fetch.py may be reading
            json.dump(resp, fh, ensure_ascii=False)
        os.replace(out + ".tmp", out)
        open(os.path.join(raw, "osm_retrieved_at.txt"), "w", encoding="utf-8").write(src + "\n")
        print(f"{slug}: {len(mine):,} features, {len(dist)} districts")
    print(f"outside every province boundary: {len(feats) - len(placed):,}")


if __name__ == "__main__":
    main()
