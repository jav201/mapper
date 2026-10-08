# Backlog reconciliation PROPOSAL — batch `2026-08-26-ui-next-batch-02`

> **Read-only on the canonical backlog.** This file proposes how every OPEN row of `.dev-flow/BACKLOG.md`
> should be classified at this batch's close; it does not edit that file. Drafted by
> `deepseek/deepseek-v4-pro` (via `opencode run`), to be verified by the orchestrator (Claude Opus 5.5).
> Merge = squash `46e190b` on `master` (2026-10-03).

Rows enumerated with `grep` from `.dev-flow/BACKLOG.md`: **63** open rows (`| B-NN |` not struck `~~B-NN~~ **DONE**`).

## Reconciliation table (file order)

| B-id | Classification | Evidence (path:line) | Remaining part / reason |
|---|---|---|---|
| B-01 | OPEN | not mentioned as closed after the row was filed; B-21 still points to "B-01/`F-M5`'s repair" as pending (`.dev-flow/BACKLOG.md:98`) | still the pending repair |
| B-02 | OPEN | not mentioned as closed | needs its own decision (rejected silently by design) |
| B-03 | OPEN | not mentioned as closed | ~20 `rich.markup.escape` no-op sites still open |
| B-04 | PARTIAL | FactoryScreen + SettingsScreen migrated: `tests/test_inc9.py:102` `test_cd9b_unmigrated_screens_shrinks_to_the_two_left` asserts `UNMIGRATED_SCREENS == ("EditorScreen", "CoverageScreen")` | EditorScreen + CoverageScreen still hold local `BINDINGS` (also B-82) |
| B-05 | CLOSED-BY-BATCH | `01-requirements.md:1636` HLR-CNV.3 "closes carry B-05"; `.dev-flow/state.json:5` "Closes carry B-05"; `tests/test_layered.py:56` `test_at_010_the_selection_tone_follows_the_focus_owner` | — |
| B-06 | OPEN | not mentioned as closed | security minors still open |
| B-08 | OPEN | not mentioned as closed | refusal-shape wording still open |
| B-09 | OPEN | not mentioned as closed | id-hygiene item still open |
| B-11 | OPEN | not mentioned as closed | security carries still open |
| B-12 | OPEN | still unwired per its own note (`.dev-flow/BACKLOG.md:89`) | `-m slow` CI lane unwired |
| B-13 | OPEN | not mentioned as closed | no wall-clock bound still |
| B-14 | OPEN | not mentioned as closed | load-sensitive arm still open |
| B-15 | OPEN | not mentioned as closed | UX judgement, not fixed |
| B-16 | OPEN | not mentioned as closed | `_pop_snapshot` guard still open |
| B-17 | OPEN | not mentioned as closed | derivation/predicate share still open |
| B-18 | CLOSED-BY-BATCH | `03-increments/increment-025-inc9.md:159` "B-18 closed in code"; `.dev-flow/state.json:950` (Inc-9 closed list); `tests/test_inc9.py:196` `test_b18_no_product_site_constructs_an_unscoped_legend` | — |
| B-19 | OPEN | not mentioned as closed | `_event_toast` assertion still absent |
| B-20 | OPEN | not mentioned as closed | cosmetic recompute still open |
| B-21 | OPEN | not mentioned as closed | sibling malformed shapes still open |
| B-22 | PARTIAL | identity half closed: `03-increments/increment-023-scrub-operator-paths.md:9`; `.dev-flow/state.json:910` "closes: B-22 identity half"; `tests/test_no_operator_paths.py:99` `test_a110_no_undeclared_user_profile_path_in_any_tracked_file` | session-UUID half open; real name remains in git HISTORY (rewrite + force push not authorized) |
| B-23 | OPEN | not mentioned as closed | `TC-R38` root-bounded still open |
| B-24 | OPEN | not mentioned as closed | `RENDERERS` hand-list still open |
| B-25 | OPEN | not mentioned as closed | scope set-equality gap still open |
| B-26 | OPEN | not mentioned as closed | `AT-R13` vacuity still open |
| B-27 | OPEN | not mentioned as closed | comment claim still open |
| B-28 | OPEN | not mentioned as closed | hand-picked roots still open |
| B-29 | CLOSED-BY-BATCH | `03-increments/increment-012-repair-se.md:8` (`AT-049`/B-29, `LLR-REPAIR.1`); card clause landed in Inc-7 (`increment-019-inc7-code-review.md`); `tests/test_repair_sidecar.py:75` `test_at049_a_phantom_sidecar_id_records_a_load_warning` | — |
| B-30 | CLOSED-BY-BATCH | `03-increments/increment-012-repair-se.md:8` (`AT-050`/B-30, `LLR-REPAIR.2`); `increment-024-g6-store-surrogates.md:222` "the exact leak `B-30` already closed for `store.load`"; `tests/test_repair_sidecar.py:162` `test_at050_a_not_found_message_names_the_map_not_the_filesystem` | — |
| B-31 | OPEN | carried as an unverified observation — mechanism withdrawn (`.dev-flow/BACKLOG.md:154`) | not a diagnosed defect |
| B-32 | OPEN | not mentioned as closed | double-fire toast still open |
| B-33 | OPEN | recorded live on `master` (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:157`) | `MAX_RENDER_NODES` counts nodes, not work |
| B-34 | OPEN | not mentioned as closed | id-grammar collision still open |
| B-35 | OPEN | `HLR-N16.4` closes key-discoverability only; content-discoverability deferred by `#D26` (`.dev-flow/BACKLOG.md:158`) | two-pane/tabbed redesign deferred |
| B-36 | OPEN | explicitly deferred by decision (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:154-156,185`) | first item of the next design batch |
| B-37 | OPEN | stays open — "G7 stays in B-37" (`.dev-flow/state.json:862`) | `MUT` recalibration still open |
| B-69 | OPEN | deferred by operator — "Agrégalo al backlog por ahora" (`.dev-flow/BACKLOG.md:182`) | prototype round first |
| B-70 | OPEN | awaits operator verdict on `UX-F7b` (`.dev-flow/BACKLOG.md:183`) | unfocused selection tone |
| B-71 | CLOSED-BY-BATCH | `VERDICT-inc-en-2026-10-02.md:7` (B-71 authority for the language); `04-validation.md:111-119` (A-129…A-137 pass); `tests/test_en1.py:66` `test_no_spanish_user_facing_string` (+ scanner self-check `:72`) | — |
| B-72 | CLOSED-BY-BATCH | `01-requirements.md:11170` (`A-135` names B-72); `04-validation.md:117` "A-135 … (`B-72`)"; `tests/test_en7.py:207` `test_no_screen_binds_the_question_mark_at_priority` | select-all overwrite closed; the blur-commit save half is the separate B-36 (still open) |
| B-73 | OPEN | torn-write detect-only residual (`.dev-flow/state.json:930`) | detects, does not repair |
| B-74 | OPEN | decision to revisit (`A-113` refusal), not a defect (`.dev-flow/BACKLOG.md:163`) | no overwrite gesture |
| B-75 | OPEN | carry — `create` is check-then-write, not atomic (`.dev-flow/BACKLOG.md:164`) | not reproduced, not measured |
| B-77 | CLOSED-BY-BATCH | `03-increments/increment-029-inc9d.md:23` (B-77a) and `:27` (B-77b); `.dev-flow/state.json:1034-1035` (Inc-9d closed list); `tests/test_inc9d.py:110` `test_inc9d_sec_f1_a_missing_tilde_path_paints_no_profile_path`, `:282` `test_inc9d_b77b_a_dot_or_separator_segment_is_refused` | — |
| B-78 | OPEN | open — "B-78 (100-char id limit unmeasured on the real Drive workspace)" (`.dev-flow/state.json:1058`) | id-rule edges still open |
| B-79 | OPEN | Inc-9 LOW residuals, next hardening pass (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:186`) | TOCTOU narrowed, not closed |
| B-80 | OPEN | toast layout, next design batch (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:187`) | prototype round first |
| B-81 | PARTIAL | 3 of 4 corrections landed: `03-increments/increment-045-inc9s.md:11` (reading-5, mutant-table, `normcase`); `.dev-flow/state.json:1218` "partly closed by Inc-9s" | `INC9R-CR-F2` (`hard_linked` pseudo-reason) still open (`increment-045-inc9s.md:16`) |
| B-82 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:189`) | coverage/editor modals have no legend route |
| B-83 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:190`) | 87-col `M` focuses hidden field |
| B-84 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:191`) | hard-link write-through |
| B-85 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:192`) | lane renderers paint raw control chars |
| B-86 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:193`) | coverage `↵` second route of B-83 |
| B-87 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:194`) | focus parks on hidden rail |
| B-88 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:195`) | connect-repo marker + `1 releases` |
| B-89 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:196`) | prompt placeholders |
| B-90 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:197`) | palette lists `legend ?` on connect-repo |
| B-91 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:198`) | connect-repo chrome |
| B-92 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:199`) | dead `c`/`r` on empty home |
| B-93 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:200`) | CSV root row `? Root` |
| B-94 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:201`) | mirror fetch config not pinned |
| B-95 | OPEN | operator "Al backlog, mergear ya" (`.dev-flow/2026-08-26-ui-next-batch-02/VERDICT-merge-2026-10-03.md:25`; `05-postmortem.md:202`) | `I`-toggle stale edge hint |
| B-96 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:203`) | repo-config parsing hardening |
| B-97 | OPEN | whole-branch gate residual (`.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md:204`) | tampered-cache hook + small carries |

## Count per classification

- **CLOSED-BY-BATCH: 7** — B-05, B-18, B-29, B-30, B-71, B-72, B-77
- **PARTIAL: 3** — B-04, B-22, B-81
- **OPEN: 53** — all other rows

**Could not decide: none.** Three rows warranted a flag for the orchestrator rather than a bare verdict:

- **B-72** — classified CLOSED on its named finding (the select-all overwrite), but the "saves it" half is a blur-commit that is tracked separately as B-36 and stays open. A reader who treats B-72 as "the whole one-keystroke-overwrite family" would call it PARTIAL.
- **B-77** — the backlog row still reads "NOT fixed … Next security pass" (`.dev-flow/BACKLOG.md:166`), yet `.dev-flow/state.json:1034-1035` records Inc-9d closing `B-77a` and `B-77b`. The record and the increment agree the two halves are fixed; the backlog note is stale. Classified CLOSED on the increment record + test nodes.
- **B-04** — PARTIAL on the basis that `UNMIGRATED_SCREENS` shrank from four screens to two; the two remaining (Editor/Coverage) are also the subject of B-82, so the residual is not lost.

## Proposed NEW rows (text only, newest-section style)

Append to the "Design — operator ideas awaiting a prototype round" table (the same `| # | Item | Routing |` shape as B-82…B-97):

