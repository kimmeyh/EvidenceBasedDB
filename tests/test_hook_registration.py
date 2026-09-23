"""Every registered hook must actually resolve to a file on disk.

F68. Two hooks were registered in `.claude/settings.json` and NEVER RAN. The
file held `\\hooks\\block-...` with a single backslash before `b`, which JSON
parses as U+0008 BACKSPACE, so the path resolved to `hooks<BS>lock-...`. That
file does not exist, and Claude Code skips a hook whose file is missing without
saying anything.

Broken since the commit that created them. The Sprint 13 retrospective recorded
that the Class 4 submission-edit hook "worked exactly as designed"; it had never
executed once, and every submission-document edit that sprint was unguarded. The
process held because the team lead approved each change in conversation, not
because anything enforced it.

WHY THIS IS THE RIGHT GUARD. The defect is invisible from the inside: a hook
that never fires looks exactly like a hook that fires and permits. Nothing in
the edit's behaviour distinguishes them, so no amount of care while editing
would have caught it. What separates the two cases is whether the registered
path exists, which is a fact about the filesystem and is cheap to assert.

This is also the F48 defect class -- a silent escape corruption -- living in the
file that registers the guard against it.

Verified by injection: reverting one registration to the single-backslash form
fails `test_every_registered_hook_path_resolves` with the offending name, and
`test_no_hook_command_contains_a_control_character` names the control character.
Restoring the doubled backslash passes both.

CONVERTED TO PYTHON, 2026-09-14. The hooks themselves moved from PowerShell to
Python (QUALITY_STANDARDS.md amendment, same date) and their command strings
now use forward slashes, which sidesteps the doubled-backslash JSON escape
that caused F68 -- forward slashes need no escaping either as a Windows path or
as a JSON string. The two guard tests below are UNCHANGED and still pass: they
assert on whatever separator style is actually present, not on backslashes
specifically, so they keep guarding the defect class even though this
repository no longer needs the doubling they were written to check.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / ".claude" / "settings.json"


def _hook_commands() -> list[tuple[str, str]]:
    """(matcher, command) for every registered hook, on EVERY event.

    Until 2026-09-19 (Sprint 4 Task I) this walked PreToolUse only, so the
    Stop hooks were never checked for a resolvable path or a control
    character -- the exact silent-skip class this file exists to catch,
    unguarded on the event verify_closeout_complete.py lives on. Now walks
    every event group so a Stop hook registered against a missing file is
    named the same way a PreToolUse one is.
    """
    if not SETTINGS.exists():
        return []
    cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    out: list[tuple[str, str]] = []
    for event_groups in cfg.get("hooks", {}).values():
        for group in event_groups:
            matcher = group.get("matcher", "<none>")
            for hook in group.get("hooks", []):
                cmd = hook.get("command")
                if cmd:
                    out.append((matcher, cmd))
    return out


def _matchers_for(event: str, filename: str) -> list[str]:
    """The matcher of every group under `event` that registers `filename`."""
    cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    return [
        group.get("matcher", "")
        for group in cfg.get("hooks", {}).get(event, [])
        for hook in group.get("hooks", [])
        if filename in (hook.get("command") or "")
    ]


def _script_path(command: str) -> Path | None:
    """The script argument of a hook command, resolved against the repo root.

    Separators are NORMALISED to forward slashes after substitution, which
    matters even now that hook commands are `python "path/with/forward/
    slashes.py"` (converted 2026-09-14 from PowerShell `-File` invocations):
    a POSIX filesystem reads a backslash as a literal filename character
    rather than a separator, so `Path(tail).exists()` is unconditionally
    False on Linux and macOS for any command that still carries one.

    Recognises both forms so a future PowerShell hook (or one not yet
    converted) is still checked: the PowerShell `-File <path>` marker, and a
    bare `python "<path>"` / `python3 "<path>"` invocation.

    Found by Copilot on PR #94. CI runs ubuntu-latest, so the first version of
    this guard would have turned CI red for exactly the fresh-clone audience the
    sprint was written to serve: a test asserting that hooks resolve, failing
    because it could not resolve them itself.
    """
    marker = "-File "
    if marker in command:
        tail = command.split(marker, 1)[1].strip().strip('"')
    else:
        m = re.match(r'^\s*python[0-9.]*(?:\.exe)?\s+"([^"]+)"', command)
        if not m:
            return None
        tail = m.group(1)
    tail = tail.replace("${CLAUDE_PROJECT_DIR}", str(ROOT))
    return Path(tail.replace("\\", "/"))


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_every_registered_hook_path_resolves():
    """A hook whose file is missing is skipped silently, so it must exist."""
    missing: list[str] = []
    for matcher, cmd in _hook_commands():
        path = _script_path(cmd)
        if path is None:
            continue                      # not a -File invocation; nothing to check
        if not path.exists():
            missing.append(f"{matcher}: {path}")
    assert not missing, (
        "these hooks are registered but their files do not exist, so Claude Code "
        f"skips them WITHOUT ERROR: {missing}. Two hooks were dead this way from "
        "the moment they were written, and a retrospective recorded one of them "
        "as working.")


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_no_hook_command_contains_a_control_character():
    """The specific corruption that killed two hooks, caught at its cause.

    `\\b` in a JSON string is a backspace, not a path separator. The path still
    LOOKS right in an editor that renders the control character as nothing,
    which is why the previous test checks existence and this one checks the
    cause: they fail for different reasons and a reader needs the second to
    understand the first.
    """
    bad: list[str] = []
    for matcher, cmd in _hook_commands():
        for ch in cmd:
            if ord(ch) < 32:
                bad.append(f"{matcher}: U+{ord(ch):04X} in {cmd!r}")
                break
    assert not bad, (
        "a hook command contains a control character, which means a backslash "
        f"escape was consumed by the JSON parser: {bad}. In the raw file a "
        "Windows path separator must be a DOUBLED backslash.")


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_the_guards_this_repository_depends_on_are_registered():
    """The hooks must be PRESENT, not merely valid paths.

    The two tests above would pass a settings file with no hooks at all.

    ADAPTED AT SEEDING, 2026-09-14. The source repository asserted on
    `block-unapproved-submission-edit.ps1` and `block-reactive-amendment.ps1`,
    which guard its frozen submission documents and its preregistration. Neither
    file exists here, and neither should: a hook guarding a missing artifact is
    a hook that cannot fire.

    What this repository depends on instead is the pair that prevents the
    silent-corruption class -- an escape eaten by a shell or a JSON parser --
    which is how two hooks in the source repository stayed dead for their entire
    life.

    When this repository gains its own frozen artifacts (a published export, a
    release tag), add them here rather than assuming the list is complete.

    Filenames updated 2026-09-14: the hooks converted from PowerShell to
    Python (QUALITY_STANDARDS.md amendment, same date), so the names this
    test looks for changed from `.ps1` to `.py` alongside them.

    block_sibling_repo_writes.py added 2026-09-15 (team lead: this session
    must not write into spamfilter-multi or hsbc-quantum-fraud-2026, read
    access only). Registered on both PreToolUse matchers, which is why this
    test's scan over every hook group (not a single matcher) matters here.

    The F15/F16/F17 hooks added 2026-09-19 (Sprint 4 Task I): the
    auto-advance-window Stop hook, the Phase 3.3.1 deliverables commit
    gate, and the mutation-lock commit gate. Each is a rule that lived only
    in prose before, which is this repository's named decay pattern.
    """
    commands = " ".join(c for _, c in _hook_commands())
    for required in ("block_unraw_escape.py",
                     "block_shell_metachar_expansion.py",
                     "block_sibling_repo_writes.py",
                     "block_ask_user_question.py",
                     "block_procedural_question_stop.py",
                     "block_missing_sprint_cards.py",
                     "block_commit_during_mutation.py"):
        assert required in commands, (
            f"{required} is not registered in .claude/settings.json. It guards "
            "the silent-corruption class: an escape consumed by a shell or a "
            "JSON parser, which produces a plausible wrong result rather than "
            "an error.")


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_ask_user_question_hook_is_on_its_own_matcher():
    """block_ask_user_question.py must fire on the AskUserQuestion tool
    itself, not merely exist somewhere in the file.

    Added 2026-09-17 (Sprint 2 retrospective improvement 2), after the
    AskUserQuestion ban lived only in CLAUDE.md and memory and was violated
    twice in one session anyway -- a rule present in a document decayed the
    moment it needed to be applied, which is this repository's own named
    pattern for every hook in the Inherited section of CLAUDE.md.
    """
    cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    matchers = [
        group.get("matcher", "")
        for group in cfg.get("hooks", {}).get("PreToolUse", [])
        for hook in group.get("hooks", [])
        if "block_ask_user_question.py" in (hook.get("command") or "")
    ]
    assert any("AskUserQuestion" in m for m in matchers), (
        f"block_ask_user_question.py is registered but not on an "
        f"AskUserQuestion matcher (found matchers: {matchers}), so it would "
        "never actually fire when the tool is called.")


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_procedural_question_stop_hook_is_on_the_stop_event():
    """block_procedural_question_stop.py (F15) reads the last assistant
    message, which only a Stop payload carries; registered anywhere else it
    would fire on tool calls with no message to inspect and allow every one.

    Verified by injection, 2026-09-19: moving its registration from the
    Stop group to the PreToolUse Bash|PowerShell group fails this test
    naming the empty matcher list, while the two path tests above stay
    green (the file still exists); restoring it passes.
    """
    matchers = _matchers_for("Stop", "block_procedural_question_stop.py")
    assert matchers, (
        "block_procedural_question_stop.py is not registered under the Stop "
        "event, so it would never see a last_assistant_message and never fire.")


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_missing_sprint_cards_hook_is_on_the_bash_matcher():
    """block_missing_sprint_cards.py (F16) inspects tool_input.command for a
    git commit, so it must sit on the PreToolUse Bash|PowerShell matcher.

    Verified by injection, 2026-09-19: removing its entry from the
    Bash|PowerShell group fails this test and
    test_the_guards_this_repository_depends_on_are_registered; restoring it
    passes both.
    """
    matchers = _matchers_for("PreToolUse", "block_missing_sprint_cards.py")
    assert any("Bash" in m and "PowerShell" in m for m in matchers), (
        f"block_missing_sprint_cards.py is not on a PreToolUse Bash|PowerShell "
        f"matcher (found: {matchers}), so it would never see a git commit.")


@pytest.mark.skipif(not SETTINGS.exists(), reason="no .claude/settings.json")
def test_commit_during_mutation_gate_is_on_the_bash_matcher():
    """block_commit_during_mutation.py (F17) inspects tool_input.command for
    a git commit, so it must sit on the PreToolUse Bash|PowerShell matcher.

    Verified by injection, 2026-09-19: removing its entry from the
    Bash|PowerShell group fails this test and
    test_the_guards_this_repository_depends_on_are_registered; restoring it
    passes both.
    """
    matchers = _matchers_for("PreToolUse", "block_commit_during_mutation.py")
    assert any("Bash" in m and "PowerShell" in m for m in matchers), (
        f"block_commit_during_mutation.py is not on a PreToolUse Bash|PowerShell "
        f"matcher (found: {matchers}), so it would never see a git commit.")


def test_every_registered_hook_is_time_bounded():
    """A hook with no timeout can hang tool execution indefinitely.

    Copilot review of PR #30, 2026-09-23: block_commit_with_piped_tests.py
    was registered without one while all nine other hooks had timeout=15.
    The gap was invisible because nothing compared the entries to each
    other.
    """
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    missing = []
    for event, matchers in settings.get("hooks", {}).items():
        for entry in matchers:
            for hook in entry.get("hooks", []):
                if "timeout" not in hook:
                    name = hook.get("command", "")[-60:]
                    missing.append(f"{event}: {name}")
    assert not missing, f"hooks registered with no timeout: {missing}"
