"""PreToolUse hook blocking Python string literals with a Windows path escape
outside a raw string. Sprint 10 retrospective improvement 1.

Converted 2026-09-14 from block-unraw-escape.ps1.

This failure has recurred five-plus times across sprints, twice in Sprint 10
alone. The shape is always the same: a heredoc'd Python snippet contains a
Windows path in a normal quoted string, e.g.

    p = 'D:\\Data\\Harold\\...'

Python reads \\D as an invalid escape (SyntaxWarning today, SyntaxError in a
future version) and \\x, \\u, \\N as hard errors. In Sprint 10 it produced a
silent wrong value once (a \\b became a backspace inside a JSON path, writing
the file to the wrong directory) and an outright crash twice.

A rule against it already exists and has not worked, because it depends on
remembering at the moment of writing. The sibling hooks (block-carry-forward-
stash, block-branch-from-develop) demonstrate that the mechanical check
succeeds where the remembered rule fails. This is the same treatment for the
same class of problem.

THE FIX IS ALWAYS THE SAME: prefix the literal with r, or use forward slashes.
Both are one keystroke.

Exit 0 = allow. Exit 2 = block; stderr fed back to Claude.
Bypass: literal token allow_unraw_escape, for the rare case where the escape
is deliberate (writing an actual tab or newline into a path string).
The escape check inspects only commands that run python.

Also blocks, on any command, a shell edit of a repository code file
(`sed -i`, `perl -i`, a redirect or `tee`, PowerShell Set-Content and its
kin onto a .py or .sql file; Sprint 8 retrospective I5), and an in-place
edit of ANY repository file (Sprint 11 retrospective I4). Bypass: the
literal token allow_shell_code_edit.
"""
from __future__ import annotations

import json
import re
import sys

# Anchor on an actual INVOCATION, not the bare substring. A bare substring
# test turns the scanner on for any command merely containing those letters:
# a path like C:/Python312/..., a filename test_python_paths.sh, `pip show
# python-dateutil`, or prose. During review of PR #58 it blocked a `gh api`
# call whose only Python content was example text inside the comment being
# posted.
# `py` is the Windows launcher (PR #77 review: `py -c` was not matched).
PYTHON_INVOCATION = re.compile(r"(?:^|[\s;&|(])(?:python[0-9.]*|py)(?:\.exe)?(?:\s|$)")

# EXACT Python string prefixes only. A substring test over an [A-Za-z]*
# capture lets an adjacent identifier ending in r -- str'...', dir'...',
# ptr'...' -- silence the block.
VALID_PREFIX = re.compile(r"(?i)^(?:r|rb|br|rf|fr)$")
QUOTED_LITERAL = re.compile(r"(?P<prefix>[A-Za-z]*)(?P<q>['\"])(?P<body>[^'\"]*)(?P=q)")

# A REAL drive-letter path: a SINGLE letter, a colon, a backslash, a letter.
# The leading letter must not be part of a longer word.
#
# Sprint 4 retrospective improvement 5. The previous pattern was
# `[A-Za-z]:\\[A-Za-z]`, which matches any letter-colon-backslash-letter, so
# ordinary prose ending in a colon before an escape matched on its last
# letter: "CITATION.cff:\n" matched as `f:\n`, "        if found:\n" as
# `d:\n`. Two legitimate commands carrying no Windows path at all were
# blocked that way in Sprint 4, and the block is mechanical, so there was no
# way past it except the bypass token. Diagnosed 2026-09-22 by printing the
# literal the hook flagged in each case, after two wrong guesses about the
# cause (a quote-boundary bug, then a segment-scoping bug); the evidence is
# what narrowed it, not the reasoning about it.
DRIVE_PATH = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:\\[A-Za-z]")


def _read_command() -> str:
    raw = sys.stdin.read()
    if not raw or not raw.strip():
        return ""
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return ""

    tool_input = payload.get("tool_input") if isinstance(payload, dict) else None
    if isinstance(tool_input, dict) and tool_input.get("command"):
        return str(tool_input["command"])
    if isinstance(payload, dict) and payload.get("command"):
        return str(payload["command"])
    return ""


