# Independent review — Increments 006b + 007 (trunk, post-join)

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increments | `006b` (help/palette seat equality, commit `23bce8a`) · `007` (hook per-line bound 240, commit `4853b16`), reviewed at HEAD `4853b16` |
| Reviewer | independent increment reviewer — code + security + UX lenses; authored none of either increment |
| Lenses | `agents/code-reviewer.md` · `agents/security-reviewer.md` · `agents/ux-reviewer.md`; record per `templates/increment-template.md` §4b |
| Scope reviewed | Inc-6b: 0 source files (test-only append to `tests/test_relmap_shell.py` +92, 4 evidence files) · Inc-7: 1 source file (`mapper/reqharness/audit.py` +46), `tests/test_hook_line_bound.py` +136 (new), `tests/test_relmap_audit.py` ±25 (2 arms re-derived), 5 evidence files |
| Contract | LLR-RVH.4.4 → AT-149 · LLR-RVU.1.1 → AT-152 (TC-RM-30) · PDR `#D4` + F-SEC-3 (escape → cut → rewrite check → print) · R1 `run_cli` D4 semantics |
| Verdict | **Inc-6b: approve-with-nits** — 0 BLOCKER · 0 MAJOR · 2 MINOR (F1, F2) · **Inc-7: approve-with-nits** — 0 BLOCKER · 0 MAJOR · 2 MINOR (F1, F2) |

Concurrency note: a second session edited `mapper/screens/home.py`, `tests/test_inc9c.py`, `tests/test_relmap_shell.py` during this review (a pure insertion at `tests/test_relmap_shell.py:813-838` — the AT-149 arms under review are untouched). Both targeted sets were re-run after that edit and are GREEN (§3). This reviewer touched none of those files; every reviewer edit was restored hash-identical (§5, §6).

---

## INCREMENT 006b — LLR-RVH.4.4 · help + palette carry the relmap scope (AT-149)

### 1 · The key question: are the entries derived from the seat, shown on the real surface?

Yes on both halves, verified independently of the packet's instruments:

