# Sync notes — `2026-08-26-ui-next-batch-02`

**Read this BEFORE running `/dev-flow-sync` for this batch.**

## Operator-path redaction at sync (coordinator ruling, 2026-08-29)

**Originals stay intact; the sync redacts its COPIES.**

Executed at Inc-4a close: the operator's Windows username appears **13 times across 10 batch
artifacts**, seven of them in already-committed Inc-3 records. They are absolute paths inside
executed evidence transcripts (`C:\Users\<user>\Github\mapper\…`).

| Plane | Action |
|---|---|
| **repo** (`.dev-flow/**`) | **NOT rewritten.** These are evidence. A rewritten record stops saying what was actually measured, and reproducibility is what makes a transcript evidence rather than prose. |
| **vault copies** | **Redact** the username path prefix to a stable placeholder — `C:\Users\<operator>\` — and add a one-line header to each affected copy: `paths redacted at sync; originals in repo`. |

**Why the split is not a fudge.** Redacting a copy does not falsify the original, and the vault is the
artifact more likely to be shared with a client or a collaborator. The repo copy stays byte-true for
anyone re-running the measurement.

**Record the transform in the sync record** — which files were touched and what the substitution was —
so the redaction is itself auditable rather than silent.

### Files affected at the time of writing (re-derive at sync, do not trust this list)

```
01d-unpark-measurements.md
02k-inc4-viewstate-architect.md
03-increments/increment-003-code-review.md
03-increments/increment-003-code-review-confirmation.md
03-increments/increment-003-security-review.md
03-increments/increment-003-security-confirmation.md
03-increments/increment-003-security-pass3.md
03-increments/increment-004a.md
03-increments/increment-004a-security-review.md
03-increments/increment-004a-security-confirmation-2.md
```

Re-derive mechanically at sync time — prose counts decay, and this batch has three separate
demonstrations of that.

## Standing carry, NOT closed by this ruling

**The username strings in committed repo history remain a declared blocker for any PUBLIC push.**
Redacting vault copies does nothing for git history. Already carried in the repair-batch risks; the
ruling above does not discharge it and must not be read as doing so.

## C-45 PUSH obligation — portable, and NOT yet landed upstream

Redacting operator paths when copying evidence to a shared surface is a **portable** control: it is
not specific to this stack, this project, or Textual. Under the flow's own classification it belongs
in the global `dev-flow-sync` procedure, not only here.

⚠ **It has NOT been pushed upstream, deliberately.** `~/.claude` and `~/.claude/skills` currently
carry **uncommitted changes that pre-date this session** (validator `V16`). `C-44` forbids sweeping up
another session's work in progress in a shared config repo, so this batch records the obligation
rather than discharging it by committing over somebody else's edit. **An unpushed control is
indistinguishable from one that was never written** — so this is a live carry, not a note.
