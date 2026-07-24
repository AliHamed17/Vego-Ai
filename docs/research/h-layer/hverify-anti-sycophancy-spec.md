# S5 H-Verify Anti-Sycophancy Specification

Status: **PROVISIONAL WORKING DRAFT.** M-04 and M-05 have not been recorded. The four-source set and two-round bound are proposals; EXP-009/010 are assumption-driven synthetic rule tests, not validation against real expert mistakes.

This document proposes the verification and anti-sycophancy behavior for H-Layer Skill S5 (H-Verify). It is intended to prevent blind acceptance of conflicting expert inputs while preserving human adjudication authority.

---

## 1. The Sycophancy Defense Mechanism

The proposed S5 flow evaluates a structured feedback record against four candidate source families. M-04 must select all four or a smaller phase-one subset:
1. **Language Templates (Agent 1):** Validates construct names, syntax rules, and mappings.
2. **Reference Guidelines (Agent 2):** Checks guideline content, severity levels, and classifications.
3. **Domain Description:** Validates domain facts, entity relationships, and constraints.
4. **Prior Stored Judgments (H3 Memory):** Detects contradictions with previously frozen expert decisions.

---

## 2. Contradiction Detection Order

### Rule-Based Conflict Checks (Deterministic)
S5 executes the following structural rules over incoming feedback:

* **Rule-1: Guideline Disabling Conflict:** If the expert selects `reject` for guideline $G$, but $G$ is marked as a core structural invariant in the Reference Guidelines, flag as conflict.
* **Rule-2: Template Syntax Inconsistency:** If the expert proposes a template revision that violates naming constraints in the active Language Template schema, flag as conflict.
* **Rule-3: Memory Divergence:** If a high-confidence lookup in H3 memory returns a matching past judgment with a conflicting decision, flag as conflict.

### Semantic Conflict Extraction (Separately Gated)
* Deterministic source and structural checks run first and produce a complete record before any semantic check is considered.
* A semantic or LLM-assisted checker is not authorized by this draft. It requires a separate implementation plan, approval, and claim boundary.
* If separately approved, a mismatch where the rationale uses negative qualifiers (for example, "does not apply" or "violates") while the decision is `approve` may be flagged as a possible negation conflict; it cannot be treated as proof that the human is wrong.

---

## 3. Bounded Dialogue Loop (M-04 Proposal)

To prevent infinite question-and-answer loops, the working draft proposes at most two question rounds followed by human adjudication. The bound is not approved until M-04 is recorded.

```mermaid
sequenceDiagram
    participant E as Expert
    participant V as S5 Verify
    participant M as H3 Memory

    E->>V: Submit Feedback
    V->>V: Execute Verification Checks
    alt Conflict Detected (Round 1)
        V->>E: Emit E11 & Present Question Card
        E->>V: Resubmit Revised Feedback
        V->>V: Re-verify
        alt Conflict Persists (Round 2)
            V->>E: Final Warn Card
            E->>V: Confirm Override with Override Rationale
            V->>V: Mark needs_adjudication; do not store as trusted memory
        else Verified
            V->>M: Store Verified Feedback (E12)
        end
    else Verified
        V->>M: Store Verified Feedback (E12)
    end
```

### Protocol Steps:
1. **First Conflict (Round 1):** S5 displays a dialog cards pointing out the contradiction:
   * *Example:* *"Your ruling rejects Guideline G-05, but G-05 is defined as a core guideline. Did you mean to flag G-05 for updating instead?"*
2. **Second Conflict (Round 2):** If the expert resubmits and the conflict persists, S5 displays a warning:
   * *Example:* *"The conflict with active guidelines persists. To proceed, please explicitly confirm this override and provide an override rationale."*
3. **Escalation:** If the conflict persists or an override is requested, mark the item `needs_adjudication` and park it. It may be written to an adjudication queue, but it must not enter trusted H3 memory until a supervisor records an explicit adjudication. The baseline continues unchanged.
