# Operator verdict — whole-branch gates · 2026-10-03

Base `9a2d1c7` (Gate-1 then landed `c2cafec..ab2106f`: FLAKE-1 and FLAKE-4 were test races, fixed;
three uninterrupted full lanes 2769/0). Whole-branch security sign-off: PASS (no HIGH; BRANCH-SEC-F1
operator paths in intermediate history, F2 personal email on 15 commits, F3 repo-local git config can run
a program via `log.showSignature`, all MEDIUM; F4–F6 LOW). Adversarial PR QA: BLOCK-UNTIL PR-QA-F1
(home `j`/`k` crash the app with ≥1 map — pre-existing, same on master, but advertised by this branch);
F3 hint blank or stale after a pan (new on the branch); F4 factory preview paints the absolute template
path and unfiltered docx text; F5 `fila-N`. Three questions were put to the operator; each took the
recommended option.

| id | Question | Answer (verbatim label) | What it rules |
|---|---|---|---|
| M1 | What is fixed before merge (Gate-2)? | Bloqueo + medios | PR-QA-F1, PR-QA-F3, BRANCH-SEC-F3, BRANCH-SEC-F4/PR-QA-F4, PR-QA-F5 in one increment with its review; LOW findings go to BACKLOG |
| M2 | How is the branch merged into `master`? | Squash merge | One clean commit on `master`; the intermediate commits (operator paths, personal email) do not enter `master`'s history |
| M3 | The remote branch after the squash | Decidir después del merge | `origin/feat/ui-next-batch-02` is left untouched until a later explicit decision; deleting it is irreversible |
