"""
shard_scrape.py — Run one shard of the DANAM scraper.

Usage (4 terminals, 4 shards):
    python shard_scrape.py --csv resourceids.csv --out data/raw --shard 0 --total-shards 4
    python shard_scrape.py --csv resourceids.csv --out data/raw --shard 1 --total-shards 4
    python shard_scrape.py --csv resourceids.csv --out data/raw --shard 2 --total-shards 4
    python shard_scrape.py --csv resourceids.csv --out data/raw --shard 3 --total-shards 4

Then export when all done:
    python danam_scraper_v2.py --csv resourceids.csv --out data/raw --export-only

Notes:
    - Each shard writes to the SAME data/raw directory (no conflicts — filenames are UUIDs).
    - Each shard maintains its own checkpoint file: data/raw/checkpoint_shard_N.txt
    - Already-scraped JSONs are skipped automatically (idempotent).
    - Adjust --delay-min / --delay-max per shard if you want to stagger them.
"""

import csv
import json
import time
import random
import argparse
import logging
from pathlib import Path
from datetime import datetime

# ── re-use all parsing logic from the main scraper ───────────────────────────
# Make sure danam_scraper_v2.py is in the same directory.
import sys
sys.path.insert(0, str(Path(__file__).parent))
from danam_scraper_v2 import extract_monument, BASE_URL, export_csvs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [shard-%(shard)s] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (HeritageQA Research Dataset; "
        "academic NLP research; contact: nabin@underdogre.dev)"
    ),
}


def scrape_shard(ids, out_dir, shard_id, delay_min=2.0, delay_max=4.0, checkpoint_every=50):
    from playwright.sync_api import sync_playwright

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-shard checkpoint — avoids file-write races between processes
    checkpoint_file = out_dir / f"checkpoint_shard_{shard_id}.txt"

    done = set()
    if checkpoint_file.exists():
        done = set(checkpoint_file.read_text().strip().split("\n"))

    # Also skip any UUID that already has a JSON file (handles restarts / overlap)
    existing = {f.stem for f in out_dir.glob("*.json")}
    done |= existing

    remaining = [rid for rid in ids if rid not in done]

    log = logging.getLogger(__name__)
    log.info(f"Shard {shard_id}: {len(remaining)} to scrape ({len(done)} already done)")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=HEADERS["User-Agent"],
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
        )
        page = context.new_page()

        for i, rid in enumerate(remaining):
            url = BASE_URL.format(rid=rid)
            record = None
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                try:
                    page.wait_for_selector("span.rp-tile-title", timeout=20000)
                except Exception:
                    log.warning(f"{rid}: tile titles not found after 20s, capturing anyway")
                html = page.content()
                record = extract_monument(html, rid)
            except Exception as e:
                log.warning(f"Failed {rid}: {e}")
                record = {
                    "resource_id": rid,
                    "status": "error",
                    "error": str(e),
                    "url": url,
                    "scraped_at": datetime.utcnow().isoformat(),
                }

            out_path = out_dir / f"{rid}.json"
            out_path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            done.add(rid)

            if (i + 1) % checkpoint_every == 0:
                checkpoint_file.write_text("\n".join(done))
                log.info(f"Checkpoint — shard {shard_id}: {i+1}/{len(remaining)} done")

            log.info(
                f"[shard {shard_id}] [{i+1}/{len(remaining)}] "
                f"{rid} → {record.get('monument_name', 'N/A')}"
            )

            time.sleep(random.uniform(delay_min, delay_max))

        browser.close()

    checkpoint_file.write_text("\n".join(done))
    log.info(f"Shard {shard_id} complete.")


def main():
    parser = argparse.ArgumentParser(description="DANAM shard scraper")
    parser.add_argument("--csv", required=True, help="CSV with resourceid column")
    parser.add_argument("--out", default="data/raw", help="Shared output dir for JSONs")
    parser.add_argument("--shard", type=int, required=True, help="This shard index (0-based)")
    parser.add_argument("--total-shards", type=int, required=True, help="Total number of shards")
    parser.add_argument("--delay-min", type=float, default=2.0)
    parser.add_argument("--delay-max", type=float, default=4.0)
    parser.add_argument("--export-only", action="store_true",
                        help="Skip scraping, just export CSVs from existing JSONs")
    parser.add_argument("--export-dir", default="data/exports")
    args = parser.parse_args()

    assert 0 <= args.shard < args.total_shards, \
        f"--shard must be in [0, {args.total_shards - 1}]"

    # Read all IDs
    ids = []
    with open(args.csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row.get("resourceid", "").strip().strip('"')
            if rid and rid != '""':
                ids.append(rid)

    # Slice this shard
    shard_ids = ids[args.shard::args.total_shards]
    print(f"Shard {args.shard}/{args.total_shards}: "
          f"{len(shard_ids)} IDs (indices {args.shard}, "
          f"{args.shard + args.total_shards}, ...)")

    if not args.export_only:
        scrape_shard(shard_ids, args.out, args.shard, args.delay_min, args.delay_max)

    if args.export_only or args.shard == 0:
        export_csvs(args.out, args.export_dir)


if __name__ == "__main__":
    main()