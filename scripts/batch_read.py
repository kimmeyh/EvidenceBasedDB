#!/usr/bin/env python3
r"""F144 (Sprint 17 Task B): read papers with no read row through the Message Batches API, one paper per request,
no tools, on the team lead's API credit. Writes NOTHING to the store.

Team lead's brief, 2026-11-07 (Q1 = 1: Batch API, Sonnet 5.5, one request per paper, no tools; Q2 = 1: the records
with no read row, in F57's relevance-ranking order; a record with no local or free copy goes on the hand-download
list, not into a batch). Sprint 17 plan Q1 (team lead): the key is ANTHROPIC_API_KEY in the repository's git-ignored
key file, read here with python-dotenv's `dotenv_values`, which returns it without putting it in the environment, so
Claude Code's own credential order never sees it. It is never printed and never written to a file, log or commit.
A key not scoped to a workspace needs the workspace id: ANTHROPIC_WORKSPACE_ID in the same file, sent as the
`anthropic-workspace-id` header.

Candidates: every paper record with no read row that no ledger group holds (a ledger record is F114's, read by its
local readers), with an arXiv id or a DOI, not a GitHub repository and not withdrawn. F57's order: the store's QML
context first (`qml`, then `qc`, `ml`, `world`, `method`), and within each the most cited first by OpenAlex
(uncounted last, by id). Each sent paper gets its own ledger group (the next free gNNN), so the existing pipeline
(`scripts/sprint13_g_check.py`, the coordinator review, `scripts/full_read_apply.py`) consumes it unchanged.

    python scripts/batch_read.py select [--write]           rank the candidates (manifests/sprint17_f144_slice.json)
    python scripts/batch_read.py fetch --n N [--apply]      free copies of the next N candidates not yet tried
    python scripts/batch_read.py submit --n N [--apply]     the next N candidates with a file: groups, briefs, one batch
    python scripts/batch_read.py poll [--apply]             save each ended batch's results, write and check each read
    python scripts/batch_read.py status                     the state file: batches, results, spend against the credit

Dry run by default: without --apply, nothing is sent, fetched or written but the slice. The state file
(`D:\Data\Harold\EvidenceBasedDB\work\f144\state.json`, outside git) is written the moment a batch is accepted, and a
record whose result is saved, or that sits in a batch not yet collected, is never sent again. Each raw result is saved
the moment it is read (`work\f144\raw\<record>.json`), then written as the reader group file the pipeline reads
(`work\f114\local\reads\group_<g>.json`, with the repository copy in `manifests/sprint13_g_reads/`), then checked;
a failing read is kept and flagged, never dropped. The cost comes from each result's `usage`; a batch whose
estimate would take the spend past the cap ($95 by default) is refused, and nothing is sent on or after 2026-11-18,
the day the credit expires.
"""
from __future__ import annotations

import base64
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import citations, connect, script_paths  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_, DB_PATH, _ = script_paths(__file__)


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MODEL = "claude-sonnet-5-5"
BETA = "output-300k-2026-03-24"  # raises max_tokens to 300,000 for batch requests on Sonnet 5.5 (Anthropic, 2026-11-07)
MAX_TOKENS = 300_000  # so no read is cut short; never a budget
# Batch prices, Claude Sonnet 5.5, per million tokens (platform.claude.com batch-processing page, read 2026-11-07).
PRICE_IN, PRICE_OUT = 1.00, 5.00
CREDIT = 100.00
CAP = 95.00
STOP = date(2026, 11, 18)  # the credit expires this day (the team lead): nothing is sent on or after it
# Request limits, not reading limits: at most 100 images in one request, and a request body of at most 32 MB. Base64
# makes image bytes 4/3 larger, so 18 MB of PNG leaves room for the text. A page over either is named in the request
# as not attached, and the reader lists its figures in `not_read`.
MAX_IMAGES = 100
MAX_IMAGE_BYTES = 18_000_000
CONTEXT_ORDER = ("qml", "qc", "ml", "world", "method")

