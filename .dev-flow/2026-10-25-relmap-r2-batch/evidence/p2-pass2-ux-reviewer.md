# Phase-2 cross-review evidence — UX-REVIEWER — SECOND (pass-2) review

- **Batch:** `2026-10-25-relmap-r2-batch` · **Branch:** `feat/relmap-r2` · **Date:** 2026-10-25
- **Pass:** P2 second pass, independent, over the P1-amended contract (amendment commit `daddd6d`,
  gate record `96f2d61`). I authored none of the artifacts under review.
- **Lens:** UX fidelity (trigger D1) · **Standard applied:** agents/ux-reviewer.md, stations/p2-review.md.
- **Inputs read:** `02-review.md` (§Findings F-UX-1/F-UX-2 + §Author dispositions), first-pass
  evidence `evidence/p2-ux-reviewer.md`, the amendment diff (`git show daddd6d`), amended
  `01-requirements.md`, `01b-acceptance-design.md`, `01-requirements-ledger.md`, `PLAN.md`.
- **Method:** every claim verified against the on-disk files (line numbers below are current
  worktree state), not against the disposition text.

## Per-finding verification (first-pass UX findings)

| ID | First-pass severity | Disposition claimed | This pass | Evidence (file:line + quote) |
|---|---|---|---|---|
| F-UX-1 | major | fixed — ledger ruling + three de-contingented sites; implementer can no longer lawfully drop the toggle, `k` or AT-136 | **REOPENED (partial)** — sites (a), (c), (d), (e) and the ledger are fixed; site (b) is only half-fixed: the LLR-RVH.4.1 normative **Statement** still omits `k` from its exhaustive "bind exactly" enumeration; `k` is asserted only in the non-normative draft-time verification. See P2U-1. | Fixed: `01-requirements.md:548` header "By-kind mode (SHIPPED per the orchestrator ruling; toggled by `k`)"; `:549` statement "presses `k` to toggle"; `:551` validation "AT-136 on the real screen (shipped per ruling — not contingent)"; `:997-998` §6.3 "The by-kind toggle SHIPS … the PDR freezes only the glyph/table details"; `01b:102` AT-136 header "(SHIPPED per ruling `LED-2026-10-25-r2.01`)", `:105` "press `k` (bound per LLR-RVH.4.1)", `:303` matrix row "RVG.1.5 (shipped, key `k`)"; IFC `:878` "(by-kind grouping: .1.5, shipped per ruling LED-2026-10-25-r2.01)"; ledger `01-requirements-ledger.md:24-36` LED-2026-10-25-r2.01 with C11 naming (Requirement / Asserting tests / Mutants). NOT fixed: `01-requirements.md:781` LLR-RVH.4.1 Statement "bind exactly: `1`/`2`/`3` … `enter` … `c` … `r` … `q` … `escape` …" — no `k`; the `k` binding lives only at `:784-787` (draft-time verification: "The by-kind toggle key `k` (OQ-G4) IS bound"). Residual live "contingent" hits: none — `01-requirements.md:551` "(shipped per ruling — not contingent)" is an explicit negation; ledger `:33-35` describes the removed wording (amendment record); `PLAN.md:141` decision row is historical and clearly marked "SUPERSEDED by the P1 amendment". |
| F-UX-2 | minor | fixed — WARN scoped to reach/severity-attention signals (lens gauge, `not computed`, sheet `◐`); no tally word/chip/chrome uses it; LLR-RVG.1.3, LLR-RVS.2.3 and PLAN OQ-G2 read consistently | **VERIFIED** | `01-requirements.md:533-535` (LLR-RVG.1.3 draft-time verification): "WARN is scoped to reach/severity-attention signals ONLY — the matrix lens reach gauge (LLR-RVM.2.2), the `not computed` state (LLR-RVM.2.2) and the sheet's tagged-binds `◐` glyph (LLR-RVS.2.3) — and no tally word, chip or other chrome uses WARN (scope ruling `LED-2026-10-25-r2.05`)"; `:624` (LLR-RVS.2.3): "The `◐` WARN tone is one of the three WARN-scoped signals … no other sheet chrome uses WARN"; `:465` (`not computed` in WARN — signal #2, LLR-RVM.2.2 statement, unchanged); severity words map HIGH→ALERT / MED→INK / LOW→MUT (`:533`), tally chips pinned lowercase `high 0 med 0 low 0 total 0` (`01b:99`) — no WARN anywhere in tally/chip chrome. Remaining WARN mentions are benign: `:293`/`:468` quoted prototype evidence, `:362` + `01b:195` negative-span censuses (assert ABSENCE of an unintended WARN span — naming the token class, consistent with the scope clause), `01b:58` AT-132 (signal #2). PLAN `PLAN.md:141` OQ-G2 row: "the WARN reservation is SCOPED by the P1 amendment — … gauge, `not computed`, sheet `◐` only". Ledger `LED-2026-10-25-r2.05` (`01-requirements-ledger.md:86-97`) matches. |

## New findings (amendment-introduced, UX lens)

| ID | Severity | One line | Evidence |
|---|---|---|---|
| P2U-1 | **major** | The de-contingented LLR-RVH.4.1 leaves `k` out of the normative seat Statement: the "bind exactly" `shall` enumeration (`01-requirements.md:781`) still lists only `1`/`2`/`3`, cursor keys, `enter`, `c`, `r`, `q`, `escape`, while LLR-RVG.1.5 (`:549`), AT-136 (`01b:102-105`) and the LLR-RVH.4.1 draft-time verification (`:784`) all require `k` — a contract self-contradiction on the exact key the F-UX-1 fix was meant to seat, so an implementer following the Statement alone ships a seat without `k` (caught later only by AT-136 / the keymap conformance test per ledger r2.01). | `01-requirements.md:781` vs `:784-787`, `:548-552`, `01b:102-105`, `01b:303`, `01-requirements-ledger.md:34` ("LLR-RVH.4.1 binds `k` unconditionally" — true only of the verification note). Fix: add "`k` to the by-kind grouping toggle" to the Statement's enumeration. |

## Amendment side-effects sweep (Task 2) — no other new findings

- **IFC FLOW blocks:** gaps flow `:878` "shipped per ruling LED-2026-10-25-r2.01" matches LLR-RVG.1.5's header; the six `FLOW: <id>` normalizations are syntax-only, no UX-language drift. ✓
- **Keymap/help seat obligations:** M-RVH-9/M-RVH-10 and LLR-RVH.4.2 seat-equality untouched in substance (ledger back-pointers added only); AT-149 seat-equality unchanged. ✓ (except the P2U-1 statement gap)
- **Two-layer acceptance table** (`02-review.md:88-96`) is the first-pass historical record; the amendment recap below it is consistent with the amended 01b. ✓
- **118-reference + 87-checked pins:** LLR-RVM.4.1 / RVG.1.4 / RVS.6.1 statements unchanged; amendment touches only ledger fields and the AT-137 cap-scale arm (adds, removes nothing). ✓
- **Darkside lowercase census:** no new ALL-CAPS literal or casing contradiction introduced by the amendment diff; new WARN-scope prose is lowercase. ✓
- **Tone/glyph language:** no new glyph or tone token introduced; severity mapping HIGH→ALERT/MED→INK/LOW→MUT intact. ✓

## ⚠ notices (declared, not blocking)

- `01b:214` (AT driver note) drives the relation row with "`j`/`k`" on the **Home** screen — the home seat's own scope, where `k` is the pre-existing cursor key; on the relation screen `k` is the by-kind toggle (SCOPE_RELMAP). Screen-scoped seats make this legal, and `01-requirements.md:160` narrative already frames the toggle as "one key away"; no conflict, but the PDR should keep the two scopes' `k` meanings explicit in the help legend (both are seat-derived, so AT-149 covers the text).
- User-evaluation act (ISO 9241-210): not performed — one-person team, no user of this surface exists outside it. Expert inspection only, as in pass 1.

## Verdict

**iterate** — F-UX-1 reopened via P2U-1 (major, requirement-class: the keymap-seat Statement still omits `k` from its normative "bind exactly" list); F-UX-2 verified. The fix is one clause in `01-requirements.md:781` and re-runs this pass.
