# P2 second-pass evidence — QA-REVIEWER lens

- **Role:** QA-REVIEWER, second independent P2 pass (authored none of the artifacts)
- **Date:** 2026-10-25
- **Batch:** 2026-10-25-relmap-r2-batch · worktree branch `feat/relmap-r2`
- **Mode:** validation — both deferred seams re-probed by executing the stored probe scripts
  fresh; every first-pass QA finding re-verified against the amended contract (amendment
  commit `daddd6d`)
- **Probe environment:** `PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 python -c "import
  mapper; print(mapper.__file__)"` printed the worktree's own `mapper\__init__.py`
  (worktree-root import proven before any probe; probe (b) also ran with
  `PYTHONPATH=<worktree>` per its stored command). Textual 8.2.8. Scratch fixtures were built
  under the system temp dir and deleted after the runs; no worktree file was modified.

## Probe re-runs (TASK 1)

### Seam (a) — AT-driver host push / fixture workspace injection — REPRODUCIBLE

- Stored command (from `evidence/p2-seam-at-driver.md`, run from the worktree root):
  `PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 python <scratch>/probe_seam_at_driver.py`
- Re-run: script reconstructed verbatim from the transcript into a fresh scratch dir;
  exit **0**; output matched the stored transcript on every assertion:
  `MapperApp` constructed with the injected tmp workspace (`app.store.workspace == ws`),
  Home screen reached via `run_test(size=(120,40))` Pilot, `#home-recents` row
  `['svc_probe', ' legacy ', '3', '0']`, `store.load('svc_probe')` → 3 nodes / 2 schema
  fields, `#home-hero` carries the map name, clean exit, `PROBE-RESULT: PASS`.
- Verdict: **reproducible** — the seam claim and the named injection point
  (`MapperApp(workspace=…)`, `mapper/app.py:250`, verified in code) are real on today's tree.

### Seam (b) — workspace-as-repo canon derivation — REPRODUCIBLE

- Stored command (from `evidence/p2-seam-workspace-repo.md`):
  `PYTHONPATH=<worktree> PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 python <scratch>/p2_probe.py`
  plus the follow-up `p2_probe2.py` (W5).
- Re-run: both scripts reconstructed verbatim; probe 1 exit **0**, probe 2 exit **0**;
  outputs matched the stored transcript: W1/W1g/W1r (bare dir / empty `.git` / real
  `git init`) derive byte-identically (4 nodes / 2 `refines` edges); W2 missing canon →
  `CanonUnavailable cause='file not found'` → `structure: unavailable (canon: file not
  found)`; W3a non-UTF-8 → `unavailable (canon: is not UTF-8 text)`; W3b garbage-UTF-8 →
  healthy empty map (not unavailable); W3c broken row → derived map + `unparsed row` note +
  MED gap; W4 corrupt descriptor → `structure: refused (probe.relmap.yml): not valid YAML -
  descriptor skipped`; audit wrapper short-circuits on non-git (`unavailable (no
  repository)`) / no-registry (`unavailable (no registry)`); W5 real git repo with
  `reqharness/` reaches the hook with `report.repo` = the git toplevel. No exception ever
  escapes; never a crash.
- Verdict: **reproducible** — the workspace-canon rule claimed by the amendment holds on
  today's code, including the recorded caveat (the `--audit` hook's git gating is the RVU
  surface, out of scope for the screen derivation path).

## First-pass findings re-verified against the amended contract (TASK 2)

