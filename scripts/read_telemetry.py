#!/usr/bin/env python3
"""F139 (Sprint 16 Task B): one telemetry file per read group, so each paper's read is measured, not guessed.

A group's file is `manifests/sprint16_f114_reads/telemetry/<group>.json`. It holds what was measured, never a
total: the totals are computed by `report` each time (a determinate fact is computed, never stored).

- papers: each record id, its file and its page count (pdfinfo), from the group's brief (`start`).
- agents: each reader or reviewer by its task id, with the tokens and minutes its completion notice reports
  (`agent`). A resumed agent's notice repeats its total tokens, so a second notice for the same id replaces the
  first; minutes are the notice's duration, which for a resumed agent may cover only its last leg or include the
  wait, so `minutes_note` says which.
- steps: each check, render, dry run, trial or apply that touched the group, with the quote checks it ran, the
  text-cache misses it caused, the pages it rendered and the assertions it wrote (entered, or with a changed quote
  or value; an apply's other rows, such as read rows and access notes, are not counted), where the step counts them.

A field no step measured is "unknown" in the report, never 0: a zero that means "not measured" is the silent
failure this file exists against. Tokens and minutes belong to an agent, and an agent reads a whole group, so they
are reported per group and per page; per paper only when a group holds one paper.

    python scripts/read_telemetry.py start <group> <brief file>
    python scripts/read_telemetry.py agent <group> <reader|reviewer> <task id> <tokens> <minutes> [note]
    python scripts/read_telemetry.py report <group> [<group> ...]
    python scripts/read_telemetry.py baseline <session transcript .jsonl> <Sprint 15 work folder>
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
FOLDER = ROOT / "manifests" / "sprint16_f114_reads" / "telemetry"
UNKNOWN = "unknown"
ROLES = ("reader", "reviewer")
STEPS = ("check", "render", "dry run", "trial", "apply")
COUNTS = ("quote_checks", "cache_misses", "pages_rendered", "assertions_written")
REPORT = ("papers", "pages", "reader_minutes", "reader_tokens", "reviewer_minutes", "reviewer_tokens",
          "quote_checks", "cache_misses", "pages_rendered", "assertions_written", "applies")


FOLDER_ENV = "EBDB_TELEMETRY_DIR"  # moves the folder, for tests


def path(group: str, folder: Path | None = None) -> Path:
    return (folder or Path(os.environ.get(FOLDER_ENV) or FOLDER)) / f"{group}.json"


def load(group: str, folder: Path | None = None) -> dict:
    p = path(group, folder)
    if not p.exists():
        return {"group": group, "papers": [], "agents": {}, "steps": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save(data: dict, folder: Path | None = None) -> Path:
    """Atomic, as the text cache is: a reader of the file never sees half of it."""
    p = path(data["group"], folder)
    p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=p.parent, suffix=".partial", delete=False) as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    Path(f.name).replace(p)
    return p


def start(group: str, brief: dict, folder: Path | None = None, pages=None) -> dict:
    """The group's papers and their page counts, from its brief. `pages`: a page counter (pdfinfo by default)."""
    if pages is None:
        from store.ocr import page_count as pages
    data = load(group, folder)
    data["papers"] = []
    for r in brief["records"]:
        try:
            n = pages(r["file"]) if str(r["file"]).lower().endswith(".pdf") else UNKNOWN
        except Exception:  # noqa: BLE001 - a file pdfinfo cannot read has an unknown page count, said so
            n = UNKNOWN
        data["papers"].append({"record_id": r["record_id"], "file": r["file"], "pages": n})
    save(data, folder)
    return data


def agent(group: str, role: str, task_id: str, tokens: int, minutes: float, note: str = "",
          folder: Path | None = None) -> dict:
    if role not in ROLES:
        raise ValueError(f"role {role!r} is not one of {ROLES}")
    data = load(group, folder)
    data["agents"][task_id] = {"role": role, "tokens": int(tokens), "minutes": float(minutes),
                               **({"minutes_note": note} if note else {})}
    save(data, folder)
    return data