LEDGER = ROOT / "manifests" / "sprint13_g_ledger.json"
SLICE = ROOT / "manifests" / "sprint17_f144_slice.json"
PROMPT = ROOT / "manifests" / "sprint17_f144_batch" / "READER_PROMPT.md"
REPO_READS = ROOT / "manifests" / "sprint13_g_reads"
REPO_BRIEFS = ROOT / "manifests" / "sprint17_f144_batch" / "briefs"
KEY_FILE = ROOT / ".env"
LOCAL = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f114\local")
WORK = Path(r"D:\Data\Harold\EvidenceBasedDB\work\f144")
PAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\Papers")
UA = "EvidenceBasedDB-fetcher/1.0"
CAPTION = re.compile(r"^\s*(Figure|Fig\.|FIG\.|Table|TABLE)\s*[0-9IVX]", re.MULTILINE)
COUNT_LINE = re.compile(r"^(\d+) problems$")


# ---------------------------------------------------------------- state

def state_path() -> Path:
    return WORK / "state.json"


def load_state() -> dict:
    p = state_path()
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"batches": {}, "results": {}, "files": {}, "spent": 0.0}


def save_state(state: dict) -> None:
    """Whole or not at all: written to a temporary name, then moved into place."""
    WORK.mkdir(parents=True, exist_ok=True)
    tmp = state_path().with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, state_path())


def in_flight(state: dict) -> set[str]:
    return {rid for b in state["batches"].values() if not b.get("collected") for rid in b["records"]}


def unsendable(state: dict) -> set[str]:
    """Records never to send again: a result is saved (whatever its type), a batch holding them is not yet
    collected, or a send of them was interrupted (`pending`)."""
    return set(state["results"]) | in_flight(state) | set((state.get("pending") or {}).get("records", []))


def cost(input_tokens: int, output_tokens: int) -> float:
    return input_tokens * PRICE_IN / 1e6 + output_tokens * PRICE_OUT / 1e6


def refusal(state: dict, worst: float, today: date, cap: float = CAP) -> str | None:
    """Why a batch may not go, or None. The cap is tested at the WORST case, never the forecast (fresh-eyes review,
    2026-11-07): each request counted at its full max_tokens of output, since adaptive thinking is output too, and a
    batch still in flight counted the same way."""
    if today >= STOP:
        return f"the credit expires {STOP.isoformat()}: nothing is sent on or after that day"
    if state.get("pending"):
        return ("a send was interrupted (state `pending`): find whether its batch exists in the Console's batch list, "
                "record it, and clear `pending` before sending again")
    spent = state.get("spent", 0.0) + sum(b.get("worst", b.get("estimate", 0.0)) for b in state["batches"].values()
                                          if not b.get("collected"))
    if spent + worst > cap:
        return (f"spent and in flight at worst ${spent:.2f} + this batch at worst ${worst:.2f} = "
                f"${spent + worst:.2f}, past the cap ${cap:.2f}")
    return None


# ---------------------------------------------------------------- the key

def api_key() -> tuple[str, str | None]:
    """The key and an optional workspace id, from the key file only. Never printed."""
    from dotenv import dotenv_values
    values = dotenv_values(KEY_FILE) if KEY_FILE.is_file() else {}
    key = values.get("ANTHROPIC_API_KEY") or ""
    if not key:
        raise SystemExit("no ANTHROPIC_API_KEY in the repository's key file")
    return key, values.get("ANTHROPIC_WORKSPACE_ID") or None


def redact(text: str, key: str) -> str:
    return text.replace(key, "<key>") if key else text


def make_client(key: str, workspace: str | None):
    import anthropic
    headers = {"anthropic-workspace-id": workspace} if workspace else None
    return anthropic.Anthropic(api_key=key, default_headers=headers)


# ---------------------------------------------------------------- candidates

