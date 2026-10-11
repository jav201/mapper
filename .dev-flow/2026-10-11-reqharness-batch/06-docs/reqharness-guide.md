# ReqHarness — user guide

ReqHarness is mapper's review-registry mechanism: a plain-YAML, hash-chained
record of who may review what, which requirement bytes were reviewed by whom,
and whether the evidence says a release is ready. Everything lives in a
`reqharness/` directory at the root of the governed repo; everything is
verifiable offline; hand edits are detected, not trusted.

## 1 · Creating a registry

A registry is created once per repo, into empty ground, through the core API
(there is deliberately no silent CLI for this — creation is a policy act):

```python
from mapper.reqharness.config import create_registry

config = create_registry(
    repo,                       # the governed repo's root
    person="alice",             # your id in the registry
    name="Alice Admin",
    email="alice@example.invalid",
)
```

This writes two files:

- `reqharness/config.yml` — the policy: people (email stored only as a
  salted-hash digest), roles (`admin`, `req-reviewer` by default), object
  classes (e.g. `HLR` objects whose normative field is `statement`), and the
  release rules.
- `reqharness/roles.yml` — the role chain, whose first event is `genesis`:
  it binds the config by hash (`config_hash`) so a later config edit without
  an approved policy event is reported as **config changed without approval**.

`create_registry` refuses to touch an existing registry — there is no
overwrite path.

## 2 · The roles screen

Open mapper in the repo and press **`R`** from the home screen (door count
includes it; `q`/`esc` returns home). The screen is a matrix: people × roles,
with a footer status band showing the chain head, who you are (the viewer),
and how many changes are pending.

Keys (all routed through the core, never a direct file edit):

- `j`/`k` — move to the next/previous person; `l`/`h` — next/previous role.
- **`space`** — *propose* the change under the cursor. If the change is about
  you, it becomes a **pending request** instead of landing immediately: one
  key applies changes to other people; your own changes need a second admin
  (two-key rule).
- **`a`** / **`r`** — (admin only) approve or reject the pending request
  under the cursor. Approval lands it as the chain event referencing the
  request. You can never approve your own request; if several requests pile
  up on one cell the screen refuses and names why. On success the hint names
  the request it resolved.
- If the chain is broken or forked, the screen paints the tamper state and
  goes read-only — `space`/`a`/`r` do nothing but explain.

## 3 · Reviews

Reviews are files under `reqharness/reviews/`, one immutable event each,
named by a content digest. Each event records the object id, the digest of
the object's **normative** fields (the rest is informative and does not
affect the state), the chain head at signing, and the signer's identity.
Derived states (never stored, always recomputed):

- `reviewed` — a signer whose role was in force at the bound head reviewed
  exactly these bytes.
- `changed · review` — the object changed after its last entitled review.
- `pre-reviewed` — signed by a reviewer whose role was not in force, or a
  model/self-declared review: visibly *not* a human approval.
- `not reviewed`, `retired`.

The parse cache (`.git/reqharness-cache/`) is a pure accelerator keyed on
content; it can never change a verdict.

## 4 · Baselines

A baseline freezes the current commit SHA and every object's derived state
under a name: `Baseline.create(repo, "m3")`. `mapper --audit <repo>
--baseline m3` then reports the diff in five classes: **new**, **changed**,
**retired**, plus the stale and unchanged-in-base comparisons. (`retired →
active` reactivation is not a class yet — see Limits.)

## 5 · Release rules and the audit

```text
mapper --audit <repo> [--baseline <name>]
```

`--audit` is strictly read-only: it verifies the chain, re-reads every review
(cache off), evaluates the release rules, and prints a verdict with exact
per-state counts. Three rules are mandatory and cannot be configured away:
`all_active_reviewed`, `chain_verified`, `signers_in_force`; the config may
add more. Exit code is 0 only when the verdict is `ready`. The report escapes
control and bidi characters, so file-derived text cannot forge the layout.

## 6 · Limits and known residuals (plain language)

- **Identity is local.** Reviewer identity is an email digest plus local git
  identity. Someone with write access to the repo can fabricate reviews in a
  persona they control; the chain proves *consistency*, not *who a human
  really is*. A strong mode was deliberately deferred.
- **A hand edit is always detectable, but detection is at read time.** The
  chain breaks loudly — yet the break is seen when the chain is next
  verified, not before.
- **The parse cache trusts file metadata for speed.** A rewrite that
  preserves name, size, mtime and file id could fool the warm cache — but
  that writer could edit the cache directly anyway, and `--audit` (cache
  off) always catches it. Rule of thumb: trust `--audit`, not the warm load.
- **Forks:** a one-event fork is recoverable with `resolve` (choose a child,
  both children paint excluded until then). A *multi-event* excluded branch
  currently reports `chain broken` with no guided recovery — B-126.
- **Screen freeze:** on opening the roles screen, git calls run on the UI
  thread; worst case is a ~30 s freeze (B-127).
- **Not built yet:** the `reactivated` diff class and review-state
  progression across baselines (B-125); the committer-vs-reviewer warning
  (B-124); multi-event fork recovery UI (B-126).
- **Input limits:** YAML event streams are depth- and size-bounded (nesting
  depth refused by name, 64 KB per config file, 4 MB per chain file, 100 000
  events); a legal-depth 4 MB load costs ~25 s by design.
