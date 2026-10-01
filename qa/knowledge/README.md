# QA knowledge

This project's QA memory. Everything the team learns by running goes here, never into the global kit.

Deliberately thin: rules and conventions live in the repo's `CLAUDE.md`, subsystem docs in
`.claude/context/`, settled decisions in the harness memory. Copying them here creates a copy that
goes stale and then gets tested against.

Typical files, created when there is something to put in them:

| File | What it holds |
|---|---|
| `environments.md` | Operational detail behind `qa/CLAUDE.md` §1 |
| `test-accounts.md` | Personas and where their credentials live (credentials themselves in git-ignored `qa/fixtures/`) |
| `historical-risk-areas.md` | Where the system has actually broken. The manager maps changed files to tests through this |
| `known-issues.md` | Accepted behaviour that looks like a bug. Check before filing |
| `incidents.md` | The stories behind this project's overlay rules |
