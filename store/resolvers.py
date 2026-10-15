"""Determinate-fact resolvers (Sprint 1 Task G).

CLAUDE.md standing rule: "Determinate facts are COMPUTED, never stored. If
a command or an artifact can answer it, the database holds a resolver, not
a copy." ADR-0004's own motivating evidence names the amendment count
specifically: A19 records that "the amendment count changed and had to be
corrected in every document that named it." Storing it as a value in this
store would reproduce the exact defect this system exists against --
resolving it live from the consumer repository's own amendment log is the
alternative.

READ-ONLY. Per CLAUDE.md's 2026-09-15 standing rule, this repository's
sessions may read hsbc-quantum-fraud-2026 but never write to it; every
function here only reads files under that repository, never writes.
"""
from __future__ import annotations

import re
from pathlib import Path

CONSUMER_REPO_PREREGISTRATION = Path(
    r"D:\Data\Harold\github\hsbc-quantum-fraud-2026\experiments\PREREGISTRATION.md"
)

# Matches the amendment log's actual line format, e.g.
# "- 2026-08-30 (A1): Freeze recorded. ..." -- verified against the live
# file rather than assumed, since an earlier guess at the format
# ("**A#**") matched zero lines against the real document.
_AMENDMENT_LINE = re.compile(r"^- \d{4}-\d{2}-\d{2} \(A\d+\):", re.MULTILINE)


