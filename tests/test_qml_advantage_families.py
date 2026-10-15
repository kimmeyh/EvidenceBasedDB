"""The QML-advantage family sort (Sprint 9 Task E, F78): titles are sorted
by the first family they match, and only titles that claim an advantage
count. Proven to fail by injection, 2026-10-15: with a sampling family
inserted ahead of the kernel family, the "Quantum kernel speedup by
sampling" precedence case went red (and so did the plain sampling case,
whose family name changed). Restored and green again."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("qaf", ROOT / "scripts" / "qml_advantage_families.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("title,expected", [
    ("Evidence of Scaling Advantage for the Quantum Approximate Optimization Algorithm", "optimization"),
    ("Supervised learning with quantum enhanced feature spaces", "kernels and feature maps"),
    ("Exponential quantum advantage in processing massive classical data", "linear algebra"),
    ("Unconditional Quantum Advantage for Sampling with Shallow Circuits", "sampling and generative models"),
    ("Quantum advantage in learning from experiments", "quantum data and sensing"),
    ("Exploring quantum mechanical advantage for reservoir computing", "quantum dynamics (reservoirs, simulation)"),
    ("Provable Advantage in Quantum PAC Learning", "learning theory"),
    ("Unleashing the Advantage of Quantum AI", "other or unspecified"),
    # precedence: a kernel title that also mentions sampling is a kernel claim
    ("Quantum kernel speedup by sampling", "kernels and feature maps"),
    # "samples" is not sampling (review, 2026-10-15)
    ("Quantum enhanced probing of multilayered-samples", "quantum data and sensing"),
])
def test_family(title, expected):
    assert _script().family(title) == expected


def test_only_claiming_titles_count():
    qaf = _script()
    assert qaf.CLAIMS.search("A quantum speed-up for clustering")
    assert not qaf.CLAIMS.search("Variational quantum classifiers on tabular data")
