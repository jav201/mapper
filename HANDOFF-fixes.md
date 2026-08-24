# HANDOFF — fix batch (the k7 fine-tuning, actionable)

**For:** the next agent. **Read first:** `REVIEW-2026-08-18.md` (the verified
findings) — this handoff turns them into an executable playbook, ordered.
**Do not:** change behavior beyond each fix's stated scope; keep the 53 tests
green; add the regression test each fix names. Base: `mapper @ 9517262`.

**Routing:** this is a *non-trivial fix set touching data-loss paths* — run it
through the repo's flow: the existing batch is at Phase 0 awaiting-gate; these
fixes belong in a NEW batch (fix batch, `mode: core` suffices per the flow's
own matrix) or appended to the current batch's backlog per the operator. Ask
once at kickoff which it is.

## Fix 1 — ids with hyphens corrupt maps on reload (DATA LOSS)

- **Where:** `mermaid.py:13-16` (id regex `\w+`), `app.py:991`
  (`action_add_child` generates `mi-hijo-nuevo`), `import_csv.py:49`.
- **Root cause:** the writer/reader grammars disagree — `\w+` reads,
  `[\w ]+`→slug-with-dashes writes. On reload the id splits at the dash; the
  sidecar re-adds the full id as an orphan; `LayeredRenderer` then dies on
  `pos[nid]`.
- **Fix:** allow `[\w-]+` in the mermaid id pattern (both parse AND dump
  sides), AND sanitize at generation/import (one `slugify` seat).
- **Regression test:** round-trip a map containing `mi-hijo` — save, reload,
  assert the node count and `pos` lookup.

## Fix 2 — editing with focus active deletes the rest of the map ON DISK (DATA LOSS)

- **Where:** `app.py:981-1000, 1022-1028` (`a` / `x` while `f` focus active).
- **Root cause:** the mutation acts on `self.graph` (the focused subtree) and
  `store.save(map_id, self.graph)` persists it as the whole map;
  `base_graph` is then overwritten, so neither `f` nor `u` recovers it.
- **Fix:** either block structural mutations while focus is active (guard +
  notify), or mutate `base_graph` always and re-derive the focused view.
  Decide once, in writing (the kanban/focus traps in taskboard are the
  precedent — hidden-but-navigable is a named bug there).
- **Regression test:** pilot test — focus on, add a child, assert the on-disk
  map still holds every node.

## Fix 3 — `ctrl+p` opens Textual's palette, and the darkside one can't dispatch

- **Where:** `app.py:1143-1147`; `CommandPalette` gets no callback;
  `action_run_selected` indexes the UNSORTED list while the view is sorted.
- **Fix:** `COMMAND_PALETTE_ENABLE = False` on `MapperApp`; wire each row to
  its real action; dispatch by the identity of the selected row, never by
  index into a different ordering.
- **Regression test:** pilot — `ctrl+p`, type `fic`, assert the darkside
  palette is the mounted screen AND that running the first row runs `add
  child`.

## Fix 4 — export SVG crashes on Windows (one line)

- **Where:** `export.py:16` — `Console(record=True, width=200, height=60)`
  without `file=`.
- **Fix:** `file=io.StringIO()`. (The lesson the handoffs already carried.)
- **Regression test:** the export test must run with stdout NOT captured
  (monkeypatch/console override) so cp1252 escapes can't hide behind pytest's
  capture.

## Fix 5 — `office.resolve` doesn't resolve fragmented/spaced tags

- **Where:** `office.py:113-115`.
- **Fix:** resolve over the per-paragraph CONCATENATED text (collapse runs at
  ingest), tolerate inner markup/whitespace inside `{{...}}`; XML-escape the
  replacement values (`&` `<` corrupt the file otherwise).
- **Regression test:** a docx whose `{{puesto}}` is split across two runs, and
  one with `{{ nombre }}` — both must resolve.

## MED stack (second pass, same batch if the operator allows)

Resume ordering (read `last_session()` before recording) + a key for the
resume row · undo persists after pop · home listens for screen-resume to
refresh recents · ONE keymap per context feeding keybar/help/palette (fix the
home keybar to arrows OR give the DataTable j/k) · editor preview marks only
real tag spans · `store._reindex` deletes children before parents + hash per
map_id + composite PK `(map_id, id)` · full local branch names + fetch in
`@work(thread=True)` · escape `]` and `\|` in mermaid dump · layered layout
skips nodes outside `pos` (or forest layout) · factory persists after `d`/`i`
+ output suffix from the source template · radial `_GREYS` never uses STEP as
TEXT color · LOW list in the review (each is one line or one decision).

## Tests that would have caught each HIGH (add them WITH the fix)

1. round-trip with a hyphenated id → catches Fix 1.
2. pilot: focus + add_child + reload from disk → catches Fix 2.
3. pilot: ctrl+p mounts the darkside palette + first row runs its action →
   catches Fix 3.
4. export with uncaptured stdout → catches Fix 4.
5. docx with a split tag → catches Fix 5.

## Out of scope for this batch

New features (the READY stories stand for the next feature batch), the
darkside contract work (HANDOFF-darkside.md), and the improvements round
(HANDOFF-improvements.md sections 1-5) — those wait until this fix batch
closes.
