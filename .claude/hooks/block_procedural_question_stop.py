"""Stop hook enforcing the sprint auto-advance window (Sprint 4 Task I, F15).

SPRINT_EXECUTION_WORKFLOW.md, Invariant 1: between Phase 3.7 approval and
the start of Phase 5's team-lead validation, do NOT ask permission at task
or phase boundaries; state the next action in one sentence and execute.
Before approval, asking is REQUIRED. From validation onward, asking is
CORRECT.

That rule lived only in prose, and this repository has already paid for a
prose-only rule of exactly this shape: the AskUserQuestion ban was violated
twice in one Sprint 2 session before `block_ask_user_question.py` made it
mechanical. Modeled on spamfilter-multi's `sprint-auto-advance.ps1`
(read-only source, 2026-09-18 survey), rewritten in Python for this
repository's own hook convention and with its own fixture set
(tests/test_block_procedural_question_stop.py).

Blocks a stop only when ALL of these hold:
  1. the branch matches ^feature/<digits>_Sprint_<N>;
  2. .claude/sprint_status.json has plan_approved true AND a Phase 4 status
     ("Phase 4.1 Execution -- ..." or the older "phase_4_execution")
     (the window: approved, executing, not yet at Phase 5);
  3. the plan document named by plan_doc exists;
  4. the last assistant message ends in a procedural question ("shall I",
     "want me to", "should I proceed", a bare "next:", a final paragraph
     ending in "?") AND does not cite a named SPRINT_STOPPING_CRITERIA.md
     criterion ("Criterion N", the "STOP:" template, "Class 1|2|3
     decision", "BLOCKED", "Manual Validation").

Outside the window the hook is silent: pre-approval and Phase 5+ questions
are correct, and a message that cites a criterion is a legitimate stop.

Exit 0 = allow stop. Exit 2 = block with guidance on stderr.
Bypass: branch name containing allow_stop_hook_bypass (same token as
verify_closeout_complete.py). Payload keys repo_override and branch_override
let tests run the hook against a scratch repository.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BRANCH_PATTERN = re.compile(r"^feature/\d+_Sprint_(\d+)")

# The window: plan approved and a Phase 4 status. Phase 5 (validation) and
# later are outside it, as is anything before approval. The phase number is
# read from either status form: "Phase 4.1 Execution -- ..." (the footer's
# format, one format since Sprint 7 retrospective I6) or the older
# "phase_4_execution". A "phase_4" prefix check read "Phase 4.1" as outside
# the window, which would have silenced this hook without a sign.
WINDOW_PHASE = 4
PHASE_NUMBER = re.compile(r"(?i)^\s*phase[ _](\d+)(?=[._ ]|$)")


def phase_number(status: str) -> int | None:
    m = PHASE_NUMBER.match(status)
    return int(m.group(1)) if m else None

# A message that names a stopping criterion (or one of the workflow's other
# sanctioned stop shapes) is allowed to stop even if it asks a question.
CRITERION_PATTERNS = [
    re.compile(r"(?i)\b(stopping\s+)?criterion\s+\d+\b"),
    re.compile(r"(?m)^\s*STOP:"),
    re.compile(r"(?i)\bclass[ -]?[123]\b"),
    re.compile(r"\bBLOCKED\b"),
    re.compile(r"(?i)\bblocked\s+precondition\b"),
    re.compile(r"(?i)\bmanual\s+validation\b"),
]

# Procedural-question shapes, scanned over the tail of the message.
QUESTION_PATTERNS = [
    re.compile(r"(?i)\bwant\s+me\s+to\b"),
    re.compile(r"(?i)\bshall\s+i\b"),
    re.compile(r"(?i)\bshould\s+i\s+(proceed|continue|go\s+ahead|start|move)\b"),
    re.compile(r"(?i)\blet\s+me\s+know\s+(if|when|whether|which|how)\b"),
    re.compile(r"(?i)\bready\s+to\s+proceed\b"),
    re.compile(r"(?i)\bwould\s+you\s+like\b"),
    re.compile(r"(?i)\bdo\s+you\s+want\b"),
    re.compile(r"(?im)^\s*next:\s*$"),
]

NUMBERED_LINE = re.compile(r"^\s*\d+[.)]\s+")


def _run(args: list[str], cwd: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=15)
        return proc.returncode, proc.stdout
    except Exception:
        return 1, ""


def _last_message(payload: dict) -> str:
    try:
        if payload.get("last_assistant_message"):
            return str(payload["last_assistant_message"])
        if payload.get("messages"):
            assistant_msgs = [m for m in payload["messages"] if m.get("role") == "assistant"]
            if assistant_msgs:
                return str(assistant_msgs[-1].get("content", ""))
    except Exception:
        return ""
    return ""


def _paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _tail(text: str) -> list[str]:
    """The final non-empty paragraph, plus the one before it when the final
    paragraph is a numbered list (a "Proceed to Task C?" followed by
    "1. Yes  2. No" is still a question, and the "?" is on the paragraph
    ABOVE the list -- checked per paragraph, not on the joined text)."""
    paras = _paragraphs(text)
    if not paras:
        return []
    tail = [paras[-1]]
    lines = [ln for ln in paras[-1].splitlines() if ln.strip()]
    if lines and all(NUMBERED_LINE.match(ln) for ln in lines) and len(paras) >= 2:
        tail.insert(0, paras[-2])
    return tail


def cites_criterion(message: str) -> bool:
    return any(p.search(message) for p in CRITERION_PATTERNS)


def ends_in_procedural_question(message: str) -> bool:
    tail = _tail(message)
    if not tail:
        return False
    if any(p.rstrip().endswith("?") for p in tail):
        return True
    joined = "\n\n".join(tail)
    return any(p.search(joined) for p in QUESTION_PATTERNS)


def _in_window(repo: Path) -> tuple[bool, str]:
    """(inside_window, reason). Every failure to establish the window is an
    allow: the hook fires only on a state it can positively read."""
    status_path = repo / ".claude" / "sprint_status.json"
    if not status_path.exists():
        return False, "no sprint_status.json"
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
        current = status["current_sprint"]
    except Exception:
        return False, "sprint_status.json unreadable"
    if not isinstance(current, dict):
        return False, "current_sprint is not an object"
    if current.get("plan_approved") is not True:
        return False, "plan not approved"
    phase = str(current.get("status") or "")
    if phase_number(phase) != WINDOW_PHASE:
        return False, f"status {phase!r} is outside Phase 4"
    plan_doc = current.get("plan_doc")
    if not plan_doc or not (repo / str(plan_doc)).exists():
        return False, "plan_doc missing"
    return True, f"plan approved, status {phase}, {plan_doc} present"


def main() -> int:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    cwd = str(payload.get("cwd") or Path.cwd())
    if payload.get("repo_override"):
        cwd = str(payload["repo_override"])
    repo = Path(cwd)

    message = _last_message(payload)
    if not message:
        return 0

    branch_override = payload.get("branch_override")
    if branch_override:
        branch = str(branch_override).strip()
    else:
        _, out = _run(["git", "-C", cwd, "branch", "--show-current"], cwd)
        branch = out.strip()
    if not branch:
        return 0
    if "allow_stop_hook_bypass" in branch:
        return 0
    if not BRANCH_PATTERN.match(branch):
        return 0

    inside, reason = _in_window(repo)
    if not inside:
        return 0

    if cites_criterion(message):
        return 0
    if not ends_in_procedural_question(message):
        return 0

    print(
        "[BLOCKED by block_procedural_question_stop hook]\n"
        "\n"
        f"The sprint is inside the auto-advance window ({reason}) and the final\n"
        "message ends in a procedural question with no stopping criterion cited.\n"
        "\n"
        "SPRINT_EXECUTION_WORKFLOW.md Invariant 1: between Phase 3.7 approval and\n"
        "Phase 5 manual validation, do NOT ask permission at task or phase\n"
        "boundaries. State the next action in one sentence and execute it.\n"
        "\n"
        "If a stop is genuinely required, say which SPRINT_STOPPING_CRITERIA.md\n"
        "criterion applies, by number (\"Criterion 2: BLOCKED ...\", a \"STOP:\"\n"
        "template, or a \"Class 1/2/3 decision\" with a plain numbered list), and\n"
        "the hook allows the stop. \"Confirming the next step\" is not a criterion.\n"
        "\n"
        "Bypass (team-lead-sanctioned only): rename the branch to include\n"
        "allow_stop_hook_bypass.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
