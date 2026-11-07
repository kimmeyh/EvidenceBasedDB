#!/usr/bin/env python3
"""F139 (Sprint 16 Task B), render once: a PDF page rendered to an image once per file, page and resolution, kept
beside the text cache, so the reviewer opens the image the reader rendered instead of rendering it again.

    python scripts/render_page.py <pdf> <page> [--dpi 100] [--group <group>]

Prints the image's path. The key is the file's SHA-256, the page, the resolution and pdftoppm's version, so a
changed file or a new pdftoppm renders again. The image is written to a file of its own and then moved into place,
so two agents rendering the same page never share a half-written image. A crop of one panel is not cached (the
reader picks its box by eye, so a crop is rarely asked twice); the prompt keeps pdftoppm's own crop command for it.
With --group, the render is counted in that group's telemetry file (`scripts/read_telemetry.py`) when it has one.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store import text_cache_dir  # noqa: E402

RENDERS: list[str] = []  # the pages this process rendered, not served from the cache


@lru_cache(maxsize=1)
def _tool() -> str:
    out = subprocess.run(["pdftoppm", "-v"], capture_output=True)
    return hashlib.sha256(" ".join((out.stdout + out.stderr).decode("utf-8", "replace").split()[:3]).encode()
                          ).hexdigest()[:12]


def render(pdf: str, page: int, dpi: int = 100) -> Path:
    digest = hashlib.sha256(Path(pdf).read_bytes()).hexdigest()
    image = text_cache_dir() / "pages" / f"{digest}-p{page}-{dpi}dpi-{_tool()}.png"
    if image.is_file() and image.stat().st_size:
        return image
    image.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=image.parent) as tmp:
        stem = Path(tmp) / "page"
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-png", "-singlefile", pdf,
                        str(stem)], capture_output=True, check=True)
        Path(f"{stem}.png").replace(image)
    RENDERS.append(f"{pdf}#{page}@{dpi}")
    return image


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    dpi, group = 100, ""
    if "--dpi" in args:
        i = args.index("--dpi")
        dpi = int(args[i + 1])
        del args[i:i + 2]
    if "--group" in args:
        i = args.index("--group")
        group = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__)
        return 1
    print(render(args[0], int(args[1]), dpi))
    if group:
        import read_telemetry
        read_telemetry.step(group, "render", pages_rendered=len(RENDERS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