# Sprint 5 retrospective improvement 2 (2026-09-25): the same class, one step
# on. Python source written THROUGH a Python string inside a shell command
# (`p='scripts/x.py'; s=open(p).read(); ...; open(p,'w').write(s)`) passes
# every escape through two interpreters. Sprint 5 broke files that way three
# times: a "\\n" meant for the target file became a real line break and left
# an unterminated string literal, found only when the file failed to parse.
# The Edit and Write tools take code verbatim and cannot do this.
# .sql too: I5 names it a code file (PR #77 review).
PY_FILE_LITERAL = re.compile(r"""['"][^'"\n]*\.(?:py|sql)['"]""")
WRITES_FILE = re.compile(r"""open\([^)]*['"]w['"]|\.write_text\(|\.write\(""")


def _writes_python_source(cmd: str) -> bool:
    return bool(PY_FILE_LITERAL.search(cmd) and WRITES_FILE.search(cmd))


# Sprint 8 retrospective I5 (2026-10-13): the same class, without Python.
# Two code lines were changed with `sed -i` in Sprint 8, against the rule
# that code files change only through Edit and Write (which show the change
# and take the text verbatim). The rule existed and was broken once, so it
# is now mechanical: an in-place `sed`/`perl`, a shell redirect or `tee`, or
# a PowerShell Set-Content/Add-Content/Out-File onto a repository .py or
# .sql file is blocked. Data is not scanned: heredoc bodies (a commit
# message, a script fed to python) and the quoted text of a -m, --message,
# --body, --title or --notes argument. A scratch file outside the
# repository is not blocked, nor is a relative path after a `cd` to a
# directory outside it.
#
# Fresh-eyes review of 2026-10-13 (seven shapes, each now in the tests): a
# `<<<` here-string opened a heredoc that never closed and hid every later
# line; sed after `xargs`, `env` or `bash -c "` escaped; `-0pi` escaped;
# `1>` and `&>` escaped; Set-Content's span ran past `;` and `|` onto a
# later .py; a `git commit -m` message was scanned; a `cd` out of the
# repository was ignored.
#
# Edge-case pass of 2026-10-13, after the review (each case in the tests):
# every code type the repository holds (.py, .sql, .yml, .ini) plus .yaml,
# .toml, .ps1 and .sh, in any case; `>|`, any fd digit (`2> x.py` writes it
# too); `tee` with options or several files; `dd of=`; `cp`, `mv`,
# `install`, Copy-Item and Move-Item onto code; `awk -i inplace` and
# `ruby -pi`; `sed -i''`; `find ... -exec sed -i` and `git ls-files '*.py'
# | xargs sed -i`, where the code path comes before the editor;
# [IO.File]::WriteAllText and its kin; New-Item -Value; PowerShell
# here-string bodies and `gh api -f body=...` values are data; a full-line
# `#` comment is not scanned; a `cd` is tracked in order, so a later `cd`
# back into the repository counts; the bypass token counts only outside
# data, so a commit message that names it does not open the gate.
#
# Known limits, not blocked: a copy into a directory (`cp a.txt store/`: the
# file's own name decides, and the hook does not see it), a target held in a
# variable (`sed -i ... "$f"`),
# `bash -c '...'` in single quotes (single-quoted text with a space is not
# read for redirects, so a `>` inside a sed or python expression is not
# taken as one), `patch`, and git's own restores (`git checkout -- x.py`,
# `git restore`), which return a file to a committed state. Blocked though
# harmless: a `>` before a code path inside double-quoted prose outside a
# message argument (`echo "a > store/x.py"`); the bypass token covers it.
HEREDOC_START = re.compile(r"(?<!<)<<(?!<)-?\s*['\"]?([A-Za-z_]\w*)['\"]?")
PS_HERE_STRING = re.compile(r"(?s)@(['\"])\r?\n.*?\r?\n\1@")
_EXT = r"\.(?:py|sql|ya?ml|ini|toml|ps1|sh)"
CODE_PATH = rf"""['"]?(?P<path>[^\s'"<>|;&]+{_EXT})['"]?(?=$|[\s;&|),])"""
CODE_ARG = re.compile(r"(?:^|[\s=])" + CODE_PATH, re.I)
_LEAD = r"(?:^|[;&|(\"`\n]|\{\}|\b(?:xargs|env|sudo|exec|command|nice|time)\s+(?:-\S+\s+|\S+=\S*\s+)*|-exec(?:dir)?\s+)"
# A quoted name runs too (`xargs "sed" -i`; Sprint 11 I4 edge case).
IN_PLACE_TOOL = re.compile(_LEAD + r"\s*(?P<tool>sed|perl|ruby|g?awk)[\"']?\s(?P<rest>[^\n]*)")
# -M and -I are perl's module and include switches (-Mstrict is not -i).
IN_PLACE_FLAG = re.compile(r"""(?:^|\s)(?:-(?![MI])[A-Za-z0-9]*i[A-Za-z0-9.'"]*|--in-place\S*)(?=\s|$)""")
COPY_ONTO = re.compile(_LEAD + r"\s*(?:cp|mv|install|Copy-Item|Move-Item|copy|move)\s(?P<rest>[^\n;&|]*)", re.I)
_PS_WRITE = r"\b(?:Set-Content|Add-Content|Out-File|sc|ac)\b"
_PS_PATH = r"-(?:Path|FilePath|LiteralPath)(?:\s+|:)"
# The target of a PowerShell write is its first positional argument or its
# -Path value, never a path named later on the line.
REDIRECT_ONTO = re.compile(
    r"(?:(?<![>=-])(?:\d|&)?>[>|]?|\bof=|"
    rf"{_PS_WRITE}(?:\s+{_PS_PATH})?\s|{_PS_WRITE}[^\n;|&]*?\s{_PS_PATH}|"
    r"\bNew-Item\b[^\n;|&]*?(?=[^\n;|&]*-Value)\s|"
    r"\[(?:System\.)?IO\.File\]::(?:WriteAll|AppendAll)\w*\(\s*)\s*" + CODE_PATH, re.I)
