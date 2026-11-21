#!/usr/bin/env python3
"""Sprint 18 Task D (F114): Roadmap-to-QML from 399b022651 (Sprint 16's release) to 7113ded1df (2026-11-10),
matched to the store; the papers it links for the first time entered at `seen`, each with its free copy.

The machinery is Sprint 16's (`scripts/sprint16_f114_roadmap.py`, itself F104's), loaded and pointed at this
release's commits, copy folder, manifest and tag. Nothing else differs. At planning (2026-11-19) the release adds 3
arXiv papers: 2611.08461, 2611.10105 and 2611.08821; the dry run counts them from the saved copy, not from this text.

    python scripts/sprint18_f114_roadmap.py --fetch   # the list's files, then metadata and PDFs, paced
    python scripts/sprint18_f114_roadmap.py           # dry run: writes the manifest; nothing written to the store
    python scripts/sprint18_f114_roadmap.py --apply   # verified backup first
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("s16roadmap", Path(__file__).with_name("sprint16_f114_roadmap.py"))
s16 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s16)
f104 = s16.f104

TODAY = "2026-11-21"
TAG = "Sprint 18 Task D, F114"
PREVIOUS = "399b022651366f0a4e7037ad3226cd7fe94e636f"
COMMIT = "7113ded1dfa7b3efcb14995b19ae9acff339d511"
MANIFEST = f104.ROOT / "manifests" / "sprint18_f114_roadmap.json"
SCRIPT = "scripts/sprint18_f114_roadmap.py"

s16.PREVIOUS, s16.TODAY, s16.TAG, s16.COMMIT, s16.MANIFEST = PREVIOUS, TODAY, TAG, COMMIT, MANIFEST
s16.PREVIOUS_DIR = f104.COPY_DIR.with_name(f"Roadmap-to-QML_{PREVIOUS[:10]}")
f104.TODAY, f104.TAG, f104.COMMIT, f104.MANIFEST = TODAY, TAG, COMMIT, MANIFEST
f104.COPY_DIR = s16.PREVIOUS_DIR.with_name(f"Roadmap-to-QML_{COMMIT[:10]}")
f104.API_CACHE = f104.COPY_DIR / "arxiv_api"
f104.FOUND_VIA = f"Roadmap-to-QML ({f104.REPO}) at commit {COMMIT[:10]}"

_s16_entry, _s16_quantum_entry = s16.entry, s16.quantum_entry


def entry(ident: str, where: tuple[str, str]) -> dict:
    out = _s16_entry(ident, where)
    out["updated_reason"] = f"{TODAY}: added by {SCRIPT} ({TAG})"
    return out


def quantum_entry(it: dict) -> dict:
    out = _s16_quantum_entry(it)
    out["updated_reason"] = f"{TODAY}: added by {SCRIPT} ({TAG})"
    return out


f104.entry, s16.entry, s16.quantum_entry = entry, entry, quantum_entry

# F104's text names "plan Task F" and F98, Sprint 12's (fresh-eyes review of this script, 2026-11-21); F98 was folded
# into F114 in Sprint 16, so a later F114 release takes the carried links.
CARRIED_WHY = ("links that are not arXiv, matched by the DOI in the URL where it has one, and not in the store; this "
               "release was sized to the arXiv ids at planning (Sprint 18 plan, Task D), and a later F114 release of "
               "the list takes them")


def main(argv: list[str] | None = None) -> int:
    old = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    rc = s16.main(argv)
    if MANIFEST.exists():
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        want = dict(m, carried_why=CARRIED_WHY)
        # A dry run writes None for the routes; Sprint 16's keep-rule keeps only a non-empty list, so an apply's
        # recorded 0 became None on the next dry run. The apply's record stands.
        if want.get("routes_added_to_held_papers") is None and old.get("routes_added_to_held_papers") is not None:
            want["routes_added_to_held_papers"] = old["routes_added_to_held_papers"]
        if want != m:
            MANIFEST.write_text(json.dumps(want, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return rc


if __name__ == "__main__":
    sys.exit(main())