def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def candidates(conn, held: set[str]) -> dict[str, dict]:
    """record id -> {context, rank, kind, ident, doi}: no read row, in no ledger group, an arXiv id or a DOI, not a
    GitHub repository, not withdrawn and not retracted (the store keeps those "so it is never cited as live evidence",
    so a read of one buys nothing)."""
    out = {}
    rows = conn.execute(
        "SELECT r.id, r.value, f.access, f.disposition FROM records r JOIN paper_fields f ON f.record_id = r.id "
        "WHERE r.class = 'paper' AND NOT EXISTS (SELECT 1 FROM paper_reads p WHERE p.record_id = r.id) "
        "ORDER BY r.id").fetchall()
    for rid, title, access, disposition in rows:
        dead = (disposition or "").startswith(("Withdrawn", "Retracted")) or (title or "").upper().startswith("RETRACTED")
        if rid in held or "github.com" in (access or "").lower() or dead:
            continue
        parsed = citations.parse_access(access or "")
        if not parsed:
            continue
        ctx = [c for (c,) in conn.execute("SELECT context_id FROM record_contexts WHERE record_id = ?", (rid,))]
        rank = min((CONTEXT_ORDER.index(c) for c in ctx if c in CONTEXT_ORDER), default=len(CONTEXT_ORDER))
        doi = f"10.48550/arxiv.{parsed[1]}".lower() if parsed[0] == "arxiv" else parsed[1].lower()
        out[rid] = {"context": CONTEXT_ORDER[rank] if rank < len(CONTEXT_ORDER) else ",".join(ctx),
                    "rank": rank, "kind": parsed[0], "ident": parsed[1], "doi": doi}
    return out


def ranked(cands: dict[str, dict], counts: dict[str, int]) -> list[dict]:
    rows = [{"record_id": rid, "context": c["context"], "cited_by_count": counts.get(c["doi"]), "kind": c["kind"],
             "ident": c["ident"]} for rid, c in cands.items()]
    return sorted(rows, key=lambda r: (cands[r["record_id"]]["rank"], r["cited_by_count"] is None,
                                       -(r["cited_by_count"] or 0), r["record_id"]))