| ID | First-pass severity | Disposition claimed | Verified / reopened | Evidence (file:line) |
|---|---|---|---|---|
| QA-01 | major | fixed — census reconciled | **verified** | Independent re-count: `grep -c "^### HLR-"` = 20, `"^### LLR-"` = 52, `"Asserting tests"` = 52; per-block script check: 52/52 LLR blocks carry exactly one `Asserting tests` field (none missing, none duplicated). §5.2 states "All 52 LLRs (20 HLRs)" (`01-requirements.md:952`); PLAN header + roadmap state 20/52 (`PLAN.md:22`, `PLAN.md:74`, `PLAN.md:107`). |
| QA-02 | major | fixed — seam discharged by executed probe | **verified** | Probe (a) re-run reproduced PASS (above). F-5 names the injection point and requires lanes 3–5 to re-verify it at entry, not only at the join (`01-requirements.md:274`); §6.3 records the discharge with the probe + ruling (`01-requirements.md:999-1003`); `01b` driver-seam header updated (`01b-acceptance-design.md:13-21`); injection point exists as claimed (`mapper/app.py:250`); ledger `LED-2026-10-25-r2.07` (`01-requirements-ledger.md:114`). |
| QA-03 | major | fixed — seam discharged by executed probe; new LLR-RVH.3.3 + AT-147 arm | **verified** | Probe (b) re-run reproduced PASS (above). LLR-RVH.3.3 exists (`01-requirements.md:772-778`), traces to HLR-RVH.3, is counted in the 52, states the workspace-canon rule (resolve at workspace root, never cwd / never upward, no git required, closed-set `unavailable` K1–K17, app alive); asserting tests `tests/test_relmap_shell.py` + AT-147 workspace-as-repo arm; ledger flag `LED-2026-10-25-r2.03` (`01-requirements-ledger.md:55`). AT-147 carries the arm with a non-git fixture workspace (`01b-acceptance-design.md:229-231`; matrix row `01b-acceptance-design.md:314`). |
| QA-04 | major | fixed — ruling folded back; ledger entries | **verified** (one stale-history exception, see below) | No `CONTINGENT`, "decided at", "ONLY IF the PDR", or "dropped otherwise" wording remains in the normative contract (`01-requirements.md`, `01b-acceptance-design.md` — greps empty). The single remaining `CONTINGENT` hit (`PLAN.md:141`) is a dated decision-log history row explicitly marked "SUPERSEDED by the P1 amendment: the standing ruling ships it, `LED-2026-10-25-r2.01`" — the declared historical exception, not live text. LLR-RVG.1.5 header/statement unconditional and SHIPPED (`01-requirements.md:548-554`); LLR-RVH.4.1 draft-time verification says `k` IS bound (`01-requirements.md:784-787`); LLR-RVU.1.1 pins bound 240 with the no-mid-spelling cut (`01-requirements.md:856`); §6.3 records the ruling (`01-requirements.md:997-998`); ledger rulings `LED-2026-10-25-r2.01` / `-r2.02` exist (`01-requirements-ledger.md:23`, `:38`). |
| QA-05 | minor | fixed — AT-152 pins 240 | **verified** | AT-152 title and body pin bound 240, assert the emitted line length ≤ 240, cut at 239 with one trailing ellipsis, after escaping (`01b-acceptance-design.md:279-291`); LLR-RVU.1.1 matches (`01-requirements.md:856`). |
| QA-06 | minor | fixed — black-box arms promoted | **verified** | FAINT dimming census on the painted frame in AT-131 (`01b-acceptance-design.md:50-52`) and AT-132 (`:61-62`); counted overflow line `… +NN more` on the real screen in AT-141 (`:169-171`) and AT-143 (`:188-190`). Both observe the shipped surface (`_painted_frame` / frame text) with no internal mapper symbol — genuinely black-box. |
| QA-07 | minor | fixed — AT-137 cap-scale arm + §2.5 A5 | **verified** | AT-137 cap-scale arm: in-test `build_map` at the shipped cap (100,000 nodes, `MAX_NODES`, `mapper/osopen.py:93-94` — constant verified in code) renders through the matrix row window with every undisplayed row declared, the sheet's counted overflow line present, derivation within a bounded wall-clock budget, audit-clean at both sizes (`01b-acceptance-design.md:119-126`); §2.5 A5 records the deliberate omission of any other very-large-map arm (`01-requirements.md:129-132`); ledger `LED-2026-10-25-r2.09` (`01-requirements-ledger.md:149`). |
| QA-08 | minor | fixed — re-traced to HLR-RVH.2 | **verified** | LLR-RVS.7.1 now traces to HLR-RVH.2 with the re-trace recorded inline (`01-requirements.md:695-696`); ledger `LED-2026-10-25-r2.04` (`01-requirements-ledger.md:75`). |

## Amendment-opened items in the QA lens (TASK 3)

- **LLR-RVH.3.3 testability:** testable as written — the oracle is named (the closed-set
  `unavailable` refusal line, the K1–K17 cause set with K3 `file not found` and K7 `is not
  UTF-8 text` given as examples, and the app-alive condition), asserting tests are named
  (`tests/test_relmap_shell.py` + the AT-147 arm), and the reddening mutants are declared
  (M-RVH-16 git-consulting, M-RVH-17 raw-exception escape).
- **AT-147 new arm black-box purity:** genuine — the driver is a fixture workspace (one
  `REQUIREMENTS.md` + one `.mmd`, no `.git`) opened through Home via a Pilot; the asserts
  are rendered-row / rendered-text / refusal-line observations; no internal symbol is named.

## New findings

| ID | Severity | One line | Evidence |
|---|---|---|---|
| P2Q-1 | **major** | LLR-RVH.4.1's normative Statement says "bind exactly:" an enumeration that OMITS `k`, contradicting the three sites that state `k` is bound/pinned in LLR-RVH.4.1 — an implementer binding exactly the listed chords ships no `k` toggle and AT-136 fails at Phase 4 | `01-requirements.md:781` (no `k` in the "bind exactly:" list) vs `01-requirements.md:552` ("the `k` binding is pinned in LLR-RVH.4.1"), `01-requirements.md:997-998` (§6.3: "LLR-RVG.1.5 + AT-136 + the `k` binding"), `01b-acceptance-design.md:105` (AT-136 driver: "press `k` … bound per LLR-RVH.4.1"). Introduced by the amendment: the old "bound ONLY IF the PDR ships" clause was removed from the draft-time verification but `k` was never added to the normative enumeration (diff of `daddd6d`). |
| P2Q-2 | low | The AT↔requirement matrix's negative-arms column is stale against two amended AT bodies | `01b-acceptance-design.md:319` (AT-152 row lists M-RVU-1/2; the body at `:290-291` also asserts M-RVU-3) and `:304` (AT-137 row lists M-RVG-5/6; the body at `:125-126` adds M-RVM-1 at cap scale). Cosmetic; bodies are authoritative. |
| P2Q-3 | low | One `assumed — verify in Phase 2` flag survives the amendment while its two siblings were removed: the RVT text-leaf landing order at LLR-RVG.3.1 is still flagged although the substance is now resolved (text leaf is trunk increment 1) — stale flag wording | `01-requirements.md:584` vs `PLAN.md:114` (trunk first). Policy-compliant at `01-requirements.md:429` (explicit flag, not silently dropped), so this is staleness, not a deferral gap. |

## Verdict

**iterate** — QA-01…QA-08 all verify as fixed and both seam probes reproduce cleanly, but
P2Q-1 (major, requirement defect: the shipped `k` binding is absent from LLR-RVH.4.1's
normative "bind exactly:" enumeration) contradicts the amendment's own fold-back and has a
concrete failure path at Phase 4; per the p2-review station a requirement-defect major
defaults to `iterate-to-refine`. P2Q-2/P2Q-3 are low and may ride the same amendment.
