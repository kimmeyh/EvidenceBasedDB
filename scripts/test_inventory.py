#!/usr/bin/env python3
"""F140 part 1 (Sprint 17 Task A): the test inventory, generated so it can be reproduced.

One row per test file under tests/: what it guards (its module docstring's first sentence), its kind, its tests and
local time (from a pytest JUnit XML file, when given), where it runs, whether it records a red proof, and the last
time it caught a real defect (CAUGHT). Written to `docs/test_inventory.json`; `tests/test_test_inventory.py` fails
when a test file is missing from it, a row names a file that is gone, or a computed field (COMPUTED) differs from
what this script computes now. Only the tests and seconds are a snapshot of one timed run.

    python scripts/test_inventory.py [--junit FILE] [--write]

Kinds, decided from the file's text (a rule, so the column can be checked):
  - live-store data check: carries the `live_store` marker (reads the real store; local only);
  - hook check: names a file under `.claude/hooks/`;
  - document check: one of run_suite's DOC_GUARDS, or reads `docs/` documents by path;
  - guard: scans every file of a kind (run_suite's MANIFEST_, SCRIPT_ and TEST_GUARDS);
  - unit: anything else.
Where it runs: "full" always; "ci" when any test in it is not live_store; "changed" names its trigger.
The JUnit file is pytest's own output on this machine (`pytest --junitxml`), never outside input.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET  # pytest's own JUnit output, written on this machine
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "test_inventory.json"
PROVEN = re.compile(r"proven (red|to fail)|INJECTED|went red", re.IGNORECASE)
COMPUTED = ("guards", "kind", "runs", "red_proof_recorded", "last_caught")  # checked against the files by a test

# The last time a test caught a real defect, where one is on record (F140 part 3: the retrospectives, INTAKE and git
# history of Sprints 11 to 16, each commit read). A record, not a computation: git does not say which test found a
# defect. Add a line when a test goes red on a real defect.
CAUGHT = {
    "tests/test_intake.py": "2026-11-04: a committed manifest no workflow named "
                            "(test_every_committed_manifest_is_named_in_the_workflow; CHANGELOG)",
    "tests/test_sprint12_reading.py": "2026-10-28: Task G's apply rewrote Task F's read rows (5e10948)",
    "tests/test_sprint13_reading.py": "2026-10-28: Task G's apply rewrote Task F's read rows (5e10948)",
    "tests/test_sprint13_g_apply.py": "2026-10-28: Task G's apply rewrote Task F's read rows (5e10948)",
    "tests/test_changelog_currency.py": "2026-10-28: commits with no CHANGELOG entry (db8aeb7, af2c2ca)",
    "tests/test_f65_dirac3s_reading.py": "2026-10-22: F92's Dirac-3 assertions not classed (Issue #116)",
}


def _run_suite():
    spec = importlib.util.spec_from_file_location("run_suite", ROOT / "scripts" / "run_suite.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def first_sentence(text: str) -> str:
    try:
        doc = ast.get_docstring(ast.parse(text)) or ""
    except SyntaxError:
        doc = ""
    flat = " ".join(doc.split())
    m = re.match(r"(.+?[.!?])(\s|$)", flat)
    return (m[1] if m else flat)[:240]


def kind(path: str, text: str, rs) -> str:
    if "live_store" in text:
        return "live-store data check"
    if ".claude/hooks/" in text.replace("\\", "/") or '"hooks"' in text:
        return "hook check"
    if path in rs.DOC_GUARDS or re.search(r"""["']docs["']|docs/[\w/]+\.md""", text):
        return "document check"
    if path in (*rs.MANIFEST_GUARDS, *rs.SCRIPT_GUARDS, *rs.TEST_GUARDS):
        return "guard"
    return "unit"


def trigger(path: str, rs) -> str:
    if path in rs.DOC_GUARDS:
        return "any document change"
    if path in rs.MANIFEST_GUARDS:
        return "any manifest change"
    if path in rs.SCRIPT_GUARDS:
        return "any script change"
    if path in rs.TEST_GUARDS:
        return "any test change"
    return "a change it names"


def junit_times(junit: Path) -> dict[str, tuple[int, float]]:
    """test file -> (tests, seconds) from a pytest JUnit XML file."""
    out: dict[str, list] = defaultdict(lambda: [0, 0.0])
    for case in ET.parse(junit).getroot().iter("testcase"):
        module = (case.get("classname") or "").split(".")
        name = next((f"tests/{m}.py" for m in module if m.startswith("test_")), None)
        if name:
            out[name][0] += 1
            out[name][1] += float(case.get("time") or 0)
    return {k: (v[0], round(v[1], 2)) for k, v in out.items()}


def _unmarked(text: str) -> str:
    """The file's text with every test under a live_store marker removed (a module-level pytestmark marks all)."""
    if re.search(r"^pytestmark\s*=.*live_store", text, re.MULTILINE):
        return ""
    return re.sub(r"@pytest\.mark\.live_store\s*\n(\s*@[^\n]*\n)*\s*def test_\w+", "", text)


def inventory(junit: Path | None = None) -> list[dict]:
    rs = _run_suite()
    times = junit_times(junit) if junit else {}
    rows = []
    for f in sorted((ROOT / "tests").glob("test_*.py")):
        path = f"tests/{f.name}"
        text = f.read_text(encoding="utf-8", errors="replace")
        k = kind(path, text, rs)
        tests, seconds = times.get(path, (None, None))
        ci = re.search(r"^def test_", _unmarked(text), re.MULTILINE) is not None
        rows.append({"file": path, "guards": first_sentence(text), "kind": k, "tests": tests, "seconds": seconds,
                     "runs": {"full": True, "ci": ci, "changed": trigger(path, rs)},
                     "red_proof_recorded": bool(PROVEN.search(text)), "last_caught": CAUGHT.get(path)})
    return rows


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    junit = Path(args[args.index("--junit") + 1]) if "--junit" in args else None
    rows = inventory(junit)
    by_kind = defaultdict(lambda: [0, 0.0])
    for r in rows:
        by_kind[r["kind"]][0] += 1
        by_kind[r["kind"]][1] += r["seconds"] or 0
    for k, (n, s) in sorted(by_kind.items(), key=lambda x: -x[1][1]):
        print(f"{k}: {n} files, {s:,.0f} s")
    print(f"{len(rows)} test files; red proof recorded in {sum(r['red_proof_recorded'] for r in rows)}; "
          f"run on CI {sum(r['runs']['ci'] for r in rows)}")
    if "--write" in args:
        timings = (f"pytest --durations=0 --junitxml, full suite, {datetime.fromtimestamp(junit.stat().st_mtime):%Y-%m-%d}"
                   f" (a snapshot: the seconds are that run's)" if junit else "none")
        OUT.write_text(json.dumps({"generated_by": "scripts/test_inventory.py", "timings_from": timings, "rows": rows},
                                  indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