def select(args: list[str]) -> int:
    L = ledger()
    held = {r["record_id"] for g in L["groups"].values() for r in g["records"]}
    with connect(DB_PATH) as conn:
        cands = candidates(conn, held)
    f80slice = _load("f80slice", "sprint9_f80_slice.py")
    counts = f80slice.fetch_counts(sorted({c["doi"] for c in cands.values()}), f80slice.dc.openalex_key())
    rows = ranked(cands, counts)
    print(f"{len(rows)} candidates; top 10:")
    for r in rows[:10]:
        print(f"  {r['record_id']}  {r['context']}  cited {r['cited_by_count']}")
    if "--write" in args:
        SLICE.write_text(json.dumps({
            "selected_on": date.today().isoformat(),
            "rule": ("F144 (Sprint 17 Task B): every paper record with no read row that no ledger group holds, with an "
                     "arXiv id or a DOI, not a GitHub repository, not withdrawn or retracted; F57's order: qml, qc, "
                     "ml, world, "
                     "method, then most cited by OpenAlex, uncounted last by id"),
            "slice": rows}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {SLICE.relative_to(ROOT)}")
    return 0


def slice_rows() -> list[dict]:
    return json.loads(SLICE.read_text(encoding="utf-8"))["slice"]


# ---------------------------------------------------------------- files

def free_copy(f89, rid: str, kind: str, ident: str, title: str, key) -> tuple[list[str], str | None, str, str] | None:
    """(urls in the order to try, arXiv id or None, target name, where) for a free copy, or None. Sprint 10's rules
    (`sprint10_f89_downloads.plan`): the arXiv copy first, then the open-access PDF of OpenAlex's best location. F144
    adds one step: the PDF link of EVERY other open-access location OpenAlex lists (a green repository copy, a gold
    journal's PDF), tried in turn, since on 2026-11-07 two gold papers of the top 20 had none at the best location and
    one best location served an HTML page. Free copies only; a failed TLS check is never worked around."""
    year = rid.split("-")[1] if rid.split("-")[1].isdigit() else "nd"
    if kind == "arxiv":
        return [f"https://arxiv.org/pdf/{ident}"], ident, f89.file_name(rid, ident, year, title), "arxiv"
    work = f89.openalex_work(ident, key)
    arxiv = f89.f80dl.dc.arxiv_of(work)
    best = ((work.get("best_oa_location") or {}).get("pdf_url") or "").strip()
    other = [(loc.get("pdf_url") or "").strip() for loc in work.get("locations") or [] if loc.get("is_oa")]
    urls = list(dict.fromkeys(u for u in ([f"https://arxiv.org/pdf/{arxiv}"] if arxiv else []) + [best] + other if u))
    if not urls:
        return None
    where = "arxiv" if arxiv else "best open location" if best else "other open location"
    return urls, arxiv, f89.file_name(rid, arxiv, year, title), f"{where}, {len(urls)} link(s)"


def fetch(args: list[str]) -> int:
    """Free copies only (`free_copy`): arXiv through the paced fetcher, else an open-access PDF OpenAlex lists; a
    paper with neither is recorded for the hand-download list, never fetched; an existing file is never overwritten,
    and a record already tried is not tried again. N counts the papers WITH a free copy: the records passed over on the
    way are recorded for the hand-download list (2026-11-07: 19 of the top 20 had none)."""
    n = int(args[args.index("--n") + 1]) if "--n" in args else 5
    apply = "--apply" in args
    state = load_state()
    f89 = _load("f89dl", "sprint10_f89_downloads.py")
    # Tried for good: a saved file, or no free copy known. A failed download is tried again on the next run.
    settled = {rid for rid, f in state["files"].items() if f.get("path") or f.get("why", "").startswith("no free copy")}
    todo, skip = [], unsendable(state) | settled
    with connect(DB_PATH) as conn:
        for r in slice_rows():
            rid = r["record_id"]
            if rid in skip:
                continue
            title = conn.execute("SELECT value FROM records WHERE id = ?", (rid,)).fetchone()[0]
            todo.append((rid, r["kind"], r["ident"], title))
    key, fetcher = f89.f80dl.dc.openalex_key(), citations.PacedFetcher()
    done = 0  # papers with a file: saved now, or already there (a dry run counts the planned ones)
    for rid, kind, ident, title in todo:
        if done >= n:
            break
        try:
            found = free_copy(f89, rid, kind, ident, title, key)
        except Exception as ex:  # noqa: BLE001 -- an OpenAlex failure is reported, never taken for "no copy"
            print(f"FAILED  {rid}: OpenAlex: {type(ex).__name__}")
            continue
        if not found:
            state["files"][rid] = {"path": "", "why": "no free copy known to OpenAlex: hand-download list"}
            print(f"no free copy: {rid} ({ident})")
            continue
        urls, arxiv, name, where = found
        target = PAPERS / name
        if target.exists():
            state["files"][rid] = {"path": str(target), "why": "exists"}
            print(f"exists  {rid}  {target.name}")
            done += 1
            continue
        if not apply:
            print(f"planned {rid} ({where}): {urls[0]} -> {target.name}")
            done += 1
            continue
        failures = []
        for url in urls:
            try:
                if "arxiv.org/" in url:
                    data = fetcher(url, "application/pdf")
                else:
                    import urllib.request
                    req = urllib.request.Request(url, headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=120) as resp:
                        data = resp.read()
            except Exception as ex:  # noqa: BLE001 -- reported; the next link, then the next paper, still run
                failures.append(f"{type(ex).__name__}: {str(ex)[:100]} ({url})")
                continue
            if not data.startswith(b"%PDF"):
                failures.append(f"not a PDF ({url}; starts {data[:40]!r})")
                continue
            target.write_bytes(data)
            state["files"][rid] = {"path": str(target), "why": "fetched", "url": url}
            print(f"saved   {rid}  {target.name}  from {url}")
            done += 1
            break
        else:
            state["files"][rid] = {"path": "", "why": "fetch failed: " + "; ".join(failures)}
            print(f"FAILED  {rid}: " + "; ".join(failures))
    if apply:
        save_state(state)
    else:
        print("DRY RUN: nothing fetched or saved. Re-run with --apply.")
    return 0


# ---------------------------------------------------------------- requests

def instructions(group: str) -> str:
    text = PROMPT.read_text(encoding="utf-8")
    return text.split("\n---\n", 1)[1].replace("{GROUP}", group)


def image_pages(pdf: str, texts: list[str], ocr: dict[int, str]) -> list[int]:
    """Pages to attach: each that holds an embedded image, a figure or table caption, or OCR text."""
    pages = set(ocr)
    listed = subprocess.run(["pdfimages", "-list", pdf], capture_output=True, text=True, encoding="utf-8",
                            errors="replace").stdout.splitlines()[2:]
    pages |= {int(line.split()[0]) for line in listed if line.split() and line.split()[0].isdigit()}
    pages |= {n for n, t in enumerate(texts, 1) if CAPTION.search(t)}
    return sorted(p for p in pages if 1 <= p <= len(texts))


def paper_message(group: str, brief: dict, pdf: str) -> tuple[list[dict], dict]:
    from store.ocr import ocr_pages, page_texts
    render = _load("render_page", "render_page.py").render
    texts = page_texts(pdf)
    ocr = dict(ocr_pages(pdf).pages)
    body = "\n".join(f"=== PAGE {n} ===\n{t}" + (f"\n|| OCR: {ocr[n]}" if n in ocr else "")
                     for n, t in enumerate(texts, 1))
    attached, left, size, images = [], [], 0, []
    for n in image_pages(pdf, texts, ocr):
        png = render(pdf, n, 100).read_bytes()
        if len(attached) >= MAX_IMAGES or size + len(png) > MAX_IMAGE_BYTES:
            left.append(n)
            continue
        attached.append(n)
        size += len(png)
        images.append((n, png))
    head = (f"Your group is {group}. Follow your instructions exactly.\n=== BRIEF ===\n{json.dumps(brief, indent=1)}\n"
            f"=== PAPER TEXT ===\n{body}\n=== PAGE IMAGES ===\nAttached below: pages "
            f"{', '.join(map(str, attached)) or 'none'}."
            + (f" Not attached (over the request's image limits): pages {', '.join(map(str, left))}." if left else ""))
    content = [{"type": "text", "text": head}]
    for n, png in images:
        content += [{"type": "text", "text": f"=== IMAGE OF PAGE {n} ==="},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                 "data": base64.standard_b64encode(png).decode("ascii")}}]
    facts = {"pages": len(texts), "images": len(attached), "image_bytes": size, "not_attached": left,
             "ocr_pages": sorted(ocr), "chars": len(head)}
    return content, facts


