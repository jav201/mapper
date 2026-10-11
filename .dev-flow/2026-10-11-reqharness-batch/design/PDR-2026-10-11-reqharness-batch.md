# Design review record — PDR — mapper — Batch 2026-10-11-reqharness-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.

> **Owed in.** `core` by trigger · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-level table, which is this fact's one home. A level marked `—` **does not owe this artifact, and its absence is not an omission**; `by trigger` means the station exists only when the `triggers` block fired, and `stations_active` in `state.json` is the authority for *this* batch. Where a SECTION or a gate row is owed more narrowly than the artifact, it says so on the row.

> **Where this lives: the VAULT + Drive.** It is **sealed** and **cited by id** from the repo.
> A record in Drive has no diff, no PR and no CI — that is a real boundary of the design, not an
> oversight. The seal is what compensates: **if this record changes after the seal it is a NEW version
> with a NEW id**, never a silent edit, and the requirement that cited the old id keeps pointing at the
> old one — which is exactly the signal you want to see.

> **Notice convention.** `⚠` yellow = notice, declare the reason and continue · `✗` red = block ·
> `✓` green = satisfied **with its evidence cited**. Without a citation an item is asserted, not satisfied.

| Field | Value |
|---|---|
| Record id | `PDR-2026-10-11-reqharness-batch` |
| Reviews | `design/design-proposal.md` (drafted by Kimi) amended by the round-1 rulings R1–R14 + D13 (`LED-2026-10-11-reqharness-batch.3`…`.17`), the round-2 rulings R15–R26 (`.18`…`.29`) and the round-3 ruling R27 (`.30`) |
| Participants | PDR: `architect` (Claude Opus) + `qa-reviewer` (Claude Sonnet) + `security-reviewer` (Claude Opus). **`ux-reviewer`:** trigger D1 fired, but the only screen in scope (the roles screen, matrix variant B) already carries the operator's prototype verdict **B-123** and no other screen class is born this batch (O2 folds the status surface into the roles footer band), so **the operator's prototype verdict stands in for the UX lens** — stated, not assumed away. · DDR: `architect` + `software-dev` + `qa-reviewer` |
| Date sealed | `2026-10-11` |
| **Verdict** | `approved with conditions` (R27 limbs a–g applied in the sealing unit; implementation conditions G1–G6/H1–H4 verified at the increment gate) |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` | ✓ | all sections present and amended through round 3 (§1 objective + out-of-scope, §2 module map + §2.1 threat model, §3.1 flow / §3.2 chain / §3.3 formats / §3.4 states / §3.5 perf / §3.6 identity+allowlist, §4 frozen-interface rows, §5 test rows, §6 risks + rejected alternatives, §8 increment plan); real alternatives rejected for cause in §6 (parallel `registry.yml`, concatenation hashing, HMAC strong mode — B-122, generated views — B-121 ruling 5); the pre-made decisions (O1–O9) are cited as operator rulings |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | the core is stdlib + PyYAML + `mapper.osopen` only, zero other mapper deps (the `views` headless precedent); `screens`/`app` → `reqharness` is the only outbound consumer edge; the ARQ amendment (§1 crossings + §2 module row + §3 rules incl. the `osopen` inbound edge) is a declared trunk act written inside increment 1 (R11/R19), never claimed earlier; no §4 frozen row is touched (§4 table) |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | derived object states → the release rule (LLR-RH.7.1) and the roles screen matrix/band (HLR-RH.8); baselines → AT-081 diff; the audit report → AT-080; the parse cache → nothing (a pure accelerator, R4 — stated); the D12 proposal document → the dev-flow ledger proposal at P6 (O7, `06-docs/`) |
| 4 | Every requirement has foreseen coverage | ✓ | HLR-RH.1–RH.8 map to §5 rows + AT-077a/b/c, AT-078, AT-079, AT-080, AT-081, AT-082, AT-083; after R24/R25 the deferred classes (B-124/B-125) and the 6a/6b split keep every SHIPPED requirement covered; the R27 arms (in-order fork + resolve, non-sibling resolve, multi-event excluded branch, `safe.directory` → `no repo`) add three test nodes to LLR-RH.3.1/3.2/3.4 and one to LLR-RH.7.2 (ledger `.30`) |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ✓ | every §5 row names its mutation, incl. the round-3 additions: M-FR3 (file-position walk vs the BY-`prev_hash` walk), M-FR4 (a `resolve` skipping the chosen child's bound-head approval rule), M-ID2 (relative/planted `git` resolution), M-AU3 (a git non-zero raising instead of the named `no repo`); the AT rows drive real keys through `MapperApp(tmp_path)` + `run_test` (the a/r resolution and the home-door growth are real persisting actions, so the oracles cannot pass vacuously) |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | one lane, six increments (6a/6b after R25), each ≤ 4 source files with an owner (PLAN §Roadmap; proposal §8); the shared-file acts (keymap seat edit, `screens/home.py` door row, ARQ amendment) are each owned by exactly one increment; every increment executes its RED proof as a transcript; the gauntlet controls per increment are named in the contract's Executed-verification lines |
| 7 | Interfaces **frozen** for the fork are listed | ✓ | §4 freezes: the §4 ARCH rows (`Canvas`, `IRenderer.render`, `Graph`, `MapScreen` F1–F3, F4 patch surface, `osopen` boundary, `design` tokens) — **untouched**; `app.main()` gains only the early `--audit` branch ahead of the UTF-8 stdout re-wrap; `keymap.py` gains the `roles` scope + home door `R` (owned by increment 6a); `app.py` gains the `RolesScreen` re-export; the home door list is data, not a frozen signature (7→8 additive) |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ | n/a — one lane (trigger A4 not fired); no file moves (B2); the family-B reverse census ran at P1 (`reqharness.*`/`RolesScreen`/the `roles` scope asserted by no existing test file); the seat edit and the home door row are declared-seat/data edits owned by exactly one increment (the data-safety Inc-1 precedent) |
| 9 | UX lens applied (if family D fired): interaction design reviewed | ⚠ | D1 fired, but the roles screen already carries the operator's prototype verdict **B-123** (matrix variant B, rendered on the real Textual 8.2.8 stack — D2 not fired), and no other screen is in scope (O2 folds the status band into the roles chrome) — **the operator's prototype verdict stands in for the UX lens**; the screen's interaction deltas (a/r keys, read-only tamper state, band detail, 118 AND 87 columns) are contract rows (LLR-RH.8.1–8.5), reviewed by the qa-reviewer in all three rounds |
| 10 | Security lens applied (if family C fired) | ✓ | family C fired (C1·C4·C6·C8): round 1 returned BLOCK-UNTIL F1–F3 → R1–R14 + D13; round 2 `approve-with-conditions` (G-block) → R15–R26 (G1 answered by R20's hardened allowlist); round 3 `approve-with-conditions` (H1–H4, no HIGH) → R27; the threat model (§2.1, layers 0–3 + residuals R23/R27a) is explicit; guard A-110 (no operator paths / account names in tracked files) is unaffected — emails are stored only as hashes (R12) |

**No increment starts without an approved PDR.**

---

## B · DDR checklist — detailed design review · **and the JOIN point when the batch forked**

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, **and why** | | |
| 2 | Frozen interfaces still intact — or the work returned to the trunk and it is declared | | |
| 3 | **Reverse census CROSSED between lanes** (the one check impossible from inside a lane) | | |
| 4 | Every `AT-NNN` realises in **exactly one** on-disk node (C-18) | | |
| 5 | Test ledger **summed** across lanes, reconciled | | |
| 6 | No lane touched another lane's file | | |
| 7 | Source-file budget: any lane that reached or exceeded 4, reviewed here | | |
| 8 | **Every open PDR condition discharged one by one, by RE-READING the artifact** | | |

**A conditional verdict is not an authorisation.** Each condition below is discharged by reading the
artifact that was supposed to change — not by trusting that the corrective pass ran.

| # | Condition left open at PDR | Discharge status | The artifact line that proves it |
|---|---|---|---|
| C-R27a | `--audit` runs NO `git status`; the dirty flag is taken only by `Baseline.create` (operator's own repo); residual stated: "baseline creation trusts the repo's `.git/config`". | **applied in this unit — re-read at DDR** | `01-requirements.md` HLR-RH.6 · LLR-RH.6.1 · LLR-RH.7.2 · LLR-RH.7.3 (allowlist drops the `git status` row from the core/audit path); proposal §1 bullet + §3.6 table row; ledger `.30` |
| C-R27b | The prefix uses `-c core.fsmonitor=false -c core.hooksPath=<os.devnull>`; verified limits stated (`include.path`/`includeIf` read-only; `core.sshCommand`/`credential.helper`/`diff.external` not invoked; `--no-pager` covers `core.pager`). | **applied in this unit — re-read at DDR** | LLR-RH.7.3 Statement; proposal §3.6 hardening paragraph + §2.1 read-only-git bullet |
| C-R27c | `git` resolved ONCE to an absolute path (`NoDefaultCurrentDirectoryInExePath=1` during resolution, `shutil.which` over an explicit PATH excluding the repo), invoked `<abs git> -C <repo>` (no `cwd=<repo>`); an argv-census arm asserts the absolute executable; M-ID2 reddens a relative/planted resolution. | **applied in this unit — re-read at DDR** | LLR-RH.7.3 Statement/Executed verification; proposal §3.6 + §5 `test_git_resolution_absolute_and_path_pinned` row |
| C-R27d | A `safe.directory` refusal (or any git non-zero) → the named result `no repo` on screen + audit, never a crash, exercised by `test_safe_directory_refusal_is_named_no_repo_not_a_crash`; M-AU3 reddens a raising path. | **applied in this unit — re-read at DDR** | LLR-RH.7.2 Statement/Boundary catalog · LLR-RH.8.1 Statement; proposal §5 `test_safe_directory_refusal_is_named_no_repo_not_a_crash` row |
| C-R27e | Verify walks the chain BY `prev_hash` from genesis; a document claiming an already-claimed parent is a fork sibling (tolerated only behind a `resolve` naming it in `resolve_excludes`); a multi-event excluded branch → `chain broken` (recovery deferred B-126); a `resolve` is valid only when the chosen child passes the approval rule at its own bound head; tests ×3 (in-order fork + resolve; non-sibling resolve; multi-event excluded branch) + M-FR3/M-FR4. | **applied in this unit — re-read at DDR** | HLR-RH.3 · LLR-RH.3.1/3.2/3.4 Statements; proposal §3.2 `verify`/`fork` block + §5 rows |
| C-R27f | The scope line reads `seq`/`roles_seq: int` (R18). | **applied in this unit — re-read at DDR** | `01-requirements.md` §1.2 line 33 |
| C-R27g | The door-count regression checklist names the guarded home tests: `tests/test_inc9c.py::test_inc9c_ux_f4_home_reads_its_labels_from_the_seat` (the `len(doors) == 6` count), `tests/test_inc9e.py::test_inc9e_l3_the_home_bar_paints_the_doors_first`, `tests/test_inc9f.py::test_inc9f_r3_cr_f3_home_keeps_its_letters_and_active_mark_under_a_rekeyed_seat`, `tests/test_key_dispatch.py::test_at_n03g_each_key_dispatches_its_own_advertised_action`, `tests/test_inc9.py::test_cd25_the_pinned_entry_seat_is_not_vacuous` + `tests/test_inc9.py::test_cd25a_the_seat_diff_is_exactly_what_inc9_declares` (the 6 home door rows of `ENTRY_ROWS`). | **applied in this unit — re-read at DDR** | LLR-RH.8.1 Numeric pass threshold; proposal §4 home-screen row |
| G1 | Hardened read-only git allowlist: argv list, `shell=False`, 10 s timeout, the `-c` pins, stripped `GIT_*`, never `cwd=<repo>`; the allowlist census finds 0 non-allowlist subprocess calls. | **planned — verified at the increment gate** (identity increment, RH chain step 3) | LLR-RH.7.3; proposal §3.6 + §5 census rows |
| G2 | The fsmonitor sentinel stays ABSENT after `--audit` and `.git/index` is byte-identical (no `git status` runs in the audit path at all). | **planned — verified at the increment gate** | LLR-RH.7.3 Executed verification; proposal §3.6 Tests |
| G3 | The loader recomputes sha8 over canonical content; a name/content mismatch is reported by name, non-closing (M-FN2). | **planned — verified at the increment gate** (reviews+pending increment) | LLR-RH.4.6; ledger `.25`; proposal §5 `test_review_file_naming_and_exclusive_create` |
| G4 | The residuals are stated, not hidden: baseline-bounded deletion detection, unbound-tail truncation, old-head binding (R17 WARN), free-text `reviewer`, layer 3; `email_sha256` pseudonymised, unsalted — jurisdiction to the operator. | **planned — verified at the increment gate** (PDR §2.1 is the home; the audit WARN arm lands in the baselines+release increment) | LLR-RH.4.2/4.4 rationale; proposal §2.1; ledger `.20`/`.26` |
| G5 | Input limits and named refusals on every parsed file (64 KB / 4 MB / 100 000; anchors/aliases + duplicate keys rejected at compose time by the custom loader subclass; malformed YAML in each of the four file kinds refused by name; a corrupt cache file bounded to a re-parse). | **planned — verified at the increment gate** | LLR-RH.3.5; proposal §5 `test_input_limits_reported_by_name` + `test_review_parse_cache_is_pure_accelerator` |
| G6 | Markup safety is the Text sink: every file-derived string through `darkside.plain` into `Text` sinks only; the sink census + the `[bold]` payload arm. | **planned — verified at the increment gate** (roles-screen increment) | LLR-RH.8.4; proposal §5 AT-077c row |
| H1 | `git status` is out of the `--audit` path (a committed `.gitattributes` `filter.<name>.clean` can run commands no fixed `-c` disables); the dirty flag is `Baseline.create`-only with the stated residual. | **planned — verified at the increment gate** | C-R27a row above (document side); the baseline increment carries the only `git status` call |
| H2 | `git` cannot be resolved from the audited repo's cwd (planted `git.exe`): absolute-path resolution + explicit PATH. | **planned — verified at the increment gate** | C-R27c row above |
| H3 | `core.hooksPath` is neutralised by `-c core.hooksPath=<os.devnull>` on every call. | **planned — verified at the increment gate** | C-R27b row above |
| H4 | A `safe.directory` refusal (or any git non-zero) is the named result `no repo`, never a crash; the verified config limits are stated. | **planned — verified at the increment gate** | C-R27d row above |

---

## C · Verdict and what it means

- `approved` — the bar is met on all three axes (Coverage · Certainty · Evidence); state which.
- `approved with conditions` — list them above; each is individually dischargeable and re-read at the next gate.
- `rejected` — **returns to DESIGN, not to implementation.** Name the gap that caused it.

**Verdict sealed 2026-10-11: `approved with conditions`** on Coverage ✓ (after R24/R25/R27e: every
shipped requirement has foreseen coverage, including the fork/resolve and `no repo` arms) ·
Certainty ✓ (after R10/R13/R27: every AT's control is reachable, named and non-vacuous, with the
M-FR3/M-FR4/M-ID2/M-AU3 mutants) · Evidence ✓ (after R16/R18/R26/R27: thresholds are counts,
byte-exact strings, named result words, or P4-measured budgets with an owner). Three review rounds
ran over the proposal (round 1 `iterate-to-refine` with security BLOCK-UNTIL F1–F3 → R1–R14 + D13;
round 2 `approve-with-conditions` → R15–R26 with B-124/B-125/B-126 deferrals and the 6a/6b split;
round 3 targeted, all three reviewers `approve-with-conditions`, no HIGH → R27), and every ruling
was applied to the contract, ledger, proposal and PLAN.md in the same unit that sealed this record
(`LED-2026-10-11-reqharness-batch.3`…`.30`). **Self-approved under the standing authorization**
(quoted in PLAN.md: mode `full + autonomous + merge`; merge only after a final independent
PR-level qa-reviewer pass comes back clean; TUI design changes need a prototype verdict — the roles
screen has one, B-123). No increment starts before its own RED proof plan is read at the increment
gate; the conditions C-R27a–g are re-read at the DDR, and G1–G6/H1–H4 are verified where they land.

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| D1 — the batch delivers a HEADLESS domain core `mapper/reqharness/` (stdlib + PyYAML + `mapper.osopen` only; zero other mapper deps; no Textual/Rich), placed per ARCHITECTURE §2/§3 with the amendment written as a trunk act inside increment 1; `screens`/`app` consume it, never vice versa | `PDR-2026-10-11-reqharness-batch#D1` | `mapper/reqharness/*.py`; `docs/ARCHITECTURE.md` §1/§2/§3 amendment (increment 1); LLR-RH.7.3 |
| D2 — storage: `reqharness/config.yml` (typed schema, `email_sha256` people); `reqharness/roles.yml` the hash chain (genesis + policy + grant/revoke + resolution + resolve, one event per YAML document); `reqharness/reviews/<yyyymmdd>-<sha8>.yml` immutable content-named events; `reqharness/pending/<yyyymmdd>-<sha8>.yml`; `reqharness/baselines/<name>.yml`; the parse cache inside `.git/reqharness-cache/` (pure accelerator) | `PDR-2026-10-11-reqharness-batch#D2` | LLR-RH.1.2 · LLR-RH.4.6 · LLR-RH.6.1; proposal §3.3 |
| D3 — the chain: genesis policy-bound from the first document (`roles_hash: "GENESIS"`, `config_hash` — R15); admin-approved `policy` events binding sha256(canonical config) (R1); head binding on every event/review/pending/baseline (`roles_seq` + `roles_hash`, authority at the bound head — R2); fork exclusion + `resolve` recovery (R7/R16), verify a WALK BY `prev_hash` from genesis, single-event forks only, multi-event excluded branch → `chain broken` (B-126), the chosen child must pass the approval rule at its own bound head (R27) | `PDR-2026-10-11-reqharness-batch#D3` | HLR-RH.3 · LLR-RH.3.1/3.2/3.4; `tests/test_reqharness_chain.py` rows |
| D4 — canonical form + loader + limits: canonical JSON (sorted keys, no whitespace, ensure_ascii=False, NFC) over the typed schema (`str` scalars except `seq`/`roles_seq` int; one exact `time` format; the writer quotes scalars); the custom loader subclass rejecting anchors/aliases + duplicate keys at compose time; limits 64 KB / 4 MB / 100 000 with named refusals | `PDR-2026-10-11-reqharness-batch#D4` | LLR-RH.1.1/1.3 · LLR-RH.3.5; `tests/test_reqharness_config.py` |
| D5 — identity + hardened read-only git: repo-local-then-global `git config --get user.name|user.email`; the reduced allowlist (`rev-parse --show-toplevel`/`HEAD`, `config --get`; `git status` ONLY in `Baseline.create`); absolute-path git resolution with `NoDefaultCurrentDirectoryInExePath=1` + explicit PATH; `-c core.fsmonitor=false -c core.hooksPath=<os.devnull>`; a `safe.directory` refusal or any git non-zero → the named result `no repo`, never a crash; residual: "baseline creation trusts the repo's `.git/config`" | `PDR-2026-10-11-reqharness-batch#D5` | LLR-RH.7.2 · LLR-RH.7.3; `tests/test_reqharness_identity.py` + `tests/test_reqharness_release.py` |
| D6 — derived states + release rules: `reviewed` · `changed · review` · `pre-reviewed` (`unentitled`) · `not verifiable` · `retired` with the R5 precedence; the release rule = three hard-coded mandatory rules (chain verified · policy verified · every closing review signed by a role in force at its bound head) + config-declared rules (additive only); `mapper --audit <repo>` prints status + counts + verdict, cache OFF, writes nothing | `PDR-2026-10-11-reqharness-batch#D6` | HLR-RH.5 · HLR-RH.7 · LLR-RH.5.x · LLR-RH.7.1; `tests/test_reqharness_registry.py` + `tests/test_reqharness_release.py` |
| D7 — the roles screen = matrix variant B (B-123): people × roles with ● ◐ ◌ ○ from `darkside` tokens; the `roles` keymap scope + home door `R` (7→8, one increment owns the seat edit and the `screens/home.py` door row); `space` propose, admin `a`/`r` resolution; footer status band (O2); read-only tamper/fork state; `plain()` + Text sinks only; 118 AND 87 columns | `PDR-2026-10-11-reqharness-batch#D7` | HLR-RH.8 · LLR-RH.8.1–8.5; `mapper/screens/roles.py`; `mapper/keymap.py`; the home-door pins of `tests/test_inc9c.py`/`test_inc9e.py`/`test_inc9f.py`/`test_key_dispatch.py`/`test_inc9.py` (re-based with the `R roles` row, the data-safety E-7 precedent) |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
vault: it is reflected in the requirement or in the module map, which are versioned beside the code.