def step(group: str, name: str, folder: Path | None = None, **counts) -> dict | None:
    """Record one step against a group that has a telemetry file; a group without one (a Sprint 15 group re-checked)
    is not measured, and nothing is written for it."""
    if name not in STEPS:
        raise ValueError(f"step {name!r} is not one of {STEPS}")
    bad = set(counts) - set(COUNTS)
    if bad:
        raise ValueError(f"unknown counts {sorted(bad)}")
    if not path(group, folder).exists():
        return None
    data = load(group, folder)
    data["steps"].append({"step": name, "at": datetime.now().isoformat(timespec="seconds"),
                          **{k: int(v) for k, v in counts.items()}})
    save(data, folder)
    return data


def _sum(values: list) -> int | float | str:
    """The sum, or "unknown" when nothing was measured or any part is unknown."""
    if not values or any(v == UNKNOWN for v in values):
        return UNKNOWN
    return round(sum(values), 1)


def totals(data: dict) -> dict:
    agents = data.get("agents", {}).values()
    steps = data.get("steps", [])
    out = {"papers": len(data.get("papers", [])),
           "pages": _sum([p["pages"] for p in data.get("papers", [])])}
    for role in ROLES:
        mine = [a for a in agents if a["role"] == role]
        out[f"{role}_minutes"] = _sum([a["minutes"] for a in mine])
        out[f"{role}_tokens"] = _sum([a["tokens"] for a in mine])
    for k in COUNTS:
        out[k] = _sum([s[k] for s in steps if k in s])
    # Written means written to the live store: a trial writes to a copy, and an apply run that wrote nothing to this
    # group (the second apply, or another group's apply) is not one of its applies (Sprint 16 Task F, g333: 1030 shown
    # for 515 written, 2 applies for 1)
    live = [s for s in steps if s["step"] == "apply" and "assertions_written" in s]
    out["assertions_written"] = _sum([s["assertions_written"] for s in live])
    out["applies"] = sum(1 for s in live if s["assertions_written"]) if steps else UNKNOWN
    return out


def per_page(t: dict) -> dict:
    pages = t["pages"]
    return {k: (round(t[k] / pages, 1) if isinstance(t[k], (int, float)) and isinstance(pages, int) and pages else
                UNKNOWN) for k in ("reader_minutes", "reader_tokens", "reviewer_minutes", "reviewer_tokens")}


BLOCK = re.compile(r"<task-notification>(.*?)</task-notification>", re.S)
AGENT = re.compile(r"<summary>Agent \\?\"([^\"\\]+)\\?\" (finished|is waiting|failed|was stopped)")
AGENT_GROUP = re.compile(r"\b(g\d{3}(?:-r1)?)")
EXCLUDED = "left out: no Sprint 15 reader or reviewer named it"


def notices(transcript: Path) -> dict[str, tuple[str, int | str, float | str]]:
    """Each agent's last notice in a session transcript: task id to (name, tokens, minutes). Each notice block is
    parsed on its own, so a background command's notice on the same line never lends its task id to the agent's
    (fresh-eyes review of Task B: g134's reviewer was counted twice). A notice repeats for a resumed agent with its
    total tokens, so the last one is kept; a failed or stopped agent's notice has no usage, so its tokens and
    minutes are "unknown"."""
    out = {}
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        for block in BLOCK.finditer(line):
            body = block[1]
            task, agent = re.search(r"<task-id>([^<]+)</task-id>", body), AGENT.search(body)
            if not (task and agent):
                continue
            tokens = re.search(r"<subagent_tokens>(\d+)</subagent_tokens>", body)
            ms = re.search(r"<duration_ms>(\d+)</duration_ms>", body)
            out[task[1]] = (agent[1], int(tokens[1]) if tokens else UNKNOWN,
                            round(int(ms[1]) / 60000, 1) if ms else UNKNOWN)
    return out


def role_of(name: str) -> str | None:
    """Sprint 15's agent names: "Reader g120", "Pilot reader g114 (Task G)", "Read Gong review paper (g146 record
    2)", "Reviewer g120"; a Sprint 14 name ("Sonnet review g043", "F114 local reader g104") is not Sprint 15's."""
    if name.startswith("Reviewer "):
        return "reviewer"
    if name.startswith(("Reader ", "Pilot reader ", "Read ")):
        return "reader"
    return None


