# Post-mortem — `2026-08-26-repair-batch`

| Field | Value |
|---|---|
| Batch | `2026-08-26-repair-batch` · PR A, the shipped-defect repair |
| Objective | Repair S-01, S-02, S-07, S-08 before any feature work lands on top of them |
| Mode | `full` |
| Base | `origin/master` @ `d6b60e6b4f18b10123fffc76bbb36891473df653` |
| Increments | 1, 2, 2b, 3, 4 — plus a whole-branch security fold at the close |
| Suite | 245 collected at intake → **429 passing** at close |
| Sessions | 5, of which 4 ended in an interruption |

---

## 0 · BLUF

**All four defects are repaired, and the batch's real product is not the four fixes — it is a
catalogue of ways a green test lies.** Every substantive defect found after increment 1 was found
by *executing* something rather than reading it, and in five separate cases the thing that had to
be executed was a piece of the batch's own evidence machinery: a harness, a probe, a byte scanner,
an oracle, and a reviewer's proposed remedy.

The single most useful sentence to carry forward:

> **Every one of these defects returned a plausible answer, not an impossible one.**

A probe that returns `-1` or `0 of 0` betrays itself and gets fixed in a minute. A probe that
returns `11 missing` when the truth is `10`, or `409 passed` against a tree that no longer exists,
reads as a measurement. That is why none of them were caught by reading, and why the ones that were
caught were caught by a *second* independent execution disagreeing with the first.

---

## 1 · What was repaired

| Defect | Was | Is |
|---|---|---|
| **S-01a** | a cycle in a `.mmd` crashed the app | refused at load with the cycle path named in Spanish; `MapStore.save` refuses **before writing** (A-2), so no poison pill is created |
| **S-01b** | renderers died on pathological depth | all three renderers iterative + capped; `resolve_document`'s recursion **deleted** |
| **S-02** | a non-string ficha field loaded clean, broke every consumer, and `coverage()` counted it as documented | scalars coerce, containers are refused and recorded, the operator is told which node and which field, and the map still loads |
| **S-07** | canvas and inspector laid out off-screen whenever the rail was visible | `#map-rail` has a width rule; the three regions are disjoint and on-screen |
| **S-08** | the help overlay painted 16 of 27 bindings | the bindings region scrolls; all 27 reachable at three terminal sizes |

---

## 2 · The harness-defect catalogue — six defects, one signature

The mutation batteries are how this batch proves anything. **Six defects were found in the
harnesses themselves**, and five of the six would have reported a falsehood that read as a result.

| # | Defect | What it would have reported |
|---|---|---|
| 1 | the pytest command carried **both `-v` and `-q`**, which cancel to verbosity 0 | 0 nodes resolve, the baseline is empty, and **every arm reports INERT**. A vacuity detector, vacuous — the C-40 rider's named failure mode, verbatim |
| 2 | no `-o addopts=`, so the `slow` lane stayed deselected | the only nodes that can redden the depth arms never run |
| 3 | the node-id pattern stopped at the first space | one node permanently invisible. Positive control on real output: old pattern 28, new 29 |
| 4 | two anchors in one file, with the second snapshot taken **after** the first mutation | wrote the intermediate mutated state back over the good restore — **left `rail.py` mutated on disk** |
| 5 | `read_text`/`write_text` are **not byte-round-trip stable on Windows** | "restored" `factory.py` while rewriting 483 line endings. Text comparison passed; `git status` still read `M`; **only sha256 caught it** |
| 6 | the byte scanner stripped `\r` **after** splitting on `\n` | reported one trailing-whitespace line **per line** for every CRLF file |

**Defect 6 is the one that recurred inside this session.** Increment 2b recorded that its own
scanner reported this falsehood; increment 3's packet claimed the correction was applied; and the
scanner sitting in the scratchpad still had the bug when increment 4 reached for it. Writing down
that a tool is broken does not fix the tool. A corrected `bytescan2.py` was written rather than the
broken one re-inherited — the third time this batch had to learn that a recorded defect is not a
closed one.

**The durable fixes are structural, not procedural:**

1. **The harness lives outside the repository it mutates.** A fault cannot then leave an untracked
   mutator sitting beside a mutated tracked file.
2. **The battery runs detached**, immune to tool-call timeouts, so a killed foreground call cannot
   abandon a mutation mid-arm.
3. **`recover.py` pins the pristine sha256 values** and can reverse any applied arm *without the
   killed process's memory*. Recovery must not depend on the process that did the damage.
