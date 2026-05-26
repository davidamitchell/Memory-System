# Capability

**Domain:** Knowledge representation and engineering

---

## Conceptual Definition

A capability is a defined, stable ability of an agent, system, or process to perform a specific class of operations or produce a specific class of outputs, under specified preconditions and within specified constraints.

**Necessary conditions:**
1. **Agent-relative** — it is attributed to a specific agent, system, or process (not to a domain in the abstract).
2. **Class-level** — it refers to a repeatable type of operation or output, not a single occurrence.
3. **Preconditioned** — it specifies the conditions under which the ability can be exercised.
4. **Constrained** — it operates within defined limits (resource, time, input type, environmental context).
5. **Stable** — it persists across multiple invocations; it is not a one-off achievement.

**Sufficient conditions:**  
Any stable, agent-attributed, preconditioned, and constrained ability to perform a class of operations or produce a class of outputs constitutes a capability.

---

## Operational Definition

A capability is operationally identified when:

1. It can be named and described by a verb phrase (e.g., "extract named entities from markdown documents").
2. Its preconditions can be listed (e.g., "given a markdown document and an entity schema").
3. Its outputs can be described (e.g., "a set of entity–type pairs").
4. Its limits can be stated (e.g., "limited to documents under 10,000 tokens").
5. It can be tested: given valid inputs meeting the preconditions, does the agent reliably produce the described output class?

---

## Distinguished From

| Term | Distinction |
|------|-------------|
| **Process** | A process is a sequence of operations; a capability is the stable ability to execute a process or class of processes. A capability may be realised by multiple processes. |
| **Function** | Function (in software) is a specific executable unit; capability is the domain-level ability that one or more functions may implement. |
| **Skill** | Skill is an informal synonym; capability is the formal, preconditioned, constrained version used in knowledge system design. |

---

## Related Terms

[process](process.md) · [model](model.md) · [knowledge](knowledge.md) · [wisdom](wisdom.md)
