#!/usr/bin/env python3
"""Sprint 14 Task C (F123, F98's release for Sprint 14): Roadmap-to-QML from
a239747648 (F104's commit) to COMMIT, matched to the store; its new arXiv
papers entered at `seen`. INTAKE_WORKFLOW.md section 57.

The machinery is F104's (`scripts/sprint12_f104_roadmap.py`), loaded and
pointed at this release's commit, copy folder, manifest and tag. Two things
differ from the first release:

- A route is added only for a held paper the list links for the first time
  since PREVIOUS. F104 routed every listed paper it held; routing them all
  again at each commit would restate the same match about 1,400 times.
- The list now marks withdrawn and retracted papers. Each mark is compared
  with the record that holds its paper (`marks`). A record is corrected only
  from the arXiv or publisher page, never from the list's mark.

    python scripts/sprint14_f123_roadmap.py --fetch   # the list's files, then arXiv metadata and PDFs, 18 s apart
    python scripts/sprint14_f123_roadmap.py           # dry run: writes the manifest; nothing written to the store
    python scripts/sprint14_f123_roadmap.py --apply   # verified backup first
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect  # noqa: E402
from store.backup import backup_before_write  # noqa: E402

_spec = importlib.util.spec_from_file_location("f104", Path(__file__).with_name("sprint12_f104_roadmap.py"))
f104 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f104)

ROOT, DB_PATH = f104.ROOT, f104.DB_PATH
PREVIOUS = f104.COMMIT
PREVIOUS_DIR = f104.COPY_DIR
TODAY = "2026-10-30"
TAG = "Sprint 14 Task C, F123"
COMMIT = "ea6f42a7c063586ecdb0b9cf4c0ab37a33eccead"
MANIFEST = ROOT / "manifests" / "sprint14_f123_roadmap.json"

f104.TODAY, f104.TAG, f104.COMMIT, f104.MANIFEST = TODAY, TAG, COMMIT, MANIFEST
f104.COPY_DIR = PREVIOUS_DIR.with_name(f"Roadmap-to-QML_{COMMIT[:10]}")
f104.API_CACHE = f104.COPY_DIR / "arxiv_api"
f104.FOUND_VIA = f"Roadmap-to-QML ({f104.REPO}) at commit {COMMIT[:10]}"

_MARK = re.compile(r"\*\*\[((?:WITHDRAWN|RETRACTED)[^*]*)\]\*\*")
_entry, _route_held = f104.entry, f104.route_held


def entry(ident: str, where: tuple[str, str]) -> dict:
    out = _entry(ident, where)
    out["updated_reason"] = f"{TODAY}: added by scripts/sprint14_f123_roadmap.py ({TAG})"
    return out


def previously_listed() -> dict[str, tuple[str, str]]:
    """The ids the list linked at PREVIOUS, from F104's saved copy."""
    current = f104.COPY_DIR
    f104.COPY_DIR = PREVIOUS_DIR
    try:
        return f104.listed()
    finally:
        f104.COPY_DIR = current


def newly_linked() -> dict[str, tuple[str, str]]:
    before = previously_listed()
    return {i: w for i, w in f104.listed().items() if i not in before}


def route_held(conn, apply: bool, everything: dict, ids: list[str], bad: dict) -> tuple[int, list[str]]:
    new = newly_linked()
    return _route_held(conn, apply, {i: w for i, w in everything.items() if i in new}, ids, bad)


f104.entry, f104.route_held = entry, route_held


def marks(conn) -> list[dict]:
    """Each withdrawn or retracted mark, with the record holding its paper and
    whether that record already says so."""
    out = []
    for name in f104.FILES:
        for line in f104.text_of(name).splitlines():
            mark = _MARK.search(line)
            if not mark:
                continue
            label, url = f104._LINK.findall(line)[0]
            ident = (f104._ARXIV.findall(url) or [None])[0]
            key = f"arXiv:{ident}" if ident else f"doi:{f104.url_doi(url)}"
            rows = conn.execute("SELECT r.id, f.disposition FROM paper_fields f JOIN records r ON r.id = f.record_id "
                                "WHERE f.access = ? OR f.access LIKE ?", (key, f"{key} |%")).fetchall()
            out.append({"file": name, "label": " ".join(label.split()), "paper": key, "mark": mark.group(1),
                        "records": [{"id": rid, "disposition": disp} for rid, disp in rows],
                        "store_agrees": bool(rows) and all(
                            (disp or "").startswith(("Withdrawn", "Retracted")) for _, disp in rows)})
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--fetch" in args:
        return f104.main(["--fetch"])
    missing = [n for n in f104.FILES if not f104.copy_of(n).exists()]
    if missing:
        print("missing list copies (run --fetch): " + ", ".join(missing))
        return 1
    apply = "--apply" in args
    if apply:
        backup_before_write(DB_PATH, "F123 Roadmap-to-QML release")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log, manifest = f104.apply_changes(conn, apply, f104.CachedFetcher())
        manifest["previous_commit"] = PREVIOUS
        manifest["newly_linked_since_previous"] = sorted(newly_linked())
        manifest["marks"] = marks(conn)
        if apply:
            conn.commit()
    finally:
        conn.close()
    # As F104's: a later run that enters nothing keeps what the earlier apply recorded.
    new_now = manifest["arxiv_ids_new"]
    old = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    if old and not new_now:
        manifest["entered"], manifest["arxiv_ids_new"] = old["entered"], old["arxiv_ids_new"]
    if old.get("routes_added_to_held_papers") and not manifest["routes_added_to_held_papers"]:
        manifest["routes_added_to_held_papers"] = old["routes_added_to_held_papers"]
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    disagree = [m["paper"] for m in manifest["marks"] if not m["store_agrees"]]
    print("\n".join(log) or "nothing to enter")
    print(f"listed {manifest['arxiv_ids_listed']} arXiv ids; newly linked {len(manifest['newly_linked_since_previous'])}; "
          f"new this run {new_now}; marks {len(manifest['marks'])}, store disagrees on {disagree or 'none'}; "
          f"carried {len(manifest['carried_to_next_release'])} other links; manifest {MANIFEST.relative_to(ROOT)}")
    print("APPLIED" if apply else "DRY RUN: nothing written to the store. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