| # | Item | Routing |
|---|---|---|
| B-98 | **`FLAKE-2` — `test_hlr_n16_4_legend_declares_its_own_keys[size0]` failed once in a full lane ("work but not painted: ['left']"), passed 10/10 alone.** `tests/test_help_scope.py::test_hlr_n16_4_legend_declares_its_own_keys` fails once under load (`left` worked but not painted), green 10/10 in isolation (`gate-run-1-flake.txt`; `.dev-flow/state.json:1184-1186` `FLAKES_OPEN`). | Re-run solo on flake; investigate order-dependence before the next whole-branch gate |
| B-99 | **`INC9G-R8` — Inc-9g mutant R8 survives per the reviewer, though `increment-033-inc9g.md` claims "34/34 run killed".** `.dev-flow/state.json:1546`: `"mutants": "34/34 run killed (record); reviewer: R8 survives, record claim wrong"`; an A-115 branch has no killing witness (`.dev-flow/2026-08-26-ui-next-batch-02/04-validation.md:189`). | Next batch: add the witness arm and correct `increment-033-inc9g.md` |

---

*Drafted by `deepseek/deepseek-v4-pro` (via `opencode run`) from existing repo evidence, to be verified by the orchestrator (Claude Opus 5.5). Every row cites a repo file (path, and line/section where present); no number or verdict is invented.*
