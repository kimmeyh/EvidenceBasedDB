#!/usr/bin/env python3
"""Sprint 13 Task G (F113): a reader's own check of its group file, before it finishes.

The same checks the write path makes (`store.quotes.require_verbatim`: every
quote verbatim in the source's text layer, every figure in a value held by
its own quotes, no stray quote mark), plus the shape this task's prompt asks
for: a verdict on every stored assertion given to the reader, a full read or
a reason for each part not read, and the grading fields. Read-only: it
writes nothing, and opens the store (read only) only for `--free-ids`.

Usage:
  python scripts/sprint13_g_check.py <group file> <group brief>
  python scripts/sprint13_g_check.py <one paper's done file> <group brief> --partial
Prints one line per problem and ends "N problems"; 0 is the reader's finish line.
With --partial the file need not hold every record of the brief.
  ... --text <paper text file>   check against that text instead of the PDF (F114's cloud readers, which are
                                 given the coordinator's extracted text, never the PDF)
  ... --sprint15                 Sprint 15's prompt as well (manifests/sprint15_f114_reads/READER_PROMPT.md): a full
                                 read lists its sections and figures, each figure is described, a value read from a
                                 figure is never high, a stored context is never changed, and each quote is on a page
                                 its anchor names
  ... --telemetry                F139: add this run's quote checks and text-cache misses to the group's telemetry
                                 file (scripts/read_telemetry.py; the group is the brief's file name), when it has one
  ... --free-ids                 F155 (Sprint 19): refuse a new assertion id that a record in the store, another
                                 group's file of the release, an earlier paper of this file or one of the record's own
                                 stored assertions already holds, and print the free id `unique_assertion_id` gives.
                                 This one reads the store, read only; a missing store is a problem, never a pass
"""
from __future__ import annotations

import functools
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.ocr import ocr_pages, page_layouts, page_texts  # noqa: E402
from store.quotes import (cells_text, ocr_only_quotes, plain, read_from_figure, require_verbatim,  # noqa: E402
                          source_text)

VERDICTS = {"confirmed", "corrected", "narrowed", "widened", "contradicted", "not in the paper"}
RESULT_TYPES = {"measured", "theoretical", "field", "claim", "cited", "vendor", "setup"}
BASES = {"setup", "scope", "definition", "proved result", "stated limit"}
KINDS = {"shown", "claimed", "cited"}
CLAIM_TYPES = {"positive", "absence", "vendor-self-claim"}
CONTEXTS = {"qml", "qc", "ml", "world", "method"}
QUOTE_CHECKS: list[str] = []  # F139: each assertion whose quotes this run checked against the source


def assertion_problems(tag: str, a: dict, text: str, stored_context: str = "") -> list[str]:
    """`stored_context`: a stored assertion's own context, which a reader keeps even when it is not one of CONTEXTS
    (Sprint 15, reader g133: two emami-2025 assertions are stored under platform:dirac-3)."""
    out = []
    quotes = a.get("quotes") or []
    if not quotes:
        return [f"{tag}: no quotes"]
    cc = "; ".join(f'"{q}" ({a.get("anchor") or "anchor"})' for q in quotes)
    value = a.get("value") or ""
    QUOTE_CHECKS.append(tag)
    try:
        require_verbatim(tag, cc, text, value=value,
                         read_from_page=read_from_figure(value) if a.get("from_figure") else ())
    except ValueError as e:
        out.append(str(e))
    if a.get("from_figure") and not re.search(r"\bread from (figure|fig\.|table|the image)", value, re.I):
        out.append(f'{tag}: a value read from a figure says so ("Read from Figure N: ...")')
    for q in quotes:
        if not 10 <= len(q) <= 300:
            out.append(f"{tag}: a quote of {len(q)} characters (10 to 300)")
    if a.get("result_type") not in RESULT_TYPES:
        out.append(f"{tag}: result_type {a.get('result_type')!r} is not one of {sorted(RESULT_TYPES)}")
    if a.get("kind") not in KINDS:
        out.append(f"{tag}: kind {a.get('kind')!r}")
    if a.get("claim_type") not in CLAIM_TYPES:
        out.append(f"{tag}: claim_type {a.get('claim_type')!r}")
    if a.get("context") not in CONTEXTS and not (stored_context and a.get("context") == stored_context):
        out.append(f"{tag}: context {a.get('context')!r}")
    if a.get("certainty_suggestion") == "high" and a.get("high_basis") not in BASES:
        out.append(f"{tag}: a high suggestion needs high_basis, one of {sorted(BASES)}")
    if a.get("certainty_suggestion") == "high" and not (a.get("certainty_reason") or "").strip():
        out.append(f"{tag}: a high suggestion says where the paper settles it, in certainty_reason")
    # F135 (Sprint 16 Task D): a limit the paper states on its own measured result keeps the type "measured" and may
    # be high on "stated limit" (the review prompt's rule since Sprint 15); reader g118 changed the type to pass.
    if (a.get("certainty_suggestion") == "high" and a.get("result_type") == "measured"
            and a.get("high_basis") != "stated limit"):
        out.append(f'{tag}: a measured result is never high (a limit the paper states on it is high on "stated '
                   'limit", with the type kept "measured")')
    if not (a.get("anchor") or "").strip():
        out.append(f"{tag}: no anchor (section and page)")
    out += [f'{tag}: the quote "{q[:60]}" is in the OCR text only, so its anchor says "OCR"'
            for q in ocr_only_quotes(cc, text) if not re.search(r"\bOCR\b", a.get("anchor") or "")]
    return out


