# PLAN — mapper — Batch 2026-10-09-modular-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓
> Seeded by `/dev-flow-init` step 4 in both modes; the living plan is owed at every gate
> that follows (`/dev-flow` §Living plan is the rule's home).

> **Field guide:** `templates/docs/plan-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

The living compendium of this batch: where-we-are · objective · per-story/per-station status ·
roadmap + increment plan · key decisions · risks/watch-items · conventions honored ·
out-of-scope carries · test ledger · decision log (the human-readable mirror of `state.json`).
**Create at batch open and update at every gate and significant checkpoint** — the
orchestrator presents the full plan in-conversation at each phase gate.

## Header

| Field | Value |
|---|---|
| Project | mapper |
| Batch | 2026-10-09-modular-batch |
| Objective | Modularise `mapper/app.py` (R-009) so that later batches can run parallel product lanes; behaviour-preserving |
| Standing authorization | Asked 2026-10-09 through AskUserQuestion. The operator's words, verbatim: «Ok, tenemos que modularizar para poder paralelizar el trabajo, eso es primordial.»; mode and authorization «full + autónomo + merge (Recomendado)». Also standing from the same message: Kimi is the primary worker («Es también primordial que te entiendas bien con kimi»). Merge only after a clean final PR-level qa-reviewer pass; a HIGH finding blocks. |
| First gate | `devflow-validate.py --brief` after the rollover on `d8cf942`: 1 block, `V7`, which is external (the installed flow bundle differs from its manifest) |
| Premises / RC-1 | `git fetch`; `origin/master` = `d8cf942` = the local tip. The P0 measurements are below. |

## Triggers

| Id | Verdict | Probe output |
|---|---|---|
| A1 | fired | new modules will be created under `mapper/screens/` (the ARQ decides which) |
| A2 | fired | `mapper/app.py`, `mapper/screens/*`, and `mapper/screens/factory.py`, which imports `mapper.app._PromptScreen` (B-02) |
| A3 | fired | names other modules consume move. `grep -rl "from mapper.app import" tests mapper` → 68 test files plus `mapper/screens/factory.py` |
| A4 | fired | the whole point: parallel extraction increments, in Kimi worktrees |
| B1 | fired | 17 test files read `app.py`'s source (AST and census tests). `grep -rln 'app.py"\|app\.__file__\|inspect.getsource' tests`. Two monkeypatch targets on `mapper.app`: `MAX_RENDER_NODES` (×5) and `refusal_sentence` (×1) |
| B2 | not fired | no file moves; code moves between files, and the files themselves stay (census per increment) |
| B3 | not fired | no golden directory |
| B4 | not fired | no artifact produced for another component |
| C1–C8 | not fired | no new input, network, secret or markup surface. `osopen` stays the only OS-handler crossing (`tests/test_arch_osopen_callers.py` re-run per increment) |
| D1, D2 | not fired | behaviour-preserving: no visible change |
| E1 | fired | ≥3 increments planned |
| E2, E3 | not fired | refactor; internal tool |
| F1 | fired | `V7` is external; `~/.claude` is not touched |
| F2 | not fired | the backlog was refreshed at the canon close |

## Where we are

P0 is open; ARQ is next.
- Kimi (`kimi-for-coding`) is running the mechanical census of `MapScreen`.
- The architect will propose the module cut from that census.
- A separate prototype round (the dev-flow audit tool) runs in parallel in its own worktree and does not touch this batch.

## Objective

1. No top-level screen class lives in `mapper/app.py` except as a re-export.
2. `MapScreen` (3454 lines) is split by concern into modules that two workers can edit at the same time without touching the same file.
3. Every existing test stays green, with no change to its behaviour assertions. Source-reading tests are generalised to scan the package.

## Measurements at P0 (`d8cf942`)

| Measure | Value |
|---|---|
| `mapper/app.py` | 5255 lines |
| `MapScreen` | lines 1536–4989 (3454 lines) |
| `HomeScreen` | 483 lines; `RepoScreen` 302; `_ImportPreviewScreen` 69; `PlugRepoScreen` 50; modals (`_PromptScreen`, `_ConfirmScreen`, `_TemplateScreen`, `_FichaScreen`, `ConstructScreen`) 264 in total |
| `MapperApp` + `main` | 266 lines |
| Test files importing `mapper.app` | 68 |
| Test files reading `app.py`'s source | 17 |

## Roadmap + increment plan

1. **ARQ:** a module map from the census (architect).
2. **P1:** stories and requirements.
3. **P2:** review.
4. **PDR:** the frozen interfaces of the cut.
5. **P3:** extraction increments, mostly run as parallel Kimi units in separate worktrees; the orchestrator verifies and integrates each.
6. **DDR, P4, P5, P6.**

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-09 | Mode `full`, autonomous + merge (operator) | structural refactor; ARQ/PDR/DDR fire |
| 2026-10-09 | Kimi is the primary worker; Claude plans, reviews, verifies | operator, 2026-10-09 |
| 2026-10-09 | Requirement ids namespaced `MOD` | B-105/B-106 convention |
| 2026-10-09 | `mapper.app` keeps re-exporting every moved name the tests import | 68 importing test files; the tests are not rewritten for the move |

## Risks / watch-items

- **Monkeypatch targets.** `MAX_RENDER_NODES` and `refusal_sentence` would silently stop patching if the code that reads them moves. The P3 census must cover them.
- **Source-reading tests (17)** assume `app.py`. Each increment that moves scanned code generalises its test to the package. They are never weakened.
- **Behaviour drift in a 3454-line move.** Mitigations: the full suite at every increment gate, and a byte-identical method-body check (moved code compared by AST dump).

## Conventions honored

- No visible change.
- Max 4 source files per increment.
- No operator paths.
- Namespaced ids.
- Kimi units are one-file-scoped where possible.

## Out-of-scope carries

- Performance B-33 (the next batch).
- The dev-flow audit tool (prototype round first).

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| full suite (canon P4, `791decb`) | 2026-10-09 | 2941 passed / 3 xfailed / 0 failed |

## Decision log

| Station | Date | Decision |
|---|---|---|
| P0 | 2026-10-09 | open — triggers A1–A4, B1, E1, F1 fired; ARQ, PDR, DDR taken up |
