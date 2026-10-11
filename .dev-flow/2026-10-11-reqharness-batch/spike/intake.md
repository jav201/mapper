# P0 intake spike — 2026-10-11-reqharness-batch

Read-only intake for the ReqHarness batch. No product or test change.

## Sources read (in order)

1. `.dev-flow/BACKLOG.md` rows **B-107** (product direction), **B-119** (gallery verdict:
   V, D2–D13, D1 registry ruling), **B-121** (registry mechanism), **B-122** (roles
   mechanism + protection), **B-123** (roles screen = matrix variant B).
2. `prototypes/reqharness_unified/NOTES.md` (unified gallery round; D1–D13 detail;
   63/7/56 measurement; US-R1…R12 / HLR-R1…R14 dedup).
3. `prototypes/roles_screen/NOTES.md` (three layouts, three states; operator verdict
   2026-10-11: **variant B**; open questions).
4. **Codex+Kimi plan rev3, 2026-09-11** (the conceptual proposal: artifact model
   US → HLR → LLR → TC/AT → EV → gate; configurable attributes; stale evidence;
   gap detector; cost guards) — readable, read in full.
5. **ReqHarness handoff, 2026-09-12** (rev3 mock screens, traps resolved) — readable,
   read in full.
6. `REQUIREMENTS.md` (the requirement canon: `Id · Statement · Owning batch · Status`;
   ~190 rows today).
7. `.dev-flow/2026-10-11-reqharness-batch/01-requirements.md` (the HLR/LLR field layout:
   Statement, Validation, Executed verification, Numeric pass threshold, Negative
   control, Boundary catalog, Ledger).
8. `docs/ARCHITECTURE.md` §1–§4 (module map, dependency bans, frozen interfaces).
9. `mapper/` top level, `mapper/screens/` (how a screen lands: a module per screen,
   `KEY_SCOPE` + `BINDINGS = screen_bindings(SCOPE_X)` from the keymap seat, chrome
   from `mapper/widgets/chrome.py`), `mapper/keymap.py` (scopes, groups, seat rules).

## Full capability list implied by the rulings

**Domain core (headless):**

1. **Registry files under `reqharness/`** (B-119 D1): a persistent, versioned,
   project-level registry — a living canon like `REQUIREMENTS.md`, NOT per batch or
   per PR. One record per object (US, HLR/LLR, AT/TC …) with configurable metadata.
   YAML is the source of truth; generated MD/HTML views are never a second source
   (B-121 ruling 5).
2. **Config** (B-122): `reqharness/config.yml` declares people, roles, object
   classes, the **normative field set** per class (statement, acceptance, threshold,
   negative control …), and release rules.
