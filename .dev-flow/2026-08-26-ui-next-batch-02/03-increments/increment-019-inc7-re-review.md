# Increment 019 · Inc-7 re-review (round 2) · 2026-09-25

Both lenses re-read the corrective pass (`6d775b8`, `c907aa6`; `15723df` is docs-only) at HEAD
`2de10da`, **serially**, under the pinned rev46+ process. Each fix was judged by the reviewer's own
counterfactual (mutate → a test must go RED → restore). Tree clean after each lens
(`git status --porcelain` = 0 lines, `git diff --quiet` passes).

## Verdicts

| Lens | Verdict | Discharged | Not discharged |
|---|---|---|---|
| code-reviewer | **BLOCK-UNTIL CR-F1, CR-F3** | CR-F2 (raise path) | CR-F1, CR-F3 |
| security-reviewer | **PASS** | SEC-F1 (applied, measured), SEC-F2 (record present in `open_blocks.B-64`) | — |

**Inc-7 stays BLOCKED on the code lens.** Both residuals repeat the defect their finding named.

## Code lens — residuals

- **CR-F1 (HIGH, false confidence).** The declared string is `mapa dañado — ↵ ver por qué`
  (01-requirements.md:3846; 01b V22). `darkside.DAMAGED_MAP_STATE` is `dañado — ↵ ver por qué`
  — no **mapa** (verified by the coordinator). The arm compares the card to the *constant*, not to
  the document: setting the constant to the correct value left the suite at 36 passed, same as the
  wrong value. **Fix:** correct the constant; the arm derives its expectation from the document.
- **CR-F3 (HIGH).** The derivation mechanism works (made-up label, drifted style → RED), but
  `darkside.py:557-558` still says "`tests/test_home.py` DERIVES from that document and compares";
  that file does not exist and never did (`git log --all` empty). The new `#:` docstring also
  overclaims: completeness is not checked (row V13 deleted → GREEN; the test is declared ⊆
  document by design), the glyph column is not derived, and members are 4-tuples, not 3.
  **Fix:** delete the old block; narrow the docstring to what is checked (label + style
  faithfulness, V22 glyph pin); name completeness and glyph fidelity as Inc-8's.

## New findings

| id | sev | where | what | disposition |
|---|---|---|---|---|
| `INC7-CR-R2-F1` | MEDIUM | app.py:649, :705 | A-102 load-warning guards on hero/resume untested (each removed → GREEN); behaviour correct today | Inc-7, non-blocking |
| `INC7-CR-R2-F2` | MEDIUM | darkside.py ~581-607 | glyph column lifted from prose, unchecked: V2 `ó`, V7 `·—`, V8 `·`, V3 `+▸`, V4 lacks braille range, V1/V4b/V12 empty; V11→`X` stays GREEN | **carry → Inc-8** (legend must derive glyphs by a written rule, row-by-row check) |
| `INC7-CR-R2-F3` | LOW | test_vocabulary_declaration.py | completeness unchecked (drop/rename row → GREEN) | carry → Inc-8 set-equality |
| `INC7-CR-R2-F4` | LOW | app.py:611-622 | load-warning toast not de-duplicated | merged with `INC7-SEC-R2-F2` |
| `INC7-SEC-R2-F1` | LOW | app.py:704, :756 | SEC-F1 guards have no regression test; structurally invisible while the `damaged` invariant holds (mutation B+M1/B+M2 → crash, M1+M2 alone → GREEN) | carry → tester / next sala increment |
| `INC7-SEC-R2-F2` | LOW | app.py:611-626, :655, :932 | warning map loaded up to 4× per mount, re-run on every return home; 8 identical toasts measured. Footprint, not injection | carry with `N-C2`, `F4` |
| `INC7-SEC-R2-F3` | LOW | state `open_blocks.B-64` | fourth-mechanism record has no file:line; site now app.py:795 | carry → B-64 re-basing |
| routed → qa | — | app.py:724-725 (`4cda8a92`, pre-batch) | `table.clear()` keeps columns, `add_columns` re-adds → 8 columns, 4 painting `None` | qa-reviewer; not Inc-7 |

## Security lens — the load-warning path

Hostile map name (`[bold`, U+202E, U+E0041) and hostile warning (`[red]`, `[link=file:///x]`,
bidi, TAG) driven through: all toasts pass `markup=False`, bidi/TAG code points come out as U+FFFD
through `darkside.plain`, tags render literal. **No injection.** Inc-7 did not worsen B-64; it
narrowed it (damaged maps no longer reach `_hero_text`).

## Tests run

Targeted only: `tests/test_repair_cycles.py` + `tests/test_vocabulary_declaration.py` → **36
passed**. Full lane not run (not needed for either lens; FLAKE-1 untouched). 12 code-lens and 5
security-lens mutations executed and restored; probe files deleted.

## Next

A corrective pass for CR-F1 + CR-F3 (and, cheaply, `INC7-CR-R2-F1`), then a **code-lens-only**
round 3 on that diff. The security lens has passed and is not owed again unless the fix touches
a sink.
