#!/usr/bin/env python3
"""F114: read the papers of Task G groups g043 to g329 in cloud sessions, one paper per session.

Team lead, 2026-10-26: "cloud runs only one paper at a time, sends the 'brief' (it needs to be essentially the
whole paper) as part of the prompt ... We just store them until 10/27 11:10pm and then complete the remaining
processing"; "do one pilot first, then adjust as needed and continue sending until completed or we run out of
weekly tokens".

How a paper reaches its session without passing through git: the paper's text (extracted here, as the quote
checker extracts it) and its one-record brief are written into the TRACKED placeholders in
`manifests/f114_cloud/inbox/`, `claude --cloud` is run with CCR_FORCE_BUNDLE=1 (the bundle carries uncommitted
changes to tracked files), and the placeholders are restored at once. The text never enters a commit
(ADR-0005 section 3); `tests/test_f114_cloud.py` fails if a placeholder is left filled.

How a result comes back: the session pushes `manifests/f114_cloud/results/<record>/` to branch
`cloud/f114/<record>` (a cloud session cannot message this one). `fetch` saves each finished paper outside the
repository, never merging, and refuses a branch that touches anything outside its own results folder.

Usage:
  python scripts/f114_cloud.py launch <record_id> [--model sonnet]   one paper (the pilot)
  python scripts/f114_cloud.py fetch                                 save finished papers, print the tally
  python scripts/f114_cloud.py run [--max 5] [--poll 300]            launch and fetch until done, or STOP exists
Local state (never in git): WORK/launches.json, WORK/results/<record>.json, WORK/logs/, WORK/STOP.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.quotes import _pdftotext, source_text  # noqa: E402

LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
INBOX = ROOT / "manifests" / "f114_cloud" / "inbox"
S13G = Path(r"C:\Users\kimme\AppData\Local\Temp\claude\D--Data-Harold-github-EvidenceBasedDB\s13g")
WORK = S13G / "f114"
LAUNCHES = WORK / "launches.json"
FIRST_GROUP = "g043"
UPLOAD_WAIT = 240
STALE_HOURS = 3  # no push for this long: the session is taken as dead, and the paper is launched again
MAX_ATTEMPTS = 3


def git(*args: str) -> str:
    # utf-8, not the Windows code page: `fetch` saves `git show` output, and cp1252 garbled every non-ASCII quote
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, encoding="utf-8", check=True).stdout


def launches() -> dict:
    return json.loads(LAUNCHES.read_text(encoding="utf-8")) if LAUNCHES.is_file() else {}


def save_launches(d: dict) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    LAUNCHES.write_text(json.dumps(d, indent=1), encoding="utf-8")


def records() -> list[tuple[str, dict]]:
    """Every record of groups g043 on, in ledger order, with its brief entry (stored assertions included)."""
    groups = json.loads(LEDGER.read_text(encoding="utf-8"))["groups"]
    out = []
    for g in sorted(x for x in groups if x >= FIRST_GROUP):
        brief = json.loads((S13G / "briefs" / f"{g}.json").read_text(encoding="utf-8"))
        out += [(g, r) for r in brief["records"]]
    return out


def done() -> set[str]:
    return {p.stem for p in (WORK / "results").glob("*.json")}


def message(rid: str) -> str:
    return (f"Read manifests/f114_cloud/READER_PROMPT.md and follow everything after its first \"---\" line exactly, "
            f"as your instructions. RECORD is {rid}. Never use a hook override token.")


def paper_text(path: str) -> str:
    """A PDF's raw text, with its line breaks and form feeds (`\\f`, one per page), so the reader can count pages
    and resume from one; `source_text` folds all whitespace and joins two layouts, which gave the pilot one line
    holding the paper twice. The quote check's `plain` folds this text to the first half of `source_text`."""
    return _pdftotext(path, False) if path.lower().endswith(".pdf") else source_text(path)


def restore_inbox() -> None:
    # From HEAD, index included: `git checkout -- path` restores the index copy, which keeps the text if staged.
    git("restore", "--source=HEAD", "--staged", "--worktree", "--", str(INBOX.relative_to(ROOT)))


