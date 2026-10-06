"""scripts/link_code_repositories.py's note parser (Sprint 6 Task K, F35). No network."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location("link", ROOT / "scripts" / "link_code_repositories.py")
link = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(link)

NOTE = """# A title

- **arXiv:** [2502.18361](https://arxiv.org/abs/2502.18361)
- **Repository:** [{repo}]({repo})

## Where the link appears

> The code is available at {repo} and
> reproduces every figure.

---
"""


def _note(tmp_path, repo: str) -> dict | None:
    p = tmp_path / "x_repo.md"
    p.write_text(NOTE.format(repo=repo), encoding="utf-8")
    return link.read_note(p)


def test_a_repository_named_after_an_arxiv_id_is_still_a_repository_regression(tmp_path):
    """Proven to fail by injection: parsing the URL with parse_access read
    'arXiv-2502.18361-QELMWITNESS' as an arXiv id and returned no repository
    (the first version of the script did this to one of the 135 notes)."""
    n = _note(tmp_path, "https://github.com/salvatore-lorenzo/arXiv-2502.18361-QELMWITNESS")
    assert n["repo"] == "salvatore-lorenzo/arXiv-2502.18361-QELMWITNESS" and n["arxiv"] == "2502.18361"
    assert n["evidence"].startswith("The code is available at") and n["evidence"].endswith("every figure.")


def test_a_malformed_or_non_github_link_is_reported_not_guessed(tmp_path):
    assert _note(tmp_path, "https://github.com/cda-tum/qcec)--with")["repo"] is None
    assert _note(tmp_path, "https://zenodo.org/records/15745370")["repo"] is None
