#!/usr/bin/env python3
"""F114: read the papers of Task G groups g043 to g329 in cloud sessions, one paper per session.

Team lead, 2026-10-26: "cloud runs only one paper at a time, sends the 'brief' (it needs to be essentially the
whole paper) as part of the prompt ... We just store them until 10/27 11:10pm and then complete the remaining
processing"; "do one pilot first, then adjust as needed and continue sending until completed or we run out of
weekly tokens".

How a paper reaches its session without passing through git: `claude --cloud` starts a session from GitHub, at
this branch as pushed (so it is linked to the repository and may push its result; a session started from an
uploaded bundle was not, and every push was refused: team lead, 2026-10-26, "q2 1"). The session's id is read
from the console it was started in (`scripts/f114_launch.ps1`), and the instructions, the one-record brief and
the paper's text (extracted here) follow as one message, `claude -p --cloud <id>`; the session saves them with
`scripts/f114_unpack.py`. The text never enters a commit (ADR-0005 section 3).

How a result comes back: the session pushes `manifests/f114_cloud/results/<record>/` to branch
`cloud/f114/<record>` (a cloud session cannot message this one). `fetch` saves each finished paper outside the
repository, never merging, and refuses a branch that touches anything outside its own results folder.

Usage:
  python scripts/f114_cloud.py launch <record_id> [--model sonnet]   one paper (the pilot)
  python scripts/f114_cloud.py fetch                                 save finished papers, print the tally
  python scripts/f114_cloud.py run [--max 5] [--poll 300]            launch and fetch until done, or STOP exists
  python scripts/f114_cloud.py rebuild                               launches.json and results/ again, from the branches
Local state (never in git): WORK/launches.json, WORK/results/<record>.json, WORK/briefs/, WORK/logs/, WORK/STOP.

WORK moved out of Temp on 2026-10-30 (Sprint 14 plan, Q3 = 1): Temp was cleared after Sprint 13, and with it
launches.json and the only local copy of the 302 results. The branches still held every result, so `rebuild`
restores both from them.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.quotes import _pdftotext, source_text  # noqa: E402

LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
WORK = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114")
BRIEFS = WORK / "briefs"
LAUNCHES = WORK / "launches.json"
# Every launch started at a commit of this branch, so a result branch's merge-base with it is its launch base.
LAUNCH_BRANCH = "feature/20261024_Sprint_13"
# Never launched again: the team lead's mark, and a paper whose three sessions pushed nothing (F114's card).
UNREAD = {
    "udaru-2025-qml-credit-risk": "team lead, 2026-10-27: \"mark udaru-2025-qml-credit-risk as unread\" (page "
                                  "images only)",
    "abbas-2020-power-quantum-neural-networks": "three sessions pushed nothing (2026-10-27); read locally by "
                                                "Sprint 14 Task F",
}
FIRST_GROUP = "g043"
# Ledger groups after this one are not Task G's and have no cloud brief: g330 holds Sprint 14 Task C's 4 papers,
# read locally by Task F (review of 1cb63bb: records() raised on its missing brief). The one exception: the
# one-paper groups that Task G's never-started groups were split into (q20 = a, g349 to g509), named by each old
# group's `superseded` note, have cloud briefs and are offered (records()).
LAST_GROUP = "g329"
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
    # q20 = a (2026-11-09): a superseded group's papers moved to one-paper groups past LAST_GROUP (g349 to g509),
    # each with a cloud brief; its old brief is history, not work. The moved papers are offered in their new groups.
    task_g = [x for x in groups if FIRST_GROUP <= x <= LAST_GROUP]
    moved = {r["moved_to"] for x in task_g for r in groups[x].get("superseded", {}).get("records", [])}
    for g in sorted((x for x in task_g if "superseded" not in groups[x]), key=lambda x: int(x[1:])) + \
            sorted(moved, key=lambda x: int(x[1:])):
        brief = json.loads((BRIEFS / f"{g}.json").read_text(encoding="utf-8"))
        out += [(g, r) for r in brief["records"]]
    return out


def done() -> set[str]:
    return {p.stem for p in (WORK / "results").glob("*.json")}


FIRST_MESSAGE = ("Reply with the one word waiting, and do nothing else. Your instructions, your brief and your "
                 "paper arrive in the next message.")


def message(rid: str, brief: dict, text: str) -> str:
    return (f"Read manifests/f114_cloud/READER_PROMPT.md and follow everything after its first \"---\" line exactly, "
            f"as your instructions. RECORD is {rid}. Never use a hook override token. This message carries your "
            f"brief and your paper's text, after the two markers below; save them with the prompt's first step, "
            f"never by copying them yourself.\n=== BRIEF ===\n{json.dumps(brief, indent=1)}\n=== PAPER TEXT ===\n"
            f"{text}")


def paper_text(path: str) -> str:
    """A PDF's raw text, with its line breaks and form feeds (`\\f`, one per page), so the reader can count pages
    and resume from one; `source_text` folds all whitespace and joins two layouts, which gave the pilot one line
    holding the paper twice. The quote check's `plain` folds this text to the first half of `source_text`."""
    return _pdftotext(path, False) if path.lower().endswith(".pdf") else source_text(path)