# "p.", "pp.", "page" and "pages", any case (fresh-eyes review, 2026-11-02: "page 9" and "P. 9" went unchecked)
PAGES = re.compile(r"\b(?:pp?\.|pages?\b)\s*(\d+(?:\s*(?:[-–—]|,|and|to)\s*\d+)*)", re.I)


def spans(anchor: str) -> list[tuple[int, int]]:
    """The pages an anchor names: "p.4", "pp.4-6", "p.4 and 9", "p. 4, 9", "pp. 123-24" (123 to 124)."""
    out = []
    for m in PAGES.finditer(anchor or ""):
        for part in re.split(r"\s*(?:,|and)\s*", m[1]):
            ends = [int(x) for x in re.findall(r"\d+", part)]
            first, last = ends[0], ends[-1]
            if last < first:  # a shortened range: "123-24"
                last = int(str(first)[:len(str(first)) - len(str(last))] + str(last))
            if 1 <= first <= last:  # "p.0" names no page; it read the last page through layer[-1]
                out.append((first, last))
    return out


@functools.lru_cache(maxsize=None)
def _ocr(path: str) -> dict[int, str]:
    return ocr_pages(path).pages  # once per file: each call hashed the whole PDF again (F139)


@functools.lru_cache(maxsize=None)
def page_text(path: str, first: int, last: int) -> str:
    """Pages first to last of a PDF: the text layer in both layouts (Copilot, PR #149), and the OCR text of any thin
    page. Both layouts come from the cached whole-file extractions, split by page (F139, Sprint 16 Task B): no
    pdftotext runs per anchor."""
    out = []
    for layer in (page_texts(path), page_layouts(path)):
        out += [layer[n - 1] for n in range(first, min(last, len(layer)) + 1)]
    ocr = _ocr(path)
    out += [ocr[n] for n in range(first, last + 1) if n in ocr]
    layer = page_texts(path)  # F134: the plain pages again with their number-only lines (table cells) kept
    cells = "\f".join(layer[n - 1] for n in range(first, min(last, len(layer)) + 1))
    return plain(" ".join(out)) + " || " + cells_text(cells)


def page_problems(tag: str, a: dict, path: str, text: str) -> list[str]:
    """Sprint 15 (F126): each quote found in the paper is on a page its anchor names, or the page after (a quote
    may run across a page break). Pages are the PDF's, counted from its first page."""
    named = spans(a.get("anchor") or "")
    if not named or not path.lower().endswith(".pdf"):  # no page to check against: never a failure
        return []
    out = []
    for q in a.get("quotes") or []:
        if plain(q) not in text:
            continue  # reported by the verbatim check
        if not any(plain(q) in page_text(path, first, last + 1) for first, last in named):
            out.append(f'{tag}: the quote "{q[:60]}" is not on {a.get("anchor")!r}; anchors are PDF pages')
    return out


FIGURE_FIELDS = ("figure", "page", "kind", "shows")


