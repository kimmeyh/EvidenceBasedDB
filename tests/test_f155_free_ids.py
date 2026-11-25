"""F155 (Sprint 19 Task C): a new assertion id is free when the reader chooses it, and the audit and map checkers
name an answered id one character off a given one.

Sprint 18 evidence (INTAKE_WORKFLOW.md section 78): five reader ids in g510 and g352 were already other sources'
and were renamed after review; audit runs a018 and a030 each mistyped one given id.

Proven red by injection, 2026-11-25, with three injections at once (`unique_assertion_id` returning `name`
unchanged, `id_problems` returning [], and the near-miss suffix removed from `f146_checks.problems`): four tests
failed (the taken name, the read checker, the audit checker, and the g352 reproduction); the three pure helpers'
tests stayed green, as they must. Restored, 7 passed.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from store.assertion_ids import near_miss, one_edit_apart, store_ids, unique_assertion_id  # noqa: E402


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


check = _load("g_check", ROOT / "scripts" / "sprint13_g_check.py")
f146 = _load("f146", ROOT / "scripts" / "f146_checks.py")
RID = "banuls-2019-simulating-lattice-gauge-theories-within"


def test_a_free_name_is_kept():
    assert unique_assertion_id(RID, "vqe-definition", {"other"}) == "vqe-definition"


def test_a_taken_name_takes_the_author_and_year():
    """f117_build_groups.prefixed's rule: the record id's first two words, then more, until free."""
    assert unique_assertion_id(RID, "vqe-definition", {"vqe-definition"}) == "banuls-2019-vqe-definition"
    assert (unique_assertion_id(RID, "vqe-definition", {"vqe-definition", "banuls-2019-vqe-definition"})
            == "banuls-2019-simulating-vqe-definition")


def test_the_read_checker_refuses_a_held_id_and_names_the_free_one():
    data = {"papers": [
        {"record_id": RID, "assertions": [{"id_suggestion": "review-scope"}, {"id_suggestion": "own-stored"},
                                          {"id_suggestion": "new-one"}]},
        {"record_id": "smith-2020-x", "assertions": [{"id_suggestion": "new-one"}]},  # the same id in one file
    ]}
    out = check.id_problems(data, {RID: {"own-stored"}}, {"review-scope"})
    assert len(out) == 3, out
    assert "take banuls-2019-review-scope" in out[0]
    assert "take banuls-2019-own-stored" in out[1]
    assert "smith-2020-x/new-one" in out[2] and "take smith-2020-new-one" in out[2]
    assert check.id_problems({"papers": [{"record_id": RID, "assertions": [{"id_suggestion": "free"}]}]},
                             {}, {"review-scope"}) == []


def test_other_groups_ids_reads_other_groups_and_their_saved_papers(tmp_path):
    reads = tmp_path / "reads"
    reads.mkdir()
    (reads / "group_g600.json").write_text(json.dumps({"papers": [{"assertions": [{"id_suggestion": "mine"}]}]}))
    (reads / "group_g601.json").write_text(json.dumps({"papers": [{"assertions": [{"id_suggestion": "theirs"}]}]}))
    done = tmp_path / "tmp_g602" / "done"
    done.mkdir(parents=True)
    (done / "x.json").write_text(json.dumps({"papers": [{"assertions": [{"id": "in-progress"}]}]}))
    own = tmp_path / "tmp_g600" / "done"
    own.mkdir(parents=True)
    (own / "y.json").write_text(json.dumps({"papers": [{"assertions": [{"id": "my-own-progress"}]}]}))
    got = check.other_groups_ids(reads / "group_g600.json", "g600", local=tmp_path, dirs=(reads,))
    assert got == {"theirs", "in-progress"}


def test_one_edit_apart_and_near_miss():
    assert one_edit_apart("a018-x", "a018-y") and one_edit_apart("abc", "abcd") and one_edit_apart("abcd", "acd")
    assert not one_edit_apart("abc", "abc") and not one_edit_apart("abc", "axy")
    assert near_miss("hi-0012", ["hi-0013", "zz"]) == "hi-0013"
    assert near_miss("hi-0012", ["zz"]) is None


def test_the_audit_checker_names_a_near_miss():
    given = [{"id": "kim-2023-utility-claim"}]
    out, answered = f146.problems("audit", given, {"kim-2023-utility-claim-": {"verdict": "held", "why": "x"}}, {})
    assert any("one character from the given id kim-2023-utility-claim" in p for p in out), out
    assert answered == set()


@pytest.mark.live_store
def test_the_sprint_18_vqe_definition_collision_is_reproduced_and_given_a_free_id(tmp_path):
    """g352's reader chose `vqe-definition`, which another source held; review renamed it
    `banuls-2019-vqe-definition` by hand. A copy of the group file with the reader's own id, checked against the
    store as it was before the apply (the renamed id taken out), is refused, and the free id is the one review
    chose."""
    data = json.loads((ROOT / "manifests" / "sprint13_g_reads" / "group_g352.json").read_text(encoding="utf-8"))
    for p in data["papers"]:
        for a in p.get("assertions", []):
            if (a.get("id_suggestion") or a.get("id")) == "banuls-2019-vqe-definition":
                a["id_suggestion"] = "vqe-definition"
    copy = tmp_path / "group_g352.json"
    copy.write_text(json.dumps(data), encoding="utf-8")
    from store import script_paths
    taken = store_ids(script_paths(str(ROOT / "scripts" / "x.py"))[1]) - {"banuls-2019-vqe-definition"}
    assert "vqe-definition" in taken, "the store no longer holds the other source's vqe-definition"
    out = check.id_problems(json.loads(copy.read_text(encoding="utf-8")), {}, taken)
    hit = [p for p in out if p.startswith(f"{RID}/vqe-definition:")]
    assert hit and hit[0].endswith("take banuls-2019-vqe-definition"), out