def launch(rid: str, model: str = "sonnet") -> str:
    """Start one cloud session from GitHub, then send it its instructions, brief and paper as one message."""
    base = git("rev-parse", "HEAD").strip()
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    if git("ls-remote", "origin", f"refs/heads/{branch}").split()[:1] != [base]:
        raise SystemExit(f"{branch} on GitHub is not HEAD; push first, since the session clones it from there")
    g, rec = next((g, r) for g, r in records() if r["record_id"] == rid)
    (WORK / "logs").mkdir(parents=True, exist_ok=True)
    log = WORK / "logs" / f"{rid}.console.txt"
    log.unlink(missing_ok=True)
    # `--cloud` creates a session only from an interactive terminal, so it runs in a console window of its own,
    # and the window's screen, read after claude exits, gives the session's id.
    proc = subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                             str(ROOT / "scripts" / "f114_launch.ps1"), "-Message", FIRST_MESSAGE, "-Model", model,
                             "-Log", str(log), "-Name", f"F114 {rid}"], cwd=ROOT, creationflags=subprocess.CREATE_NEW_CONSOLE)
    try:
        rc = proc.wait(timeout=UPLOAD_WAIT)
    except subprocess.TimeoutExpired:
        rc = None
    screen = log.read_text(encoding="utf-8-sig", errors="replace") if log.is_file() else ""
    ids = re.findall(r"\b(?:session|cse)_[A-Za-z0-9]{20,}\b", screen)
    if not ids:
        raise SystemExit(f"{rid}: no session id on the launch window's screen (exit {rc}): {screen.strip()[-800:]}")
    sid = ids[-1]
    payload = message(rid, {"group": g, "records": [rec]}, paper_text(rec["file"]))
    sent = subprocess.run(["claude", "-p", "--cloud", sid, "--output-format", "json"], cwd=ROOT,
                          input=payload.encode("utf-8"), capture_output=True)
    out = sent.stdout.decode("utf-8", "replace")
    if sent.returncode != 0 or '"ok":true' not in out.replace(" ", ""):
        raise SystemExit(f"{rid}: session {sid} started, but its paper was not sent: "
                         f"{(out + sent.stderr.decode('utf-8', 'replace'))[-800:]}")
    d = launches()
    attempts = d.get(rid, {}).get("attempts", 1 if rid in d else 0) + 1
    d[rid] = {"group": g, "session": sid, "base": base, "attempts": attempts,
              "launched": datetime.now().isoformat(timespec="seconds"), "model": model}
    save_launches(d)
    return f"launched {sid} (attempt {attempts}), sent {len(payload)} characters"


def fetch(remote: bool = True) -> dict:
    """Save each finished paper outside the repository; refuse a branch any of whose commits touches more than
    its folder. `stale` lists the papers whose session has pushed nothing for STALE_HOURS (since its launch, or
    its branch's last commit)."""
    if remote:
        git("fetch", "--quiet", "origin", "+refs/heads/cloud/f114/*:refs/remotes/origin/cloud/f114/*")
    (WORK / "results").mkdir(parents=True, exist_ok=True)
    tally = {"launched": 0, "done": 0, "refused": [], "stale": []}
    now = datetime.now().astimezone()
    for rid, info in launches().items():
        tally["launched"] += 1
        if rid in done():
            continue
        ref = f"origin/cloud/f114/{rid}"
        # A rebuilt entry has no launch time: it is never called stale until its branch gives one.
        last = datetime.fromisoformat(info["launched"]).astimezone() if info.get("launched") else None
        if git("branch", "-r", "--list", ref).strip():
            # F127 (Sprint 15 Task E), the review of d2fcc8d: a merged branch is refused here, for every record, not
            # only by rebuild for a record not yet launched; one already in launches.json was checked from its old
            # base and saved. A record with no launch base (an unread mark) is refused too, never a KeyError.
            # A branch pushed before its first commit sits at its launch base, which is also "in" LAUNCH_BRANCH: it is
            # pending, not merged (fresh-eyes review, 2026-11-02)
            if merged(ref) and not (info.get("base") and git("rev-parse", ref).strip() == info["base"]):
                tally["refused"].append(f"{rid}: already in {LAUNCH_BRANCH}, so its commits cannot be checked")
                continue
            if not info.get("base"):
                tally["refused"].append(f"{rid}: no launch base, so its commits cannot be checked")
                continue
            folder = f"manifests/f114_cloud/results/{rid}/"
            # Every commit, not only the final tree: a file committed and then deleted was still pushed.
            touched = set(git("log", "--name-only", "--format=", f"{info['base']}..{ref}").split())
            stray = sorted(f for f in touched if not f.startswith(folder))
            if stray:
                tally["refused"].append(f"{rid}: touches {stray}")
                continue
            try:
                # cat-file, not show: show stats its argument as a file name first, and on Windows a long record
                # id made that "Filename too long", which read as "not finished" (xu-2025-accelerating-...).
                entry = git("cat-file", "blob", f"{ref}:{folder}done/{rid}.json")
                (WORK / "results" / f"{rid}.json").write_text(entry, encoding="utf-8")
                continue
            except subprocess.CalledProcessError:
                pushed = datetime.fromisoformat(git("log", "-1", "--format=%cI", ref).strip())
                last = max(last, pushed) if last else pushed
        if last and (now - last).total_seconds() > STALE_HOURS * 3600:
            tally["stale"].append(rid)
    tally["done"] = len(done())
    return tally


