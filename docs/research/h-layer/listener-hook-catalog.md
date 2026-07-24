# S1 Listener Hook Catalog

Status: **PROVISIONAL WORKING DRAFT.** M-03 and M-05 have not been recorded. The catalog maps candidate observation points; no live listener or protected-path change is approved.

This document proposes the event catalog E1-E15 and maps baseline actions across Agents 1-4 to real code symbols. E1-E14 are framework/lifecycle events. E15 is evaluation-only and must be routed out without framework action.

## Governance Boundary
All event observations must be passive, append-only, default-off, and fail-open. No listener may interrupt execution or alter prompts, state transitions, artifacts, classifications, or timeout policy. Live work remains offline-only until M-05 and a separate implementation authorization are recorded. See `allowed-touch-proposal.md`.

---

## 1. Event Registry & Payload Specifications

### E1: Language Template Created or Revised
* **Stage:** Early
* **Producer:** Agent 1 (Language Advisor)
* **Trigger Point:** After `phase1_build_language_template()` assigns `state.language_template`; a persisted phase-boundary artifact is written later by `run_setting()`.
* **Payload Schema:**
  ```json
  {
    "event_id": "E1_LT_CREATION",
    "timestamp": "ISO-8601",
    "case_id": "string",
    "template_version": "integer",
    "template_content": "string",
    "refinement_source_event_id": "string | null"
  }
  ```
* **Candidate Hook Point:** `VEGO-AI/framework/orchestrator.py::phase1_build_language_template`, observed at the phase boundary rather than inside an agent module.

### E2: Downstream Agent Requests Clarification (Q&A)
* **Stage:** Early-mid
* **Producer:** Agent 2 (Domain Advisor) or Agent 3 (Model Inspector)
* **Trigger Point:** Questions extracted from Agent 2/3/4 results before `_answer_lang_questions()` or `_answer_dom_questions()`; stable IDs are assigned by the registry.
* **Payload Schema:**
  ```json
  {
    "event_id": "E2_QA_REQUEST",
    "timestamp": "ISO-8601",
    "from_agent": "string (Agent2 | Agent3)",
    "to_agent": "string (Agent1 | Agent2)",
    "question_text": "string",
    "context_model_element": "string"
  }
  ```
* **Candidate Hook Point:** `VEGO-AI/framework/qa_registry.py::allocate_ids`, with orchestration context from `VEGO-AI/framework/orchestrator.py`.

### E3: Upstream Agent Answers Q&A
* **Stage:** Early-mid
* **Producer:** Agent 1 (Language Advisor) or Agent 2 (Domain Advisor)
* **Trigger Point:** Answers returned from `_answer_lang_questions()` or `_answer_dom_questions()` and passed to `QARegistry.record_answers()`.
* **Payload Schema:**
  ```json
  {
    "event_id": "E3_QA_ANSWER",
    "timestamp": "ISO-8601",
    "question_event_id": "string",
    "answer_text": "string",
    "requires_revision": "boolean"
  }
  ```
* **Candidate Hook Point:** `VEGO-AI/framework/qa_registry.py::record_answers`, with answer payloads produced by `VEGO-AI/framework/orchestrator.py::_answer_lang_questions` and `_answer_dom_questions`.

### E4: Domain Advisor Creates or Refines Reference Guidelines
* **Stage:** Early-mid
* **Producer:** Agent 2 (Domain Advisor)
* **Trigger Point:** After `phase2_build_reference_guidelines()` assigns `state.reference_guidelines`; later revisions occur in the Agent 4 feedback block of `phase4_variability_analysis()`.
* **Payload Schema:**
  ```json
  {
    "event_id": "E4_RG_CREATION",
    "timestamp": "ISO-8601",
    "guidelines_version": "integer",
    "guidelines_list": [
      {
        "guideline_id": "string",
        "content": "string",
        "severity": "integer"
      }
    ]
  }
  ```
* **Candidate Hook Point:** Phase boundaries in `VEGO-AI/framework/orchestrator.py`; do not instrument `agent2_domain_advisor.py` in phase one.