def baseline(transcript: Path, work: Path, pages=None) -> dict:
    """Sprint 15's reads, measured from what they left: the groups are the work folder's tmp_<group> folders; papers
    from each brief; pages by pdfinfo; images rendered as the PNG files in the group's folder; reader and reviewer
    tokens and minutes from the session's completion notices; the span of the folder's file times as a second
    minutes figure. Quote checks, cache misses and assertions written were not counted then: "unknown"."""
    if pages is None:
        from store.ocr import page_count as pages
    agents: dict[str, dict] = {}
    for task, (name, tokens, minutes) in notices(transcript).items():
        role, named = role_of(name), AGENT_GROUP.findall(name)
        for g in named if role else []:  # "Reviewer g064-r1, g076-r1": one agent's use split evenly, and said so
            label = name if len(named) == 1 else f"{name} (split evenly over {len(named)} groups)"
            share = (lambda v, r=0: v if v == UNKNOWN else round(v / len(named), r))
            agents.setdefault(g, {}).setdefault(role, []).append(
                (task, label, share(tokens), share(minutes, 1)))
    groups, excluded = {}, []
    for folder in sorted(work.glob("tmp_g*")):
        g = folder.name[len("tmp_"):]
        if g not in agents:  # Sprint 14's readers ("F114 local reader g104") left folders here too
            excluded.append(g)
            continue
        brief = json.loads((work / "briefs" / f"{g}.json").read_text(encoding="utf-8"))
        papers = []
        for r in brief["records"]:
            try:
                n = pages(r["file"]) if str(r["file"]).lower().endswith(".pdf") else UNKNOWN
            except Exception:  # noqa: BLE001 - said so, never a guess
                n = UNKNOWN
            papers.append({"record_id": r["record_id"], "pages": n})
        times = [f.stat().st_mtime for f in folder.rglob("*") if f.is_file()]
        mine = agents.get(g, {})
        groups[g] = {
            "papers": papers,
            "images_rendered": sum(1 for _ in folder.rglob("*.png")),
            "file_span_minutes": round((max(times) - min(times)) / 60, 1) if times else UNKNOWN,
            # Known usage summed; an agent that failed or was stopped has none, and is counted beside the sum, so
            # the sum reads as a lower bound where that count is not 0 (fresh-eyes review: never a silent zero).
            **{f"{role}_{what}": (round(sum(a[i] for a in mine[role] if a[i] != UNKNOWN), 1) if role in mine
                                  else UNKNOWN)
               for role in ROLES for what, i in (("tokens", 2), ("minutes", 3))},
            **{f"{role}_agents_without_usage": sum(1 for a in mine.get(role, []) if a[2] == UNKNOWN)
               for role in ROLES},
            "agents": {role: [a[1] for a in mine.get(role, [])] for role in ROLES},
            "quote_checks": UNKNOWN, "cache_misses": UNKNOWN, "assertions_written": UNKNOWN,
        }
    return {"groups": groups, EXCLUDED: excluded}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 1
    if args[0] == "start":
        data = start(args[1], json.loads(Path(args[2]).read_text(encoding="utf-8")))
        print(f"{args[1]}: {len(data['papers'])} papers, pages {[p['pages'] for p in data['papers']]}")
        return 0
    if args[0] == "agent":
        agent(args[1], args[2], args[3], int(args[4]), float(args[5]), " ".join(args[6:]))
        return 0
    if args[0] == "baseline":
        found = baseline(Path(args[1]), Path(args[2]))
        out = {"measured": datetime.now().date().isoformat(),
               "sources": f"the work folder {args[2]} (briefs; each tmp_<group> folder's file times and PNG files), "
                          f"pdfinfo page counts, and the completion notices in session transcript {Path(args[1]).name}",
               **found}
        save({"group": "baseline_sprint15", **out})
        print(f"{len(found['groups'])} groups, {len(found[EXCLUDED])} excluded -> {path('baseline_sprint15')}")
        return 0
    if args[0] == "report":
        for g in args[1:]:
            t = totals(load(g))
            print(g, json.dumps(t), "per page", json.dumps(per_page(t)))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
