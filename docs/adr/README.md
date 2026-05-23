# Architecture Decision Records

Decisions are recorded here using the [MADR](../../glossary/madr.md) format.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-standardise-agent-instructions.md) | Standardise Agent Instructions | accepted |

## Naming

Files are named `NNNN-short-title.md` (zero-padded 4 digits).

## Status values

`proposed` → `accepted` → `superseded` / `deprecated`

## When to write an ADR

- A new tool, dependency, or external service is adopted
- A file format, naming convention, or workflow is established
- A non-trivial architectural choice is made that would be costly to reverse

Use the `decisions` [skill](../../glossary/skill.md) in `.github/skills/decisions/SKILL.md` when writing ADRs.

## References

1. [MADR — Official Documentation](https://adr.github.io/madr/) — the format used for all ADRs in this folder.
2. [ADR GitHub Organisation](https://adr.github.io/) — canonical resource for ADR formats and tooling.
3. [`.github/copilot-instructions.md` §4](../../.github/copilot-instructions.md) — the agent instruction that mandates ADRs for non-trivial decisions.
