#!/usr/bin/env python3
"""Download GeoNames' Nepal file once (data_collection/collected/raw/geonames/NP.zip) with its retrieval time.

GeoNames: CC BY 4.0, attribution "GeoNames" (https://www.geonames.org/). One request; skipped if the file exists.
build.py keeps the heritage and religious feature codes (FEATURE_CODES there) and assigns districts.

Usage:  python3 tools/collect/geonames.py
"""
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import UA  # noqa: E402
from provinces import OUT  # noqa: E402

URL = "https://download.geonames.org/export/dump/NP.zip"


def main():
    raw = os.path.join(OUT, "raw", "geonames")
    os.makedirs(raw, exist_ok=True)
    path = os.path.join(raw, "NP.zip")
    if os.path.exists(path):
        print("already downloaded:", path)
        return
    t = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    subprocess.run(["curl", "-sS", "-m", "300", "-A", UA, "--fail", "-o", path, URL], check=True)
    open(os.path.join(raw, "retrieved_at.txt"), "w").write(f"{t} {URL}\n")
    print("downloaded", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
