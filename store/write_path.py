"""The static write-path rule for scripts in scripts/, and the gate that
runs it before a store write (Sprint 11 retrospective I1b, 2026-10-23).

The rule came from Sprint 10's retrospective (I1 and I2) and lived in
tests/test_verified_writes.py, so it ran only with the full suite. In
Sprint 11 Tasks F and G were applied to the live store first, and the
suite found the missing `require_edit_basis` only afterwards. Now
`store.backup.backup_before_write`, which every `--apply` calls before it
writes, runs the same rule on the calling script and refuses on a problem,
so the scan comes before the write instead of after it. The test still
scans every script, so a problem is also found at the desk without an
apply.
"""
from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

# Each problem a new script can have, by the rule it breaks. Names, not
# calls, so an aliased import (`import insert_assertion as ins`) or an
# attribute reference is caught too (fresh-eyes review, 2026-10-21);
# `insert_verified_assertion` does not match. Comments are not code.
_DIRECT_WRITE = re.compile(r"\b(insert|sync)_assertion\b")
_TOKEN_NAME = re.compile(r"\bVerified\b")
_WRITES = re.compile(r"\b(insert|sync)_(verified_)?assertion\b")
_EDIT_TABLE = re.compile(r"(?m)^(VALUE|QUOTE|CONTEXT)_[A-Z_]+\s*[:=]")
# A reading script's HIGH comes only from store.grading, with its basis
# (Sprint 11 retrospective I3, built in Sprint 12 Task G): no literal
# "high" of its own, in a grade table or a certainty argument.
_HIGH_LITERAL = re.compile(r"""["']high["']""")
# Its LOW names a reason through store.grading.low_grade too (Sprint 12
# retrospective I2, built in Sprint 13 Task F): no "Started LOW" text of its own.
# The fresh-eyes review of dd620c7: "Started " + "LOW" and a bare ("low", reason) passed; a literal "low" is
# refused as a literal "high" is, and an aliased import of low_grade counts.
# The fresh-eyes review of cec6020: matching the bare name let the import line alone pass, so a CALL is required,
# of low_grade or of the name it is imported as. Known limits, not closed: a LOW built by concatenation with no
# quoted "low" ('LO' + 'W', or 'LOW'.lower()) passes; a reading script that compares a literal 'low' (a
# count) is refused. The fresh-eyes review of f782e53 found two more, also not closed: "low_grade(" inside a
# string or a docstring counts as a call, and so does a call to a low_grade the script defines for itself. The
# fresh-eyes review of ce2412e found a third, not closed: comments are stripped with "#.*" before the LOW checks,
# so a "#" inside a string literal hides the rest of that line from them.
_LOW_LITERAL = re.compile(r"""Started LOW|["']low["']""")
_LOW_ALIAS = re.compile(r"\blow_grade\s+as\s+(\w+)")


def _calls_low_grade(code: str) -> bool:
    names = {"low_grade", *_LOW_ALIAS.findall(code)}
    return any(re.search(rf"\b{n}\s*\(", code) for n in names)

# The scripts written before this rule (Sprint 10 and earlier). They have
# run, and stay as they are; every other script in scripts/ is held to it,
# whatever its name.
LEGACY = {
    "ingest_hsbc_b1_variable_count.py", "ingest_lenat_marcus.py", "sprint4_task_h_extraction.py",
    "sprint5_task_i_pilot.py", "sprint6_mv_dirac3_fidelity.py", "sprint6_task_g_cyc_and_facts.py",
    "sprint7_f44_cycorp_papers.py", "sprint7_f45_dirac3_reading.py", "sprint8_f65_dirac3s_reading.py",
    "sprint8_f71_qci_dirac3s_reading.py", "sprint9_f46_pending_facts.py", "sprint9_f78_ceiling_reading.py",
    "sprint9_f79_phase2_b4_b5_inbound.py", "sprint9_f80_reading.py", "sprint10_f83_optimization_bounds.py",
    "sprint10_f84_dirac1.py", "sprint10_f85_dirac3s_verify.py", "sprint10_f89_reading.py",
}
# Reading scripts written before the grading rule: they have run, and stay
# as they are. Every other script whose name says it reads is held to it.
GRADING_LEGACY = {"sprint11_reading.py"}


def script_problems(text: str, name: str = "") -> list[str]:
    code = re.sub(r"#.*", "", text)
    out = []
    if "reading" in name and name not in GRADING_LEGACY and _WRITES.search(code):
        if "high_grades(" not in code or _HIGH_LITERAL.search(code):
            out.append("grades HIGH outside store.grading (a reading script names each HIGH's basis through "
                       "high_grades and grade, and holds no literal \"high\")")
        if not _calls_low_grade(code) or _LOW_LITERAL.search(code):
            out.append("grades LOW outside store.grading (a reading script names each LOW's reason through "
                       "low_grade, and holds no \"Started LOW\" text of its own)")
    if _DIRECT_WRITE.search(code):
        out.append("writes an assertion without the quote check (use insert_verified_assertion)")
    if _TOKEN_NAME.search(code):
        out.append("names Verified (only require_verbatim makes one; pass on what it returns)")
    if _WRITES.search(code) and _EDIT_TABLE.search(code) and "require_edit_basis(" not in code:
        out.append("edits readers' values, quotes or contexts without require_edit_basis")
    return out


def calling_scripts() -> set[Path]:
    """The scripts in scripts/ on the call stack, and the one run as
    __main__: a script run from the shell, or a script's `main()` called
    in-process by a test."""
    files = {Path(f.filename).resolve() for f in inspect.stack(0)}
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    if main:
        files.add(Path(main).resolve())
    return {f for f in files if f.parent == SCRIPTS and f.suffix == ".py"}


def require_clean_callers() -> None:
    """Refuse, before anything is written, a store write made from a
    script that breaks the write-path rule."""
    for script in sorted(calling_scripts()):
        if script.name in LEGACY:
            continue
        problems = script_problems(script.read_text(encoding="utf-8"), script.name)
        if problems:
            raise RuntimeError(f"{script.name}: refused before the backup and the write "
                               f"(store.write_path, Sprint 11 retrospective I1b): {'; '.join(problems)}")