def consumer_amendment_count(path: Path = CONSUMER_REPO_PREREGISTRATION) -> int:
    """Count the amendment log entries in the consumer repository's frozen
    preregistration, computed live from the document rather than stored.

    Raises FileNotFoundError if the consumer repository is not present on
    this machine (e.g. a fresh clone of EvidenceBasedDB elsewhere) --
    callers that need a value regardless should catch this and report the
    resolver as unavailable, never substitute a remembered number.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. This resolver reads the consumer repository "
            "live and does not cache a fallback value -- a remembered "
            "number is exactly the defect (A19) this resolver exists to "
            "avoid reproducing."
        )
    text = path.read_text(encoding="utf-8")
    return len(_AMENDMENT_LINE.findall(text))


# ---------------------------------------------------------------------------
# ADR-0004 A6 (2026-10-03, Sprint 6 Task E): the two computed certainty caps.
# Stored `certainty` stays the assessor's GRADE judgment; these are a second,
# mechanical reading beside it, exported as derived keys and never written
# back into the store.

LEVELS = ("high", "moderate", "low", "very-low")
_RANK = {level: i for i, level in enumerate(LEVELS)}
_UNUSABLE = ("withdrawn", "retracted")


def certainty_caps(conn) -> dict[str, tuple[str, str]]:
    """{assertion id: (cap, reason)} for every assertion a cap LOWERS, and
    for every UNRATED assertion a cap applies to (with no stored judgment,
    the cap is the only reading there is, even when it is `high`).

    Synthesis cap (A6 (c)): a synthesized assertion is no stronger than the
    weakest assertion that `supports` it (Cyc's strength_combine), each
    input read at its own retraction floor when one applies. An unrated
    input counts as very-low: an input nobody graded cannot lift the
    conclusion. Retraction floor (A6 (d)): an assertion whose every
    yielding source has publication_status withdrawn or retracted is
    very-low. Three queries, whatever the store's size."""
    certainty = {r[0]: r[1] for r in conn.execute("SELECT id, certainty FROM records WHERE class = 'assertion'")}
    caps: dict[str, list[tuple[str, str]]] = {}

    # The retraction floor first: a synthesis inherits it through its inputs
    # (fresh-eyes review, 2026-10-03: an input stored `high` whose every
    # source is retracted must not lift the learning built on it).
    sources_of: dict[str, list[tuple[str, str | None]]] = {}
    for assertion_id, paper_id, status in conn.execute(
            "SELECT y.assertion_id, y.paper_id, p.value FROM paper_yields y "
            "LEFT JOIN paper_probes p ON p.record_id = y.paper_id AND p.field = 'publication_status' "
            "ORDER BY y.assertion_id, y.paper_id"):
        sources_of.setdefault(assertion_id, []).append((paper_id, status))
    floored = set()
    for assertion_id, sources in sources_of.items():
        if all(status in _UNUSABLE for _, status in sources):
            floored.add(assertion_id)
            caps.setdefault(assertion_id, []).append(("very-low", (
                "retraction floor (ADR-0004 A6 (d)): every yielding source is withdrawn or retracted ("
                + ", ".join(f"{p}: {s}" for p, s in sources) + ")")))

    def effective(assertion_id: str) -> int:
        return 3 if assertion_id in floored else _RANK.get(certainty.get(assertion_id), 3)

    inputs: dict[str, list[str]] = {}
    for target, source in conn.execute(
            "SELECT a.to_assertion_id, a.from_assertion_id FROM assertion_relations a "
            "JOIN assertion_fields f ON f.record_id = a.to_assertion_id "
            "WHERE a.relation = 'supports' AND f.derivation = 'synthesized' "
            "ORDER BY a.to_assertion_id, a.from_assertion_id"):
        inputs.setdefault(target, []).append(source)
    for target, sources in inputs.items():
        weakest = max(effective(s) for s in sources)
        at_floor = [s for s in sources if effective(s) == weakest]
        caps.setdefault(target, []).append((LEVELS[weakest], (
            f"synthesis cap (ADR-0004 A6 (c)): no stronger than its weakest supporting input, "
            f"{LEVELS[weakest]} ({', '.join(at_floor)})")))

    out = {}
    for assertion_id, found in caps.items():
        stored = _RANK.get(certainty.get(assertion_id), -1)  # unrated: any cap applies
        lowering = [(cap, why) for cap, why in found if _RANK[cap] > stored]
        if lowering:
            cap = LEVELS[max(_RANK[c] for c, _ in lowering)]
            out[assertion_id] = (cap, "; ".join(why for _, why in lowering))
    return out


# ---------------------------------------------------------------------------
# ADR-0004 A9 (2026-10-15, Sprint 9 Task I, F56; team lead, plan Q6 = 1): the
# computed "corroborated" flag. It is shown beside the stored certainty and
# never moves it; the assessor decides any upgrade and records the reason.

_INITIALS = re.compile(r"^(?:[A-Z]\.?-?)+$|^[A-Z][a-z]?\.?$")
_ORG_NOISE = re.compile(r"\b(?:inc|ltd|llc|corp|corporation|co|gmbh|plc|the)\b")


def _org_keys(name: str) -> set[str]:
    """An organization's comparable forms: its first comma part, lower-case,
    punctuation and legal-form words removed, and the initials of every word
    of a name with two or more words. "Quantum Computing Inc., Leesburg"
    gives {"quantum computing", "qci"}, so it meets "QCi" (live store,
    2026-10-15: the Dirac-3 guide's author is "QCi", the Dirac-3S guide's
    "Quantum Computing Inc.")."""
    words = re.sub(r"[^\w\s]", " ", name.split(",")[0].lower()).split()
    keys = {" ".join(_ORG_NOISE.sub(" ", " ".join(words)).split())}
    if len(words) >= 2:
        keys.add("".join(w[0] for w in words))
    return {k for k in keys if k}


def _people_and_orgs(citation: str) -> tuple[set[str], set[str]]:
    """(author family names, corporate authors) from a rendered citation:
    the part before the quoted title, read as "Family, I." pairs; a name
    with no initials after it is a corporate author."""
    head = citation.split(', "')[0] if ', "' in citation else ""
    toks = [t.strip() for t in head.split(",") if t.strip()]
    people, orgs, i = set(), set(), 0
    while i < len(toks):
        if toks[i].lower().startswith("et al"):
            i += 1
        elif i + 1 < len(toks) and _INITIALS.match(toks[i + 1].replace(" ", "")):
            people.add(toks[i].lower())
            i += 2
        else:
            orgs |= _org_keys(toks[i])
            i += 1
    return people, orgs


def corroboration(conn) -> dict[str, dict[str, list[tuple[str, str]]]]:
    """{assertion id: {"by": [(supporter, why)], "not_counted": [(supporter,
    why)]}} for every assertion that another assertion `supports`.

    A supporter corroborates when it is rated at the same or a higher
    certainty AND independent: both come from papers, no paper is shared,
    both name their authors and no family name is shared, and no
    organization is shared (corporate authors and registry affiliations,
    compared by name and by initials). When either is a vendor's claim
    about its own product, both sides must name their organizations, or
    independence from the vendor cannot be shown and the supporter is not
    counted. Unknown is never independent."""
    rows = {r[0]: (r[1], r[2]) for r in conn.execute(
        "SELECT r.id, r.certainty, f.claim_type FROM records r LEFT JOIN assertion_fields f ON f.record_id = r.id "
        "WHERE r.class = 'assertion'")}
    papers: dict[str, set[str]] = {}
    for aid, pid in conn.execute("SELECT assertion_id, paper_id FROM paper_yields"):
        papers.setdefault(aid, set()).add(pid)
    citation = {r[0]: r[1] or "" for r in conn.execute(
        "SELECT r.id, r.provenance FROM records r WHERE r.class = 'paper'")}
    affil: dict[str, set[str]] = {}
    for pid, value in conn.execute("SELECT record_id, value FROM paper_probes WHERE field = 'affiliations'"):
        affil[pid] = {k for part in value.split(";") for k in _org_keys(part)}

    def side(aid: str) -> tuple[set[str], set[str], set[str]]:
        ps = papers.get(aid, set())
        people, orgs = set(), set()
        for pid in ps:
            pe, og = _people_and_orgs(citation.get(pid, ""))
            people |= pe
            orgs |= og | affil.get(pid, set())
        return ps, people, orgs

    def independent(x: str, y: str) -> tuple[bool, str]:
        (px, ax, ox), (py, ay, oy) = side(x), side(y)
        if not px or not py:
            return False, "not both from papers"
        if px & py:
            return False, f"same paper ({', '.join(sorted(px & py))})"
        if not ax or not ay:
            # A corporate or repository name shows overlap but cannot show
            # independence (live store, 2026-10-15: two of the team lead's own
            # project documents, cited by repository name, read as independent).
            return False, "no named author on one side"
        if ax & ay:
            return False, f"shared author(s): {', '.join(sorted(ax & ay))}"
        if ox & oy:
            return False, f"shared organization(s): {', '.join(sorted(ox & oy))}"
        if "vendor-self-claim" in (rows[x][1], rows[y][1]) and not (ox and oy):
            return False, "a vendor's own claim, and one side names no organization, so independence is not shown"
        return True, "different papers, authors and organizations"

    out: dict[str, dict[str, list[tuple[str, str]]]] = {}
    for y, x in conn.execute("SELECT from_assertion_id, to_assertion_id FROM assertion_relations "
                             "WHERE relation = 'supports' ORDER BY to_assertion_id, from_assertion_id"):
        entry = out.setdefault(x, {"by": [], "not_counted": []})
        cx, cy = rows.get(x, (None, None))[0], rows.get(y, (None, None))[0]
        if cx not in _RANK or cy not in _RANK:
            entry["not_counted"].append((y, "unrated"))
        elif _RANK[cy] > _RANK[cx]:
            entry["not_counted"].append((y, f"rated lower ({cy} against {cx})"))
        else:
            ok, why = independent(x, y)
            entry["by" if ok else "not_counted"].append((y, why))
    return out


def synthesis_input_problems(conn) -> list[str]:
    """A6 (b): every synthesized assertion has at least two `supports`
    inputs. Not a door check: the rebuild writes relations after every
    assertion exists. One line per problem; empty means none."""
    rows = conn.execute(
        "SELECT f.record_id, (SELECT COUNT(*) FROM assertion_relations a "
        "  WHERE a.to_assertion_id = f.record_id AND a.relation = 'supports') AS n "
        "FROM assertion_fields f WHERE f.derivation = 'synthesized' ORDER BY f.record_id")
    return [f"{r[0]}: {r[1]} supporting input(s), at least 2 required" for r in rows if r[1] < 2]
