"""scripts/discover_candidates.py (F62 pilot): no network; OpenAlex answers
are fixtures shaped like the real response."""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _mod():
    spec = importlib.util.spec_from_file_location("discover", ROOT / "scripts" / "discover_candidates.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


WORK = {
    "id": "https://openalex.org/W1", "doi": "https://doi.org/10.1109/QAI.2025.33", "title": "Explaining  Anomalies",
    "publication_year": 2024, "cited_by_count": 10,
    "open_access": {"oa_status": "green", "oa_url": "https://arxiv.org/pdf/2505.03911"},
    "abstract_inverted_index": {"tensor": [1], "We": [0], "networks": [2]},
    "primary_location": {"source": {"display_name": "QAI", "host_organization_name": "IEEE"}},
    "locations": [{"landing_page_url": "https://arxiv.org/abs/2505.03911"}],
    "primary_topic": {"display_name": "Anomaly Detection"},
}


def test_the_key_goes_only_in_the_header_regression():
    """A key in the URL reaches logs and exception messages. Proven to fail
    by injection, 2026-10-06: with api_key added to the query parameters,
    the URL assertion went red."""
    req = _mod().request_for({"search": "x"}, "SECRET-KEY")
    assert "SECRET-KEY" not in req.full_url
    assert req.get_header("Authorization") == "Bearer SECRET-KEY"
    assert _mod().request_for({"search": "x"}, None).get_header("Authorization") is None


def test_a_candidate_carries_abstract_rank_and_free_copy():
    c = _mod().candidate(WORK, "tensor", date(2026, 10, 6))
    assert c["abstract"] == "We tensor networks"
    assert c["doi"] == "10.1109/QAI.2025.33" and c["arxiv"] == "2505.03911"
    assert c["cites_per_year"] == round(10 / 3, 1) and c["title"] == "Explaining Anomalies"


def test_store_duplicates_are_found_by_doi_arxiv_or_title_regression():
    """Proven to fail by injection, 2026-10-06: with the title check
    removed from held_by_store, the title-only duplicate came back None."""
    mod = _mod()
    c = mod.candidate(WORK, "tensor", date(2026, 10, 6))
    assert mod.held_by_store(c, ({"10.1109/qai.2025.33"}, set(), set())) == "doi"
    assert mod.held_by_store(c, (set(), {"2505.03911"}, set())) == "arxiv"
    assert mod.held_by_store(c, (set(), set(), {mod.norm_title("Explaining anomalies!")})) == "title"
    assert mod.held_by_store(c, (set(), set(), set())) is None


def test_it_refuses_to_write_inside_the_repository(capsys):
    assert _mod().main(["--out", str(ROOT / "discovery")]) == 2
    assert "inside the repository" in capsys.readouterr().err


def test_a_stream_request_uses_the_stream_spec():
    seen = []

    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"results": [WORK]}).encode()

    def opener(req, timeout):
        seen.append(req.full_url)
        return Resp()
    assert _mod().fetch_stream("fraud", 5, None, opener=opener) == [WORK]
    assert "title.search%3Afraud" in seen[0] and "title_and_abstract.search" in seen[0] and "per_page=5" in seen[0]