TEE = re.compile(r"\btee\b(?P<rest>[^\n;&|]*)")
# Data: the quoted value of a message, body or field argument.
MESSAGE_ARG = re.compile(r"""(?:^|\s)(?:-m|--message|--body|--title|--notes|--subject|-[fF]\s+\w+=|"""
                         r"""--(?:raw-)?field\s+\w+=)[\s=]*(?:"(?:[^"\\]|\\.)*"|'[^']*')""")
# Single-quoted text holding a space or a `>` is an expression or prose, not
# a path; a single-quoted lone path ('store/x.py') is still read.
SINGLE_QUOTED = re.compile(r"'[^'\n]*[\s>][^'\n]*'")
CD_TO = re.compile(r"""(?:^|[;&|(\n])\s*(?:cd|Set-Location|sl|pushd|Push-Location)\s+['"]?(?P<dir>[^\s'";&|)]+)""")
CODE_GLOB_SOURCE = re.compile(r"\b(?:find|ls-files|grep\s+-\w*l\w*|rg\s+-\w*l\w*|ls|dir|Get-ChildItem)\b[^\n;&]*?"
                              + CODE_PATH, re.I)


# Sprint 11 retrospective I4 (team lead, 2026-10-23: "'sed -i' usage has
# been eliminated as innefective and results in many errors. Suggest a way
# to do all of the 'sed -i' items a way that works successfully every
# time"). The way is the Edit tool, for every repository file, as
# spamfilter-multi's CLAUDE.md ("`sed` - Use the Edit tool instead") and
# Phase 2's TROUBLESHOOTING.md (Sprint 24 IMP-4) already say. So an
# in-place sed, perl, ruby or awk edit is blocked on ANY repository file,
# not only code; and the false blocks stop: a double-quoted search pattern
# of a search command (`grep -n "sed -i" docs/x.md; cat store/x.py`) is
# data, where before it opened an editor whose fail-closed search found the
# later .py. A quote opened by `bash -c`, `$(` or a backtick still runs.
ANY_ARG = re.compile(r"""(?:^|[\s=])['"]?(?P<path>(?!-)[^\s'"<>|;&]*\.[A-Za-z0-9]+)['"]?(?=$|[\s;&|),])""")
SEARCH_COMMANDS = {"grep", "egrep", "fgrep", "rg", "ag", "findstr", "select-string", "sls"}


