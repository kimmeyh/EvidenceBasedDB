#!/usr/bin/env python3
r"""Sprint 19 Task D step 3 (F114, 60 papers from one list): the selection and the local readers' briefs.

The 60 (team lead q2, q3 and q5 = b, 2026-11-25): `scripts/reading_list.py`'s list from the top, the manifest's
`first` papers first (arXiv 2611.27815, the one paper Roadmap-to-QML added at 24853a7acb). A paper whose copy cannot
be read is noted with why and the next one is taken, until 60 are selected:

- no local copy (a free copy is fetched first by `scripts/sprint10_f89_downloads.py`'s rules; a paper still without
  one goes on the hand-download list);
- a copy that is not a document: a package archive or other binary (`qci-package-eqc-models` is a .tar.gz), or a
  directory (Sprint 16's rule);
- a saved page with under MIN_PAGE_TEXT characters of text: the site's menus, no article (Sprint 15's g069 and
  g072; QCi's space-logistics page and its package index pages are such pages);
- a paper whose group's reader file is written and not applied (F144's Batch API reads, g335 to g347): its read
  is not this task's (Sprint 18's rule), and reading it again would pay twice.

Each selected paper gets one brief. A one-paper ledger group's brief is the group's own name; a paper in a group of
several gets a re-entry brief `<g>-rN` (F125's form), N the next number free for that group, holding that paper
alone, so up to 5 readers run at once on single papers. A brief handed to a reader is never rewritten, and a second
--write adds nothing: the selection is saved as `selected` in `manifests/sprint19_reading_ranking.json` (record id,
group, brief) with `skipped` (record id, why) the first time, and later runs keep it.

    python scripts/sprint19_f114_local.py           # what would be selected and written
    python scripts/sprint19_f114_local.py --write   # the selection, the briefs and each brief's telemetry file
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import read_telemetry  # noqa: E402
import reading_list as rl  # noqa: E402
from store.quotes import source_text  # noqa: E402

_spec = importlib.util.spec_from_file_location("g_ledger", ROOT / "scripts" / "sprint13_g_ledger.py")
g_ledger = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g_ledger)

LOCAL = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114\local")
TOTAL = 60
MIN_PAGE_TEXT = 2000
DOCUMENTS = (".pdf", ".html", ".htm", ".md", ".txt", ".ipynb")


def unreadable(row: dict, P: dict[str, dict]) -> str | None:
    """Why the paper's copy cannot be read, or None."""
    if row["needs"] == "read, not applied":
        return f"its group {row['group']}'s reader file is written and not applied (F144's Batch API reads)"
    f = rl.local_copy(P[row["record_id"]]["access"])
    if not f:
        return "no local copy (fetch it first, or the hand-download list)"
    if Path(f).is_dir() or not f.lower().endswith(DOCUMENTS):
        return f"its copy is not a document ({Path(f).name})"
    if f.lower().endswith((".html", ".htm")):
        n = len(source_text(f))
        if n < MIN_PAGE_TEXT:
            return f"a saved page of {n} characters: the site's menus, no article"
    return None


def brief_names(selected: list[dict], L: dict, briefs: Path = LOCAL / "briefs") -> dict[str, str]:
    """record id -> brief name: the group's own for a one-paper group, else `<g>-rN`, N the next free."""
    groups = rl.ledger_groups(L)
    taken = {p.stem for p in Path(briefs).glob("g*.json")}
    out = {}
    for x in selected:
        g = x["group"]
        if len(groups[g]) == 1:
            out[x["record_id"]] = g
            continue
        n = 1
        while f"{g}-r{n}" in taken:
            n += 1
        taken.add(f"{g}-r{n}")
        out[x["record_id"]] = f"{g}-r{n}"
    return out


def select(rows: list[dict], P: dict[str, dict], total: int = TOTAL) -> tuple[list[dict], list[dict]]:
    chosen, skipped = [], []
    for x in rows:
        if len(chosen) == total:
            break
        why = unreadable(x, P)
        if why:
            skipped.append({"record_id": x["record_id"], "why": why})
        else:
            chosen.append(x)
    return chosen, skipped


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    write = "--write" in args
    L = json.loads(rl.LEDGER.read_text(encoding="utf-8"))
    ranking = rl.load_ranking()
    with rl.read_only() as conn:
        P = rl.papers(conn)
        if ranking.get("selected"):
            selected = ranking["selected"]
            print(f"the selection is saved ({len(selected)} papers, {len(ranking.get('skipped', []))} skipped); kept")
        else:
            rows = rl.rows(L, P, ranking, rl.group_read_files())
            chosen, skipped = select(rows, P)
            names = brief_names(chosen, L)
            selected = [{"record_id": x["record_id"], "group": x["group"], "brief": names[x["record_id"]]}
                        for x in chosen]
            for s in skipped:
                print(f"skip {s['record_id']}: {s['why']}")
            if len(selected) < TOTAL:
                print(f"only {len(selected)} papers can be read; nothing written")
                return 1
            if write:
                ranking.update(selected=selected, skipped=skipped)
                rl.RANKING.write_text(json.dumps(ranking, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        for i, s in enumerate(selected, 1):
            path = LOCAL / "briefs" / f"{s['brief']}.json"
            if path.exists():
                held = [r["record_id"] for r in json.loads(path.read_text(encoding="utf-8"))["records"]]
                if held != [s["record_id"]]:
                    raise ValueError(f"{path.name} holds other records than this selection; look again")
                print(f"{i}. exists {path.name}: {s['record_id']}")
                continue
            print(f"{i}. {'write' if write else 'would write'} {path.name}: {s['record_id']}")
            if write:
                f = rl.local_copy(P[s["record_id"]]["access"])
                brief = {"group": s["brief"], "records": [{"record_id": s["record_id"], "file": f,
                                                           "stored_assertions": g_ledger.stored_assertions(
                                                               conn, s["record_id"])}]}
                path.write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
                if not read_telemetry.path(s["brief"]).exists():
                    read_telemetry.start(s["brief"], brief)
    print(f"{len(selected)} papers selected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