- **Derivation (static read):** the legend's keymap section renders `bindings_for(self.scope)` and nothing else (`mapper/screens/help.py:433-440`; the presented-set contract is a prior sealed requirement, LLR-R05.2, whose own comment names the census). The palette fills `self._items` from `palette_items(query, self.scope)` (`mapper/screens/palette.py:141`). The scope itself arrives from the screen's `KEY_SCOPE` through `app.action_help` / `app.action_palette` (LLR-RVH.4.4's draft-time verification, `01-requirements.md:813`). No hand-listed row exists on either path.
- **Real surface (reviewer's own pilot):** `MapperApp(workspace=…)` + `run_test()` at **118×34 and 87×34** (tmp workspace, since deleted): `?` → `HelpScreen` with `scope == relmap`; the painted `#help-content` rows equal `{(glyph, label)}` of `bindings_for(SCOPE_RELMAP)` as a SET (15 rows: 13 relmap + 2 app chords), both directions; the legend paints on the composited frame (not merely stored); `escape` returns to the relmap screen; `ctrl+p` → `CommandPalette(scope=relmap)`, offered items equal the palette seat as a set; typing `mat` filters to exactly `[('1','matrix','matrix')]`; `down` + `enter` lands on the matrix view. **PASS at both widths.**

### 2 · Findings

**BLOCKER — none.** **MAJOR — none.**

**F1 — the palette arm alone is blind to a DROPPED seat row (derivation-relative equality).**
- **What:** the palette arm compares `palette._items` to `palette_items("", SCOPE_RELMAP)` — both sides derive from the same seat, so dropping a seat row shrinks both sides and the equality still holds. Demonstrated live by reviewer mutant M-R-6B-2 (§5): with the `c chain` seat row removed, the palette arm stayed GREEN; only the help arm reddened — and it reddened on its AT-149 named-chord sub-assert (`('c','chain') in painted`), not on its set equality, which is equally derivation-relative. The packet's battery covered the hand-added direction (M-RVH-12 both surfaces) but no mutant covers the dropped-seat direction.
- **Where:** `tests/test_relmap_shell.py` (`test_at_149_palette_offers_the_seat_and_runs_matrix`); `tests/test_relmap_shell.py:1157-1160` (the named-chord sub-assert that caught the drop).
- **Why it matters:** none alone — the pair plus the whole-seat census (`tests/test_keymap.py`, green in the commissioned run) pins the seat itself, so a dropped row reddens the suite somewhere. But the claim "a dropped seat row reddens this [palette] arm" (arm docstring) is only true via the sibling arm; the palette arm by itself cannot fail on a seat drop.
- **Suggested fix:** one named-action sub-assert on the palette side (e.g. `('c','chain','chain') in offered`), mirroring the help arm; or reword the docstring.

**F2 — `_help_key_rows` bakes the legend row anatomy into the test.**
- **What:** the parser hard-codes the 2-cell indent + 10-cell glyph column of `HelpScreen._append_key_group` (`mapper/screens/help.py:420-422`). A legend layout redesign would silently break the parse. **Already declared** in packet §5 risks — recorded here so the DDR does not re-litigate; my 87-width pilot confirms the anatomy holds at the narrow width (the equality is layout-relative but width-insensitive over 87…118).
- **Where:** `tests/test_relmap_shell.py:1094-1105`.
- **Severity:** MINOR (declared risk; the set equality would fail loudly, not vacuously, on an anatomy change — an empty parse ≠ seat).

### 3 · Controls re-run (evidence states: executed)

| Control | Method | Result |
|---|---|---|
| Import provenance | `python -c "import mapper; print(mapper.__file__)"` with `PYTHONPATH=<worktree>` | resolves inside the worktree ✓ |
| Commissioned suite | `pytest -q -p no:cacheprovider tests/test_hook_line_bound.py tests/test_relmap_audit.py tests/test_help*.py tests/test_palette*.py tests/test_keymap.py tests/test_reqharness_release.py` | **263 passed, 1 skipped** (109s, exit 0) |
| AT-149 arms at baseline | `pytest tests/test_relmap_shell.py -k "at_149"` | **2 passed** (green control before the battery; re-run GREEN after the concurrent session's insertion at :813) |
| Reviewer's own pilot | probe under the declared tmp dir, real keys at 118 and 87 | **PASS** (§1) |
| RED cross-read | `evidence/p3-inc006b-red-mutant.txt` | both arms RED on the hand row, exit 1, restore digest `17011f2f…e8ed093a` — consistent with the packet; that digest equals my pre-review baseline of `help.py` |
| Evidence re-hash (C-59) | `sha256sum` of the packet's 4 evidence files | **4/4 MATCH** (§7) |
| Source-file count | `git show --stat 23bce8a` | 0 source / 4 allowed — declared deviation (assertion-only increment), justified by the contract's own draft-time verification; writing source would itself be the M-RVH-12 defect |

### 4 · Verdict for Inc-6b

**approve-with-nits** — F1, F2. The derivation is real and generic, the equality is two-directional on the painted/emitted form, the AT driver presses the real keys through the real screens (C-16), the RED counterfactual and the author's 2/2 mutants check out against the arms on disk, and my two reviewer mutants (§5) both die in the predicted direction with hash-proven restores. No HIGH finding; the increment may advance with F1/F2 on the orchestrator's ledger.

---

## INCREMENT 007 — LLR-RVU.1.1 · the `--audit` hook per-line bound 240 (AT-152)

### 1 · The key question: does the F-SEC-3 order hold on the emitted form, for hostile lines?

Yes, verified beyond the shipped fixtures:

- **Pipeline order (static read):** the print loop is exactly `shown = _cut_hook_line(_visible(line))` → `verdict: ` rewrite check → `print` (`mapper/reqharness/audit.py:473-477`), matching PDR D4 + F-SEC-3 verbatim; the sink comment and `_hook_lines` docstring pin the same order. Every hook line — fixed no-repo/no-registry lines and the truncation line included — passes this single print door, so the bound applies to the whole hook surface by construction (load-bearing emptiness is honest: the only print door is the loop itself).
- **Bound on the escaped form:** `_cut_hook_line` predicates over the escaped line (constant comment `mapper/reqharness/audit.py:83-88`); kept = first 239 cells + one ellipsis → emitted ≤ 240, backing to a spelling start when the boundary straddles a `\xNN`/`\uXXXX` spelling, re-checking adjacent spellings (`mapper/reqharness/audit.py:127-154`). The back-off loop strictly shortens `kept` each iteration and terminates (rfind < len).
- **Reviewer's hostile probes (real `run_cli`, registry-repo fixture):**
  - `\x1b` straddle (`"e"*237 + ESC`, escaped 241) → `"e"*237 + "…"` (238 cells);
  - U+202E straddle (`"u"*236 + U+202E`, escaped 242) → `"u"*236 + "…"`;
  - combining marks (`"a"*234 + U+0301×2`, escaped 246, boundary mid-second-spelling) → `"a"*234 + "…"`;
  - wide CJK (`"漢"*300`) → `"漢"*239 + "…"` — 239 code points + ellipsis (code-point counting per the contract's "characters" wording; see F2);
  - `verdict: ` + 400 cells → `"structure: " + "verdict: " + "v"*230 + "…"` — the guard fires **after** the cut; exactly one `verdict: `-prefixed line in the whole output (census);
  - a short `verdict: short` line still rewrites (R1 semantics intact);
  - under-bound line with escapes passes through byte-for-byte;
  - exit code identical with and without the hook on every payload;
  - no raw control char anywhere on stdout in any run. **PASS.**
- **Boundary sweep (reviewer-authored, over `_cut_hook_line` directly):** every straddle start position for the `\xNN`, `\u202e`, `\u0301` classes; the 239/240/241 edges; adjacent and only-spellings lines; empty/short passthrough — invariant held everywhere: emitted ≤ 240, exactly one trailing ellipsis when cut, kept is always a whole-spelling-clean prefix of the escaped form. **PASS (no failures).**

### 2 · The R1 gate amendment — honest or a silent stretch?

Honest. The two re-derived arms (`tests/test_relmap_audit.py:727-745` `test_at_125…`, `:853-868` `test_snapshot_run`) move qualifier CONTENT to the D5 seam and assert the bound on the emitted form:

- The seam contract is on disk and says what the packet claims: `structure_lines` returns **UNESCAPED** lines and "the caller's sink must escape them" (`mapper/relmap/audit.py:173-177`) — content authority on the seam is the layer that owns content; the sink gained a `≤ 240` pin the arms never had.
- Block order and figures stay byte-pinned (`test_snapshot_run`: block[0..4], gap/note counts, total); the qualified-count assertion moved to the seam keeps counting exactly 2.
- The supersession-completeness claim checks out: the only whole-text reads left on the emitted snapshot surface are the seam-based re-derivations (grep for `canon rows near this id` shows them at :740-742 and :866-867).
- The enumeration genuinely ran before the edit — the instrument RED-proof table records the first GREEN-audit pass failing on exactly these two arms (risk #6 firing as the PDR predicted).
- R1 D4 untouched in substance: the 1,000-line bound, the prefix rewrite, the fixed lines, the exit code — the R1 suite is green inside the commissioned run (`tests/test_relmap_audit.py`: 48 passed, 1 skipped of the commissioned 263).

### 3 · Findings

**BLOCKER — none.** **MAJOR — none.**

**F1 — packet prose under-measures the `verdict:` corner by one cell ("250 cells"; "the 10-cell `structure: ` rewrite").**
- **What:** `"structure: "` is **11** cells, so the shipped corner emits **251** cells — my live probe measured 251, and the shipped order arm asserts the exact 251-cell string (`"structure: " + "verdict: " + "v"*230 + "…"`) without naming the number. The packet's §1, §4 layer-A row and §5 risk bullet all say 250 / "10-cell". The CODE and the TEST are correct; the PROSE is off by one.
- **Where:** packet `03-increments/increment-007.md` §1/§4/§5; code `mapper/reqharness/audit.py:476`; test `tests/test_hook_line_bound.py:121-123`.
- **Why it matters:** a future reader reconciling AT-152's "the emitted line length is ≤ 240" against a measured 251-cell line will trip on the packet first. The LLR itself is unambiguous (the bound predicates over the pre-rewrite escaped line; the rewrite is R1-frozen downstream), so this is documentation accuracy, not behavior.
- **Suggested fix:** one-line packet amendment: "251 cells (the 11-cell `structure: ` prefix + the 240-cell cut form)"; optionally spell AT-152's ≤240 as "the pre-rewrite hook line".

**F2 — the bound counts code points, not display cells; wide glyphs can paint ~2× the bound.**
- **What:** `_cut_hook_line` slices by Python characters; a CJK-heavy line emits 239 wide glyphs + ellipsis (~480 display cells). The contract's wording is "characters" (`LLR-RVU.1.1`, ruling `LED-2026-10-25-r2.02`) and the hostile vocabulary the escaper re-spells (Cf/Zl/Zp/Mn/Me/Zs/controls) is exactly the width-spoofing class — the packet declares this trade in §5 for the DDR. My probe confirms the shipped form matches the code-point reading.
- **Where:** `mapper/reqharness/audit.py:139-141`.
- **Severity:** MINOR as shipped (declared, contract-conformant); it becomes MAJOR only if a later contract re-reads "characters" as "cells" — which is why it belongs in the DDR notes.

### 4 · Controls re-run (evidence states: executed)

| Control | Method | Result |
|---|---|---|
| Commissioned suite (includes `tests/test_relmap_audit.py` — the R1 suite with the amended arms) | the commissioned 6-file command | **263 passed, 1 skipped** — the 2 re-derived arms green in place |
| Hook-bound file at baseline | `pytest tests/test_hook_line_bound.py` | **7 passed** (green control; re-run GREEN after every restore) |
| RED cross-read | `evidence/p3-inc7-red.txt` | 6 failed / 1 by-design pass on the unmodified sink, exit 1 — consistent with the packet |
| Reviewer hostile probes + boundary sweep | real `run_cli` + direct unit sweep, §1 | **PASS** |
| A3 census / R1 goldens | not in the commissioned set — covered by the packet's guard transcript (`evidence/p3-inc7-green-guards.txt`, re-hashed MATCH); the reverse-census claims re-read consistently with the code on disk (B1 consumers unchanged; B3: no golden captures a >240-cell hook line) |
| Evidence re-hash (C-59) | `sha256sum` of the packet's 5 evidence files | **5/5 MATCH** (§7) |
| Source-file count | `git show --stat 4853b16` | 1/1 — exactly the PLAN Inc-7 row; `run_cli(argv, extra_lines=None)` signature unchanged (A3) |

### 5 · Verdict for Inc-7

**approve-with-nits** — F1, F2. The F-SEC-3 order is the code as written and as pinned; the bound predicates over the emitted form (C-42); the spelling back-off is correct at every straddle position my sweep tried; the `verdict: ` exclusivity census and exit code are unchanged from R1; the two re-derived R1 arms are a genuine re-pointing at the layer that owns content, enumerated by their own failing run before the first edit — not a weakening. My three reviewer mutants (§6) die in the predicted arms with hash-proven restores. No HIGH finding; the increment may advance with F1/F2 on the orchestrator's ledger.

---

## 6 · Reviewer mutation battery — Increment 006b (control C-2: apply → run → restore → sha256)

Baseline (pre-review) digests: `mapper/screens/help.py` `17011f2f…e8ed093a` · `mapper/keymap.py` `319877a5…012a247` — both match the packet's own restore digests.

| Id | Site | Change (a plausible defect) | Instruments run | Verdict |
|---|---|---|---|---|
| M-R-6B-1 | `mapper/screens/help.py:439` | a hand-written row appended in `_render_keymap` beside the seat read (`zz` / `hand added`) — the M-RVH-12 class from the other side | `pytest tests/test_relmap_shell.py -k "at_149"` | **KILLED** — help arm RED: `hand-added: [('zz', 'hand added')], missing: []`; palette arm GREEN by design (single-surface mutation). Restore sha256 `17011f2f…e8ed093a` — **MATCH**; arms re-run GREEN after restore (2 passed) |
| M-R-6B-2 | `mapper/keymap.py:355` | the `c chain` seat row dropped — the direction the packet's battery never tried | same | **KILLED ×1 (partial)** — help arm RED: `AT-149 names the row c chain`; palette arm GREEN (drop-blind — finding F1). Restore sha256 `319877a5…012a247` — **MATCH**; arms re-run GREEN (2 passed) |

## 6b · Reviewer mutation battery — Increment 007

Baseline (pre-review) digest: `mapper/reqharness/audit.py` `cd73899eb083a0eb…789733ff` — matches the packet's restore digest.

| Id | Site | Change (a plausible defect) | Instruments run | Verdict |
|---|---|---|---|---|
| M-R-7-1 | `mapper/reqharness/audit.py:141` | off-by-one: `kept = shown[:HOOK_LINE_CELLS]` (240 kept + ellipsis = 241 emitted) | `pytest tests/test_hook_line_bound.py` | **KILLED ×4** — unit boundaries, unit spelling-backoff, AT basic bound, AT verdict-order all RED. Restore sha256 `cd73899e…733ff` — **MATCH**; 7 passed after restore |
| M-R-7-2 | `mapper/reqharness/audit.py:474` | order swap inside the pair: `_visible(_cut_hook_line(line))` — cut on the RAW line, escape after (miscounts every spelling) | same | **KILLED ×2** — AT escaped-form predicate + AT straddling arms RED (plain-line arms GREEN by construction — 280-char payload has no escapes). Restore **MATCH** |
| M-R-7-3 | `mapper/reqharness/audit.py:473-477` | F-SEC-3 order swap: the `verdict: ` rewrite moved BEFORE the cut | same | **KILLED** — AT order arm RED (emitted the 240-cell cut of the rewritten line, not `structure: ` + the 240-cell cut form). Restore **MATCH** |

Restore control: every mutated file's post-restore sha256 equals its pre-review baseline, and the targeted suites were re-run after the final restore (2 passed; 7 passed). My instruments therefore demonstrably report FAILURE on the mutated tree and PASS on the restored tree — no fabricated kills. (Author's batteries cross-read consistently with the arms on disk; their BAD controls are recorded in-band in the re-hashed transcripts.)

## 7 · Evidence re-hash (C-59)

| Transcript | Recomputed sha256 | Packet-declared | Verdict |
|---|---|---|---|
| `evidence/p3-inc006b-red-mutant.txt` | `78c414d27bee9113…bf60885` | `78c414d2…f60885` | **MATCH** |
| `evidence/p3-inc006b-green-targeted.txt` | `e92e22edf33bdf3c…3a06185` | `e92e22ed…a06185` | **MATCH** |
| `evidence/p3-inc006b-mutants.txt` | `d1cb936399f09fb1…85a2ea` | `d1cb9363…85a2ea` | **MATCH** |
| `evidence/p3-inc006b-green-guards.txt` | `45fa28160a28051c…f1b3696` | `45fa2816…f1b3696` | **MATCH** |
| `evidence/p3-inc7-red.txt` | `6ba3bc8cd514e9a2…ccd03e` | `6ba3bc8c…ccd03e` | **MATCH** |
| `evidence/p3-inc7-green-targeted.txt` | `3cbfdd7e7147cbc0…4afa17` | `3cbfdd7e…4afa17` | **MATCH** |
| `evidence/p3-inc7-green-audit.txt` | `1605f75d3aba9196…abd8f2d` | `1605f75d…abd8f2d` | **MATCH** |
| `evidence/p3-inc7-mutants.txt` | `b3f5955a9aab887d…32870b` | `b3f5955a…32870b` | **MATCH** |
| `evidence/p3-inc7-green-guards.txt` | `4137bd3a963eab60…5ad8150` | `4137bd3a…5ad8150` | **MATCH** |

9/9 MATCH. Reviewer scratch (pilot/probes/sweep + tmp workspaces) lived outside the worktree under the declared temp dir and was deleted after the runs; no stray files, no commits.

## 8 · Lens summary

| Lens | Inc-6b | Inc-7 |
|---|---|---|
| code | 2 MINOR (F1 palette-arm drop-blindness alone; F2 parser anatomy — declared risk) — **approve-with-nits** | 2 MINOR (F1 packet prose 250→251; F2 code-point counting — declared for DDR) — **approve-with-nits** |
| security | no findings — the equality is a set census over the painted form; hostile labels flow through the seat's own escape discipline; no new surface, no secrets, no outbound action | no findings — the bound closes the arbitrarily-long-line hole at the only print door; escape spellings never split (no partial-escape tail can reach the terminal); `verdict: ` exclusivity census = 1 after the cut; exit code untouched; read-only audit, no destructive surface |
| ux | real-mechanism walkthrough **performed** at 118 and 87 (real keys `?`/`escape`/`ctrl+p`/typing/`enter`; painted frame read via the compositor) — help and palette list exactly the seat at both widths; user evaluation **not performed** — one-person team, no external user of this surface | operator-surface check via the CLI seam (the shipped entry point, real stdout bytes) — bounded lines, one ellipsis, whole spellings, fixed lines and verdict exclusivity as before; user evaluation **not performed** — same one-person declaration |