def _searched_pattern(text: str, quote_at: int) -> bool:
    """Whether the double quote at `quote_at` opens an argument of a search
    command, whose text is a pattern and never runs."""
    line_start = text.rfind("\n", 0, quote_at) + 1
    segment = re.split(r"&&|\|\||[;|\n]|\$\(|`|\(", text[line_start:quote_at])[-1].split()
    if not segment:
        return False
    word = segment[0].lower().rsplit("/", 1)[-1].removesuffix(".exe")
    return word in SEARCH_COMMANDS or (word == "git" and len(segment) > 1 and segment[1] in ("grep", "log"))


SHELL_READS_HEREDOC = re.compile(r"(?:^|[\s;&|(])(?:bash|sh|zsh|dash|ksh|pwsh|powershell)(?:\.exe)?(?:\s+-\S+)*\s*$",
                                 re.I)
_TRUNCATE = re.compile(r"\btruncate\b[^\n;|&]*?\s" + CODE_PATH, re.I)


def _data_removed(cmd: str) -> str:
    """The command with its data taken out: heredoc bodies, PowerShell
    here-string bodies, message and field values, full-line comments."""
    cmd = PS_HERE_STRING.sub("''", cmd)
    lines, tag, body, runs_body = [], None, [], False
    for line in cmd.split("\n"):
        if tag is not None:
            if line.strip() == tag:
                if runs_body:
                    lines += body  # a shell runs this body: it is commands
                tag, body = None, []
            else:
                body.append(line)
            continue
        lines.append(line)
        m = HEREDOC_START.search(line)
        if m:
            tag = m.group(1)
            # PR #77 review: `bash <<EOF ... sed -i ... EOF` passed, because
            # the body was taken as data.
            runs_body = bool(SHELL_READS_HEREDOC.search(line[:m.start()]))
    # A heredoc that never closes was not one (a quoted `<<` in prose, say):
    # its "body" is command text and is scanned.
    kept = [ln for ln in lines + body if not ln.lstrip().startswith("#")]
    return MESSAGE_ARG.sub(" ''", "\n".join(kept))


def _absolute(path: str) -> bool:
    return bool(re.match(r"^(?:[A-Za-z]:[\\/]|/|~|\$)", path))


def _in_repository(path: str, outside_cwd: bool = False) -> bool:
    p = path.replace("\\", "/")
    if "CLAUDE_PROJECT_DIR" in p or "github/evidencebaseddb/" in p.lower().rstrip("/") + "/":
        return True
    return not outside_cwd and not _absolute(p)


_UNQUOTE = re.compile(r"""["']""")


def _own_command(rest: str, opened: str = "") -> str:
    """The editor's own command: `rest` up to the first `;`, `&` or `|`
    outside quotes. F81 (Sprint 10 Task A): the flag and target search ran
    over the whole line, so `sed -n 1,5p x.py; grep -i y z` read the later
    `grep -i` as `sed -i` and blocked a read. Quotes are tracked so a
    separator inside a sed or perl script (`'s/a/b/; s/c/d/'`) does not
    cut the command before its file.

    Task A review (2026-10-18; a fresh-eyes reviewer and the automated
    security review): a backslash escapes the next character outside single
    quotes (`\\;`, `\\"`); the `&` of a redirect (`2>&1`, `>&2`) is not a
    separator; nothing inside `$(...)` or backticks cuts. `opened` is the
    quote the editor already stands inside (`bash -c "sed -n 1p x.py" |
    ...`), so that quote's close ends the editor's command. A cut can still
    misjudge a shape this does not model, so the caller fails closed: the
    cut decides only whether the flag is present, never that no code file
    is named."""
    quote, depth, tick = opened, 0, False
    i = 0
    while i < len(rest):
        ch = rest[i]
        if ch == "\\" and quote != "'":
            i += 2
            continue
        if quote:
            if ch == quote:
                # The opened quote's close ends the editor's command only
                # where the shell word ends; `"sed "'-i ...'` is one word
                # (second security review of the Task A fix).
                if opened and rest[i + 1:i + 2] in ("", " ", "\t", ";", "&", "|", "\n"):
                    return rest[:i]
                opened = ""
                quote = ""
        elif ch in "'\"":
            quote = ch
        elif ch == "`":
            tick = not tick
        elif rest.startswith("$(", i):
            depth += 1
            i += 2
            continue
        elif ch == ")" and depth:
            depth -= 1
        elif depth or tick:
            pass
        elif ch == "&" and (rest[i - 1:i] in (">", "<") or rest[i + 1:i + 2] == ">"):
            pass
        elif ch in ";&|":
            return rest[:i]
        i += 1
    return rest