def merged(ref: str) -> bool:
    """The branch is already in LAUNCH_BRANCH: its merge-base is its own tip, so base..ref would be empty and the
    stray-file check would see nothing (review of 92d7634)."""
    return git("merge-base", ref, LAUNCH_BRANCH).strip() == git("rev-parse", ref).strip()


def logged_launches() -> dict[str, dict]:
    """Session and attempt per paper, from the run log's "launch <rid>: launched <session> (attempt n)" lines.
    The first lines of the log name no session, so a paper may be missing here."""
    log = WORK / "logs" / "run.txt"
    out = {}
    for m in re.finditer(r"^  launch (\S+): launched ((?:session|cse)_\w+) \(attempt (\d+)\)",
                         log.read_text(encoding="utf-8") if log.is_file() else "", re.M):
        out[m[1]] = {"session": m[2], "attempts": int(m[3])}
    return out


def rebuild(remote: bool = True) -> dict:
    """launches.json and results/ again from the result branches, after the local copy was lost. Each branch's
    base is its merge-base with LAUNCH_BRANCH; `fetch` then runs the same stray-file check from it and saves
    each result. An entry launches.json already holds keeps its fields (only the unread mark is set). A branch
    already merged into LAUNCH_BRANCH is refused: its merge-base is its own tip, so base..ref would be empty and
    the stray-file check would see nothing (review of 92d7634)."""
    if remote:
        git("fetch", "--quiet", "origin", "+refs/heads/cloud/f114/*:refs/remotes/origin/cloud/f114/*")
    groups = {r["record_id"]: g for g, v in json.loads(LEDGER.read_text(encoding="utf-8"))["groups"].items()
              for r in v["records"]}
    logged = logged_launches()
    d = launches()
    unlaunched_merged = []
    for ref in git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/cloud/f114/").split():
        rid = ref.rsplit("/", 1)[1]
        if merged(ref):  # fetch refuses it for a launched record; one never launched is named here
            if rid not in d and rid not in UNREAD:
                unlaunched_merged.append(f"{rid}: already in {LAUNCH_BRANCH}, so its commits cannot be checked")
            continue
        d.setdefault(rid, {"group": groups[rid], "base": git("merge-base", ref, LAUNCH_BRANCH).strip(),
                           **logged.get(rid, {}), "launched": None, "rebuilt": datetime.now().date().isoformat()})
    for rid, why in UNREAD.items():
        d.setdefault(rid, {"group": groups[rid], **logged.get(rid, {}), "launched": None,
                           "rebuilt": datetime.now().date().isoformat()})["unread"] = why
    save_launches(d)
    tally = fetch(remote)
    tally["refused"] = sorted(tally["refused"] + unlaunched_merged)
    return tally


def run_all(max_inflight: int = 5, poll: int = 300, model: str = "sonnet") -> None:
    """A refused, failed or stale paper is logged and skipped, never a reason to stop the run; a stale paper is
    launched again (its session resumes from what it pushed) until MAX_ATTEMPTS, then set aside."""
    while not (WORK / "STOP").exists():
        tally = fetch()
        started = launches()
        # Marked unread by the team lead (an image-only PDF, 2026-10-27): never in flight, never launched again.
        refused = {x.split(":")[0] for x in tally["refused"]} | {r for r, v in started.items() if v.get("unread")}
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
    elif argv[0] == "rebuild":
        print(json.dumps(rebuild(), indent=1))
    elif argv[0] == "run":
        run_all(int(opt.get("--max", 5)), int(opt.get("--poll", 300)), opt.get("--model", "sonnet"))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
