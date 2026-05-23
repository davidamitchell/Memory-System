# Design Space

This folder contains conceptual and architectural design artefacts for the [Memory System](../../README.md).

Design work happens here **before** implementation. Files in this folder are living documents — they evolve as the design is refined.

## Index

| Document | Description | Status |
|----------|-------------|--------|
| [ontology-system-design.md](./ontology-system-design.md) | Ontology-based memory architecture — components, processors, diagrams | draft |

## Conventions

- Files are named `<kebab-case-topic>.md`
- Each design document carries a **Status** (`draft` → `reviewed` → `accepted` → `superseded`)
- When a design decision is finalised, a corresponding [ADR](../adr/README.md) is written and linked back here
- Diagrams use [Mermaid](https://mermaid.js.org/) embedded in fenced code blocks (`\`\`\`mermaid`)

## References

1. [`docs/adr/README.md`](../adr/README.md) — Architecture Decision Records that formalise decisions made in this design space
2. [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md) — agent instructions governing this repository
