# RHS scale spike -- reqharness storage

Batch: `2026-10-11-reqharness-batch`. Measurement only. Question: is the
planned storage (`reqharness/roles.yml` chained event stream +
`reqharness/reviews/` one file per review event, plus normative digests
from a `REQUIREMENTS.md`-shaped table) fast enough at realistic and large
scale, using only `yaml.safe_load`/`yaml.safe_dump` (what
`mapper/store.py` uses) and `hashlib.sha256`?

Loader availability: see the `loader availability` row.

| Case | Size | Median s | Note |
|---|---|---|---|
| roles chain N=10 |  | 0.0113 | load+verify=0.0086s |
| roles chain N=100 |  | 0.1012 | load+verify=0.0749s |
| roles chain N=1000 |  | 0.8913 | load+verify=0.6544s |
| reviews M=500 R=200 | 500 | 0.2352 | 500 files, 82 KiB, load=0.234s |
| reviews M=5000 R=2000 | 5000 | 2.3355 | 5000 files, 818 KiB, load=2.326s |
| reviews_20000_200 |  | not measured (timeout) | exceeded the 120 s subprocess timeout |
| reviews_20000_2000 |  | not measured (timeout) | exceeded the 120 s subprocess timeout |
| normative digests R=200 | 200 | 0.0008 | 200 rows, 34 KiB markdown |
| normative digests R=2000 | 2000 | 0.0064 | 2000 rows, 345 KiB markdown |
| baseline file R=200 | 200 | 0.1161 | 42 KiB on disk |
| baseline file R=2000 | 2000 | 1.0528 | 425 KiB on disk |
| loader availability |  | 0.2699 | CSafeLoader available; safe=0.2699s vs csafe=0.0436s (1000 docs) |

## Verdict

The small and medium cases are cheap: the roles chain verifies at O(N) hash-recompute
cost (≤ 0.9 s at N=1000), and normative digests stay in the millisecond range at
R=2000. The review-file line, however, does NOT "sit far inside any interactive
budget" at scale: 5 000 review files already take 2.3 s per load with
`yaml.safe_load` (one open+parse per file, linear in file count), and BOTH 20 000-file
cases timed out (> 120 s) — they are not measured, and any claim about their cost is
a guess, not a result. Observation, not measurement: the unit's own log recorded
~60 s for the FIRST read of freshly written files on this Windows machine (a
one-time on-access antivirus scan of new files) and ~9 s warm — so cold-cache first
reads on this machine carry an OS-level cost that no in-process optimization removes.
`CSafeLoader` is available and ~6× faster than the pure-Python loader
(0.2699 s → 0.0436 s for 1 000 docs). The earlier claim that "20,000 review files
load in nanoseconds" was wrong and is withdrawn.

## Recommendation

Per orchestrator ruling R-SCALE: (1) YAML loading shall use `yaml.CSafeLoader` when
available, falling back to `yaml.SafeLoader` — never `yaml.load` with any other
loader; this alone divides bulk parse cost by ~6. (2) Review event files are
IMMUTABLE once written (append-only event store; a correction is a new event), so
mapper keeps a LOCAL, git-ignored parse cache (`.reqharness-cache/reviews.json`,
keyed by file name + size + mtime → parsed event, invalidated per entry); the cold
cost is paid once per NEW file, never per load. (3) Budget: with a warm cache,
deriving all object states for 5 000 review events and 2 000 requirements completes
in ≤ 0.5 s (median of 3) on this machine — a P4 measurement, not a wall-clock
assertion in the suite. (4) The cache never feeds the release verdict without
re-validating each event's digest/role semantics — it caches PARSING only, and
deleting it must change no result. The roles chain and baseline shapes are unchanged
(verification is cheaper than any index at N≤1000).
