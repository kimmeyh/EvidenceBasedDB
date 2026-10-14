"""F61 (Sprint 8 Task F): the Massoli list is parsed, its duplicates are
found before anything is entered, and each entry gets one class. Runs on
two entries in the list's own markup; no network."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

LIST = """# Surveys

### 2021
<details><summary>[Bharti et al] <b><a href=https://arxiv.org/abs/2101.08448> Noisy intermediate-scale quantum (NISQ) algorithms. </a></b> <i>arXiv.</i> <code><b>[Variational Quantum Algorithms]</b></code> <code><i>(Gate Model)</i></code></summary><pre><code>@article{bharti2021noisy,
  title={Noisy intermediate-scale quantum (NISQ) algorithms},
  author={Bharti, Kishor and Cervera-Lierta, Alba},
  journal={arXiv preprint arXiv:2101.08448},
  year={2021}
}</code></pre></details>

# Papers

### 2020
<details><summary>[Mangini et al] <b><a href=https://iopscience.iop.org/article/10.1209/0295-5075/134/10002/meta> Quantum computing models for artificial neural networks. </a></b> <i>EPL (Europhysics Letters).</i> <code><b>[Quantum Neural Networks]</b></code> </summary><pre><code>@article{mangini2021quantum,
  title={Quantum computing models for artificial neural networks},
  author={Mangini, Stefano and Tacchino, Francesco},
  journal={EPL (Europhysics Letters)},
  year={2021}
}</code></pre></details>
<details><summary>[Ablayev et al] <b><a href=https://ieeexplore.ieee.org/document/8935094> On quantum methods for machine learning problems part I: Quantum tools. </a></b> <i>Big Data Mining and Analytics.</i> <code><b>[Quantum Machine Learning]</b></code></summary><pre><code>@Article{ablayev2020quantum1,
  Title                    = {{On quantum methods for machine learning problems part I: Quantum tools}},
  Author                   = {Ablayev, Farid and Ablayev, Marat},
  Year                     = {2020}
}
</code></pre></details>
<details><summary>[Somebody] <b><a href=https://www.Nature.com/articles/s41598-021-85208-3> Speeding up quantum perceptron via shortcuts to adiabaticity. </a></b> <i>Scientific Reports.</i> <code><b>[Quantum Perceptron]</b></code></summary><pre><code>@article{x,
  title={Speeding up quantum perceptron via shortcuts to adiabaticity},
  author={Ban, Yue},
  year={2021}
}</code></pre></details>
"""


def _mod():
    spec = importlib.util.spec_from_file_location("f61", ROOT / "scripts" / "sprint8_f61_massoli_list.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parse_reads_section_year_link_title_and_tags():
    entries = _mod().parse(LIST)
    assert [(e["section"], e["year"]) for e in entries] == [("Surveys", "2021"), ("Papers", "2020"),
                                                             ("Papers", "2020"), ("Papers", "2020")]
    first = entries[0]
    assert first["title"] == "Noisy intermediate-scale quantum (NISQ) algorithms"
    assert first["authors"] == "Bharti et al" and first["tags"] == ["Variational Quantum Algorithms", "Gate Model"]
    assert entries[2]["bib"]["title"] == "On quantum methods for machine learning problems part I: Quantum tools"


def test_identifiers_from_links_and_bibtex():
    m = _mod()
    entries = m.parse(LIST)
    assert m.identifiers(entries[0]) == ("2101.08448", "")
    assert m.identifiers(entries[1]) == ("", "10.1209/0295-5075/134/10002")
    assert m.identifiers(entries[2]) == ("", "")
    assert m.identifiers(entries[3]) == ("", "10.1038/s41598-021-85208-3")


def test_duplicates_are_found_before_anything_is_entered():
    """Proven to fail by injection, 2026-10-12: with the title match removed
    from match(), the Ablayev entry was classed `enter` by its searched DOI
    instead of `in store`."""
    m = _mod()
    entries = m.parse(LIST)
    idx = {"arxiv": {"2101.08448": "bharti-2021"}, "doi": {},
           "title": {m.norm("On quantum methods for machine learning problems part I: Quantum tools"):
                     [("ablayev-2020", "Ablayev, F., Ablayev, M., ...")]}}
    m.classify(entries, idx, fetcher=None, search=lambda title, f: "10.1109/BDMA.2019.9020001")
    got = [(e["cls"], e["record"]) for e in entries]
    assert got == [("in store", "bharti-2021"), ("enter", "DOI:10.1209/0295-5075/134/10002"),
                   ("in store", "ablayev-2020"), ("enter", "DOI:10.1038/s41598-021-85208-3")]


def test_link_debris_is_not_part_of_the_doi():
    """Found in the 2026-10-12 dry run: seven DOIs kept a file suffix or a
    query string and the door refused them as unregistered."""
    m = _mod()
    assert m.doi_from_link("https://www.nature.com/articles/Nature10012.pdff") == "10.1038/Nature10012"
    assert m.doi_from_link("https://link.springer.com/content/pdf/10.1007/s42484-020-00012-y.pdf") == \
        "10.1007/s42484-020-00012-y"
    assert m.doi_from_link("https://link.springer.com/article/10.1007/s10773-017-3514-4&casa_token=CO3V") == \
        "10.1007/s10773-017-3514-4"


def test_an_entry_with_no_identifier_is_refused_with_the_reason():
    m = _mod()
    entries = m.parse(LIST)[2:3]
    m.classify(entries, {"arxiv": {}, "doi": {}, "title": {}}, fetcher=None, search=lambda title, f: "")
    assert entries[0]["cls"] == "refused" and "no exact-title match" in entries[0]["reason"]


@pytest.mark.live_store
def test_the_entered_records_name_the_list_and_sit_at_seen(live_conn):
    """The 2026-10-12 apply: 137 papers at `seen`, each found via the list,
    and the list's repository linked to the survey as dataset-of."""
    rows = live_conn.execute(
        "SELECT f.tier FROM paper_fields f JOIN paper_found_via v ON v.record_id = f.record_id "
        "WHERE v.route LIKE 'Massoli et al. survey list%'").fetchall()
    assert len(rows) >= 137 and {r[0] for r in rows} <= {"seen", "screened", "read"}
    assert live_conn.execute("SELECT 1 FROM source_links WHERE to_id = ? AND link_type = 'dataset-of'",
                             (_mod().SURVEY,)).fetchone()


def test_a_title_match_needs_the_first_author():
    m = _mod()
    entry = m.parse(LIST)[1]
    idx = {"arxiv": {}, "doi": {}, "title": {m.norm(entry["title"]): [("other", "Someone Else, A.")]}}
    assert m.match(entry, "", "", idx) == ("", "")
