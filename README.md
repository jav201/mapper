# mapper

TUI for concept and structure maps where every node is a ficha.

## Install

```bash
pip install -e .
```

For PNG export support:

```bash
pip install -e ".[export]"
```

## Run

```bash
mapper [workspace-directory]
```

The workspace directory stores maps as `.mmd` + `_nodos.yml` pairs. A rebuildable
`mapper.db` SQLite index is created locally and must never be committed.

## Audit

```bash
mapper --audit <repository>
```

Prints the release-readiness report of a repository that carries the registry. How to read it:

- **The verdict is the line that starts with `verdict: `.** It is not the last line: structure lines
  follow it. In a CI step use `grep '^verdict: '`, not `tail -n 1`.
- **The `structure:` block is informational.** It starts with the line
  `structure: informational - does not change the verdict or the exit code`, and it never changes
  the verdict or the exit code. Its lines start with `structure:`, `structure gap:` or
  `structure note:`; a line such as `structure: gaps shown 20 of 21 ...` is a count, not a gap row.
- **`reach=<n>`** on a gap row is how many other nodes a change to that node reaches, following the
  links downstream from it (the node itself is not counted). It is a ranking aid, not a severity.
- The first line, `repo: <path>`, prints the absolute path of the repository.

## Keys

From the home screen:

- `c` — focus the map list and consult existing maps
- `p` — plug a GitHub repo (`owner/name`)
- `n` — construct a new map
- `q` — quit

In a map view:

- `j` / `k` — next / previous sibling
- `h` / `l` — parent / child
- `/` — search titles, notes, fields, attachment names
- `f` — focus subtree
- `Esc` — unfocus
- `o` — toggle outline view
- `r` — toggle radial mind-map view
- `e` — export current view to SVG
- `q` — back to home

## Persistence

- **Truth:** text files in the workspace (`<map>.mmd` for structure,
  `<map>_nodos.yml` for fichas, schema, and attachments).
- **Derived index:** `mapper.db` is rebuilt automatically from the text files;
  it is listed in `.gitignore` and must not be committed.

## Architecture

See `docs/ARCHITECTURE.md` for the module map, dependency rules, and frozen
interfaces.
