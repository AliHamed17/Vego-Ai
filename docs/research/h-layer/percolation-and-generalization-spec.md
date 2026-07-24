# S7 Percolation and Generalization Specification

Status: **PROVISIONAL WORKING DRAFT.** M-02, M-04, and M-05 have not been recorded. This document proposes trusted-memory rules; it does not authorize automatic memory reuse, generalization, or correction.

This document proposes the storage schema, retrieval keys, conflict resolution policies, and scope rules for H-Layer Skill S7 (Percolate / Learn).

---

## 1. Storage and Retrieval Indexing

Only S5-verified or explicitly supervisor-adjudicated judgments are eligible for append-only trusted storage. Timeout, rejection, unresolved conflict, and missing approval remain parked outside trusted memory. To support explainable, non-embedding-based retrieval, the working draft proposes five discrete categorical keys:
1. **`domain_id`:** The model domain (e.g., `cheers`, `parkwise`).
2. **`diagram_type`:** The modeling syntax (e.g., `class_diagram`, `use_case_diagram`).
3. **`guideline_id`:** The specific guideline number (e.g., `cd_ch-P1`).
4. **`pattern_signature`:** The stable structural pattern signature hash.
5. **`keywords`:** Tokenized keywords extracted from the model element label and rationale.

### Retrieval Matching Order
When advising downstream agents, memory is fetched using strict hierarchical fallback:
* **Match-1 (Exact):** `guideline_id` + `pattern_signature` matches (highest confidence).
* **Match-2 (Pattern-wide):** `guideline_id` matches + keyword overlap in similar patterns.
* **Match-3 (Domain-wide):** `domain_id` + `diagram_type` matches.

---

## 2. Conflict Adjudication Policy

When a new expert feedback record $F_{\text{new}}$ is processed for a context that matches a previously stored memory $M_{\text{old}}$, S7 checks for conflicts:

* **Conflict Definition:** A conflict exists if:
  $$\text{Match}(F_{\text{new}}, M_{\text{old}}) \quad \text{AND} \quad F_{\text{new}}.\text{decision} \neq M_{\text{old}}.\text{decision}$$
* **Conflict Flagging:** S7 does not overwrite $M_{\text{old}}$ and does not append unresolved $F_{\text{new}}$ to trusted memory. It writes the conflict to a separate adjudication queue with `conflict_status = "active_disagreement"` and `conflicting_memory_id`.
* **Adjudication Flow:** S7 marks matching retrievals `conflict_warning_unresolved` and asks S2/S3 to route a priority review item for supervisor adjudication. Only the recorded adjudication result may later enter trusted memory.

---

## 3. Generalization Scope Transitions

The expert defines the boundary of reuse by selecting the `validity_scope` during elicitation (S4). S7 enforces retrieval limits based on this scope:

```text
+-------------------------------------------------------------+
| General (Global framework scope, e.g. language syntax)      |
|  +-------------------------------------------------------+  |
|  | Domain-Specific (e.g. all Cheers models)             |  |
|  |  +-------------------------------------------------+  |  |
|  |  | Pattern-Specific (e.g. all ucd_ch-P2 patterns)  |  |  |
|  |  |  +-------------------------------------------+  |  |  |
|  |  |  | Case-Specific (No reuse; audit only)      |  |  |  |
|  |  |  +-------------------------------------------+  |  |  |
|  |  +-------------------------------------------------+  |  |
|  +-------------------------------------------------------+  |
+-------------------------------------------------------------+
```

1. **Case-Specific:** `reusable = false`. No retrieval is allowed. The feedback is used only to grade or resolve the active model case.
2. **Pattern-Specific:** Retrieval is limited to cases where the structural pattern signature matches exactly.
3. **Domain-Specific:** A candidate retrieval may be surfaced across different models within the same domain, subject to approval and leakage labeling.
4. **General:** A candidate may be surfaced across diagram types or domains only after explicit scope approval. No candidate is applied automatically.

---

## 4. Evaluation Leakage Prevention (Thesis Integrity)

To preserve the validity of generalization claims in the thesis:
* **The Leakage Threat:** If the framework uses human feedback from a specific setting (e.g., Cheers Class Diagrams) to resolve errors in that same setting, this is a *same-pattern mechanism check*, not a proof of generalization.
* **Leakage Tagging Proposal:** A future authorized S7 implementation would compute and tag every retrieval:
  ```json
  {
    "evaluation_leakage_status": {
      "is_leakage": "boolean (true if domain_id of memory == domain_id of current run)",
      "leakage_type": "same_pattern | same_domain | cross_domain"
    }
  }
  ```
* **Evaluation Filter:** EXP-012 now reads the validated EXP-005 export, requires an explicit safe-candidate indicator and allowlisted leakage state, excludes blank/unknown provenance, and cross-checks the canonical EXP-003 evaluator. The current validated-safe count is 0, so M-D remains `NOT YET COMPUTABLE`. Same-pattern records remain excluded from the main story.
