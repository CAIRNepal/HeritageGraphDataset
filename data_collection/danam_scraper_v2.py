"""
DANAM Heritage Scraper v2
─────────────────────────
Requires Playwright (JS-rendered pages).

Install:
    pip install playwright beautifulsoup4 lxml
    playwright install chromium

Run:
    python danam_scraper_v2.py --csv resourceids.csv --out data/raw --limit 5   # test
    python danam_scraper_v2.py --csv resourceids.csv --out data/raw              # full

Then export CSVs:
    python danam_scraper_v2.py --csv resourceids.csv --out data/raw --export-only

Outputs:
    data/raw/<uuid>.json          — one file per monument
    data/exports/monuments.csv    — flat monument attributes
    data/exports/events.csv       — historical events (FK: resource_id)
    data/exports/objects.csv      — objects (FK: resource_id)
"""

import csv
import json
import time
import random
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

BASE_URL = "https://danam.cats.uni-heidelberg.de/report/{rid}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (HeritageQA Research Dataset; "
        "academic NLP research; contact: nabin@underdogre.dev)"
    ),
}

# ─── HTML parsing helpers ────────────────────────────────────────────────────

def get_section_soup(soup, title):
    """Return the BeautifulSoup subtree for a named section tile."""
    span = soup.find("span", class_="rp-tile-title",
                     string=lambda s: s and title.lower() in s.lower())
    if span:
        return span.find_parent()
    return None


def extract_dt_dd(section_soup):
    """Extract all dt→dd label/value pairs from a section."""
    result = {}
    if not section_soup:
        return result
    dts = section_soup.find_all("dt")
    for dt in dts:
        label = dt.get_text(strip=True)
        dd = dt.find_next_sibling("dd")
        value = dd.get_text(strip=True) if dd else None
        if label and value:
            result[label] = value
    return result


def extract_repeated_cards(soup, card_title_keyword):
    """
    Extract a list of dicts from repeated card sections (events, objects).
    Each card containing card_title_keyword is parsed as one item.
    """
    items = []
    all_cards = soup.find_all("span", class_="rp-tile-title")
    current = {}
    in_block = False

    for span in all_cards:
        title = span.get_text(strip=True)
        parent = span.find_parent()

        if card_title_keyword.lower() in title.lower():
            # Save previous item
            if current:
                items.append(current)
            current = {}
            in_block = True

        if in_block and parent:
            pairs = extract_dt_dd(parent)
            current.update(pairs)

    if current:
        items.append(current)

    return items


