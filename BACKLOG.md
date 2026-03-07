# Backlog

---

## W-0001

status: done
created: 2026-03-07
updated: 2026-03-07

### Outcome

Repository structure is standardised: single `.github/copilot-instructions.md` source of truth, `.github/skills` submodule, `sync-skills.yml` workflow, `BACKLOG.md`, `PROGRESS.md`, `CHANGELOG.md`, and `docs/adr/` all present and consistent.

### Context

Standardisation pass to remove AGENTS.md and align with all other repos in the davidamitchell organisation.

## W-0002

status: proposed
created: 2026-03-07
updated: 2026-03-07

### Outcome

Concurrent Copilot branches stay in sync with main so that PRs don't require a manual rebase.

### Context

When multiple Copilot feature branches are open simultaneously they may diverge from a main that has received merged PRs. Detected during the headless-mode setup PR which required a manual rebase after main replaced AGENTS.md.

### Notes

Consider adding a scheduled workflow or PR check that detects when a Copilot branch is more than N commits behind main and posts a comment prompting a rebase.

---

