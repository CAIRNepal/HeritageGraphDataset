#!/usr/bin/env python3
"""DANAM Heritage Scraper CLI Dispatcher.

Provides guidance and quick entrypoints for DANAM monument scraping and CSV exporting.
"""
import sys


def main():
    print("=================================================================")
    print(" DANAM Data Collection Pipeline")
    print("=================================================================")
    print("Available scripts:")
    print("  1. danam_scraper_v2.py  - Main scraper & CSV exporter")
    print("     Usage:")
    print("       python danam_scraper_v2.py --csv resourceids.csv --out data/raw --limit 5")
    print("       python danam_scraper_v2.py --csv resourceids.csv --out data/raw --export-only")
    print("")
    print("  2. shard_scrape.py      - Distributed / parallel shard runner")
    print("     Usage:")
    print("       python shard_scrape.py --csv resourceids.csv --out data/raw --shard 0 --total-shards 4")
    print("=================================================================")


if __name__ == "__main__":
    main()