3. **Hash-chained role log** (B-122): role changes are approved events (who
   requested, who approved, previous hash). Genesis admin declared once at registry
   creation; only `admin` approves; nobody approves a change to themselves (a sole
   admin's own-role change stays pending until a second admin exists). A hand edit
   breaks the chain: mapper ignores it, keeps the last approved roles, and shows
   `config changed without approval`.
4. **Review events bound to content digests** (B-119 D1, B-121 ruling 2): each
   review record binds to the digest of the object's **normative** fields; a change
   there makes the object `needs review` automatically. **Informative** fields (why,
   evidence, notes) leave a visible `changed (informative)` mark without
   invalidating.
5. **Derived states**: `reviewed` · `needs review` (normative change or new object)
   · `changed (informative)` · `not readable` (D8, declared, no backfill) ·
   pre-review (model reviews from Claude/Kimi are recorded as pre-review and never
   close the state — B-121 ruling 3).
6. **Owner field** (D10): inherited rev3 enum with `unassigned` declared; reviewer
   identity from git `user.name`.
7. **US canon** (B-121 ruling 1): alongside `REQUIREMENTS.md` (HLR/LLR), a
   user-story canon.
8. **AT → test-node table** (B-121 ruling 1): test cases are canonical as the test
   nodes themselves; a thin AT → node table replaces prose TCs that can drift.
9. **Graduated AT→test edge** (D2): bound ● (named `test_atNNN`) · tagged ◐ ·
   none ○; backfill names only on open ATs.
10. **Declared vs EV test results** (B-121 ruling 4, D4): both count toward release;
    the baseline shows which is which; a pass in prose with no executed verification
    is a declared third state `declared pass · no EV` carrying its source file:line.
    EV is bound to the baseline commit. Evidence capture `e` stays OUT (D3, later,
    with allowlist + security-check-before-tools).
11. **Baselines** (B-119 D1): version/release freezes the review state; a later
    baseline shows what was already reviewed vs new / changed / pending; baseline
    diff between two baselines.
12. **Release-rule evaluation** (B-122 ruling 2, B-119 D1): blocks on a broken chain
    or on a review signed by someone without the role in force at that time
    (`not ready · registry not verifiable`); criteria: every TC pass, every
    requirement reviewed, release rules from config. A software board reads these
    artifacts.
13. **Role-bound approval** (B-121 ruling 3): only the role the configuration
    designates for an object class may mark it reviewed; one person may hold several
    roles.
14. **rev3 model in memory + read-only dev-flow adapter** (D5), pinned by template
    revision; **tolerant `(retired)` parser** (D9) likewise pinned; a structured
    retirement field is proposed to dev-flow, not parsed here.
15. **(batch, id) keys** (D7): every canon id is keyed by its owning batch;
    qualified ids proposed to dev-flow separately.
16. **Review depth capped at `light`** (D11).
17. **Entry root from the connected repo** (D13), with a CLI argument shortcut.

**Screens:**

18. **Roles screen** — matrix variant B (B-123): people × roles grid, ● in force ·
    ◐ pending · ○ not held; cursor cell to cell; `space` proposes a change inline;
    pending requests and hash-chain status in the footer band; a non-admin's edits
    become requests; a hand-edited config shows the broken chain, keeps the last
    approved roles, blocks the release. **Prototype verdict already given — no
    prototype round owed.**
19. **Review/signing screen** — mark objects reviewed (role-checked), show
    digest-bound review state. **No prototype exists → prototype round required
    before implementation** (standing authorization condition).
20. **Baseline/release view** — baseline freeze, diff, release-rule readout.
    **No prototype exists → prototype round required.**
21. **Minimal read-only status view** — registry summary + chain + release state
    at a glance. See open question O2 (can be folded into the roles screen chrome).

**dev-flow side (proposed TO dev-flow, not code in this repo):**

22. **D12**: the 05-close human review ledger is *derived* from the registry —
    a proposed dev-flow change (dev-flow must know the review canon). This batch
    writes the proposal; dev-flow adoption is outside the repo.
23. D7 qualified ids, D9 structured retirement field, D5/D9 template revision —
    proposals to dev-flow, not parser work here.

## Proposed slicing

**Recommendation (agrees with the orchestrator's starting point): this batch
delivers a coherent, usable vertical slice = the headless domain core +
the roles screen (variant B, prototyped) + a minimal read-only status surface.
Everything that needs a prototype round or touches dev-flow lands in follow-up
batches.**

### This batch — `2026-10-11-reqharness-batch` (recommended slice)

- **RH1 — package skeleton + config** (new source files ≤4): `mapper/reqharness/
  __init__.py`, `model.py` (value objects: Person, Role, ObjectRecord, Review,
  Baseline, ChainEvent), `config.py` (config schema: people/roles/classes/normative
  fields/release rules; load + validate; genesis creation). Headless, stdlib + YAML
  only.
- **RH2 — role chain** (≤2 source files): `chain.py` — genesis event, append,
  hash verification, tamper detection, approve rules (admin only, no
  self-approval), effective-roles derivation, `config changed without approval`
  state.
- **RH3 — registry + digests + derived state** (≤3 source files): `registry.py`
  (load/save `reqharness/registry.yml`, one record per object), `digest.py`
  (normative vs informative field digests), `derive.py` (reviewed / needs review /
  changed (informative) / not readable / declared pass · no EV with source file:line).
- **RH4 — baselines + release rules** (≤3 source files): `baseline.py` (freeze,
  diff new/changed/pending), `release.py` (criteria evaluation; blocks on broken
  chain or signer-without-role-in-force → `not ready · registry not verifiable`).
- **RH5 — roles screen in-app** (≤4 source files): `mapper/screens/roles.py`
  (variant B matrix per B-123), `mapper/keymap.py` (new `roles` scope — one
  increment owns the seat), `mapper/app.py` + home entry wiring. Colours from
  `darkside.py` tokens, glyphs from the seat, English copy. Tampered state and
  release block painted from the real chain.
- **RH6 — read-only status surface** (≤2 source files): recommend folding into the
  roles screen header/footer band (chain chip + release verdict + counts) so no new
  screen class is born — see open question O2. If ruled a separate screen, it owes
  a prototype round first.

Counts above are source files per increment; each increment's tests land in the
same increment.

### Follow-up batches

- **B-next-1 — review/signing screen** (prototype round first, then screen +
  keymap scope + wiring on top of RH3's derived states).
- **B-next-2 — US canon + AT → test-node extraction** (D5 read-only dev-flow
  adapter pinned by template revision; D2 graduated edge; D7 (batch,id) keys;
  D8/D9 parsers; D10 owner enum; D11 depth cap) — a headless `adapter.py` batch
  with its own spike on template revision detection.
- **B-next-3 — baselines/release UI** (prototype round first; baseline freeze +
  diff + release-rule readout on top of RH4).
- **B-next-4 — generated MD/HTML views** (B-121 ruling 5: generated, never a
  second source).
- **B-next-5 — dev-flow proposals** (D12 ledger derivation write-up, D7/D9
  structured fields) — documents, not repo code.
- **Out entirely**: D3 evidence capture `e` (later, gated on
  security-check-before-tools); B-122 optional strong mode (CODEOWNERS + signed
  commits); rev3 phase-2 items (term harmonisation, OOXML bindings).

### Prototype-round flags

- Roles screen: **none owed** (B-123 verdict, variant B).
- Status surface: **none if folded into the roles screen**; prototype owed if it
  becomes its own screen (standing authorization: every other new screen goes back
  as a prototype round).
- Review/signing screen: **prototype owed** (follow-up batch).
- Baseline/release view: **prototype owed** (follow-up batch).

## Risks

- **Identity spoofing — stated honestly.** The chain detects hand edits to
  `reqharness/config.yml` and mapper ignores them, but reviewer identity is git
  `user.name` (self-claimed), and anyone with commit access can rewrite the file
  *and* the chain together. The mechanism is "simple but effective" against
  accidental edits, unapproved changes, and audit-trail disputes — not against a
  determined insider. The honest ceiling is B-122's optional strong mode
  (CODEOWNERS + branch protection + signed commits); it stays out of scope and
  should be named as the upgrade path in the requirements.
- **YAML merge conflicts on an append-only log.** Parallel PRs appending role
  events or reviews to one YAML file will conflict. Mitigation candidates: a
  one-event-per-line append-only log file (git merges appends cleanly in most
  cases) with the YAML as a derived/indexed view; or serialising writes through
  one owner. Needs a ruling (O4).
- **Performance on large canons.** Digest derivation over every object on load is
  O(canon); the mapper canon is ~190 rows today, but the US canon + AT table will
  grow it. Mitigation: derive incrementally, cache digests in the registry, and
  keep the D11 depth cap. No guard mechanism is owed in this batch, but the
  derivation API should not force full-canon recomputation.
- **Module map placement.** `mapper/reqharness/` is a new module: per the
  staleness rule, `docs/ARCHITECTURE.md` §2 gains a row *before* requirements are
  derived (ARQ fires on its own). Proposed placement: a headless sibling of
  `model`/`store` — depends on stdlib + YAML only; forbidden: `reqharness` →
  anything in `mapper` except `design` coercion if ever needed (start with zero
  mapper deps); `screens`/`app` may import it; it never imports Textual. The
  dependency row must be written at ARQ, not discovered mid-batch.

## Open questions for the orchestrator

- **O1 — Registry file layout.** One `registry.yml` vs one file per object under
  `reqharness/objects/`? (Merge-conflict and review-diff trade-offs; rev3 used
  per-object files, B-119's "living canon" suggests fewer files.)
- **O2 — Status surface.** Fold the read-only status view into the roles screen
  chrome (no new screen, no prototype round — recommended) or a separate screen
  (prototype round owed)?
- **O3 — Genesis copy.** First chain event reads `approved: genesis` or
  `declared at registry creation`? (Open from the roles-screen prototype notes.)
- **O4 — Append-only log format.** One-event-per-line log + derived YAML index
  (merge-friendly) vs single YAML file (simple, conflict-prone)? This decision
  shapes RH2/RH3 file formats.
- **O5 — Admin edit path.** An admin's `space` on someone else records a pending
  change and `a` approves it (two keys, as prototyped) vs approve-by-default for
  admins (one key)? The prototype left this open.
- **O6 — Role removal glyph.** Matrix B models pending adds as ◐; removals are
  unmodelled (◑? strikethrough?). Needed before the roles screen increment.
- **O7 — D12 in this batch?** Does this batch write the dev-flow ledger-derivation
  proposal document, or is it fully deferred to a follow-up batch?
- **O8 — Registry root.** Confirm `reqharness/` at the connected-repo root (D13)
  with the CLI shortcut argument name (`--audit` per the gallery recommendation?).
- **O9 — Baseline identity.** Are baselines named + bound to a git commit, and do
  they live under `reqharness/baselines/`? (Affects RH4.)
