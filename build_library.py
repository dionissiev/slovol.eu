#!/usr/bin/env python3
"""Scan audio/ and write library.json.

Run from the repo root after adding or removing files:
    python3 build_library.py

Layout it expects:
    audio/<folder>/<track>.m4a
Optional: audio/<folder>/description.txt (one short paragraph shown under the folder name)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
OUT = ROOT / "library.json"


def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def pretty(stem):
    s = re.sub(r"^\d+\s*[-_.]\s*", "", stem)  # drop a leading "01-" style number
    s = re.sub(r"[-_]+", " ", s).strip() or stem
    return s[0].upper() + s[1:]


# keep the site title and subtitle if library.json already exists
old = {}
if OUT.exists():
    try:
        old = json.loads(OUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        pass

folders = []
if AUDIO.is_dir():
    for d in sorted((p for p in AUDIO.iterdir() if p.is_dir()), key=lambda p: natural(p.name)):
        files = sorted((f for f in d.iterdir() if f.suffix.lower() == ".m4a"), key=lambda f: natural(f.name))
        if not files:
            continue
        desc_file = d / "description.txt"
        folders.append({
            "id": d.name,
            "name": pretty(d.name),
            "description": desc_file.read_text(encoding="utf-8").strip() if desc_file.exists() else "",
            "tracks": [{"title": pretty(f.stem), "file": f.relative_to(ROOT).as_posix()} for f in files],
        })

library = {
    "title": old.get("title", "slovol"),
    "subtitle": old.get("subtitle", "Audio, sorted into folders."),
    "folders": folders,
}
OUT.write_text(json.dumps(library, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {OUT.name}: {len(folders)} folders, {sum(len(f['tracks']) for f in folders)} tracks")
