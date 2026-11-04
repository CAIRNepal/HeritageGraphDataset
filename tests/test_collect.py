"""tools/collect: point-in-polygon, folder names, and the collected tables' consistency."""
import csv
import os
import random
import sys

from conftest import REPO

sys.path[:0] = [os.path.join(REPO, "tools", "collect"), os.path.join(REPO, "tools", "pilot")]
import build  # noqa: E402
import geo  # noqa: E402
import match  # noqa: E402

COLLECTED = os.path.join(REPO, "data_collection", "collected")


def test_inside_agrees_with_match():
    # a square with a square hole, plus a separate triangle: even-odd over all rings
    rings = [[(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)], [(1, 1), (3, 1), (3, 3), (1, 3), (1, 1)],
             [(5, 0), (7, 0), (6, 2), (5, 0)]]
    rnd = random.Random(0)
    pts = [(rnd.uniform(-1, 8), rnd.uniform(-1, 5)) for _ in range(2000)]
    expected = [match.inside(x, y, rings) for x, y in pts]
    assert geo.inside_many(pts, rings) == expected
    assert [geo.inside(x, y, rings) for x, y in pts] == expected


def test_slug_and_district_name():
    assert build.slug("Achham") == "achham" and build.slug("Kanchanpur") == "kanchanpur"
    assert build.slug("Nawalparasi W") == "nawalparasi-w"
    assert build.district_name({"name:en": "Darchula District (Nepal)"}) == "Darchula"


def test_collected_tables():
    if not os.path.exists(os.path.join(COLLECTED, "index.csv")):
        return
    index = list(csv.DictReader(open(os.path.join(COLLECTED, "index.csv"), encoding="utf-8")))
    real = [r for r in index if r["district_osm_relation"]]
    assert len(real) == 77  # Nepal's 77 districts
    for name, col in (("osm", "osm_total"), ("wikidata", "wikidata"), ("geonames", "geonames"), ("danam", "danam")):
        rows = list(csv.DictReader(open(os.path.join(COLLECTED, f"all_{name}.csv"), encoding="utf-8")))
        assert len(rows) == sum(int(r[col]) for r in index), name
