# D12 — dev-flow review-ledger proposal (LLR-RH.9.1)

> **What this is:** a proposal FROM the mapper project TO dev-flow, delivered at
> the close of batch 2026-10-11-reqharness-batch. It proposes that dev-flow's
> human-auditable review ledger become a *living canon* derived from a
> ReqHarness-style review registry. It changes nothing in dev-flow by itself;
> adoption is a dev-flow-side decision, outside this repository. Discharge:
> LLR-RH.9.1 (HLR-RH.9) — content verified at P6 against 04-validation §
> "LLR-RH.9.1" (numeric threshold: 0 unresolved findings).

## 1 · The observation

Dev-flow's per-batch artifacts already encode the information a review ledger
needs: P1 rulings, P2/PDR/DDR conditions, per-increment review verdicts, and
the 05-close ledger of who reviewed what and what they caught. But today that
information is:

- **Batch-scoped and write-once.** A closed batch's ledger is frozen prose.
  Nothing binds a review verdict to the exact bytes it reviewed; an amended
  requirement after the seal leaves the recorded review describing text that
  no longer exists, with no signal.
- **Self-attested.** A packet records its own review outcome. There is no
  independent, chain-backed record that a named reviewer approved *these
  normative fields* at *this chain head*.
- **Hard to query across batches.** "Which requirements changed after their
  last human approval?" is a research project, not a command.

ReqHarness (mapper, `mapper/reqharness/`) was built to solve exactly this for
one project's requirements. The D12 question: what should dev-flow adopt?

## 2 · What dev-flow would adopt

Four mechanisms, each already shipped and mutation-tested in this batch:

1. **Content-bound review events.** A review is a YAML event naming the
   object's id, a digest of its normative fields, and the chain head at
   signing (`mapper/reqharness/reviews.py`, LLR-RH.4.1/4.5). Edit the
   requirement and the object visibly returns to `changed · review`; the
   binding is to content, never to trust in process memory.
2. **A hash-chained role log with policy-bound config.** Who may sign what is
   not configuration folklore: it is an admin-approved event chain, genesis
   policy-bound from the first document, verified by walking `prev_hash`
   (`chain.py`, LLR-RH.1–3). Hand edits break the chain and are detected.
3. **Derived states under a published precedence table.** `reviewed` ·
   `changed · review` · `pre-reviewed` · `not reviewed` · `retired` are
   derived, not stored (`derive.py`, LLR-RH.5.1, precedence per PDR §3.4) —
   one algorithm, one answer, everywhere.
4. **Release rules evaluated by a read-only audit.** `mapper --audit <repo>`
   writes nothing, runs cache-off, and reports a verdict plus per-state
   counts and baseline diffs (`audit.py`/`release.py`, HLR-RH.6/7) — the
   gate's evidence becomes a command, not a promise.

## 3 · Proposed file layout (in a dev-flow canon home)

```
<flow canon>/
├── registry/                  # one registry per governed canon tree
│   ├── roles.yml              # hash-chained role events (append-only)
│   ├── pending.yml            # pending requests (resolved via chain events)
│   ├── reviews/               # one immutable file per review event, sha8-named
│   ├── baselines/             # named, commit-bound snapshots
│   └── .git/reqharness-cache/ # content-keyed parse cache (gitignored)
└── ledger/                    # GENERATED views — never edited by hand
    ├── by-object.md           # object → reviews → current derived state
    ├── by-batch.md            # batch → review events that governed its seal
    └── release.md             # audit verdict + counts + baseline diff
```

Rule: `registry/` is the canon; `ledger/` is derived. Any hand edit to
`ledger/` is regenerated away; any hand edit to `registry/` breaks the chain
and the audit says so. The current 05-close prose ledger remains, but becomes
a *view* — the 05 author cites the derived ledger instead of restating it.

## 4 · Migration path

1. **Pilots (one batch).** Stand up a registry beside an existing batch's
   01-requirements.md; backfill reviews from the closed batch's 02-review
   records as `pre-reviewed` (model-signed events never close a state —
   LLR-RH.4.3), so history is preserved without being laundered into human
   approval.
2. **Gate hook.** The closing-gate validator (V-rules) gains one rule: every
   normative row sealed by the batch carries a review event bound to the
   bytes on disk. The `--fold-canon` step already rewrites REQUIREMENTS.md;
   the new rule binds reviewers to exactly what the fold shipped.
3. **Ledger derivation.** 05-postmortem's review sections are generated from
   `ledger/by-batch.md`; the human-written parts (lessons, root causes) stay
   human.
4. **Cross-batch queries.** "Changed since last human approval" becomes a
   ledger query feeding the backlog triage.

## 5 · Open questions for the dev-flow owners

- **Granularity:** bind reviews to whole requirement records (as ReqHarness
  does) or to finer fields? Finer binds catch smaller edits but multiply
  event volume.
- **Identity:** ReqHarness's ceiling is "email + local git identity, hashed"
  (LLR-RH.4.4). Is that enough for a flow canon, or does adoption wait on
  the deferred strong mode (B-122)?
- **Multi-repo canons:** one registry per tree, or one registry with
  object-id namespaces? Fork/merge semantics differ (LLR-RH.3.2/R27).
- **Ledger staleness at seals:** derive at close (simple, occasionally
  stale between seals) or on every canon edit (fresh, needs the cache
  discipline of LLR-RH.5.3/5.4)?
- **Adoption scope:** all four mechanisms, or only content binding (1) +
  audit (4) with roles left to the existing V-rules?

## 6 · Evidence this works

- 36 LLRs, 9 HLRs shipped under this model; 24+ named reddening mutations
  executed RED (hand edits, forged genesis, cache poisoning, traversal,
  escaping — per `04-validation.md`).
- The P4 measurement miss (5.27 s warm derive vs ≤ 0.5 s) was found by the
  audit command at scale and fixed to 0.44 s — the model surfaces its own
  economics (`evidence/p4-timing.transcript`).
- The gate full suite caught 8 repo-wide guard failures per-increment slices
  missed; under D12, exactly that class of surprise is what the audit's
  per-state counts exist to make impossible to miss twice.
