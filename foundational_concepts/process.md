# Process

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A process is a defined, bounded sequence of operations that transforms one or more inputs into one or more outputs according to specified rules, with identifiable start and end states.

**Necessary conditions:**
1. **Sequential** — it consists of operations in a defined order (even if some are parallel or conditional).
2. **Transformative** — it changes the state of its inputs, producing outputs that differ from the inputs.
3. **Bounded** — it has a defined start state and a defined end state (termination condition).
4. **Rule-governed** — the transitions between operations follow explicit or specifiable rules.
5. **Reproducible** — given the same inputs and rules, it produces the same class of outputs (deterministic or stochastically equivalent).

**Sufficient conditions:**  
Any bounded, sequential, rule-governed, transformative sequence of operations with defined start and end states constitutes a process.

---

## Operational Definition

A process is operationally identified when:

1. Its inputs and outputs can be named and typed.
2. Its steps can be enumerated in order.
3. Its termination condition can be stated.
4. It can be executed or simulated, and the outputs can be verified against expected results.
5. Its instances can be monitored: at any point during execution, the current state is identifiable.

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Capability** | A capability is the stable ability to perform a class of processes; a process is a specific operational sequence that realises that capability. |
| **Workflow** | A workflow is a process in which operations are assigned to agents or roles; process is the underlying structure independent of assignment. |
| **Function** | A function (mathematical or software) maps inputs to outputs atomically; a process has internal, inspectable sequential structure. |

---

## Related Terms

[capability](capability.md) · [model](model.md) · [knowledge extraction](knowledge-extraction.md) · [component](component.md)
