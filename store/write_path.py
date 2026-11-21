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

import ast
import inspect
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

# Each problem a new script can have, by the rule it breaks. Names, not
# calls, so an aliased import (`import insert_assertion as ins`) or an
# attribute reference is caught too (fresh-eyes review, 2026-10-21);
# `insert_verified_assertion` does not match.
# Since Sprint 13 Phase 5.3 (team lead, 2026-10-25: "q2 fix now before reading any more papers") the rule reads
# the parsed code (ast), not its text: a comment is not code, a call is a call node (a "low_grade(" in a string is
# not one), and a "#" inside a string hides nothing. That closes the three bypasses the fresh-eyes reviews of f782e53
# and ce2412e found. Names and quoted grades inside string and bytes constants still count, as the text rule
# counted them (the reviews of ed53933, 6173bad and b6cdcd0), so a docstring naming insert_assertion is refused.
_DIRECT_WRITE = re.compile(r"^(insert|sync)_assertion$")
_TOKEN_NAME = re.compile(r"^Verified$")
_WRITES = re.compile(r"^(insert|sync)_(verified_)?assertion$")
_EDIT_TABLE = re.compile(r"^(VALUE|QUOTE|CONTEXT)_[A-Z_]+$")
# A reading script's HIGH comes only from store.grading, with its basis
# (Sprint 11 retrospective I3, built in Sprint 12 Task G): no literal
# "high" of its own, in a grade table or a certainty argument.
# Its LOW names a reason through store.grading.low_grade too (Sprint 12
# retrospective I2, built in Sprint 13 Task F): no "Started LOW" text of its own.
# The fresh-eyes review of dd620c7: "Started " + "LOW" and a bare ("low", reason) passed; a literal "low" is
# refused as a literal "high" is, and an aliased import of low_grade counts.
# The fresh-eyes review of cec6020: the import line alone passed, so a CALL is required.
# Closed 2026-10-25 by the parse: "low_grade(" in a string or a docstring is not a call; a low_grade (or
# high_grades) the script defines or assigns for itself is refused, and only names imported from store.grading
# count; a "#" in a string no longer hides the rest of its line. Known limits, still not closed: a LOW built by
# concatenation with no quoted "low" ('LO' + 'W', or 'LOW'.lower()) passes; a reading script that compares a
# literal 'low' (a count) is refused.
_GRADING = "store.grading"
# A grade quoted inside a string (exec("g='high'")), as the 1980406 text rule read it (the review of b6cdcd0).
_QUOTED = re.compile(r"""["'](high|low)["']""")