4. **Byte-level I/O and sha256 everywhere.** `git status` is not evidence — and for an untracked
   file it is worse than useless, since it reports identically whether or not the mutation was
   reverted.
5. **The expected arm count is asserted before any verdict is trusted.** An arm the harness cannot
   see is an arm it cannot report inert.

Increment 4 reused the proven harness by **copying** it rather than rewriting, so all six defects
stayed closed by inheritance instead of being re-derived. It then earned its keep immediately: it
**refused four of eight anchors** as ambiguous, because a single-line anchor carrying no newline is
byte-identical in LF and CRLF form and the harness cannot know which convention to write back.
Refusing beats guessing.

---

## 3 · Mutations left on disk — three incidents, and why the third was different

Incidents one and two are harness defects 4 and 5 above: an arm aborted and left a file mutated,
and a "restore" that rewrote every line ending. Both were caught by hash, not by inspection.

**The third incident was not a mutation left on disk — it was a measurement left in the
scratchpad**, and it is the more dangerous shape.

After increment 3's review returned **BLOCKED**, the code was fixed and the battery re-run. The v2
transcript was produced, correct and complete: 20 arms, `INERT ARMS: none`, hashes matching. **It
was never copied into `03-increments/`.** The file the packet cited remained the superseded 18-arm
run over a tree that no longer existed, whose pinned hashes for `store.py` and `model.py` no longer
matched disk.

Nothing was mis-measured. The measurement was sound and *unlanded*, which to every later reader is
indistinguishable from a measurement that was never taken. It was caught at the re-gate by
comparing the transcript's pinned hashes against an independent `sha256sum` — the only check that
could have caught it, because the packet, the transcript and the code were each internally
consistent.

**Durable fix:** a gate checklist item that asks whether *the evidence file on disk is the one this
packet cites*, verified by hash rather than by filename. Plus a `SUPERSEDED BY` banner at the head
of the retired transcript naming its hashes as pre-fix — because the incident being closed was
*"the wrong one of these two files was cited"*, and leaving the retired artifact self-describing as
authoritative leaves the identical trap set for the next reader.

---

## 4 · The dead-computation lesson

`Graph.resolve_document` walked the parent chain rebuilding the same mapping at every level and
returning what it started with. `documents` is graph-level and keyed by name — there is no per-node
document store — so the walk was **a no-op costing one stack frame per level**, which is why a
depth-5000 map raised `RecursionError` inside `FactoryScreen._preview`, outside every guard.

Increment 3's first fix replaced the recursion with an *iterative* fold. The equivalence oracle
compared it against a verbatim copy of the shipped recursion across **173 comparisons, 0
mismatches** — the strongest possible evidence that the fold was correct, and completely beside the
point. **An implementation with the walk deleted is indistinguishable from one that keeps it over
every graph**, so no assertion over output could separate them.

The visible signal was in the transcript the whole time:

| | v1 battery (18 arms) | v2 battery (20 arms) |
|---|---|---|
| `TC-R22` — the node certifying the traversal | **RED in 0 of 18 arms** | (renamed `TC-R33`) **0 of 20** |
| `TC-R35` — the walk-count gate that replaced it | did not exist | **RED in 3 arms** |

**A node that appears in zero arms of a battery designed to redden things is telling you something,
and nobody read the column.** It took an independent reviewer to say it out loud.

Two riders worth keeping:

- **The fix was to change what is observed, not to write a better assertion.** `TC-R35` counts
  calls to `Graph.parent_of` and asserts zero, with a positive control first proving the counter can
  count. The declared subject is finally *in the predicate's expression*.
- **The gate is only as broad as its expression.** `TC-R35`'s docstring first claimed a chain walk
  *"of any kind"* reddens it. A reviewer measured that false — a walk deriving each parent by
  scanning the edge list inline never touches `parent_of` and leaves it green. The docstring was
  narrowed to what is actually asserted. **A docstring is a load-bearing claim in this batch**, and
  an overclaiming gate is the same failure as an inert one at lower amplitude.

Fix A also *dissolved* a hazard rather than mitigating it: the walk needed a cycle guard whose only
regression mode was a **hang**, and CI cannot enforce a guard that hangs instead of failing. Deleting
the walk removed the guard and the hazard together, so `Risk 4` and its pending item were **deleted,
not carried**.

---

## 5 · The vacuous-check catalogue