### E5: Model Inspector Applies Guidelines
* **Stage:** Mid
* **Producer:** Agent 3 (Model Inspector)
* **Trigger Point:** After `_phase3_one_case()` assigns `state.compliance_vectors[case_id]` and saves state.
* **Payload Schema:**
  ```json
  {
    "event_id": "E5_COMPLIANCE_EVAL",
    "timestamp": "ISO-8601",
    "model_id": "string",
    "element_id": "string",
    "applied_guideline_ids": ["string"],
    "is_compliant": "boolean",
    "rationale": "string"
  }
  ```
* **Candidate Hook Point:** `VEGO-AI/framework/orchestrator.py::_phase3_one_case`; do not instrument `agent3_model_inspector.py` in phase one.

### E6: Model Inspector Emits Uncertainty (Trigger)
* **Stage:** Mid
* **Producer:** Agent 3 (Model Inspector)
* **Trigger Point:** Candidate derivation from persisted compliance/uncovered-fragment fields after `_phase3_one_case()`. A direct, canonical uncertainty event is not currently emitted by the baseline.
* **Payload Schema:**
  ```json
  {
    "event_id": "E6_UNCERTAINTY_SIGNAL",
    "timestamp": "ISO-8601",
    "model_id": "string",
    "uncertain_element": "string",
    "signal_type": "string (requires_review | low_confidence | update_flag)",
    "confidence_score": "float",
    "reasoning": "string"
  }
  ```
* **Candidate Hook Point:** Offline reconstruction first; any future live observation is limited to the `orchestrator.py` phase boundary. The missing direct signal remains an instrumentation gap.

### E7: Variability Explorer Receives Artifacts
* **Stage:** Mid-late
* **Producer:** Agent 4 (Variability Explorer)
* **Trigger Point:** `phase4_variability_analysis()` immediately before the Agent 4 pattern-identification call receives compliance vectors, uncovered fragments, and reference guidelines.
* **Payload Schema:**
  ```json
  {
    "event_id": "E7_VE_INPUT_RECEIVED",
    "timestamp": "ISO-8601",
    "compliance_vectors": "array",
    "reference_guidelines_version": "integer"
  }
  ```
* **Candidate Hook Point:** `VEGO-AI/framework/orchestrator.py::phase4_variability_analysis`; do not instrument `agent4_variability_explorer.py`.

### E8: Agent 4 Classifies Variability
* **Stage:** Late
* **Producer:** Agent 4 (Variability Explorer)
* **Trigger Point:** After `phase4_variability_analysis()` assigns `state.variability_classifications` and saves state.
* **Payload Schema:**
  ```json
  {
    "event_id": "E8_VE_CLASSIFICATION",
    "timestamp": "ISO-8601",
    "classification_results": [
      {
        "element_id": "string",
        "class": "string (substantial | occasional | Undetermined)",
        "confidence": "float"
      }
    ]
  }
  ```
* **Candidate Hook Point:** `VEGO-AI/framework/orchestrator.py::phase4_variability_analysis`; observing E8 does not authorize changing Agent 4.

### E9: Q&A Reveals Template or Guideline Ambiguity
* **Stage:** Early-mid
* **Producer:** Q&A circle monitoring
* **Trigger Point:** Triage layer detecting repetitive QA loops.
* **Payload Schema:**
  ```json
  {
    "event_id": "E9_QA_AMBIGUITY",
    "timestamp": "ISO-8601",
    "topic_keywords": ["string"],
    "loop_count": "integer",
    "related_guideline_ids": ["string"]
  }
  ```
* **Hook Point:** Passive check in S2 triage over accumulated QA observations.

### E10: Human Feedback Received
* **Stage:** Any
* **Producer:** H2 Expert Interface (S4 Capture)
* **Trigger Point:** User saving resolved feedback.
* **Payload Schema:**
  ```json
  {
    "event_id": "E10_FEEDBACK_RECEIVED",
    "timestamp": "ISO-8601",
    "review_id": "string",
    "reviewer_id": "string",
    "decision": "string (approve | reject | revise)",
    "rationale": "string",
    "confidence": "float",
    "reusable": "boolean",
    "validity_scope": "string"
  }
  ```
