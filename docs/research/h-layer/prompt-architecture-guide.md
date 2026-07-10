# H-Layer Prompt Architecture Guide

This document defines the prompt requirements, context structures, step-by-step reasoning guidelines, negative constraints, and structured JSON schemas for each H-layer skill prompt. It serves as the engineering blueprint for prompt implementation while strictly complying with supervisor directive **D11** (no final prompt text).

---

## 1. Skill S2: Dosage Triage Prompt

* **Role:** Analyzes incoming run events to determine whether they trigger a human expert review task.
* **Objective:** Minimize expert workload by filtering high-certainty and low-severity warnings.

### Context Inputs (Variables)
* `setting`: Active VEGO-AI pipeline mode (`cd_ch`, `cd_pw`, etc.).
* `event_type`: The hook event code (`E5_compliance_vector`, `E6_inspector_uncertainty`, etc.).
* `uncertainty`: Numeric value (0 or 1) indicating baseline model uncertainty.
* `detail_payload`: Text description of the warning context.
* `active_templates`: The baseline design templates under evaluation.

### Step-by-Step Reasoning Instructions
1. Inspect the `detail_payload` for indicators of structural syntax changes (e.g. brace templates, guideline deletions).
2. Compare the payload with `active_templates` to check if a known format is violated.
3. Assess the severity level:
   * **Level 3 (Review):** Hard compliance violations or core template changes.
   * **Level 2 (Review):** Low certainty anomalies.
   * **Level 1 (Pass):** Redundant notifications or informational logs.
4. Output the triage decision and severity.

### JSON Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "S2TriageResponse",
  "type": "object",
  "properties": {
    "triage_ruling": {
      "type": "string",
      "enum": ["Review", "Pass"]
    },
    "assigned_severity": {
      "type": "integer",
      "minimum": 0,
      "maximum": 3
    },
    "rationale": {
      "type": "string",
      "description": "Justification for the triage ruling and severity score."
    }
  },
  "required": ["triage_ruling", "assigned_severity", "rationale"]
}
```

---

## 2. Skill S4: Blind-Elicitation Prompt

* **Role:** Queries the human expert for rulings without introducing confirmation bias.
* **Objective:** Present cases cleanly, hiding model labels and confidence flags.

### Context Inputs (Variables)
* `subject_key`: Bundled review item key (`case_XXXXX`, `pattern_XXXXX`).
* `alerts`: List of raw alert details grouped under this subject.
* `domain_specification`: Natural language descriptions of target guideline rules.

### Step-by-Step Reasoning Instructions
1. Strip all confidence flags, model scores, and baseline predictions from the input variables.
2. Group related warnings to construct a unified problem description.
3. Formulate the elicitation text in objective, domain-expert terms (e.g., "Review the template constructs below for compliance").
4. Provide structured multiple-choice options (e.g. "Approve", "Reject") to simplify human response input.

### JSON Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "S4ElicitationResponse",
  "type": "object",
  "properties": {
    "human_prompt_text": {
      "type": "string",
      "description": "The exact wording to present to the human reviewer in the interface."
    },
    "required_options": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Rulings available for the user to select."
    }
  },
  "required": ["human_prompt_text", "required_options"]
}
```

---

## 3. Skill S5: H-Verify Prompt (Dialogue Verification)

* **Role:** Analyzes the human reviewer's feedback to catch sycophancy, syntax mistakes, or contradictions.
* **Objective:** Ensure human feedback is safe and structurally sound before persistent logging.

### Context Inputs (Variables)
* `expert_ruling`: The user's input decision (`Approve` or `Reject`).
* `expert_rationale`: Text description justifying the decision.
* `proposed_details`: Proposed template edits or guideline modifications.
* `active_guidelines`: Reference database rules.
* `reference_templates`: Baseline templates.

### Step-by-Step Reasoning Instructions
1. **Rule-1 Check (Core Guidelines):** Match `expert_ruling` against `active_guidelines`. If the ruling rejects a guideline with mapping certainty $\le 0.7$, trigger a warning.
2. **Rule-2 Check (Template Braces):** Inspect `proposed_details`. If braces `{` or `}` are mismatched or incomplete, trigger a syntax warning.
3. **Semantic Check (Sycophancy/Mismatch):** If the decision is `Approve` but `expert_rationale` contains negative descriptors ("violates", "broken", "incorrect"), flag a mismatch.

### JSON Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "S5VerifyResponse",
  "type": "object",
  "properties": {
    "verification_status": {
      "type": "string",
      "enum": ["Pass", "Fail"]
    },
    "triggered_rule": {
      "type": "string",
      "enum": ["Rule-1", "Rule-2", "Semantic-Mismatch", "None"]
    },
    "warning_card": {
      "type": "string",
      "description": "User-facing message explaining the conflict, or null if Pass.",
      "nullable": true
    }
  },
  "required": ["verification_status", "triggered_rule", "warning_card"]
}
```

---

## 4. Skill S7: Generalization Synthesis Prompt

* **Role:** Synthesizes isolated feedback tuples into clean, abstract instructions.
* **Objective:** Convert retrieval-cached logs into generalized prompt guidelines.

### Context Inputs (Variables)
* `raw_feedback_records`: List of tuples containing settings, rulings, and expert rationales.
* `target_pattern`: The unseen pattern signature under evaluation.

### Step-by-Step Reasoning Instructions
1. Group feedback records by common target patterns and settings.
2. Analyze the rationales for repetitive logic, keywords, or domain rules.
3. Abstract the concrete rulings into generic domain guidelines (e.g. "Do not apply construct X when context Y is present").
4. Output the synthesized rule array and define its applicability boundary.

### JSON Response Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "S7GeneralizationResponse",
  "type": "object",
  "properties": {
    "synthesized_rules": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Consolidated general rules derived from raw feedback."
    },
    "applicability_scope": {
      "type": "string",
      "description": "Scope constraints defining where the synthesized rules apply."
    }
  },
  "required": ["synthesized_rules", "applicability_scope"]
}
```
