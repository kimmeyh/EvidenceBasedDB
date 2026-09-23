"""scripts/adjudication_timing.py (Sprint 4 retrospective improvement 6).

Runs the real script against a synthetic packet in tmp, so the committed
F11 log is never touched.

Proven by injection 2026-09-22: making `done` stamp `start` instead of
`end` turns test_done_measures_the_interval_between_show_and_done red;
dropping the "already shown" guard in `show` turns
test_re_showing_a_record_does_not_restart_its_clock red.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "adjudication_timing.py"

PACKET = """# Packet

## The 2 records

### 1. `alpha-2026-first`

- **Title**: First
- **Access**: https://arxiv.org/abs/1111.11111

### 2. `beta-2026-second`

- **Title**: Second
- **Access**: https://doi.org/10.1/2

## Timing sheet

### 99. `not-a-record`
"""


def load():
    spec = importlib.util.spec_from_file_location("adjudication_timing", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def packet(tmp_path):
    p = tmp_path / "SPRINT_9_TEST_PACKET.md"
    p.write_text(PACKET, encoding="utf-8")
    return p


def test_sections_stop_at_the_timing_sheet(packet):
    secs = load().sections(packet)
    assert set(secs) == {1, 2}, "the timing sheet's own headings are not records"
    assert secs[1][0] == "alpha-2026-first"


def test_show_starts_the_clock_and_prints_the_record(packet, capsys):
    mod = load()
    assert mod.show(packet, 1) == 0
    out = capsys.readouterr().out
    assert "Record 1 of 2: `alpha-2026-first`" in out
    assert "https://arxiv.org/abs/1111.11111" in out
    log = json.loads(mod.log_path(packet).read_text(encoding="utf-8"))
    assert log["records"][0]["start"] and log["records"][0]["end"] is None


def test_re_showing_a_record_does_not_restart_its_clock(packet):
    mod = load()
    mod.show(packet, 1)
    first = json.loads(mod.log_path(packet).read_text(encoding="utf-8"))["records"][0]["start"]
    mod.show(packet, 1)
    again = json.loads(mod.log_path(packet).read_text(encoding="utf-8"))["records"][0]["start"]
    assert again == first, "a redisplay must not reset the interval being measured"


def test_done_measures_the_interval_between_show_and_done(packet, monkeypatch):
    mod = load()
    stamps = iter(["2026-09-21T22:00:00", "2026-09-21T22:01:30", "2026-09-21T22:01:30"])
    monkeypatch.setattr(mod, "now", lambda: next(stamps))
    mod.show(packet, 1)
    mod.done(packet, 1, "1 accept all")
    entry = json.loads(mod.log_path(packet).read_text(encoding="utf-8"))["records"][0]
    assert entry["minutes"] == 1.5
    assert entry["answer"] == "1 accept all"
    assert entry["end"] == "2026-09-21T22:01:30"


def test_done_shows_the_next_record_in_the_same_call(packet, capsys):
    mod = load()
    mod.show(packet, 1)
    mod.done(packet, 1, "1")
    out = capsys.readouterr().out
    assert "logged record 1" in out
    assert "Record 2 of 2: `beta-2026-second`" in out


def test_done_on_a_record_never_shown_is_refused(packet):
    mod = load()
    assert mod.done(packet, 2, "1") == 1


def test_summary_reports_the_number_and_the_mode(packet, capsys, monkeypatch):
    mod = load()
    # One stamp per now() call, in order: show(1) start; done(1) end;
    # show(2) start, which done(1) performs; done(2) end.
    stamps = iter(["2026-09-21T22:00:00", "2026-09-21T22:01:00",
                   "2026-09-21T22:01:00", "2026-09-21T22:03:00"])
    monkeypatch.setattr(mod, "now", lambda: next(stamps))
    mod.show(packet, 1, mode="cold")
    mod.done(packet, 1, "1")
    mod.done(packet, 2, "2 revise: title")
    capsys.readouterr()
    mod.summary(packet)
    out = capsys.readouterr().out
    assert "records    : 2" in out
    assert "total      : 3.0 min" in out
    assert "per record : 1.50 min" in out
    assert "mode       : cold" in out, "the protocol mode is part of the measurement"


def test_the_log_lives_beside_the_packet(packet):
    mod = load()
    assert mod.log_path(packet).name == "SPRINT_9_TEST_TIMING_LOG.json"
