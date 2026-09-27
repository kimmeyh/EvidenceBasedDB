"""Task F's person matching (Sprint 5, F5 sub-part 2).

The disambiguation rule in docs/research/2026-09-24_F5_qci_affiliated_people.md
rests on one primitive: deciding that a name a source prints IS one of the
18 people. The first version keyed names on family plus first initial, and
"Huang, Y." would then have made any stranger's paper a QCi "seed" for Sam
Wu. These cases pin the tightened rule. Proven to fail by reverting the
COMMON_FAMILIES check: the stranger-seed case goes red.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import sprint5_qci_authors as q  # noqa: E402


@pytest.mark.parametrize("given,family,person,expected", [
    ("Yuping", "Huang", ("Yu-Ping", "Huang"), True),        # hyphen dropped, full name
    ("Y.", "Huang", ("Yu-Ping", "Huang"), False),           # an initial on a common family is nobody
    ("S.", "Wu", ("Sam", "Wu"), False),
    ("Samuel", "Wu", ("Sam", "Wu"), False),                 # conservative on a common family
    ("N.", "Chancellor", ("Nicholas", "Chancellor"), True),  # an initial on an uncommon family
    ("Nicholas", "Vrahoretis", ("Nick", "Vrahoretis"), True),
    ("R. J.", "Rupert", ("R. Joseph", "Rupert"), True),
    ("Y. M.", "Sua", ("Yong Meng", "Sua"), True),
    ("Nicholas", "Chancelor", ("Nicholas", "Chancellor"), False),  # family must match exactly
])
def test_is_person(given, family, person, expected):
    assert q.is_person(given, family, person) is expected


def test_a_strangers_initial_does_not_seed_a_common_name_regression():
    """The case the tightening exists for. Proven to fail by injection:
    removing "huang" from COMMON_FAMILIES makes this assert go red."""
    stranger = {"authors": [("Sam", "Wu"), ("Y.", "Huang")]}
    assert q.names_other_qci_person(stranger, ("Sam", "Wu")) is False
    real = {"authors": [("Sam", "Wu"), ("Yu-Ping", "Huang")]}
    assert q.names_other_qci_person(real, ("Sam", "Wu")) is True


def test_network_rule_needs_two_shared_coauthors():
    person = ("Nicholas", "Chancellor")
    seed = {"id": "arXiv:1", "authors": [person, ("Uchenna", "Chukwu"), ("Viv", "Kendon"), ("Halim", "Kusumaatmaja")]}
    one = {"id": "arXiv:2", "authors": [person, ("Viv", "Kendon"), ("A.", "Stranger")]}
    two = {"id": "arXiv:3", "authors": [person, ("Viv", "Kendon"), ("Halim", "Kusumaatmaja")]}
    accepted, unresolved = q.disambiguate(person, [seed, one, two])
    assert {a["id"]: a["rule"] for a in accepted} == {"arXiv:1": "seed", "arXiv:3": "network"}
    assert [u["id"] for u in unresolved] == ["arXiv:2"]
