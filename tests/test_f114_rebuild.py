"""Sprint 14 Task E (F117): the F114 results rebuilt from their branches after
Temp lost the only local copy. A throwaway git repository stands in for this
one, with a launch branch and two result branches as `origin` refs."""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _cloud():
    spec = importlib.util.spec_from_file_location("f114_cloud", ROOT / "scripts" / "f114_cloud.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
                          cwd=repo, capture_output=True, text=True, check=True).stdout


def _result_branch(repo: Path, rid: str, base: str, extra: str | None = None) -> None:
    _git(repo, "checkout", "-q", "-b", f"cloud-{rid}", base)
    done = repo / "manifests" / "f114_cloud" / "results" / rid / "done" / f"{rid}.json"
    done.parent.mkdir(parents=True)
    done.write_text(json.dumps({"papers": [{"record_id": rid}]}), encoding="utf-8")
    if extra:
        (repo / extra).write_text("stray", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", rid)
    _git(repo, "update-ref", f"refs/remotes/origin/cloud/f114/{rid}", "HEAD")


def test_rebuild_restores_each_result_from_its_branch_and_refuses_a_stray_one(tmp_path, monkeypatch):
    """Proven to fail by injection, 2026-10-30, three ways: with the base
    taken as the launch branch's tip instead of the merge-base, the base
    assertion went red; with the UNREAD marks dropped, the unread paper had
    no entry; with the stray-file check disabled, the stray branch's result
    was saved; with the merged-branch refusal removed (review of 92d7634), the
    merged branch r3, which holds a stray file, was saved unchecked."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "launch")
    (repo / "README").write_text("x", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD").strip()
    _result_branch(repo, "r1", base)
    _result_branch(repo, "r2", base, extra="stray.txt")
    _result_branch(repo, "r3", base, extra="stray3.txt")
    _git(repo, "checkout", "-q", "launch")
    _git(repo, "merge", "-q", "--no-ff", "-m", "r3 merged", "cloud-r3")
    (repo / "later").write_text("y", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "later work on the launch branch")

    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"groups": {"g043": {"records": [
        {"record_id": r, "file": f"D:\\{r}.pdf"} for r in ("r1", "r2", "r3", "u")]}}}), encoding="utf-8")
    work = tmp_path / "work"
    (work / "logs").mkdir(parents=True)
    (work / "logs" / "run.txt").write_text("  launch r1: launched session_0123456789abcdefghijKL (attempt 2), sent 9 "
                                           "characters\n", encoding="utf-8")
    cloud = _cloud()
    for name, value in {"ROOT": repo, "WORK": work, "LAUNCHES": work / "launches.json", "LEDGER": ledger,
                        "LAUNCH_BRANCH": "launch", "UNREAD": {"u": "page images only"}}.items():
        monkeypatch.setattr(cloud, name, value)

    tally = cloud.rebuild(remote=False)
    assert sorted(p.name for p in (work / "results").glob("*.json")) == ["r1.json"]
    assert tally["refused"] == ["r2: touches ['stray.txt']", "r3: already in launch, so its commits cannot be checked"]
    d = json.loads((work / "launches.json").read_text(encoding="utf-8"))
    assert "r3" not in d
    assert d["r1"]["base"] == d["r2"]["base"] == base
    assert (d["r1"]["session"], d["r1"]["attempts"]) == ("session_0123456789abcdefghijKL", 2)
    assert d["u"]["unread"] == "page images only"
    assert cloud.rebuild(remote=False)["refused"] == tally["refused"]


def test_fetch_refuses_a_merged_branch_already_launched_and_skips_an_unread_mark(tmp_path, monkeypatch):
    """F127 (Sprint 15 Task E), from the review of d2fcc8d: only rebuild refused a merged branch, and only for a
    record not yet in launches.json, so a merged record already there was checked from its old base, saved, and also
    listed as refused; an unread record whose merged branch gave it no base made fetch raise KeyError. Proven to
    fail, 2026-11-01: run before the change, fetch raised KeyError on u; by injection, with fetch's merged check
    removed, r4 was saved from its old base."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "launch")
    (repo / "README").write_text("x", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD").strip()
    for rid in ("r4", "u"):
        _result_branch(repo, rid, base)
        _git(repo, "checkout", "-q", "launch")
        _git(repo, "merge", "-q", "--no-ff", "-m", f"{rid} merged", f"cloud-{rid}")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"groups": {"g043": {"records": [{"record_id": r} for r in ("r4", "u")]}}}),
                      encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    (work / "launches.json").write_text(json.dumps({"r4": {"group": "g043", "base": base, "launched": None}}),
                                        encoding="utf-8")
    cloud = _cloud()
    for name, value in {"ROOT": repo, "WORK": work, "LAUNCHES": work / "launches.json", "LEDGER": ledger,
                        "LAUNCH_BRANCH": "launch", "UNREAD": {"u": "page images only"}}.items():
        monkeypatch.setattr(cloud, name, value)
    tally = cloud.rebuild(remote=False)
    assert not list((work / "results").glob("*.json"))
    assert tally["refused"] == ["r4: already in launch, so its commits cannot be checked",
                                "u: already in launch, so its commits cannot be checked"]


def test_fetch_keeps_a_branch_with_no_commits_yet_pending(tmp_path, monkeypatch):
    """Fresh-eyes review, 2026-11-02: a session that pushed its branch before its first commit sits at its launch
    base, which merged() reads as already in the launch branch, so fetch set it aside as refused and never retried
    it. Proven to fail by injection, 2026-11-02: with the base comparison removed, r5 was refused."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "launch")
    (repo / "README").write_text("x", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD").strip()
    _git(repo, "update-ref", "refs/remotes/origin/cloud/f114/r5", base)
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"groups": {"g043": {"records": [{"record_id": "r5"}]}}}), encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    (work / "launches.json").write_text(json.dumps({"r5": {"group": "g043", "base": base, "launched": None}}),
                                        encoding="utf-8")
    cloud = _cloud()
    for name, value in {"ROOT": repo, "WORK": work, "LAUNCHES": work / "launches.json", "LEDGER": ledger,
                        "LAUNCH_BRANCH": "launch", "UNREAD": {}}.items():
        monkeypatch.setattr(cloud, name, value)
    tally = cloud.fetch(remote=False)
    assert tally["refused"] == []
    assert not list((work / "results").glob("*.json"))