* **Current Offline Source:** `VEGO-AI/framework/human_feedback_manager.py::attach_feedback` / `report_feedback`. A live H2 interface does not yet exist.

### E11: Feedback Conflicts with Source Evidence
* **Stage:** Any
* **Producer:** S5 H-Verify Check
* **Trigger Point:** Contradiction detected during verification.
* **Payload Schema:**
  ```json
  {
    "event_id": "E11_VERIFY_CONFLICT",
    "timestamp": "ISO-8601",
    "feedback_event_id": "string",
    "conflicting_source": "string (template | guidelines | description | memory)",
    "conflict_details": "string"
  }
  ```
* **Future Source:** Proposed S5 verification module. No live S5 module exists.

### E12: Verified or Adjudicated Feedback Stored
* **Stage:** Any
* **Producer:** H3 Memory (S7 Learn)
* **Trigger Point:** Ingestion of S5-verified or explicitly supervisor-adjudicated feedback.
* **Payload Schema:**
  ```json
  {
    "event_id": "E12_FEEDBACK_STORED",
    "timestamp": "ISO-8601",
    "feedback_id": "string",
    "memory_id": "string"
  }
  ```
* **Current Offline Source:** `VEGO-AI/framework/human_judgment_memory.py::build_memory_item` and `write_memory`. Only verified or supervisor-adjudicated records may be eligible in the future design.

### E13: Prior Feedback Retrieved
* **Stage:** Any
* **Producer:** H3 Retrieval Engine
* **Trigger Point:** Matching stored memory for active run.
* **Payload Schema:**
  ```json
  {
    "event_id": "E13_MEMORY_RETRIEVED",
    "timestamp": "ISO-8601",
    "context_element_id": "string",
    "matched_memory_id": "string",
    "match_reason": "string"
  }
  ```
* **Current Offline Source:** `VEGO-AI/framework/memory_advisor.py::build_advice_items`. Existing advisory behavior is evaluation history, not an H-layer auto-application path.

### E14: Knowledge Correction Proposed
* **Stage:** Any
* **Producer:** S6 Integration
* **Trigger Point:** Proposing artifact correction.
* **Payload Schema:**
  ```json
  {
    "event_id": "E14_CORRECTION_PROPOSED",
    "timestamp": "ISO-8601",
    "target_agent": "string",
    "target_artifact": "string (template | guidelines)",
    "proposed_change": "string",
    "supporting_memory_id": "string"
  }
  ```
* **Future Source:** Proposed S6 module. E14 is a reviewable correction proposal only; no live integration module exists.

### E15: Evaluation Event Routed Out
* **Stage:** Evaluation-only
* **Producer:** Parked evaluation track
* **Trigger Point:** A comparison, label, or evaluation result is available for evaluation bookkeeping.
* **Payload Schema:** Uses the relevant evaluation artifact and provenance manifest; it is not a framework correction event.
* **Routing Rule:** Record or route to the parked evaluation track only. E15 must never create a framework action, trusted-memory write, or correction proposal.

---

## 2. Baseline Instrumentation Gaps & Hook Requirements

The current baseline does not natively log or preserve certain early-stage communication events. The following are design gaps, not authorized changes:

1. **Q&A capture:** E2/E3 can be observed at `QARegistry.allocate_ids` and `record_answers`; answer/context completeness must be tested before claiming full capture.
2. **Template revision lineage:** The orchestrator phase boundary exposes final state, but intermediate revision lineage remains incomplete.
3. **Uncertainty semantics:** Direct E6 and recurring-ambiguity E9 signals are not native baseline events and must remain `reconstructed` or `unobservable` until supported.
4. **Allowed touch:** Any live implementation is restricted to the provisional proposal in `allowed-touch-proposal.md` and still requires M-05 plus a separate authorization.
