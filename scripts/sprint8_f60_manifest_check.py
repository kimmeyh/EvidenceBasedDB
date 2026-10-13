#!/usr/bin/env python3
"""Sprint 8 Task E (F60): check every QMLPapers manifest row against its file.

`D:\\Data\\Harold\\EvidenceBasedDB\\QMLPapers\\` is outside the repository and
is only read here. For each manifest row with an `arxiv_id`, the file's
first page is read (pdftotext, page 1) and its arXiv stamp
("arXiv:2108.00131v2 [cs.LG] ...") compared with the row's id. Found in
Sprint 7 Task E: the row for Asfaw et al. names `2108.0131` (one digit
short) and its file is a different paper.

Classes, one per row:
  match       the stamp names the row's id
  mismatch    the stamp names another id (the file is another paper, or the
              row's id is wrong)
  no stamp    the first page carries no arXiv stamp (a journal version, or
              a scan); listed, never guessed
  missing     the row's file is not in the folder
  no id       the row has no arXiv id (NonArxiv); not checked by stamp
Files in a folder that no manifest row names are listed too.

Read-only: writes nothing to the store or the folder. `--out <file>`
writes the report as JSON.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

QMLPAPERS = Path(r"D:\Data\Harold\EvidenceBasedDB\QMLPapers")
_STAMP = re.compile(r"arXiv:(\d{4}\.\d{4,5})(v\d+)?")


def first_page(path: Path) -> str:
    return subprocess.run(["pdftotext", "-l", "1", str(path), "-"], capture_output=True,
                          check=False).stdout.decode("utf-8", "replace")


def classify(row_id: str, text: str) -> tuple[str, str]:
    """(class, the stamped id or '')."""
    stamps = _STAMP.findall(text)
    if not stamps:
        return "no stamp", ""
    ids = [s[0] for s in stamps]
    return ("match", row_id) if row_id in ids else ("mismatch", ids[0])


def check(root: Path = QMLPAPERS, read=first_page) -> list[dict]:
    rows = []
    for manifest in sorted(root.glob("*/manifest.tsv")):
        folder = manifest.parent
        named = set()
        with manifest.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                name = row.get("file", "").strip()
                named.add(name)
                rid = (row.get("arxiv_id") or "").strip()
                path = folder / name
                entry = {"folder": folder.name, "file": name, "row_id": rid, "title": row.get("title", "")}
                if not path.exists():
                    entry.update(cls="missing", stamped="")
                elif not rid:
                    entry.update(cls="no id", stamped="")
                else:
                    cls, stamped = classify(rid, read(path))
                    entry.update(cls=cls, stamped=stamped)
                rows.append(entry)
        for pdf in sorted(folder.glob("*.pdf")):
            if pdf.name not in named:
                rows.append({"folder": folder.name, "file": pdf.name, "row_id": "", "title": "",
                             "cls": "no manifest row", "stamped": ""})
    return rows


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    rows = check()
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["cls"]] = counts.get(r["cls"], 0) + 1
    print("rows by class: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    for r in rows:
        if r["cls"] not in ("match", "no id"):
            print(f"{r['cls']:15} {r['folder']}/{r['file']} row {r['row_id'] or '-'}"
                  + (f" stamp {r['stamped']}" if r["stamped"] else ""))
    if "--out" in args:
        Path(args[args.index("--out") + 1]).write_text(json.dumps(rows, indent=1, ensure_ascii=False),
                                                         encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