---

## E · DDR amendments — appended after the seal (do not rewrite sealed text)

> This section records DDR follow-up rulings that amend sealed text. The sealed text above is
> **not rewritten**; each amendment names the sealed row it supersedes and the reason, and the live
> contract / proposal carry the corrected wording (ledger `.32`–`.35`).

| Amendment | Sealed text it supersedes | New ruling (already in `01-requirements.md` + proposal) |
|---|---|---|
| **ARCH C1 — git resolution** | §B condition `C-R27c` (and §D `D5`): "`git` resolved ONCE to an absolute path (`NoDefaultCurrentDirectoryInExePath=1` during resolution, `shutil.which` over an explicit PATH excluding the repo)" | `git` is resolved ONCE to an absolute path by **walking PATH itself** — each directory that resolves to the audited repo, the cwd, `.` or an empty entry is skipped (compared resolved), then `git` + each PATHEXT extension on Windows (fallback `.COM;.EXE;.BAT;.CMD`), plain `git` on POSIX, first existing regular file wins. `shutil.which` + the `NoDefaultCurrentDirectoryInExePath` mutation are GONE. Reason: review finding **F4 HIGH** — before Python 3.12 `shutil.which` searches `.` on Windows regardless of that variable. |
| **ARCH C1 — loader mechanism** | §B condition `G5` / §D `D4`: "the custom loader subclass rejecting anchors/aliases + duplicate keys at compose time" | The subclass refuses **duplicate keys at construction time** and **anchors/aliases by an event-stream pre-scan before construction** (the C composer resolves aliases before Python-level overrides can see them — one `yaml.parse` scan serves both loader bases). |
| **ARCH C2 — audit branch order** | §A row 7: "`app.main()` gains only the early `--audit` branch ahead of the UTF-8 stdout re-wrap" | The `--audit` branch runs **AFTER** the UTF-8 stdout re-wrap (so the report prints in UTF-8), not ahead of it. |
| **Residual — `ready` semantics (D6)** | §D `D6` release rule = three hard-coded mandatory rules + config-declared rules | `ready` does **NOT** mean every object was reviewed — that holds only when `config.yml` declares the `all_active_reviewed` rule. The hard-coded mandatory rules are chain verified · policy verified · every closing review signed by a role in force at its bound head; `all_active_reviewed` is config-declared (a default, not a hard-coded rule — D6 as designed). |
| **Residual — approver ≠ requester (SEC F5-era)** | — | `approver != requester` (nobody approves a change to themselves) is now **enforced in the verify walk** — a code-lane fact, recorded here, no requirement-text change. |
| **Residual — legal-depth 4 MB load cost (K3 re-check LOW-2)** | — | A 4 MB `roles.yml` at the LEGAL depth limit (63) costs ~25 s CPU to load: the event-stream depth bound (SEC F2) refuses only depth > 64, not byte volume at legal depth, and a depth-63 document of 4 MB of small mappings is expensive but legitimate YAML. Accepted residual, no code change: the 4 MB cap (`LIMIT_ROLES_YML_BYTES`, R9) bounds the input; registry writes are **repo-write-gated (layer 3)** — only the operator's own commits land, so the cost cannot be inflicted by a third party; the cost is paid once at load, never mid-interaction; and `config.yml` is now capped further at 64 KB (close-out LOW-4). Recorded here as a stated residual (R23-style). |
| **Residual — stat fast path (PERF-RH, ledger .36)** | — | The review parse cache's stat fast path (ruling, ledger LED-…-batch.36): a warm load reuses the validated parse when (relative name, st_size, st_mtime_ns, st_ino, st_dev) ALL match a fully-checked entry, without reading the file; any mismatch takes the full path; `--audit` stays cache-OFF. Residual: a local writer who can preserve size+mtime+file-id while changing bytes in place (possible on Windows — an in-place rewrite keeps the NTFS file index `st_ino` reports) defeats the fast path and is served the stale parse. That writer can equally write `.git/reqharness-cache` itself (the same trust boundary as R4); `--audit` and release evaluation via audit are unaffected (cache-OFF re-reads every file). Test-pinned in `tests/test_reqharness_cache_fastpath.py`; measured effect: LLR-RH.5.4 warm-cache budget MET at 0.4432 s median (was 5.27 s). Recorded here as a stated residual (R23-style). |

### Mutant catalogue additions (QA C6)

| Mutant | What it mutates (one line) |
|---|---|
| **M-CH6** | Remove the genesis-position pin `(event.action == "genesis") == (position == 1)` and restore the unconditional `_passes_approval` genesis shortcut → a forged seq-2 `genesis` by a non-admin verifies clean and mints an admin → `test_genesis_only_at_position_one` RED. |
| **M-FS1** | Drop the `-c core.fsmonitor=false` pin (R27b) → the fsmonitor sentinel appears after the hardened calls → `test_fsmonitor_sentinel_absent_after_hardened_calls` RED. |
| **M-ID3** | Remove the repo/cwd/`.`/empty-entry exclusions from the PATH walk → a `git.exe` planted in the audited repo's cwd wins resolution → `test_git_resolution_excludes_repo_and_cwd` RED. |

