#!/usr/bin/env python3
"""Sprint 10 Task J (F87): what the discovery filters drop, on Sprint 9's own pool.

Reads the ranked pool Sprint 9's review run saved
(`D:\\Data\\Harold\\EvidenceBasedDB\\discovery\\f62_review_2026-10-15.json`,
outside git) and applies `discover_candidates.off_topic` to it. No request
is sent: the pool, its ranking and the team lead's Sprint 9 decisions
(`sprint9_f62_enter_seen.OFF_TOPIC`, 13 excluded; the other 87 of the four
top-25 lists accepted) are fixed, so before and after are measured on the
same candidates. Prints, per stream: the records each filter drops (named),
the team lead's excluded records still in the top 25, any accepted record
the filters would lose (must be none), and the records that move up into
the top 25 for review. `--report <file>` also writes it as Markdown,
outside the repository.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dc = _load("dc", "discover_candidates.py")
f62 = _load("f62", "sprint9_f62_enter_seen.py")

POOL = Path(r"D:\Data\Harold\EvidenceBasedDB\discovery\f62_review_2026-10-15.json")


def measure(rows: list[dict]) -> dict[str, dict]:
    before = f62.top_lists(rows)
    out = {}
    for stream in f62.STREAMS:
        excluded = {i for (s, i) in f62.OFF_TOPIC if s == stream}
        top = before[stream]
        accepted = [c for i, c in enumerate(top, 1) if i not in excluded]
        off = [c for i, c in enumerate(top, 1) if i in excluded]
        pool = [c for c in rows if c["stream"] == stream and c["citation_check"] != "unchecked"]
        kept = [c for c in pool if not dc.off_topic(c)]
        after = kept[:f62.TOP]
        after_titles = {c["title"] for c in after}
        out[stream] = {
            "dropped_from_pool": [(c["title"], dc.off_topic(c)) for c in pool if dc.off_topic(c)],
            "excluded_before": len(off),
            "excluded_still_in_top": [c["title"] for c in off if c["title"] in after_titles],
            "accepted_lost": [c["title"] for c in accepted if dc.off_topic(c)],
            "new_in_top": [c["title"] for c in after if c["title"] not in {x["title"] for x in top}],
        }
    return out


def render(m: dict[str, dict]) -> str:
    lines = ["# F87: discovery filters measured on Sprint 9's pool (2026-10-15 run)", "",
             "Sprint 10 Task J. The same candidates and ranking as Sprint 9's review; no new request. "
             "'Excluded' are the 13 the team lead excluded at Sprint 9 Manual Validation (Q4 = 1).", ""]
    for stream, r in m.items():
        lines += [f"## {stream}", "",
                  f"- Excluded in the top 25 before: {r['excluded_before']}; still in the top 25 after: "
                  f"{len(r['excluded_still_in_top'])}" + (f" ({'; '.join(r['excluded_still_in_top'])})"
                                                          if r["excluded_still_in_top"] else ""),
                  f"- Accepted records lost: {len(r['accepted_lost'])}",
                  f"- Dropped from the pool ({len(r['dropped_from_pool'])}):"]
        lines += [f"  - {t} -- {why}" for t, why in r["dropped_from_pool"]]
        lines.append(f"- Moved up into the top 25, for review ({len(r['new_in_top'])}):")
        lines += [f"  - {t}" for t in r["new_in_top"]]
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    m = measure(json.loads(POOL.read_text(encoding="utf-8")))
    text = render(m)
    print(text)
    if "--report" in args:
        target = Path(args[args.index("--report") + 1]).resolve()
        if target == dc.REPO_ROOT or dc.REPO_ROOT in target.parents:
            print("error: refusing to write inside the repository", file=sys.stderr)
            return 2
        target.write_text(text + "\n", encoding="utf-8")
    return 1 if any(r["accepted_lost"] for r in m.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