def _shell_edits_code(text: str) -> list[str]:
    # Each `cd` sets whether relative paths after it point outside the
    # repository, in command order.
    cds = [(m.start(), _absolute(m["dir"]) and not _in_repository(m["dir"])) for m in CD_TO.finditer(text)]

    def outside_at(pos: int) -> bool:
        state = False
        for at, out in cds:
            if at < pos:
                state = out
        return state

    def keep(m, base: int = 0) -> list[str]:
        # `base` places a match found inside an editor's own text back on the
        # line, where the `cd` positions are (Task A third security review:
        # they were compared as if both counted from the line's start).
        return [m["path"]] if _in_repository(m["path"], outside_at(base + m.start())) else []

    hits = []
    # Each match's `rest` runs to the end of the line, so a second editor on
    # the same line (`sed -n 1p a; sed -i ... x.py`) is searched for from
    # inside the first one's text, not after it (F81).
    tools, pos = [], 0
    while (m := IN_PLACE_TOOL.search(text, pos)):
        tools.append(m)
        pos = m.start("rest")
    for tool in tools:
        lead = text[tool.start():tool.start("tool")].strip()
        quote_at = tool.start() + text[tool.start():tool.start("tool")].rfind('"')
        if lead.endswith('"') and _searched_pattern(text, quote_at):
            continue  # a search pattern that mentions sed (I4)
        # Quotes join words in the shell (`"'-i` is the flag -i, `x'.py'` is
        # x.py, `in"place"` is inplace), so every check below reads the
        # command with its quote characters removed (Task A security reviews).
        rest = _UNQUOTE.sub("", _own_command(tool["rest"], '"' if lead.endswith('"') else ""))
        if not IN_PLACE_FLAG.search(rest) or (tool["tool"].endswith("awk") and "inplace" not in rest):
            continue
        base = tool.start("rest")
        # Any repository file, not only code (I4).
        targets = [p for m in ANY_ARG.finditer(rest) for p in keep(m, base)]
        if not targets:
            # Fail closed: the cut found the flag but no file, so the
            # whole line is searched (Task A review).
            targets = [p for m in ANY_ARG.finditer(_UNQUOTE.sub("", tool["rest"])) for p in keep(m, base)]
        if not targets:
            # The code path can come before the editor: find ... -exec sed -i,
            # git ls-files '*.py' | xargs sed -i.
            line_start = text.rfind("\n", 0, tool.start()) + 1
            segment = re.split(r"&&|\|\||;", text[line_start:tool.start()])[-1]
            targets = [p for m in CODE_GLOB_SOURCE.finditer(segment) for p in keep(m, tool.start() - len(segment))]
        hits += targets
    for cp in COPY_ONTO.finditer(text):
        operands = [m for m in CODE_ARG.finditer(cp["rest"])]
        tokens = [t for t in cp["rest"].split() if not t.startswith("-")]
        if operands and tokens and tokens[-1].strip("'\"").lower().endswith(operands[-1]["path"].lower()):
            hits += keep(operands[-1], cp.start("rest"))
    unquoted = SINGLE_QUOTED.sub(lambda m: " " * len(m.group(0)), text)
    hits += [p for m in REDIRECT_ONTO.finditer(unquoted) for p in keep(m)]
    hits += [p for t in TEE.finditer(unquoted) for m in CODE_ARG.finditer(t["rest"]) for p in keep(m, t.start("rest"))]
    hits += [p for m in _TRUNCATE.finditer(unquoted) for p in keep(m)]
    return list(dict.fromkeys(hits))