def estimate(facts: dict) -> float:
    """A forecast for the cap only (never a limit on a read): about 3.5 characters a token, about 1,300 tokens a
    100-dpi page image, the instructions about 6,000 tokens; output about 3,000 tokens a page, at least 20,000."""
    inp = facts["chars"] / 3.5 + facts["images"] * 1300 + 6000
    out = max(20_000, facts["pages"] * 3000)
    return cost(int(inp), int(out))


def worst_case(facts: dict) -> float:
    """The most one request can cost: a cautious input count (2.5 characters a token, 1,600 tokens an image, 10,000
    for the instructions) and the full max_tokens of output."""
    return cost(int(facts["chars"] / 2.5 + facts["images"] * 1600 + 10_000), MAX_TOKENS)


# Request size limits (Anthropic, 2026-11-07): a Messages request at most 32 MB, a batch at most 256 MB.
MAX_REQUEST_BYTES = 32_000_000
MAX_BATCH_BYTES = 256_000_000


def next_group(L: dict) -> str:
    n = max(int(m[1]) for g in L["groups"] if (m := re.match(r"g(\d+)$", g)))
    return f"g{n + 1:03d}"


def submit(args: list[str], today: date | None = None, client_factory=make_client) -> int:
    n = int(args[args.index("--n") + 1]) if "--n" in args else 5
    cap = float(args[args.index("--cap") + 1]) if "--cap" in args else CAP
    today = today or date.today()
    apply = "--apply" in args
    state = load_state()
    skip = unsendable(state)
    picks = [r["record_id"] for r in slice_rows()
             if r["record_id"] not in skip and state["files"].get(r["record_id"], {}).get("path")][:n]
    if not picks:
        print("nothing to send: fetch first, or every candidate with a file is sent")
        return 0
    g_ledger = _load("g_ledger", "sprint13_g_ledger.py")
    L = ledger()
    requests, plan, total, worst, size = [], {}, 0.0, 0.0, 0
    with connect(DB_PATH) as conn:
        for rid in picks:
            g = next_group(L)
            pdf = state["files"][rid]["path"]
            L["groups"][g] = {"records": [{"record_id": rid, "file": pdf}]}
            brief = {"group": g, "records": [{"record_id": rid, "file": pdf,
                                              "stored_assertions": g_ledger.stored_assertions(conn, rid)}]}
            content, facts = paper_message(g, brief, pdf)
            est, top = estimate(facts), worst_case(facts)
            total, worst = total + est, worst + top
            plan[rid] = {"group": g, "brief": brief, "facts": facts, "estimate": est}
            request = {"custom_id": g, "params": {
                "model": MODEL, "max_tokens": MAX_TOKENS, "thinking": {"type": "adaptive"},
                "system": instructions(g), "messages": [{"role": "user", "content": content}]}}
            facts["request_bytes"] = len(json.dumps(request))
            size += facts["request_bytes"]
            requests.append(request)
            print(f"{g}  {rid}  {facts['pages']} pages, {facts['images']} images "
                  f"({facts['image_bytes']:,} bytes), not attached {facts['not_attached'] or 'none'}, "
                  f"request {facts['request_bytes']:,} bytes, forecast ${est:.2f}, at worst ${top:.2f}")
    too_big = [plan[rid]["group"] for rid in picks if plan[rid]["facts"]["request_bytes"] > MAX_REQUEST_BYTES]
    why = (f"requests over {MAX_REQUEST_BYTES:,} bytes: {', '.join(too_big)}" if too_big
           else f"the batch is {size:,} bytes, over {MAX_BATCH_BYTES:,}" if size > MAX_BATCH_BYTES
           else refusal(state, worst, today, cap))
    if why:
        print(f"REFUSED: {why}")
        return 1
    print(f"{len(requests)} requests, {size:,} bytes, forecast ${total:.2f}, at worst ${worst:.2f}; "
          f"spent so far ${state['spent']:.2f} of ${CREDIT:.2f}")
    if not apply:
        print("DRY RUN: nothing sent. Re-run with --apply.")
        return 0
    key, workspace = api_key()
    groups = {rid: plan[rid]["group"] for rid in picks}
    # Before the send (fresh-eyes review, 2026-11-07): `pending` holds the records, so a crash between the send and
    # the save cannot let them go again unseen; the ledger holds the groups, so no later run reuses them.
    old_ledger = LEDGER.read_text(encoding="utf-8")
    state["pending"] = {"records": picks, "groups": groups, "since": datetime.now().isoformat(timespec="seconds")}
    save_state(state)
    LEDGER.write_text(json.dumps(L, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        client = client_factory(key, workspace)
        batch = client.beta.messages.batches.create(betas=[BETA], requests=requests)
    except Exception as ex:  # noqa: BLE001 -- the key never reaches the message
        print(f"FAILED to send: {type(ex).__name__}: {redact(str(ex), key)[:500]}")
        LEDGER.write_text(old_ledger, encoding="utf-8")  # the API refused it: nothing is in flight
        state.pop("pending")
        save_state(state)
        return 1
    state["batches"][batch.id] = {"records": picks, "groups": groups,
                                  "submitted": datetime.now().isoformat(timespec="seconds"),
                                  "estimate": total, "worst": worst,
                                  "facts": {rid: plan[rid]["facts"] for rid in picks}, "collected": False}
    state.pop("pending")
    save_state(state)  # before anything else, so a closed session loses nothing
    for rid in picks:
        g, brief = plan[rid]["group"], plan[rid]["brief"]
        for folder in (LOCAL / "briefs", REPO_BRIEFS):
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{g}.json").write_text(json.dumps(brief, indent=1, ensure_ascii=False) + "\n",
                                              encoding="utf-8")
    print(f"sent batch {batch.id}: {len(picks)} papers; state saved")
    return 0


# ---------------------------------------------------------------- results

def reply_json(message: dict) -> dict | None:
    text = "".join(b.get("text", "") for b in message.get("content", []) if b.get("type") == "text").strip()
    start, end = text.find("{"), text.rfind("}")
    try:
        return json.loads(text[start:end + 1]) if start >= 0 else None
    except json.JSONDecodeError:
        return None


def group_files(group: str) -> tuple[Path, Path]:
    return LOCAL / "reads" / f"group_{group}.json", REPO_READS / f"group_{group}.json"


def check(group: str) -> str:
    local, _ = group_files(group)
    out = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts" / "sprint13_g_check.py"), str(local),
                          str(LOCAL / "briefs" / f"{group}.json"), "--sprint15"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    counts = [m[0] for line in out.splitlines() if (m := COUNT_LINE.match(line.strip()))]
    if not counts:
        return "FLAGGED: the check printed no count"
    return "passed: 0 problems" if counts[-1] == "0 problems" else f"FLAGGED: {counts[-1]}"


def collect(state: dict, batch_id: str, results) -> None:
    """Each result: the raw result saved first, then its cost, then the reader group file, then the check. A result
    that fails at any step is kept and flagged, never dropped."""
    b = state["batches"][batch_id]
    by_group = {g: rid for rid, g in b["groups"].items()}
    (WORK / "raw").mkdir(parents=True, exist_ok=True)
    for res in results:
        raw = res.model_dump(mode="json") if hasattr(res, "model_dump") else res
        rid = by_group[raw["custom_id"]]
        if state["results"].get(rid, {}).get("batch") == batch_id:
            # A collection retried after a failure part way (fresh-eyes review, 2026-11-07): saved and costed once.
            print(f"{raw['custom_id']}  {rid}  already saved")
            continue
        (WORK / "raw" / f"{rid}.json").write_text(json.dumps(raw, indent=1, ensure_ascii=False), encoding="utf-8")
        entry = {"group": raw["custom_id"], "batch": batch_id, "type": raw["result"]["type"]}
        if raw["result"]["type"] == "succeeded":
            msg = raw["result"]["message"]
            u = msg.get("usage") or {}
            entry.update(input_tokens=u.get("input_tokens", 0), output_tokens=u.get("output_tokens", 0),
                         stop_reason=msg.get("stop_reason"))
            entry["cost"] = cost(entry["input_tokens"], entry["output_tokens"])
            state["spent"] = state.get("spent", 0.0) + entry["cost"]
            data = reply_json(msg)
            if data is None:
                entry["check"] = "FLAGGED: the reply is not JSON"
            else:
                for path in group_files(raw["custom_id"]):
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
                entry["check"] = check(raw["custom_id"])
            if msg.get("stop_reason") == "max_tokens":
                entry["check"] = f"FLAGGED: cut short at max_tokens; {entry.get('check')}"
        else:
            entry["check"] = f"FLAGGED: {raw['result']['type']}"
        state["results"][rid] = entry
        save_state(state)
        print(f"{raw['custom_id']}  {rid}  {entry['type']}  ${entry.get('cost', 0):.4f}  {entry['check']}")
    b["collected"] = True
    save_state(state)


def poll(args: list[str], client_factory=make_client) -> int:
    state = load_state()
    waiting = [bid for bid, b in state["batches"].items() if not b.get("collected")]
    if not waiting:
        print("no batch waiting")
        return 0
    key, workspace = api_key()
    try:
        client = client_factory(key, workspace)
        for bid in waiting:
            batch = client.beta.messages.batches.retrieve(bid)
            print(f"{bid}: {batch.processing_status} {batch.request_counts}")
            if batch.processing_status == "ended" and "--apply" in args:
                collect(state, bid, client.beta.messages.batches.results(bid))
    except Exception as ex:  # noqa: BLE001
        print(f"FAILED: {type(ex).__name__}: {redact(str(ex), key)[:500]}")
        return 1
    print(f"spent ${state['spent']:.4f} of ${CREDIT:.2f} (cap ${CAP:.2f})")
    return 0


def status(args: list[str]) -> int:
    state = load_state()
    if state.get("pending"):
        print(f"PENDING (a send was interrupted): {state['pending']}")
    for bid, b in state["batches"].items():
        print(f"{bid}: {len(b['records'])} papers, estimate ${b['estimate']:.2f}, "
              f"{'collected' if b.get('collected') else 'waiting'}")
    for rid, r in state["results"].items():
        print(f"  {r['group']}  {rid}  {r['type']}  in {r.get('input_tokens', 0):,}  out {r.get('output_tokens', 0):,}"
              f"  ${r.get('cost', 0):.4f}  {r.get('check', '')}")
    hand = sorted(rid for rid, f in state["files"].items() if not f.get("path"))
    if hand:
        print(f"no file ({len(hand)}): " + ", ".join(hand))
    spent = state.get("spent", 0.0)
    print(f"spent ${spent:.4f} of ${CREDIT:.2f} (cap ${CAP:.2f}); left ${CREDIT - spent:.2f}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    commands = {"select": select, "fetch": fetch, "submit": submit, "poll": poll, "status": status}
    if not args or args[0] not in commands:
        print(__doc__)
        return 1
    return commands[args[0]](args[1:])


if __name__ == "__main__":
    sys.exit(main())