def sprint15_problems(p: dict, stored_contexts: dict[str, str], text: str, pdf: str) -> list[str]:
    rid = p.get("record_id", "?")
    out = []
    figures = p.get("figures")
    if not isinstance(figures, list):
        out.append(f"{rid}: figures lists every figure and image read (an empty list when the paper has none)")
        figures = []
    elif p.get("figure_count") != len(figures):
        out.append(f"{rid}: figure_count {p.get('figure_count')!r} is not the {len(figures)} figures listed")
    if p.get("read_extent") == "full" and not p.get("sections_read"):
        out.append(f"{rid}: a full read lists each section and appendix read, in sections_read")
    for f in figures:
        tag = f"{rid}/figure {f.get('figure', '?')}"
        out += [f"{tag}: no {k}" for k in FIGURE_FIELDS if not str(f.get(k) or "").strip()]
        quote = (f.get("confirmed_by") or "").strip()
        if not quote and f.get("no_text_confirms") is not True:
            out.append(f"{tag}: quote the passage that confirms it in confirmed_by, or set no_text_confirms")
        elif quote and plain(quote) not in text:
            out.append(f"{tag}: confirmed_by is not verbatim in the paper")
    for e in p.get("existing", []):
        stored = stored_contexts.get(e.get("id"))
        if e.get("id") in stored_contexts and e.get("context") and e["context"] != stored:
            out.append(f"{rid}/{e.get('id')}: context {e['context']!r} changes the stored {stored!r}; a reader "
                       "never changes a stored context")
    for a in [*p.get("existing", []), *p.get("assertions", [])]:
        tag = f"{rid}/{a.get('id') or a.get('id_suggestion')}"
        if a.get("from_figure") and a.get("certainty_suggestion") == "high":
            out.append(f"{tag}: a value read from a figure is never high on the figure alone")
        if pdf and a.get("quotes"):
            out += page_problems(tag, a, pdf, text)
    return out


def paper_problems(p: dict, given: set[str], brief_file: str = "", text_file: str = "",
                   stored_contexts: dict[str, str] | None = None) -> list[str]:
    """`text_file`: the paper's text as extracted on the coordinator's machine (F114's cloud readers have the text,
    not the PDF); the entry's `file` must then be the brief's path as written. `stored_contexts` (each stored
    assertion's context, from the brief) turns on Sprint 15's checks."""
    rid = p.get("record_id", "?")
    out = []
    path = p.get("file") or ""
    if text_file:
        text = plain(Path(text_file).read_text(encoding="utf-8"))
        if brief_file and path != brief_file:
            out.append(f"{rid}: file is not the brief's ({brief_file})")
        brief_file = ""
    elif not Path(path).is_file():
        return [f"{rid}: file not found: {path}"]
    else:
        text = plain(source_text(path))
    if p.get("read_extent") not in ("full", "partial"):
        out.append(f"{rid}: read_extent must be full or partial")
    if p.get("read_extent") == "partial" and not (p.get("not_read") or "").strip():
        out.append(f"{rid}: a partial read names each part not read and why, in not_read")
    if p.get("read_extent") == "full" and (p.get("not_read") or "").strip():
        out.append(f"{rid}: a part was not read, so read_extent is partial, not full")
    if not p.get("bears_on_context") and not (p.get("why_not") or "").strip():
        out.append(f"{rid}: bears on no context, so why_not says why")
    if brief_file and Path(path).resolve() != Path(brief_file).resolve():
        out.append(f"{rid}: file is not the brief's ({brief_file})")
    answered = {e.get("id") for e in p.get("existing", [])}
    for missing in sorted(given - answered):
        out.append(f"{rid}: no verdict on stored assertion {missing}")
    for e in p.get("existing", []):
        tag = f"{rid}/{e.get('id')}"
        if e.get("verdict") not in VERDICTS:
            out.append(f"{tag}: verdict {e.get('verdict')!r} is not one of {sorted(VERDICTS)}")
            continue
        if e["verdict"] == "not in the paper":
            if not (e.get("note") or "").strip():
                out.append(f"{tag}: say in note what the paper says instead")
            continue
        if e["verdict"] != "confirmed" and not (e.get("value") or "").strip():
            out.append(f"{tag}: a {e['verdict']} verdict gives the new value")
        if e["verdict"] != "confirmed" or e.get("quotes"):
            out += assertion_problems(tag, e, text, (stored_contexts or {}).get(e.get("id"), ""))
        if e["verdict"] != "confirmed" and not (e.get("note") or "").strip():
            out.append(f"{tag}: say in note what changed and why")
    if p.get("bears_on_context") and not p.get("assertions") and not p.get("existing"):
        out.append(f"{rid}: bears on a context but has no assertions")
    for a in p.get("assertions", []):
        # Sprint 15 (reader g117): 36 of one paper's assertions said `id`, the prompt's key is `id_suggestion`
        if stored_contexts is not None and not (a.get("id_suggestion") or "").strip():
            out.append(f"{rid}/{a.get('id')}: name a new assertion's id `id_suggestion`")
        out += assertion_problems(f"{rid}/{a.get('id_suggestion')}", a, text)
    if stored_contexts is not None:
        out += sprint15_problems(p, stored_contexts, text, "" if text_file else path)
    return out


LOCAL = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114\local")
GROUP_FILE_DIRS = (LOCAL / "reads", ROOT / "manifests" / "sprint13_g_reads")