def main() -> int:
    try:
        cmd = _read_command()
    except Exception:
        return 0  # fail open on malformed payload

    if not cmd or not cmd.strip():
        return 0
    try:
        return _check(cmd)
    except Exception as ex:  # noqa: BLE001
        # Fail open, deliberately and visibly: a bug in this hook must not
        # block every command (PR #77 review: an exception here exited 1,
        # which also allows the command, but said nothing about why).
        print(f"[hook warning] block_unraw_escape.py could not check this command: {type(ex).__name__}: {ex}",
              file=sys.stderr)
        return 0


def _check(cmd: str) -> int:
    runs_python = PYTHON_INVOCATION.search(cmd)

    if runs_python and "allow_python_writes_code" not in cmd and _writes_python_source(cmd):
        print(
            "[BLOCKED] Python code rewriting a .py file from inside a shell command\n"
            "(Sprint 5 retrospective improvement 2).\n"
            "\n"
            "Escapes pass through two interpreters here: a \"\\n\" meant for the target file\n"
            "becomes a real line break and leaves an unterminated string. Sprint 5 broke\n"
            "three files this way.\n"
            "\n"
            "FIX: change code files with the Edit tool (or Write for a new file); they take\n"
            "the text verbatim. Keep python heredocs for data and prose files.\n"
            "\n"
            "If a script genuinely must write a .py file, re-run with the literal token\n"
            "allow_python_writes_code in the command.",
            file=sys.stderr,
        )
        return 2

    command_text = _data_removed(cmd)
    edited = [] if "allow_shell_code_edit" in command_text else _shell_edits_code(command_text)
    if edited:
        print(
            "[BLOCKED] A shell command editing a repository code file, or any repository\n"
            "file in place (Sprint 8 retrospective I5; Sprint 11 retrospective I4):\n"
            f"    {', '.join(edited[:3])}\n"
            "\n"
            "Edit with the Edit tool (or Write for a new file), which shows the change and\n"
            "takes the text verbatim, every time, in any file. sed -i, perl -i and their kin\n"
            "are not used in this repository: their quoting failed and was blocked often.\n"
            "For JSON data, a python heredoc using the json module is fine. Read with the\n"
            "Read and Grep tools.\n"
            "\n"
            "If a shell write to a code file is genuinely needed (restoring a file for a\n"
            "test injection, say), re-run with the literal token allow_shell_code_edit in\n"
            "the command.",
            file=sys.stderr,
        )
        return 2

    # The checks below look only at commands that actually run python.
    if not runs_python:
        return 0

    if "allow_unraw_escape" in cmd:
        return 0

    # Only a DRIVE-LETTER path is unambiguous enough to block on. Legitimate
    # newline and tab escapes, and raw strings, must pass untouched: a hook
    # that blocks the correct fix is worse than no hook.
    bad: list[str] = []

    for line in cmd.split("\n"):
        if line.strip().startswith("#"):
            continue

        for m in QUOTED_LITERAL.finditer(line):
            if VALID_PREFIX.match(m.group("prefix")):
                continue
            body = m.group("body")
            probe = body.replace("\\\\", "")
            if DRIVE_PATH.search(probe):
                bad.append(m.group(0))

    if bad:
        sample = "\n    ".join(bad[:3])
        print(
            "[BLOCKED] Python string with an unescaped Windows path (Sprint 10 retro item 1).\n"
            "\n"
            "Found:\n"
            f"    {sample}\n"
            "\n"
            "Python reads \\D, \\H, \\U as invalid escapes and \\b, \\x, \\n as real control\n"
            "characters, so this either warns, crashes, or -- worst -- silently produces the\n"
            "wrong value. In Sprint 10 a \\b inside a path became a backspace and wrote a\n"
            "file to the wrong directory; the JSON looked fine.\n"
            "\n"
            "FIX, one keystroke either way:\n"
            "    r'D:\\Data\\Harold\\...'      <- raw string, preferred\n"
            "    'D:/Data/Harold/...'       <- forward slashes work on Windows\n"
            "\n"
            "This has recurred five-plus times, twice in this sprint. The rule existed and\n"
            "did not hold, which is why it is now mechanical.\n"
            "\n"
            "If the escape is genuinely intended, re-run with the literal token\n"
            "allow_unraw_escape in the command.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