### 5.1 `LLR-R03.4` — a requirement whose notice could be disabled with zero reddening

Every assertion increment 3 first wrote observed `graph.load_warnings`, which is **the model**. The
battery's app-layer arm disabled `_notice_load_warnings` entirely and **reddened nothing**: not one
node drove the shipped surface. A story whose promise is *"the operator is told"* was covered by a
list on an object.

C-40 limb 1 exactly — the declared subject never appeared in any predicate's expression — and it
was found by **mutation, not by review**.

### 5.2 A plausible-weaker arm that was not weak enough

Two arms in increment 4's first battery came back inert, and the packet retired both as *"no-op
mutations"*. One diagnosis was right and one was wrong, and the difference matters:

- **`L4` genuinely was a no-op.** It deleted an explicit `overflow-y: auto`, but
  `VerticalScroll.DEFAULT_CSS` already declares it. Verified against the framework's own default.
- **`L5` was a genuinely inert arm.** The packet claimed `height: 90%` binds before `max-height: 44`
  so the dialog never changed size. **Measured, the dialog grows 28 → 40 rows** and the scrollable
  surplus collapses from 14 to 2. The packet even contradicted itself — its own Risk 2 stated the
  arithmetic correctly while §4 used the inverted form to close the arm.

**The lesson is the distinction, not either verdict.** An inert arm and a no-op mutation look
identical in the summary — both print `0` — and they demand opposite responses. A no-op mutation
means *aim at the declaration that actually decides the property*. An inert arm means *rewrite the
predicate, do not re-argue it*. Re-arguing an inert arm on a premise that measurement refutes is how
a battery becomes theatre, and this batch did it once.

