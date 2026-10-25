# Independent review - Increment 3 (relmap-r1)

Reviewer: code-reviewer (code + security lenses), independent of the author.
Scope: commits ecfea03 (golden, alone) and 1163ee9 (Inc-3). Source files: `mapper/yamlscan.py` (new),
`mapper/relmap/descriptor.py` (new), `mapper/store.py` (delegation) = 3 (<= 4). Read-only toward the
diff; mutations were restored and hash-verified.

## Verdict: APPROVE (no BLOCKER, no MAJOR; 3 MINOR notes, none blocking)

## Check results

1. Golden provenance - PASS (executed). I added a detached worktree of 25d69fe, ran
   `evidence/inc3-golden-capture.py` against its `store.py` (`mapper.__file__` proved in that tree).
   The 8 lines are byte-identical (CRLF normalised) to the committed `inc3-golden-capture-output.txt`
   and to a run of the same script on 1163ee9. So the goldens come from base code and survive the
   extraction. Temp worktree removed (`git worktree list` back to the 2 pre-existing entries).
2. `yamlscan.py` / `store.py` behaviour preservation - PASS. The old loop moved verbatim into `prescan`;
   only the raise changed to a typed `YamlLimitError`, and `_prescan_sidecar` re-words with the same two
   f-strings (`{exc.shown!r}`, `{exc.limit}` = MAX_DEPTH) and `from None`. `YamlLimitError` is not a
   `ValueError`/`YAMLError`, so the callers' parser nets cannot rewrite it (M-RML-12 is guarded).
   `ANCHOR_NAME_DISPLAY` has no remaining importer of `store` (grep clean; a test asserts it is gone).
3. `descriptor.py` - PASS. `read_repo_text` = lstat -> `is_link` (symlink and reparse) -> `S_ISREG` ->
   one `os.open` (O_NONBLOCK, O_BINARY) -> `fstat` identity (regular, st_dev, st_ino only when both
   non-zero, M1) -> `read_capped`. Every `RepoReadError`/`DescriptorError` cause is a `CAUSE[...]`
   literal (a `MappingProxyType`, M2); no `str(exc)`, path, anchor or YAML value reaches a message;
   `ContentReadError` text is only prefix-matched, never forwarded. K16/K17 fill only a fixed field name
   and a reason from `confine_reason`'s closed set (allow_list, colon, normalised, outside). Discovery:
   `sorted` then `[:8]`, remainder counted. Base name is `Path.name`, cut to 120 in `refusal_line`.
4. Hostile inputs (own, executed on Windows, all typed refusals, none over 0.25 s, no hang):
   - directory junction named `jd.relmap.yml`: `is a link` (K1). (A junction to a big file is not
     creatable on Windows; the reparse branch is the same `is_link` and the 200 MiB sparse file was never
     opened through it.)
   - 8.4 MiB descriptor over the cap: `exceeds the 8388608 byte limit` (K5), 0.01 s.
   - nested-anchor alias bomb (9^3 expansion): K8, refused before compose, 0.01 s.
   - NUL-laced (`kind: relation\0`, and a NUL inside a word): `looks binary` (K6).
   - 100,000-deep flow nesting: K9 in 0.23 s (iterative scan, no RecursionError).
   - invalid UTF-8: K7. `!!python/object/apply` tag: `not valid YAML` (K10), not executed.
   - 5,000-digit integer: K10 (ValueError net). `source.us_canon: {a: 1}`: K16 with the field name only.
   - `us_canon: ../../etc/passwd`: K17 `(outside)`, value not echoed.
   - 11 `*.relmap.yml` entries: 8 returned sorted, `3` reported as the remainder.
5. Mutants of my own, tests = golden + yamlscan + descriptor (all KILLED, restored, sha256 equal to the
   pre-mutation `descriptor.py` 4aad6f80..., `yamlscan.py` 084327f8...):
   - drop the `st_ino` zero guard (`before.st_ino != after.st_ino`): killed (1 failed)
   - drop the st_dev and inode comparison (`or False`): killed
   - `MAX_DESCRIPTORS` 8 -> 9: killed
   - anchor cut `>` -> `>=` (ellipsis boundary at exactly 40): killed
   - depth `>` -> `>=` at MAX_DEPTH: killed
   - K6 mapped to K7: killed
   - remove `sorted` in discovery: killed
6. Evidence re-hash: all 14 `inc3-*` artifacts match the packet's SHA-256 prefixes. Final-run count in
   my reduced file set was 227 passed, 1 skipped (the skip is `test_relmap_descriptor.py:136`, "Windows has
   no mkfifo", correctly labelled n/a). Traces: LLR-RML.1.x and K1-K17 are cited in module docstrings,
   test docstrings and the packet; the PDR conditions (N1, M1, M2, M4, D-3, D-7, D-8) each have a
   named node or mutant in the packet table.

## Findings

- MINOR-1 `mapper/relmap/descriptor.py:104-112` (`read_repo_text`): the file is opened twice (identity
  `os.open`+`fstat`, then `read_capped` opens again). The docstring states the residual window (needs
  write access to the audited repo; the read stays read-only and capped), so this is accepted, not a
  defect. If a later batch gets an fd-based `read_capped`, collapse to one open and drop the window.
- MINOR-2 `descriptor.py:151` (`ignored_keys`) and the `name` in `DescriptorError`: repository-derived
  text (keys, base names with control characters) is cut but UNESCAPED by design; safety depends on the
  sink escaping (module docstring says `run_cli` does). Confirm that when `run_cli` lands (Inc-5/6) with
  an ESC-in-filename test (my write of such a file failed on Windows, so I could not exercise it here).
- MINOR-3 `descriptor.py:128` net `(yaml.YAMLError, ValueError, RecursionError)` omits `MemoryError`;
  it is bounded by the 8 MiB cap plus the anchor ban, so not reachable by an alias bomb. No action.

No other issues. The `git status` "MM" on `descriptor.py` seen during my run is index/EOL noise from the
concurrent editor: `git diff HEAD` on the file is empty and its hash equals the packet's.