REVIEW_DIRS = (ROOT / "manifests" / "sprint13_g_reviews", Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114\review\signoff"))


def review_ids(dirs=REVIEW_DIRS) -> set[str]:
    """The ids a review's `id_fix` moves an assertion to, and the ids a sign-off's `add` enters: held before they
    reach the store (`f117_build_groups.written_ids`; fresh-eyes review of e0904f1)."""
    out = set()
    for d in dirs:
        for f in Path(d).glob("g*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            out |= set((data.get("id_fix") or {}).values()) | set(data.get("add") or {})
    return out


def other_groups_ids(own_file: Path, group: str, local: Path = LOCAL, dirs=GROUP_FILE_DIRS) -> set[str]:
    """The new assertion ids in every other group's file and in every other group's saved papers (a reader's
    `tmp_<group>/done/*.json`), so two readers of one release never choose one id. Compared by name, not by
    resolved path (fresh-eyes review of e0904f1: resolving 323 paths took about 6 seconds a run)."""
    from store.assertion_ids import group_file_ids
    own = Path(own_file).name
    files = [f for d in dirs for f in Path(d).glob("group_*.json") if f.name not in (own, f"group_{group}.json")]
    files += [f for t in Path(local).glob("tmp_*") if t.name != f"tmp_{group}" for f in (t / "done").glob("*.json")]
    return group_file_ids(files)


def id_problems(data: dict, given: dict[str, set[str]], taken: set[str]) -> list[str]:
    """F155: each new assertion id that is already held, with the free id to take instead. The free id is also free
    of every id in this file and of every id already suggested in this run (fresh-eyes review of e0904f1: a later
    id of the same file, or two papers given one suggestion)."""
    from store.assertion_ids import unique_assertion_id
    out, seen, suggested = [], set(), set()
    in_file = {a.get("id_suggestion") or a.get("id") for p in data.get("papers", []) for a in p.get("assertions", [])}
    for p in data.get("papers", []):
        rid = p.get("record_id", "?")
        for a in p.get("assertions", []):
            aid = a.get("id_suggestion") or a.get("id")
            if not aid:
                continue
            held = taken | seen | given.get(rid, set())
            if aid in held:
                free = unique_assertion_id(rid, aid, held | in_file | suggested)
                suggested.add(free)
                out.append(f"{rid}/{aid}: id {aid} is already held (store, another group, this file or a stored "
                           f"assertion of this record); take {free}")
            seen.add(aid)
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    text_file = ""
    if "--text" in args:
        i = args.index("--text")
        text_file = args[i + 1]
        del args[i:i + 2]
    data = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    brief = json.loads(Path(args[1]).read_text(encoding="utf-8"))
    given = {r["record_id"]: {e["id"] for e in r.get("stored_assertions", [])} for r in brief["records"]}
    files = {r["record_id"]: r["file"] for r in brief["records"]}
    contexts = {r["record_id"]: {e["id"]: e.get("context") or "" for e in r.get("stored_assertions", [])}
                for r in brief["records"]}
    held = {p.get("record_id") for p in data.get("papers", [])}
    # --partial: one finished paper saved on its own (the reader prompt's "Progress and restart"), not the group file
    problems = [] if "--partial" in args else [f"{rid}: no entry for this record" for rid in sorted(set(given) - held)]
    problems += [f"{rid}: not a record of this brief" for rid in sorted(held - set(given))]
    problems += [x for p in data.get("papers", [])
                 for x in paper_problems(p, given.get(p.get("record_id"), set()), files.get(p.get("record_id"), ""),
                                         text_file,
                                         contexts.get(p.get("record_id"), {}) if "--sprint15" in args else None)]
    if "--free-ids" in args:
        from store import script_paths
        from store.assertion_ids import store_ids
        try:
            taken = store_ids(script_paths(__file__)[1])
        except FileNotFoundError as ex:
            problems.append(f"--free-ids: {ex}")
        else:
            taken |= other_groups_ids(Path(args[0]), Path(args[1]).stem) | review_ids()
            problems += id_problems(data, given, taken)
    for x in problems:
        print(x)
    print(f"{len(problems)} problems")
    if "--telemetry" in args:  # F139: this run's checks against the group's telemetry file, named by its brief
        from store.quotes import extraction_misses
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import read_telemetry
        recorded = read_telemetry.step(Path(args[1]).stem, "check", quote_checks=len(QUOTE_CHECKS),
                                       cache_misses=extraction_misses())
        print(f"telemetry: {'recorded' if recorded else 'not recorded (no file)'} for {Path(args[1]).stem}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