The response was to write the predicate (`TC-R36`, which asserts which declaration governs the
dialog's height at each size) and re-run the identical mutation against it. It reddens.

### 5.3 A negative control is not an inert arm — say which you meant, in advance

`L4b` — swap in a plain `Vertical` while *keeping* the CSS rule — returned 0 RED and appears under
`INERT ARMS` in the summary, because the harness counts RED verdicts. That label is mechanically
correct and substantively wrong: **`L4b`'s greenness is the evidence**, proving the explicit
`overflow-y` rule overrides `Vertical`'s `overflow: hidden` and is a genuine second guard rather
than the redundancy `L4` made it look like.

What makes that a legitimate reading rather than a rationalisation is that **"Expected GREEN" was
written into the arm before it ran.** A pre-registered prediction is evidence; the same sentence
written afterwards is an excuse. Harnesses should carry an explicit `expect: green` field so the
summary can distinguish the two instead of leaving it to prose.

### 5.4 The oracle was the finding, twice

S-08's whole result rests on reading painted output. **Three candidate oracles were measured and two
were wrong in opposite directions:**

| Oracle | Missing at 140×45, pre-fix | Verdict |
|---|---:|---|
| `Screen.render_line(y)` | **27 of 27** | **false-fails a correct implementation** — renders the screen's own line, not the composited frame |
| the content widget's own `render_lines` | **0 at every size** | **vacuous** — the `Static` really does render all 27 rows; `max-height` clips them, and a widget's own paint cannot see a *reachability* defect |
| composited frame **clipped to the dialog** | **11 — the whole `view` group** | correct |
| the same read **unclipped** | **10** | under-reports by exactly one word |

The second row is the trap worth naming: *"region-clipped by construction"* sounded strictly safer
and was worthless, because the defect was never that the content was missing — it was that the
content was unreachable.

**Then the oracle's own guard turned out to be vacuous.** `AT-R14` intersected `rstrip`ped
outside-rows with width-**padded** inside-rows: **0 of 28 rows were even eligible to match.** The
limb passed by padding, not by clipping. And because the clip is *two* conjuncts while the arm
mutated both at once, the column clip — the one that matters, since the leaked `cobertura` sits
inside the dialog's row band and escapes only via the column slice — was **entirely unguarded**. A
reviewer measured that an oracle clipped in rows but not columns reports 10 missing instead of 11
and `AT-R14` stays green: it would pass a fix that still hid a binding.

**Rider: a conjunctive criterion needs one mutation per conjunct.** The packet's own C-55 table said
so, and the packet violated it. The fix splits the arm (`L8a`, `L8b`) and asserts each conjunct's
geometry separately.

---

### P-05 applied to this batch's own flake

`P-05` is an existing process carry: *treat a flaky test as a poisoned instrument — it invalidates
every counterfactual that touches it, not just its own run.* `test_at_r16b` flaked once under load,
and it is a RED node in increment 3's arms. So the rule points at this batch.

**Checked rather than assumed:** `M10` reddens **five** nodes, of which `AT-R16b` is one and
`TC-R29`, `AT-R17`, `TC-R34` and `TC-R35` are the others; `M11` reddens three and **does not touch
`AT-R16b` at all**. No arm's verdict rests on the flaky node, so no counterfactual is poisoned.

Worth noting the asymmetry that makes this survivable: a flake that fails *spuriously* makes a
mutation look **more** effective, never less — so the risk it carries is a falsely-confident RED,
not a missed inert arm. That is the safer direction, but it is safe by luck rather than by design,
and the node still belongs in the lane nothing routinely runs.

---

## 6 · The pattern this batch paid for six times

| # | Where | Found by |
|---|---|---|
| 1 | increment 1, `F2` | code review |
| 2 | increment 2b, `F3` | code review |
| 3 | increment 3 re-gate, `G1` | re-gate |
| 4–5 | security pass, `M1` (two sites) | security |
| 6 | security pass, `M3` | security |

### The finding underneath the finding: B-07

`B-07` has been sitting in the canonical backlog since the **batch-01 close**:

> *"**N-14 remainder** — uncoerced `notify` / `_event_toast` sinks on the repo, import, template and
> export paths. Same class as the ones fixed in batch 01. **Enumerated, not left to rediscovery.**"*

**The class was already written down, with its sites enumerated, before this batch began.** Three
independent reviews then rediscovered instances of it one at a time, and each fixed the instance.

So "six occurrences" understates the lesson. The real one is:

> **A backlog entry that names a class is not a control.** Nothing reads the backlog at the moment
> the defect is being reintroduced.

That is this project's oldest meta-rule — *a control that mandates re-reading with no artifact
degrades to "I thought about it"* — turned on the backlog itself. The backlog is where a control
goes to wait; it is not where a control runs. Only an executable census runs at the moment of
reintroduction, and `TC-R38` is the first artifact in this project that does.

**It also caught the census being too narrow.** `B-07` named `_event_toast` as a sibling sink
family, which sent me looking, which is how the f-string blind spot surfaced (below). The backlog
entry could not prevent the defect, but it could still aim the search — which is a fair statement of
what a backlog is actually for.

### And B-10 closes the loop, at a measurable price

`B-10`, written at the same batch-01 PR gate:

> *"The `notify(` source census the security sign-off **conditioned N-2/N-14 on** was **never written
> as an artifact** — B-07's line list is its partial substitute and **may go stale**."*

So batch 01's merge gate **closed conditionally on this census being written, and it was never
written.** That is C-44's origin pattern exactly: a conditional verdict whose corrective item never
landed while the batch merged anyway. The backlog even predicted the failure mode — *"may go
stale"* — and then it did.

**The price is now measurable.** One batch later the class recurred **six times across three
independent reviews**, each costing a full review cycle to find and a fix to close. `TC-R38` is the
artifact `B-10` asked for, a batch late, and it discharges `B-07` and `B-10` together.

**The rule this yields is sharper than "write the census":**

> A gate that closes *conditionally* has not closed. Either the condition is discharged before the
> merge, or the gate is a **BLOCK**. "We'll do it next batch" is how a control becomes a backlog
> entry, and a backlog entry is not a control.

### The census's own blind spot, found the same way

`TC-R38`'s first version required `markup=False` only where the message is an **interpolating
f-string**. That shape-based predicate had a shape-shaped hole: `notify(str(exc), ...)` passes a
`Call`, not a `JoinedStr`, and was skipped — including a live site carrying remote-derived
`GitHubError` text with no keyword at all.

**A census with a shape-shaped hole does not close a class**, and the hole is invisible precisely
because the census looks rigorous. The rule is now shape-free: *anything that is not a compile-time
constant can carry injected markup, however it was built* — f-string, `%`, `.format()`,
concatenation or a call. Censused sites went 17 → 19.

`_event_toast` was measured **safe by construction** — it builds via `darkside.Text.assemble`, and
`Text` does not parse markup — so it needs no keyword. Nothing asserts that, which is a residual:
a future change routing it through `notify` would be silent.

**One mechanism every time:** a test stub spelled `lambda msg, **kw: notices.append(str(msg))`
captures the message and **discards the kwargs**, so `markup=False` — which is the entire defense at
a sink rendering file-derived text, since `App.notify` defaults to `markup=True` and
`darkside.plain()` deliberately preserves markup — can be deleted with the suite green.

The response, five times running, was to arm one more sink by hand. **Closing instances does not
close a class, and the recurrence is the evidence.**

`TC-R38` closes it as a class: it walks the AST of every module, collects every `notify` whose first
argument is an interpolating f-string, and requires `markup=False` at each. Seventeen sites found;
thirteen needed the keyword. Three properties make it durable — the set is **derived, never
hand-listed** (C-31), there is **deliberately no exemption list** (an allowlist is a hand-listed set
that rots, and no toast here wants markup), and it carries **its own vacuity guard** (`scanned >= 15`,
because a broken AST walk finds zero sites and reports a clean census).

**The general rule:** when the same finding recurs across three independent reviews, stop fixing the
instance. The recurrence has told you the unit of repair is wrong.

---

## 7 · A reviewer's remedy is a hypothesis

Twice in this batch a review's *proposed fix* was written, executed, and found not to work:

1. The flow's own C-50 rider documents an adversarial review that correctly found a guard
   overpromising and proposed an output assertion; **it was written, executed, and stayed green**,
   because two expressions that are the same set counted from opposite ends cannot be separated by
   any output.
2. The security pass reported `M2` — an over-long integer field denying the map — and attributed it
   to `_coerce_field`'s `str(value)`. **The guard was written, executed, and measured unreachable.**
   CPython caps integer *parsing* as well as formatting, and PyYAML's constructor calls `int(token)`,
   so the raise happens inside `yaml.safe_load` before the coercion ladder runs at all. The
   reviewer's probe was consistent with both mechanisms; **only running the proposed fix separated
   them.**

**And the correct fix was narrower than the one requested.** Treating an unparseable sidecar as
absent would open the map with every ficha blank, and `MapStore.save` would write that back over the
operator's real data. Refusing loudly is the safer contract for a file-backed tool. What changed is
that the refusal is now typed, Spanish and names the file, instead of escaping as a bare
`ValueError`.

**Rule:** apply a review's *finding* with the same scepticism you applied to the code. Reproduce the
mechanism, not just the symptom — a probe that returns the right symptom for the wrong reason is the
same failure class this whole batch is about.

---

## 8 · Process defects — the orchestrator's own

Recorded at the operator's instruction, held to the same standard as the code findings.

| # | Defect | Cost |
|---|---|---|
| 1 | the A3 census was 6 files short | caught at review |
| 2 | the S-08 oracle read another widget's pixels | designed-in, caught by measurement before implementation |
| 3 | the P-19 arithmetic | corrected in place |
| 4 | a malformed S-02 fixture | corrected |
| 5 | **the v2 battery transcript was never landed**, so the packet cited a superseded run | caught at re-gate by hash |
| 6 | **`A-9` and `A-10` were allocated as amendment ids and never written** into the requirements — `A-9` for four sessions | caught at the increment-4 close while discharging a re-gate finding about the *same* omission one table-row away |
| 7 | the §4 fast-lane row carried `393/16` from a 409-node tree; `393 + 16 = 409` gave it away | caught at gate |
| 8 | `L5` retired as a no-op on arithmetic that measurement refutes, while the same packet's Risk 2 stated it correctly | caught at gate |

**Defect 6 is a pattern, not a slip.** Twice an id was allocated in a packet and the artifact it
pointed at was never written. It is the same shape as defect 5 — *the work was done and the record
was not landed* — and the same shape as C-44's origin. Three instances in one batch.

**Defect 8 deserves its own note:** the packet contradicted itself in two sections, and the correct
version was the one written first. Later sections are written when the author is most tired and most
committed to a conclusion; that is exactly where a self-contradiction survives.

---

## 8b · What the merge gate found, and the fourth instance

The whole-branch `qa-reviewer` pass returned **CLEAR TO MERGE, zero HIGH**, conditional on two
one-line actions. Both were the batch's own declared standard, unmet at the moment of merge.

**`PM-1` — `prototypes/` was never added to `.gitignore`.** The plan states "never staged" three
times as a scope invariant; `.gitignore` was opened *this batch* for preventive entries
(`scratch/`, `out.txt`, `.env`); and this one — the only one with live files on disk — was omitted.
`git add -A --dry-run` staged **five prototype files**, and decision D13's ruff figure of 29 is only
valid while they stay untracked. The invariant was written down three times and enforced zero.

**`PM-2` — the traceability registry was false against disk, and it is `G5(b)` recurring.** §6
asserted *"18 AT · 38 TC … every id is enumerated individually"*; disk carried **22 AT · 48 TC**,
with four ids never registered at all. The increment-3 re-gate raised **exactly this defect about
exactly this table**, it was discharged, and increment 4 plus the close-out fold reintroduced it.

**That is the fourth instance of *the work was done and the record was not landed*** — after the
unlanded v2 transcript, `A-9`, and `A-10`. Four instances, one batch. The fix applied is not another
correction: **the count is no longer maintained by hand.** It is now stated as the output of a walk
over `tests/test_repair_*.py`, because a hand-maintained census is the defect this batch exists to
stop and that table was the last one still hand-maintained.

### And the gate recorded my own process defect

`P-1` in `04-validation.md`: **the tree was edited while that gate was running.** Three edits landed
after the review began. Every measurement taken before them was **voided and re-taken**.

I disclosed it unprompted and asked that it be recorded rather than absorbed, which is the only
reason it was recoverable — but the disclosure is not the lesson. The lesson is that I did to the
merge gate precisely what I had instructed four reviewers not to do to me, in the same session, in
writing, four times. **Knowing a rule and holding it under time pressure at the end of a long
session are different capacities**, and the second one failed. The gate names it as the same failure
family as the unlanded-v2 incident, and it is right.

**Durable form:** once a whole-branch gate is dispatched, the tree is frozen. Findings that arrive
during it are queued, not applied. That is why every finding in this gate touching `mapper/` or
`tests/` was carried to the backlog rather than fixed at the close, however cheap — `M-2`, `M-5`,
`M-6`, `L-4`, `L-5`, `L-6` are all one-expression fixes and all of them waited.

---

## 9 · What worked

- **Independent review earned its cost, unambiguously.** Every HIGH in this batch came from a
  reviewer, not from the suite: `F1` (the dead walk), `G1` (the third sink), `F1` again in increment
  4 (the unguarded clip conjunct). A green suite found none of them.
- **Re-gating after a BLOCKED verdict, with the original review left sealed.** The first review is
  the record of what was found; the re-gate is the record of the response. Editing the first would
  have destroyed the only evidence that the process worked.
- **Reverting a later increment's edits on an isolated copy** to prove no cross-increment regression,
  rather than inferring it from pass counts. The increment-4 reviewer did this and it is strictly
  stronger; it should be the default technique.
- **Executing the defect before designing the fix** (C-35). Both increment-4 defects were reproduced
  first, and in both cases the measurement changed the design — S-07's discriminating negative came
  from noticing the rail auto-collapses at 100×24, and S-08's entire oracle strategy was chosen by
  measuring three candidates rather than by picking the one that sounded safest.
- **Declining a finding, in writing, with its reason.** `F7`, `F8`, `F9`, `M4` and `M5` were not
  fixed, and each says why and where a later batch will find it. A declined finding with a recorded
  reason is a closed loop; a silently skipped one is not.

## 10 · Items proposed for the next batch

1. `-m slow` CI lane — this batch's depth acceptance runs only when someone types it.
2. A suite-level wall-clock bound: nothing fails if a test hangs rather than fails.
3. `test_at_r16b`'s **load-sensitivity** — it failed once under sustained load, passes in isolation
   and in clean full runs. A depth-5000 node whose verdict depends on ambient machine state is a weak
   gate, and it lives in the lane nothing runs.
4. `MAX_RENDER_NODES = 12000` admits ~50 s of frozen UI; O(n²) measured. A UX judgement, not a defect.
5. `_pop_snapshot` unguarded against this batch's new raises — unreachable today, but resting on an
   invariant this batch made load-bearing.
6. `_text_attributes()` recomputed per node; `str` unreachable in `("str", str)`.
7. `TC-R15`'s derivation and its oracle **share a predicate**, so an annotation-form change shrinks
   both sides at once.
8. Three screens push `HelpScreen()` with **no scope**, shadowed today by a priority binding.
9. `F-M5` — one malformed node denying a whole map — still open and still fenced out.
10. Operator identity and a session UUID inside the `.dev-flow/**` transcripts: a blocker for any
    public push.
11. A harness `expect: green` field, so a negative control stops being reported as an inert arm.
12. `.dev-flow/2026-08-26-ui-next-batch-02/` is untracked and **pre-dates this session** — reported
    as found, not swept into this PR (C-44).