class _Code:
    """What the rule reads from one script: its names, its calls, its string constants and its module-level
    table names, each from the parsed code."""

    def __init__(self, tree: ast.AST):
        self.names: set[str] = set()
        self.strings: list[str] = []
        self.called: set[str] = set()
        self.defined: set[str] = set()
        self.grading_modules: set[str] = set()
        self.from_grading: dict[str, str] = {}  # local name -> the store.grading name it binds
        self.tables: set[str] = set()
        for node in getattr(tree, "body", []):
            for target in self._targets(node):
                self.tables.add(target)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                self.names.add(node.id)
                if isinstance(node.ctx, ast.Store):
                    self.defined.add(node.id)
            elif isinstance(node, ast.Attribute):
                self.names.add(node.attr)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.defined.add(node.name)
            elif isinstance(node, ast.arg):
                self.defined.add(node.arg)
            elif isinstance(node, ast.alias):
                self.names.add(node.name.rsplit(".", 1)[-1])
                if node.asname:
                    self.names.add(node.asname)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                self.strings.append(node.value)
            elif isinstance(node, ast.Constant) and isinstance(node.value, bytes):
                self.strings.append(node.value.decode("latin-1"))  # the review of b6cdcd0: eval(b'...') too
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    local = alias.asname or alias.name
                    if node.module == _GRADING:
                        self.from_grading[local] = alias.name
                    elif node.module == "store" and alias.name == "grading":
                        self.grading_modules.add(local)
                    else:
                        self.defined.add(local)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == _GRADING:
                        self.grading_modules.add(alias.asname or _GRADING)
                    elif alias.asname:
                        self.defined.add(alias.asname)
            elif isinstance(node, ast.Call):
                self.called.add(self._callee(node.func))

    @staticmethod
    def _targets(node: ast.AST) -> list[str]:
        if isinstance(node, ast.Assign):
            return [t.id for t in node.targets if isinstance(t, ast.Name)]
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            return [node.target.id]
        return []

    def _callee(self, func: ast.AST) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            owner = ast.unparse(func.value)
            return f"{owner}.{func.attr}"
        return ""

    def calls_grading(self, name: str) -> bool:
        """A call of store.grading's `name`, under the name it was imported as or through the module, and
        never of a function the script binds for itself under that name."""
        local = {k for k, v in self.from_grading.items() if v == name}
        if local & self.defined or name in self.defined:
            return False
        return bool(local & self.called) or any(f"{m}.{name}" in self.called for m in self.grading_modules) \
            or f"store.grading.{name}" in self.called

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
# F147 (Sprint 18 Task B, team lead q2 = a, 2026-11-19): a stored assertion is synced only through
# store.ingest.sync_decided_assertion, which refuses a field no review decided before it is written. The one-time
# appliers of Sprints 11 to 17 that call sync_verified_assertion have run, and are frozen as they are: this list is
# closed. The 6 one-time appliers of Sprints 9 and 10 call sync_assertion and are LEGACY (above); the rule refuses
# sync_assertion in every other script. A new script that names sync_verified_assertion is refused, so it cannot be
# added here by copying an old applier. full_read_apply.py, the live applier, is not on it. tests/test_sync_decided.py
# checks that each name here still calls sync_verified_assertion (fresh-eyes review of Task B: a frozen name that does
# not would let a later edit add a direct sync unseen).
SYNC_FROZEN = frozenset({
    "sprint11_f91_magic_state.py", "sprint11_f92_qci_answers.py", "sprint11_f93_f108_ceiling.py",
    "sprint11_reading.py", "sprint12_f101_corrections.py", "sprint12_f102_phase2_sprint28.py",
    "sprint12_f103_intake.py", "sprint12_reading.py", "sprint13_f108_phase2.py", "sprint13_reading.py",
    "sprint14_f119_reading.py", "sprint14_f120_phase2.py", "sprint15_f130_phase2.py", "sprint16_f51_cvqboost.py",
    "sprint17_q23_corrections.py", "sprint17_q29_q31_grades.py",
})
_UNDECIDED_SYNC = re.compile(r"^sync_verified_assertion$")


def script_problems(text: str, name: str = "") -> list[str]:
    try:
        code = _Code(ast.parse(text))
    except SyntaxError as e:
        return [f"does not parse, so the write-path rule cannot read it ({e.msg}, line {e.lineno})"]
    out = []
    # A name spelled inside a string counts as the name (the fresh-eyes reviews of ed53933 and 6173bad:
    # getattr(d, 'insert_assertion'), eval('store.ingest.insert_assertion') and exec('insert_assertion(...)')
    # passed the parse, and the text rule had refused each).
    named = code.names | {w for s in code.strings for w in re.findall(r"[A-Za-z_]\w*", s)}
    writes = any(_WRITES.match(n) for n in named)
    if "reading" in name and name not in GRADING_LEGACY and writes:
        if not code.calls_grading("high_grades") or "high" in code.strings \
                or any("high" in _QUOTED.findall(s) for s in code.strings):
            out.append("grades HIGH outside store.grading (a reading script names each HIGH's basis through "
                       "high_grades and grade, and holds no literal \"high\")")
        if not code.calls_grading("low_grade") or "low" in code.strings \
                or any("low" in _QUOTED.findall(s) for s in code.strings) \
                or any("Started LOW" in s for s in code.strings):
            out.append("grades LOW outside store.grading (a reading script names each LOW's reason through "
                       "low_grade, and holds no \"Started LOW\" text of its own)")
    if any(_DIRECT_WRITE.match(n) for n in named):
        out.append("writes an assertion without the quote check (use insert_verified_assertion)")
    if name not in SYNC_FROZEN and any(_UNDECIDED_SYNC.match(n) for n in named):
        out.append("syncs a stored assertion without the review's decided fields (use sync_decided_assertion, "
                   "F147)")
    if any(_TOKEN_NAME.match(n) for n in named):
        out.append("names Verified (only require_verbatim makes one; pass on what it returns)")
    edit_basis = any(c == "require_edit_basis" or c.endswith(".require_edit_basis") for c in code.called)
    # A table name inside a string counts too (the review of a3b8074: exec('VALUE_A = {}') passed the parse).
    tables = code.tables | {w for s in code.strings for w in re.findall(r"(?m)^\s*([A-Z_]+)\s*[:=]", s)}
    if writes and any(_EDIT_TABLE.match(t) for t in tables) and not edit_basis:
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