def extract_coordinates(soup):
    """Extract GeoJSON coordinates from the page."""
    # Look for JSON-like coordinate data in script tags or data attributes
    scripts = soup.find_all("script")
    for script in scripts:
        text = script.string or ""
        if "coordinates" in text and "geometry" in text:
            # Try to find JSON blob
            import re
            match = re.search(r'\{[^{}]*"coordinates"\s*:\s*\[[^\]]+\][^{}]*\}', text)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass

    # Fallback: look in page text for coordinate values
    text = soup.get_text()
    import re
    match = re.search(r'\{[^{}]*"coordinates"\s*:\s*\[[^\]]+\][^{}]*"type"\s*:\s*"Point"[^{}]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return None


# ─── Main extractor ──────────────────────────────────────────────────────────

def extract_monument(html, rid):
    """
    Parse a fully-rendered DANAM monument page into structured data.
    Returns a dict suitable for JSON export.
    """
    soup = BeautifulSoup(html, "html.parser")

    record = {
        "resource_id": rid,
        "url": BASE_URL.format(rid=rid),
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "status": "ok",

        # ── Names ─────────────────────────────────────────────────────────
        "monument_name": None,
        "anglicized_name": None,
        "name_devanagari": None,

        # ── Typology ──────────────────────────────────────────────────────
        "monument_type": None,
        "main_deity": None,
        "religion": None,

        # ── Location ──────────────────────────────────────────────────────
        "province": None,
        "district": None,
        "municipality": None,
        "tola": None,
        "coordinates_lon": None,
        "coordinates_lat": None,
        "coordinates_geojson": None,

        # ── Descriptions ──────────────────────────────────────────────────
        "description_en": None,
        "description_ne": None,

        # ── Architecture — basic ───────────────────────────────────────────
        "num_storeys": None,
        "monument_length": None,
        "monument_depth": None,
        "monument_height": None,
        "monument_diameter": None,
        "monument_shape": None,

        # ── Architecture — roofs ──────────────────────────────────────────
        "num_roofs": None,
        "roof_type": None,

        # ── Architecture — walls ──────────────────────────────────────────
        "wall_thickness": None,
        "brick_type": None,

        # ── Architecture — plinth ─────────────────────────────────────────
        "num_plinth": None,
        "base_plinth_width": None,
        "base_plinth_depth": None,
        "base_plinth_height": None,
        "top_plinth_width": None,
        "top_plinth_depth": None,
        "top_plinth_height": None,
        "profile_at_base": None,
        "edge_at_platform": None,
        "platform_floor": None,

        # ── Condition ─────────────────────────────────────────────────────
        "monument_assessment": None,
        "identified_threats": None,

        # ── References ────────────────────────────────────────────────────
        "references": None,
        "editorial_team": None,

        # ── Related lists (separate CSVs) ─────────────────────────────────
        "historical_events": [],   # list of dicts
        "objects": [],             # list of dicts
    }

    # ── NAMES section ─────────────────────────────────────────────────────
    names_sec = get_section_soup(soup, "NAMES")
    if names_sec:
        kv = extract_dt_dd(names_sec)
        record["monument_name"] = kv.get("Monument name")
        record["anglicized_name"] = kv.get("Anglicized name")
        record["name_devanagari"] = kv.get("Name in Devanagari")

    # ── TYPOLOGY section ──────────────────────────────────────────────────
    typo_sec = get_section_soup(soup, "TYPOLOGY")
    if typo_sec:
        kv = extract_dt_dd(typo_sec)
        record["monument_type"] = kv.get("Monument type")
        record["main_deity"] = kv.get("Main deity in the sanctum")
        record["religion"] = kv.get("Religion")

    # ── LOCATIONS section ─────────────────────────────────────────────────
    loc_sec = get_section_soup(soup, "LOCATIONS")
    if loc_sec:
        kv = extract_dt_dd(loc_sec)
        record["province"] = kv.get("Province number")
        record["district"] = kv.get("District")
        record["municipality"] = kv.get("Municipality / village council")
        record["tola"] = kv.get("City quarter (tola)")

    # ── COORDINATES ───────────────────────────────────────────────────────
    coords = extract_coordinates(soup)
    if coords and coords.get("type") == "Point":
        lon, lat = coords["coordinates"]
        record["coordinates_lon"] = lon
        record["coordinates_lat"] = lat
        record["coordinates_geojson"] = json.dumps(coords)

    # ── DESCRIPTION section ───────────────────────────────────────────────
    desc_sec = get_section_soup(soup, "DESCRIPTION")
    if desc_sec:
        kv = extract_dt_dd(desc_sec)
        # EN description is usually just "Description"
        record["description_en"] = kv.get("Description")
        record["description_ne"] = kv.get("Description in Nepali")

    # ── ARCHITECTURAL DETAILS ─────────────────────────────────────────────
    # Basic measurements
    basic_sec = get_section_soup(soup, "Basic measurements")
    if basic_sec:
        kv = extract_dt_dd(basic_sec)
        record["num_storeys"] = kv.get("Number of storeys")
        record["monument_length"] = kv.get("Monument length")
        record["monument_depth"] = kv.get("Monument depth")
        record["monument_height"] = kv.get("Monument height (approximate)")
        record["monument_diameter"] = kv.get("Monument diameter")
        record["monument_shape"] = kv.get("Monument shape")

    # Roofs
    roofs_sec = get_section_soup(soup, "Roofs")
    if roofs_sec:
        kv = extract_dt_dd(roofs_sec)
        record["num_roofs"] = kv.get("Number of roofs")
        record["roof_type"] = kv.get("Type of roof")

    # Walls & bricks
    walls_sec = get_section_soup(soup, "Walls")
    if walls_sec:
        kv = extract_dt_dd(walls_sec)
        record["wall_thickness"] = kv.get("Thickness of main wall")
        record["brick_type"] = kv.get("Type of bricks")

    # Bases / plinths
    plinth_sec = get_section_soup(soup, "Bases")
    if plinth_sec:
        kv = extract_dt_dd(plinth_sec)
        record["num_plinth"] = kv.get("Number of plinth")
        record["base_plinth_width"] = kv.get("Base plinth's width")
        record["base_plinth_depth"] = kv.get("Base plinth's depth")
        record["base_plinth_height"] = kv.get("Base plinth's height")
        record["top_plinth_width"] = kv.get("Top plinth's width")
        record["top_plinth_depth"] = kv.get("Top plinth's depth")
        record["top_plinth_height"] = kv.get("Top plinth's height")
        record["profile_at_base"] = kv.get("Profile at base")
        record["edge_at_platform"] = kv.get("Edge at platform")
        record["platform_floor"] = kv.get("Platform's floor")

    # ── CONDITION ASSESSMENT ──────────────────────────────────────────────
    cond_sec = get_section_soup(soup, "CONDITION ASSESSMENT")
    if cond_sec:
        kv = extract_dt_dd(cond_sec)
        record["monument_assessment"] = kv.get("Monument assessment")
        record["identified_threats"] = kv.get("Identified threats")

    # ── REFERENCES ────────────────────────────────────────────────────────
    refs_sec = get_section_soup(soup, "REFERENCES")
    if refs_sec:
        record["references"] = refs_sec.get_text(separator=" ", strip=True)

    # ── AUTHORS ───────────────────────────────────────────────────────────
    auth_sec = get_section_soup(soup, "AUTHORS")
    if auth_sec:
        kv = extract_dt_dd(auth_sec)
        record["editorial_team"] = kv.get("Editorial team")

    # ── HISTORICAL EVENTS ─────────────────────────────────────────────────
    # Each event is a card section containing "Event name" dt
    events = []
    event_name_dts = soup.find_all("dt", string=lambda s: s and "Event name" in s)
    for dt in event_name_dts:
        # Walk up to the card container
        card = dt.find_parent(class_=lambda c: c and "card" in c.lower()) \
               or dt.find_parent()
        kv = {}
        # Collect all dt/dd within this card hierarchy
        parent = dt.find_parent()
        while parent and not parent.get("class"):
            parent = parent.find_parent()

        # Safer: just grab sibling dt/dd pairs from grandparent
        container = dt.find_parent()
        if container:
            all_dts = container.find_all("dt")
            for adt in all_dts:
                label = adt.get_text(strip=True)
                add = adt.find_next_sibling("dd")
                if add:
                    kv[label] = add.get_text(strip=True)

        event = {
            "resource_id": rid,
            "event_name": kv.get("Event name"),
            "event_description": kv.get("Description"),
            "date_bce_ce": kv.get("Date (BCE/CE)"),
            "period": kv.get("Period"),
            "year_ss_ns_vs": kv.get("Year (ŚS/NS/VS)"),
            "nepali_month": kv.get("Nepali month"),
            "paksha": kv.get("Pakṣa"),
            "tithi": kv.get("Tithi"),
            "sources": kv.get("Sources"),
        }
        if event["event_name"]:
            events.append(event)
    record["historical_events"] = events

    # ── OBJECTS ───────────────────────────────────────────────────────────
    objects = []
    obj_id_dts = soup.find_all("dt", string=lambda s: s and "Object ID" in s)
    for dt in obj_id_dts:
        container = dt.find_parent()
        kv = {}
        if container:
            all_dts = container.find_all("dt")
            for adt in all_dts:
                label = adt.get_text(strip=True)
                add = adt.find_next_sibling("dd")
                if add:
                    kv[label] = add.get_text(strip=True)

        obj = {
            "resource_id": rid,
            "object_id": kv.get("Object ID number"),
            "object_name": kv.get("Name"),
            "object_type": kv.get("Object type"),
            "object_material": kv.get("Object material"),
            "object_location": kv.get("Object location"),
            "date_bce_ce": kv.get("Date (BCE/CE)"),
            "date_vs_ns": kv.get("Date (VS/NS)"),
        }
        if obj["object_id"] or obj["object_name"]:
            objects.append(obj)
    record["objects"] = objects

    return record


# ─── Playwright scraper ───────────────────────────────────────────────────────

def scrape_one(rid, page):
    """Fetch one monument page using a Playwright page object."""
    url = BASE_URL.format(rid=rid)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # Wait for the monument content to load
        try:
            page.wait_for_selector("span.rp-tile-title", timeout=20000)
        except Exception:
            log.warning(f"{rid}: tile titles not found after 20s, capturing anyway")

        html = page.content()
        record = extract_monument(html, rid)
        return record
    except Exception as e:
        log.warning(f"Failed {rid}: {e}")
        return {"resource_id": rid, "status": "error", "error": str(e),
                "url": url, "scraped_at": datetime.now(timezone.utc).isoformat()}


def scrape_all(ids, out_dir, delay_min=2.0, delay_max=4.0, checkpoint_every=50):
    from playwright.sync_api import sync_playwright

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_file = out_dir / "checkpoint.txt"

    done = set()
    if checkpoint_file.exists():
        done = set(checkpoint_file.read_text().strip().split("\n"))
        log.info(f"Resuming — {len(done)} already done")

    remaining = [rid for rid in ids if rid not in done]
    log.info(f"To scrape: {len(remaining)} records")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=HEADERS["User-Agent"],
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
        )
        page = context.new_page()

        for i, rid in enumerate(remaining):
            record = scrape_one(rid, page)
            done.add(rid)

            # Save JSON
            (out_dir / f"{rid}.json").write_text(
                json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            if (i + 1) % checkpoint_every == 0:
                checkpoint_file.write_text("\n".join(done))
                log.info(f"Checkpoint — {i+1}/{len(remaining)} done")

            log.info(f"[{i+1}/{len(remaining)}] {rid} → {record.get('monument_name', 'N/A')}")

            # Polite delay
            time.sleep(random.uniform(delay_min, delay_max))

        browser.close()

    checkpoint_file.write_text("\n".join(done))
    log.info("Scraping complete")


# ─── CSV export ───────────────────────────────────────────────────────────────

MONUMENT_FIELDS = [
    "resource_id", "url", "scraped_at", "status",
    "monument_name", "anglicized_name", "name_devanagari",
    "monument_type", "main_deity", "religion",
    "province", "district", "municipality", "tola",
    "coordinates_lat", "coordinates_lon", "coordinates_geojson",
    "description_en", "description_ne",
    "num_storeys", "monument_length", "monument_depth",
    "monument_height", "monument_diameter", "monument_shape",
    "num_roofs", "roof_type",
    "wall_thickness", "brick_type",
    "num_plinth", "base_plinth_width", "base_plinth_depth", "base_plinth_height",
    "top_plinth_width", "top_plinth_depth", "top_plinth_height",
    "profile_at_base", "edge_at_platform", "platform_floor",
    "monument_assessment", "identified_threats",
    "references", "editorial_team",
    "event_count", "object_count",
]

EVENT_FIELDS = [
    "resource_id", "monument_name", "event_index",
    "event_name", "event_description", "date_bce_ce", "period",
    "year_ss_ns_vs", "nepali_month", "paksha", "tithi", "sources",
]

OBJECT_FIELDS = [
    "resource_id", "monument_name", "object_index",
    "object_id", "object_name", "object_type", "object_material",
    "object_location", "date_bce_ce", "date_vs_ns",
]


def export_csvs(raw_dir, export_dir):
    raw_dir = Path(raw_dir)
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for f in sorted(raw_dir.glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
            if r.get("status") == "ok":
                records.append(r)
        except Exception as e:
            log.warning(f"Skip {f.name}: {e}")

    log.info(f"Loaded {len(records)} valid records for CSV export")

    # ── monuments.csv ──────────────────────────────────────────────────────
    monuments_path = export_dir / "monuments.csv"
    with open(monuments_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MONUMENT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            row = {k: r.get(k) for k in MONUMENT_FIELDS}
            row["event_count"] = len(r.get("historical_events", []))
            row["object_count"] = len(r.get("objects", []))
            writer.writerow(row)
    log.info(f"→ monuments.csv ({len(records)} rows)")

    # ── events.csv ────────────────────────────────────────────────────────
    events_path = export_dir / "events.csv"
    event_rows = []
    for r in records:
        mname = r.get("monument_name") or r["resource_id"]
        for idx, ev in enumerate(r.get("historical_events", [])):
            row = {k: ev.get(k) for k in EVENT_FIELDS}
            row["resource_id"] = r["resource_id"]
            row["monument_name"] = mname
            row["event_index"] = idx
            event_rows.append(row)
    with open(events_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EVENT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(event_rows)
    log.info(f"→ events.csv ({len(event_rows)} rows)")

    # ── objects.csv ───────────────────────────────────────────────────────
    objects_path = export_dir / "objects.csv"
    object_rows = []
    for r in records:
        mname = r.get("monument_name") or r["resource_id"]
        for idx, obj in enumerate(r.get("objects", [])):
            row = {k: obj.get(k) for k in OBJECT_FIELDS}
            row["resource_id"] = r["resource_id"]
            row["monument_name"] = mname
            row["object_index"] = idx
            object_rows.append(row)
    with open(objects_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OBJECT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(object_rows)
    log.info(f"→ objects.csv ({len(object_rows)} rows)")

    log.info(f"CSV export complete → {export_dir}/")
    return records


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="DANAM heritage scraper v2 (Playwright + structured CSV export)"
    )
    parser.add_argument("--csv", required=True, help="CSV file with resourceid column")
    parser.add_argument("--out", default="data/raw", help="Output directory for JSONs")
    parser.add_argument("--export-dir", default="data/exports",
                        help="Output directory for CSV exports")
    parser.add_argument("--delay-min", type=float, default=2.0,
                        help="Min delay between requests (seconds)")
    parser.add_argument("--delay-max", type=float, default=4.0,
                        help="Max delay between requests (seconds)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit records for testing")
    parser.add_argument("--export-only", action="store_true",
                        help="Skip scraping, just (re)export CSVs from existing JSONs")
    args = parser.parse_args()

    # Read IDs
    ids = []
    with open(args.csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row.get("resourceid", "").strip().strip('"')
            if rid and rid != '""':
                ids.append(rid)

    if args.limit:
        ids = ids[:args.limit]

    log.info(f"Loaded {len(ids)} resource IDs from {args.csv}")

    if not args.export_only:
        scrape_all(ids, args.out, args.delay_min, args.delay_max)

    # Always export CSVs after scraping
    export_csvs(args.out, args.export_dir)


if __name__ == "__main__":
    main()