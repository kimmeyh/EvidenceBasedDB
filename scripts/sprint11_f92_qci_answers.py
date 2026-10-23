#!/usr/bin/env python3
"""Sprint 11 Task C (F92): QCi's answers of 2026-10-20 and 2026-10-21 to Phase 2's Dirac-3S questions.

Three emails, read 2026-10-21 and 2026-10-22 in hsbc-qfraud-phase2's
`docs/qci_package/` (read only, F79). Phase 2 git-ignores that folder, so
no commit names them: each source record names the file, its SHA-256 at
read, the sender and the send date, and this script refuses to run when a
file's hash has changed.

- The 2026-10-20 reply (a QCi field service engineer) answers Phase 2's
  questions 3 to 14 of 2026-10-19 one line each.
- The 2026-10-21 reply (a QCi engineer the field service engineer named
  as having information on the eqc-models software) answers the question still open from 2026-09-25: whether eqc-models
  builds J = HH^T + lambda*I, C = -2Hy.
- The 2026-10-21 reply (the same field service engineer) reports the
  integer solver raised to 954 levels.

Each answer is a vendor statement by email, not a published document:
claim_type vendor-self-claim, evidence_tag N/A, certainty MODERATE for a
plain statement, LOW where the answer is hedged ("I assume") or states a
plan. Values name roles, not people; citations name the sender, as an
email citation does.

Stored assertions are not rewritten (F92 acceptance): a newer statement is
related to them. ADR-0004 A8 (b) links `supports` only when a whole claim
is confirmed and `contradicts` only when both cannot hold. No link
qualifies. The first apply linked the resolution answer `supports`
`dirac3s-analog-resolution-about-200-to-1`; the fresh-eyes review the same
day found it fails A8 (b) (that record states what the guide says; answer 9
narrows the ratio to linear contributions; the "yes" answered a two-part
question), so WITHDRAWN removes it. Every bearing is named in the value
instead, with the reason no link is made.

Every quote is checked by `require_verbatim` before anything is written,
and written only through `insert_verified_assertion` /
`sync_verified_assertion` (intake sections 26 and 31);
`tests/test_f92_qci_answers.py` checks the same against the files. DRY-RUN
BY DEFAULT; `--apply` takes a verified backup first. Idempotent.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import connect, script_paths  # noqa: E402
from store.backup import backup_before_write  # noqa: E402
from store.ingest import (AssertionRecord, insert_paper, insert_verified_assertion,  # noqa: E402
                          append_updated_reason, sync_verified_assertion, validate_assertion)
from store.quotes import plain, require_verbatim  # noqa: E402

_spec = importlib.util.spec_from_file_location("intake", Path(__file__).with_name("intake.py"))
intake = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intake)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT, DB_PATH, EXPORT_DIR = script_paths(__file__)
TODAY = "2026-10-22"
TAG = "Sprint 11 Task C, F92"
FOLDER = Path(r"D:\Data\Harold\github\hsbc-qfraud-phase2\docs\qci_package")

ANS = "qci-2026-10-20-email-dirac3s-answers"
HAM = "qci-2026-10-21-email-eqc-models-hamiltonian"
LEV = "qci-2026-10-21-email-integer-solver-levels"

FILES = {
    ANS: ("20261021 QCi Answers to Follow-up with Dirac-3S questions and two 925 questions.msg",
          "76a7c14d82b186600bab872662ab0b69a106b4273dfcf1c0321015ec7360161a"),
    HAM: ("20261021 QCi Answers to Follow-up with Dirac-3S questions - Wes Dyk on Hamiltonian.msg",
          "e79296e68a0d82bcd385ae71856fc4cb23e156cdd4141960c1e5928c59cf44a9"),
    LEV: ("20261021 QCi Answers to Follow-up with Dirac-3S questions - Charlotte Brown on integer solver levels.msg",
          "6f9254b78b208df2100dd4270172388e70087b20563fdfc506e31a451af0e9f1"),
}


def source_bytes(src: str) -> bytes:
    return (FOLDER / FILES[src][0]).read_bytes()


def source_text(src: str) -> str:
    """The .msg body text. An Outlook .msg stores its text as UTF-16LE at
    either byte alignment, so both decodings are joined; quotes are matched
    in the result, never in a hand copy."""
    data = source_bytes(src)
    return data.decode("utf-16le", errors="replace") + "\n" + data[1:].decode("utf-16le", errors="replace")


def _source(src, *, title, sender, sent, disposition, transcribed_from, applicability, read_detail):
    name, sha = FILES[src]
    return {
        "id": src, "kind": "reference", "context": "platform:dirac-3s", "tier": "read",
        "title": title,
        "citation": (f'{sender} (Quantum Computing Inc.), email reply "Re: External Sender Follow-up with Dirac-3S '
                     f'questions and two 9/25 questions," {sent}; filed by the team lead in hsbc-qfraud-phase2 docs/qci_package/ '
                     "(hand-transcribed from the email's header and signature)"),
        "transcribed_from": transcribed_from,
        "disposition": disposition,
        "access": str(FOLDER / name),
        "evidence": (f"SHA-256 {sha} (the file as read on {TODAY}), which the local-file check compares against. "
                     "Phase 2 git-ignores docs/qci_package/, so no commit names the file; the record depends on the "
                     "file and its hash. A private email, not a published document. Read-only from this repository "
                     "(F79)."),
        "found_via": "the team lead, 2026-10-21: filed in Phase 2's docs/qci_package/ and named in the session",
        "cited_as": name,
        "checked_against_source": f"{TODAY}, Claude, read the whole reply; {read_detail}",
        "reads": [["Claude", TODAY, "full", read_detail]],
        "applicability": applicability,
        "updated_reason": f"{TODAY}: added by scripts/sprint11_f92_qci_answers.py ({TAG}); read in full",
    }


SOURCES = [
    _source(ANS, title="QCi's answers to Phase 2's Dirac-3S questions 3 to 14",
            sender="Charlotte Brown, Field Service Engineer",
            sent="Tuesday, October 20, 2026, 10:38 AM",
            disposition=("Reference: QCi's one-line answers to Phase 2's Dirac-3S questions of 2026-10-19 (cloud "
                         "configuration, billing, integer levels, queues, resolution, error correction, raw values, "
                         "naming, where the guide's results were measured, sample cap, seeding)"),
            transcribed_from=("the header line \"Date: Tuesday, October 20, 2026 at 10:38 AM\" quoted in the later "
                              "reply, the subject line and the signature \"Charlotte Brown / Field Service Engineer\""),
            applicability=[
                ["platform:dirac-3s", "the vendor's answers on the Dirac-3S cloud device -- answers 3 and 5 to 14"],
                ["platform:dirac-3", "the dirac-3 cloud device unchanged by the Dirac-3S release -- answer 4"],
                ["hsbc-2026", "answers to the consumer project's own questions about its Dirac-3S runs -- the quoted "
                              "question email of 2026-10-19"],
            ],
            read_detail=("the whole reply (answers 3 to 14 and the two 9/25 items) and the 2026-10-19 question "
                         "email it quotes, to its measurement summary; the older thread below not read")),
    _source(HAM, title="QCi confirms eqc-models' CVQBoost Hamiltonian",
            sender="Wesley Dyk", sent="Wednesday, 21 October 2026, 14:55",
            disposition=("Reference: QCi's answer to Phase 2's question open since 2026-09-25: the Hamiltonian "
                         "eqc_models.ml.classifierqboost builds follows Phase 2's formula"),
            transcribed_from=("the header line \"Sent: Wednesday, 21 October 2026 14:55:49\" quoted in the later "
                              "reply and the signature \"Wes\""),
            applicability=[
                ["platform:dirac-3", "the eqc-models CVQBoost Hamiltonian, which Phase 1's Dirac-3 runs used "
                                     "(inferred from the question, not stated in the reply) -- the reply"],
                ["hsbc-2026", "the consumer project's fidelity argument rests on this reading -- the quoted "
                              "question"],
            ],
            read_detail="the whole reply and the quoted question it answers; the older thread below not read"),
    _source(LEV, title="QCi raises the integer solver to 954 levels",
            sender="Charlotte Brown, Field Service Engineer", sent="21 October 2026, after 14:55",
            disposition=("Reference: QCi's notice that the integer solver now has 954 levels on Dirac-3 and "
                         "Dirac-3S, with 9980 planned on Dirac-3S"),
            transcribed_from=("the reply's greeting and signature \"Charlotte Brown\", and the quoted reply under it "
                              "sent \"Wednesday, 21 October 2026 14:55:49\""),
            applicability=[
                ["platform:dirac-3s", "the integer solver's levels on Dirac-3S, and the planned 9980 -- the reply"],
                ["platform:dirac-3", "the integer solver's levels on Dirac-3 -- the reply"],
            ],
            read_detail="the whole reply and the header of the reply it quotes; the older thread below not read"),
]

VENDOR = "A vendor's own statement about its own device, by email, not a published document"


def A(src: str, **kw) -> AssertionRecord:
    kw.setdefault("updated", TODAY)
    kw.setdefault("updated_reason", f"{TODAY} ({TAG}): extracted from {src}, read in full on {TODAY}")
    kw.setdefault("derivation", "extracted")
    kw.setdefault("evidence_tag", "N/A")
    kw.setdefault("context", "platform:dirac-3s")
    kw.setdefault("fidelity", "scoped")
    kw.setdefault("claim_type", "vendor-self-claim")
    kw.setdefault("certainty", "moderate")
    kw.setdefault("certainty_reasons", VENDOR)
    return AssertionRecord(**kw)


HEDGED = VENDOR + "; LOW: the answer is hedged"
PLAN = VENDOR + "; LOW: a stated plan, not a capability"

ASSERTIONS: list[tuple[str, AssertionRecord]] = [
    (ANS, A(ANS, id="qci-email-dirac3s-cloud-queue-is-base-plus-expansion",
            value=("QCi states the cloud dirac-3s queue is served by the base unit with its expansion module, not "
                   "the base unit alone. Bears on dirac3s-variable-ceiling-by-configuration (the expansion "
                   "configuration's ceilings would apply if the cloud exposes the full configuration; QCi named the "
                   "hardware, not the ceilings); no link: that record states the guide's ceilings, which this does "
                   "not change"),
            provenance=f"{ANS}, answer to question 3",
            citation_context=('"Which configuration serves the cloud `dirac-3s` queue: the base unit, or the base '
                              'unit with its expansion?" (question 3); "Base Unit + Expansion module" (answer 3)'))),
    (ANS, A(ANS, id="qci-email-dirac3-cloud-unchanged-by-3s-release", context="platform:dirac-3",
            value="QCi states the dirac-3 cloud device was not altered with the release of Dirac-3S",
            provenance=f"{ANS}, answer to question 4",
            citation_context='"Dirac-3 on the cloud has not been altered with the release of 3S" (answer 4)')),
    (ANS, A(ANS, id="qci-email-dirac3s-billing-same-pool-as-dirac3",
            value=("QCi states the seconds used are counted the same way on Dirac-3 and Dirac-3S, from one billing "
                   "pool. The answer does not restate Phase 2's measured rule (the rounded-up sum of per-sample run "
                   "times, dirac3s-time-per-sample-schedule-2-by-size), so no link"),
            provenance=f"{ANS}, answer to question 5",
            citation_context='"seconds used is exactly the same between -3 and -3s.  one pool for billing." (answer 5)')),
    (ANS, A(ANS, id="qci-email-dirac3s-integer-limit-16-levels-hedged", certainty="low", certainty_reasons=HEDGED,
            value=("Asked whether the integer budget is still the sum of levels and whether the limit is 16 or 17 "
                   "levels per variable, QCi answered, hedged, that the limit is 16 levels, citing the guide's range "
                   "of 0 to 15; its \"yes\" may also confirm the sum-of-levels budget. Followed the next day by "
                   "qci-email-dirac3s-integer-solver-954-levels (unit not stated, so whether it changes this "
                   "per-variable limit is open). Bears on dirac3s-guide-gives-two-integer-ranges (the guide still "
                   "gives two ranges, so no link) and on dirac3-integer-variables-bounded-0-to-16 (a different "
                   "device, so no link)"),
            provenance=f"{ANS}, answer to question 6",
            citation_context=('"Is the integer budget still the sum of levels, and is the limit 16 or 17 levels per '
                              'variable?" (question 6); "I assume yes limit is 16 levels (User guide section 2 states '
                              'range of 0 to 15)" (answer 6)'))),
    (ANS, A(ANS, id="qci-email-dirac3-and-dirac3s-separate-devices-24x7",
            value=("QCi states dirac-3 and dirac-3s are two separate devices running 24x7, and an organization "
                   "enabled for dirac-3 can use either"),
            provenance=f"{ANS}, answer to question 7",
            citation_context=('"dirac-3 and dirac-3s are 2 separate devices running 24x7.  if your organization is '
                              'enabled for dirac-3, you get access to either." (answer 7)'))),
    (ANS, A(ANS, id="qci-email-dirac3s-resolution-same-as-dirac3",
            value=("Asked whether Dirac-3S's effective resolution is the same as Dirac-3's (about 200:1), or whether "
                   "200:1 is only its stated maximum, QCi answered yes: resolution follows the same math and "
                   "physical parameters, and although the output has more decimal places, only that resolution is "
                   "guaranteed. The yes does not say which part of the question it answers. QCi also said Phase 2's "
                   "200:1 finding about Dirac-3 seems consistent with its estimate from the user guide, and offered "
                   "to read the report. Bears on dirac3s-analog-resolution-about-200-to-1; no link: that record "
                   "states what the guide says, and QCi's next answer narrows the ratio to linear contributions"),
            provenance=f"{ANS}, answer to question 8 and the reply to the 9/25 item on the 200:1 finding",
            citation_context=('"Is Dirac-3S\'s effective resolution the same as Dirac-3\'s (about 200:1), or is 200:1 '
                              'only its stated maximum?" (question 8); "yes, resolution follows the same math logic / '
                              'physical parameters. While output contains more decimal places, we only guarantee this '
                              'resolution of accuracy." (answer 8); "the resolution limitation is based on the ratio of '
                              'max and min linear contributions" (answer 9); "a real and publishable engineering result about '
                              'Dirac-3" (the 9/25 item); "This seems consistent with our estimate from the user guide, '
                              'but we would be willing to take a look at your report" (reply to the 9/25 item)'))),
    (ANS, A(ANS, id="qci-email-dirac3s-cloud-outputs-after-error-correction",
            value=("QCi states the cloud system has built-in error correction and its outputs are currently after "
                   "error correction. Bears on dirac3s-returned-weights-finer-than-0005-step, whose cause Phase 2 "
                   "left unverified, and on dirac3s-error-correction-is-a-post-processing-step; neither whole claim "
                   "is confirmed, so no link"),
            provenance=f"{ANS}, answer to question 8a",
            citation_context=('"cloud system has built in error correction, outputs are currently post error '
                              'correction" (answer 8a)'))),
    (ANS, A(ANS, id="qci-email-dirac3s-raw-values-not-yet-on-cloud", certainty="low", certainty_reasons=PLAN,
            value=("Asked whether raw values can be had from the cloud, QCi answered that it is working to offer "
                   "them: they are not offered yet. Bears on dirac3s-returned-weights-finer-than-0005-step (\"QCi "
                   "states raw values come back too\", from the guide): both hold, the guide describing raw values "
                   "and the cloud not yet returning them, so no link"),
            provenance=f"{ANS}, answer to question 8b",
            citation_context=('"Can we get the raw values from the cloud?" (question 8b); "We are working to offer '
                              'output of raw values on the cloud" (answer 8b)'))),
    (ANS, A(ANS, id="qci-email-dirac3s-resolution-relative-to-linear-terms",
            value=("QCi states the resolution limit is set by the ratio of the largest to the smallest linear "
                   "contribution in the guide's section 2 equation, and by the resolution of the difference between "
                   "the largest and smallest values in that range (guide section 5.3); and that the Hamiltonian is "
                   "scaled to support the problem's dynamic range. Bears on "
                   "dirac3s-analog-resolution-about-200-to-1 (largest coefficient against smallest), which this "
                   "narrows to linear contributions; no link: that record states the guide, and both can hold"),
            provenance=f"{ANS}, answers to questions 9 and 9a",
            citation_context=('"the resolution limitation is based on the ratio of max and min linear contributions '
                              'shown in the equation in section 2 and resolution from the difference between max and '
                              'min values in that range. (User guide section 5.3)" (answer 9); "Hamiltonian is scaled '
                              'to support the dynamic range of the problem." (answer 9a)'))),
    (ANS, A(ANS, id="qci-email-dirac3s-to-replace-dirac3-names-distinct", certainty="low", certainty_reasons=PLAN,
            value=("QCi states it plans for Dirac-3S eventually to replace Dirac-3, with the two names kept "
                   "distinct; no date or notice is given. Consistent with dirac3s-replaced-dirac-3-on-qci-product-page"
                   " (the product page); no link, as that record is about the page"),
            provenance=f"{ANS}, answer to question 10",
            citation_context=('"Our plan is for Dirac-3S to eventually replace Dirac-3, but the names should remain '
                              'distinct." (answer 10)'))),
    (ANS, A(ANS, id="qci-email-dirac3s-guide-results-measured-on-premises",
            value=("QCi states the guide's Table 4 was measured on-premises on a Dirac-3S, computation time only, "
                   "without pre- or post-processing or queue time, and that all results in the user guide were "
                   "measured on-premises. Answers the gap dirac3s-guide-reuses-dirac-3-text-and-figures names (the "
                   "guide does not say); no link, as that record states what the guide says, which still holds"),
            provenance=f"{ANS}, answer to question 11",
            citation_context=('"Was the guide\'s Table 4 measured on Dirac-3S, and on the cloud or on-premises?" '
                              '(question 11); "On premises on a 3S system. These results are only for the '
                              'computation time, not including any pre- or post-processing or queue time. All '
                              'results in the user guide were done on-prem." (answer 11)'))),
    (ANS, A(ANS, id="qci-email-dirac3s-much-better-results-no-comparison-named", certainty="low",
            certainty_reasons=VENDOR + "; LOW: a general claim, with no comparison or problem class named",
            value=("Asked what comparison supports the claim of much better results, and on which problem class, "
                   "QCi named neither: it stated that Dirac-3S has improved speed, scale and solution quality"),
            provenance=f"{ANS}, answer to question 12",
            citation_context=('"much better results" (question 12); "On which problem class?" '
                              '(question 12); "Dirac 3S features improved computation speed, improved scale '
                              '(supporting a higher number of variables), and improved solution quality." (answer 12)'
                              ))),
    (ANS, A(ANS, id="qci-email-dirac3s-cloud-cap-100-samples",
            value=("QCi confirms the cloud cap is still 100 samples per job on dirac-3s. Consistent with "
                   "dirac3s-on-premises-has-no-100-sample-cap, which is about on-premises units; no link"),
            provenance=f"{ANS}, answer to question 13",
            citation_context='"Is the cloud cap still 100 samples per job on `dirac-3s`? - Yes" (question and answer 13)')),
    (ANS, A(ANS, id="qci-email-dirac3s-sampling-not-seedable",
            value=("QCi states a Dirac-3S job cannot be repeated with a sampling seed: randomness comes from "
                   "measuring the quantum state, and each sample is computed the same way"),
            provenance=f"{ANS}, answer to question 14",
            citation_context=('"Randomness is inherent to the measuring of the quantum state and is a physical '
                              'phenomenon, not a seeded option." (answer 14); "Problem computation is performed in the '
                              'same way for each sample." (answer 14)'))),
    (HAM, A(HAM, id="qci-email-eqc-models-cvqboost-hamiltonian-confirmed", context="platform:dirac-3",
            value=("A QCi engineer, named by the field service engineer as having information on eqc-models, "
                   "confirms that the Hamiltonian eqc_models.ml.classifierqboost builds "
                   "follows Phase 2's formula, J = HH^T + lambda*I and C = -2Hy, with sum constraint 1.0 and "
                   "w >= 0; the reply opens by assuming the question meant Phase 2's eqc_submit module. Bears on "
                   "dirac3-matches-exact-optimum-on-convex-cvqboost, whose \"identical Hamiltonian\" rests on this "
                   "reading; no link, as it confirms that record's premise, not its result"),
            provenance=f"{HAM}, the reply to the question open since 2026-09-25",
            certainty_reasons=VENDOR + "; the reply's opening assumption is kept in the value",
            citation_context=('"We solve J = HH^T + lambda*I, C = -2Hy with sum constraint 1.0 and w >= 0." (the '
                              'question, quoted in the thread); "Should have info about the eqc-models software." '
                              '(the field service engineer, in the thread); "assuming you are referring to your eqc_submit module" '
                              '(reply); "I can confirm that the Hamiltonian constructed in eqc_models.ml.classifierqboost'
                              ' follows the formula described." (reply)'))),
    (LEV, A(LEV, id="qci-email-dirac3s-integer-solver-954-levels",
            value=("QCi states the integer solver was raised to 954 levels on Dirac-3S (and on Dirac-3). The email "
                   "does not say whether 954 is per variable or the total budget; the unit is not stated. Newer "
                   "than qci-email-dirac3s-integer-limit-16-levels-hedged; no contradicts, as the email reports a "
                   "change, not that the earlier limit was wrong"),
            provenance=f"{LEV}, the reply",
            units="levels (per variable or total budget: not stated)",
            citation_context=('"We have increased to 954 levels on the integer solver on both the 3 and 3S systems." '
                              '(reply)'))),
    (LEV, A(LEV, id="qci-email-dirac3-integer-solver-954-levels", context="platform:dirac-3",
            value=("QCi states the integer solver was raised to 954 levels on Dirac-3 (and on Dirac-3S). The email "
                   "does not say whether 954 is per variable or the total budget; the unit is not stated. Bears on "
                   "dirac3-integer-variables-bounded-0-to-16; no contradicts, as the unit is not given and the email "
                   "reports a change"),
            provenance=f"{LEV}, the reply",
            units="levels (per variable or total budget: not stated)",
            citation_context=('"We have increased to 954 levels on the integer solver on both the 3 and 3S systems." '
                              '(reply)'))),
    (LEV, A(LEV, id="qci-email-dirac3s-integer-levels-9980-planned", certainty="low", certainty_reasons=PLAN,
            value=("QCi states it plans, in the coming weeks, to raise the possible integer levels on Dirac-3S to "
                   "9980; a stated plan, not a capability, unit not stated. 9980 is also the one-expansion "
                   "second-order variable ceiling in dirac3s-variable-ceiling-by-configuration; the email does not "
                   "connect the two"),
            provenance=f"{LEV}, the reply",
            units="levels (per variable or total budget: not stated)",
            citation_context=('"In the coming weeks, we will be also increasing the possible levels on 3S to 9980 '
                              'levels as well." (reply)'))),
]


def check_hashes() -> list[str]:
    bad = []
    for src, (name, sha) in FILES.items():
        digest = hashlib.sha256(source_bytes(src)).hexdigest()
        if digest != sha:
            bad.append(f"{name} differs from the copy read on {TODAY} (SHA-256 {digest})")
    return bad


def verify_all() -> list:
    """Every quote verbatim in its email BEFORE anything is written
    (INTAKE_WORKFLOW.md sections 26 and 31)."""
    texts = {src: plain(source_text(src)) for src in FILES}
    return [(src, a, require_verbatim(a.id, a.citation_context, texts[src], value=a.value)) for src, a in ASSERTIONS]


# Relations this script wrote and withdrew. The sync adds relations and never
# removes them (other scripts add links it does not know about), so a link
# this script itself got wrong is removed here, by name, with the reason
# appended to the record's updated_reason.
WITHDRAWN = [
    ("qci-email-dirac3s-resolution-same-as-dirac3", "dirac3s-analog-resolution-about-200-to-1", "supports",
     "the supports link to dirac3s-analog-resolution-about-200-to-1 withdrawn after the fresh-eyes review: it "
     "fails ADR-0004 A8 (b), as that record states what the guide says and answer 9 narrows the ratio to linear "
     "contributions"),
]


def _correct_source(conn, entry) -> list[str]:
    """Bring a source record this script wrote to the script's current
    citation and applicability rationales (the fresh-eyes review of
    2026-10-22 corrected both); return the names of what changed."""
    paper = intake.build_record(entry, today=TODAY)
    changed = []
    if conn.execute("SELECT provenance FROM records WHERE id = ?", (paper.id,)).fetchone()[0] != paper.citation:
        conn.execute("UPDATE records SET provenance = ? WHERE id = ?", (paper.citation, paper.id))
        changed.append("citation")
    stored = dict(conn.execute("SELECT context_id, rationale FROM paper_applicability WHERE record_id = ?",
                               (paper.id,)).fetchall())
    for context_id, rationale in paper.applicability:
        if stored.get(context_id) != rationale:
            conn.execute("UPDATE paper_applicability SET rationale = ? WHERE record_id = ? AND context_id = ?",
                         (rationale, paper.id, context_id))
            changed.append(f"applicability {context_id}")
    if changed:
        append_updated_reason(conn, paper.id, f"{TODAY} ({TAG}): corrected after the fresh-eyes review: "
                              + ", ".join(changed), TODAY)
    return changed


def apply_changes(conn) -> list[str]:
    checked = verify_all()
    log = []
    for entry in SOURCES:
        if conn.execute("SELECT 1 FROM paper_fields WHERE record_id = ?", (entry["id"],)).fetchone() is None:
            insert_paper(conn, intake.build_record(entry, today=TODAY))
            log.append(f"paper  {entry['id']} [read]")
            continue
        changed = _correct_source(conn, entry)
        log.append(f"update {entry['id']} [{', '.join(changed)}]" if changed else f"exists {entry['id']}")
    for from_id, to_id, relation, why in WITHDRAWN:
        cur = conn.execute("DELETE FROM assertion_relations WHERE from_assertion_id = ? AND to_assertion_id = ? "
                           "AND relation = ?", (from_id, to_id, relation))
        if cur.rowcount:
            append_updated_reason(conn, from_id, f"{TODAY} ({TAG}): {why}", TODAY)
            log.append(f"unlink {from_id} -{relation}-> {to_id}")
    for src, a, verified in checked:
        if not conn.execute("SELECT 1 FROM records WHERE id = ?", (a.id,)).fetchone():
            insert_verified_assertion(conn, a, verified, yielded_by=src)
            log.append(f"assert {a.id} <- {src} [{a.certainty}, {a.context}]")
            continue
        changed = sync_verified_assertion(conn, a, verified, f"{TODAY} ({TAG}): corrected to the script's current "
                                          "text", TODAY)
        log.append(f"update {a.id} [{', '.join(changed)}]" if changed else f"exists {a.id}")
    return log


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    bad = check_hashes()
    if bad:
        print("\n".join(bad))
        return 1
    if "--apply" not in args:
        for entry in SOURCES:
            intake.build_record(entry, today=TODAY)  # validates the entry; nothing written
            print(f"paper  {entry['id']} [read]")
        for src, a, _ in verify_all():
            validate_assertion(a)  # the checks insert_assertion runs; nothing written
            print(f"assert {a.id} <- {src} [{a.certainty}, {a.context}]")
        print("DRY RUN: nothing written. Re-run with --apply.")
        return 0
    backup_before_write(DB_PATH, "F92 QCi answers of 2026-10-20 and 2026-10-21")
    conn = connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout = 120000")
    try:
        log = apply_changes(conn)
        conn.commit()
    finally:
        conn.close()
    print("\n".join(log))
    print("APPLIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