def launch(rid: str, model: str = "sonnet") -> str:
    """Fill the inbox, start one cloud session from a bundle of the working tree, restore the inbox."""
    if git("status", "--porcelain", "--untracked-files=no").strip():
        raise SystemExit("tracked files are modified; commit first, so the bundle carries only the inbox")
    g, rec = next((g, r) for g, r in records() if r["record_id"] == rid)
    base = git("rev-parse", "HEAD").strip()  # before the wait, so a commit made meanwhile is not taken as the base
    try:
        (INBOX / "brief.json").write_text(json.dumps({"group": g, "records": [rec]}, indent=1), encoding="utf-8")
        (INBOX / "paper.txt").write_text(paper_text(rec["file"]), encoding="utf-8")
        env = dict(os.environ, CCR_FORCE_BUNDLE="1")
        # `--cloud` refuses a non-interactive terminal, so it runs in a console window of its own; the result
        # comes back by branch, so the session id is not needed here. The inbox is restored once the bundle is
        # uploaded: when the window's process exits, or after UPLOAD_WAIT seconds.
        # stderr goes to a log (stdin and stdout stay the console's), so a failed launch says why.
        (WORK / "logs").mkdir(parents=True, exist_ok=True)
        log = WORK / "logs" / f"{rid}.err.txt"
        # cmd does the redirect: a handle passed by Popen would make claude's stdin and stdout this session's
        # pipes too, and `--cloud` then refuses them.
        line = subprocess.list2cmdline(["claude", "--cloud", message(rid), "--model", model])
        proc = subprocess.Popen(f'cmd /c "{line} 2> "{log}""', cwd=ROOT, env=env,
                                creationflags=subprocess.CREATE_NEW_CONSOLE)
        try:
            rc = proc.wait(timeout=UPLOAD_WAIT)
        except subprocess.TimeoutExpired:
            rc = None
    finally:
        restore_inbox()
    if rc not in (None, 0):
        raise SystemExit(f"{rid}: the cloud launch window exited with {rc}: "
                         f"{log.read_text(encoding='utf-8', errors='replace')[-800:]}")
    d = launches()
    attempts = d.get(rid, {}).get("attempts", 1 if rid in d else 0) + 1
    d[rid] = {"group": g, "window_rc": rc, "base": base, "attempts": attempts,
              "launched": datetime.now().isoformat(timespec="seconds"), "model": model}
    save_launches(d)
    return f"launched (window exit code {rc}, attempt {attempts})"


def fetch() -> dict:
    """Save each finished paper outside the repository; refuse a branch any of whose commits touches more than
    its folder. `stale` lists the papers whose session has pushed nothing for STALE_HOURS (since its launch, or
    its branch's last commit)."""
    git("fetch", "--quiet", "origin", "+refs/heads/cloud/f114/*:refs/remotes/origin/cloud/f114/*")
    (WORK / "results").mkdir(parents=True, exist_ok=True)
    tally = {"launched": 0, "done": 0, "refused": [], "stale": []}
    now = datetime.now().astimezone()
    for rid, info in launches().items():
        tally["launched"] += 1
        if rid in done():
            continue
        ref = f"origin/cloud/f114/{rid}"
        last = datetime.fromisoformat(info["launched"]).astimezone()
        if git("branch", "-r", "--list", ref).strip():
            folder = f"manifests/f114_cloud/results/{rid}/"
            # Every commit, not only the final tree: a file committed and then deleted was still pushed.
            touched = set(git("log", "--name-only", "--format=", f"{info['base']}..{ref}").split())
            stray = sorted(f for f in touched if not f.startswith(folder))
            if stray:
                tally["refused"].append(f"{rid}: touches {stray}")
                continue
            try:
                entry = git("show", f"{ref}:{folder}done/{rid}.json")
                (WORK / "results" / f"{rid}.json").write_text(entry, encoding="utf-8")
                continue
            except subprocess.CalledProcessError:
                last = max(last, datetime.fromisoformat(git("log", "-1", "--format=%cI", ref).strip()))
        if (now - last).total_seconds() > STALE_HOURS * 3600:
            tally["stale"].append(rid)
    tally["done"] = len(done())
    return tally


def run_all(max_inflight: int = 5, poll: int = 300, model: str = "sonnet") -> None:
    """A refused, failed or stale paper is logged and skipped, never a reason to stop the run; a stale paper is
    launched again (its session resumes from what it pushed) until MAX_ATTEMPTS, then set aside."""
    while not (WORK / "STOP").exists():
        tally = fetch()
        started = launches()
        refused = {x.split(":")[0] for x in tally["refused"]}
        given_up = {r for r in tally["stale"] if started[r].get("attempts", 1) >= MAX_ATTEMPTS}
        retry = [r for r in tally["stale"] if r not in given_up and r not in refused]
        inflight = [r for r in started if r not in done() and r not in tally["stale"] and r not in refused]
        todo = retry + [r["record_id"] for _, r in records() if r["record_id"] not in started]
        print(f"{datetime.now():%H:%M} launched {len(started)}, done {tally['done']}, in flight {len(inflight)}, "
              f"to launch {len(todo)} ({len(retry)} again), set aside {len(given_up) + len(refused)}", flush=True)
        for x in tally["refused"]:
            print(f"  REFUSED {x}", flush=True)
        if not todo and not inflight:
            return
        if git("status", "--porcelain", "--untracked-files=no").strip():
            print("  tracked files are modified; no launch this round", flush=True)
        else:
            for rid in todo[:max(0, max_inflight - len(inflight))]:
                try:
                    print(f"  launch {rid}: {launch(rid, model)}", flush=True)
                except SystemExit as e:
                    print(f"  FAILED {e}", flush=True)
        time.sleep(poll)


def main(argv: list[str]) -> None:
    opt = {k: argv[argv.index(k) + 1] for k in ("--model", "--max", "--poll") if k in argv}
    if argv[0] == "launch":
        print(launch(argv[1], opt.get("--model", "sonnet")))
    elif argv[0] == "fetch":
        print(json.dumps(fetch(), indent=1))
    elif argv[0] == "run":
        run_all(int(opt.get("--max", 5)), int(opt.get("--poll", 300)), opt.get("--model", "sonnet"))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
