#!/usr/bin/env python3
"""Download the hallway clip this demo plays.

The file is ``samples/data/vtest.avi`` from the OpenCV 4.11.0 tag. OpenCV is
Apache-2.0. The clip shows people walking outdoors past a building. It is the
sample OpenCV's own HOG people detector is demonstrated with. It is not a
retail camera, and it is not committed to this repository
(``demo-videos/*.avi`` is gitignored).
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "demo-videos" / "sample.avi"
URL = "https://github.com/opencv/opencv/raw/4.11.0/samples/data/vtest.avi"
SHA256 = "45cddc9490be69345cbdab64ca583be65987e864ca408038e648db99e10516cf"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(dest: Path = DEST) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and sha256(dest) == SHA256:
        print(f"already present: {dest}")
        return dest

    print(f"downloading {URL}")
    request = urllib.request.Request(URL, headers={"User-Agent": "sentri-fetch-sample"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"checksum mismatch: expected {SHA256}, got {digest}")
    dest.write_bytes(data)
    print(f"wrote {dest} ({len(data)} bytes)")
    return dest


if __name__ == "__main__":
    try:
        fetch()
    except Exception as exc:  # noqa: BLE001 — surface a single message for the CLI
        print(f"fetch failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
