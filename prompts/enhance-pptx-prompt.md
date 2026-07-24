# Comprehensive Prompt: Enhance VEGO-AI Thesis Presentation

Copy everything below this line and paste it into a new Claude session with the `vego-ai` folder connected.

---

## Context

I have an MSc thesis titled **"Reusable Human Judgment in AI-Assisted Domain Model Assessment: The VEGO-AI Case"** and an existing 23-slide PPTX at `VEGO-AI-Thesis-Progress.pptx` in my connected folder. The current deck uses a dark bento-box aesthetic with neon purple accents — keep and enhance that visual style.

Read the existing PPTX first using `extract-text` to understand what's already there, then read these thesis chapters for deep content:
- `thesis/chapters/05-human-ai-co-reasoning-artifact.md` (full artifact design)
- `thesis/chapters/06-evaluation-methodology.md` (methodology + metrics)
- `thesis/chapters/07-experimental-results.md` (current evidence + experiment results)
- `thesis/chapters/appendix-a-supplementary.md` (policy table, schemas, annotation sheet)
- `thesis/chapters/02-background-and-related-work.md` (literature positioning)
- `thesis/chapters/03-problem-and-research-questions.md` (RQs and sub-questions)
- `thesis/outline.md` (evidence map, gates, milestone story, contribution chain)

## What I Need

Enhance the presentation by **adding 12–15 new slides** with professional research visualizations. Keep all 23 existing slides and insert the new ones in logical positions. The final deck should be 35–38 slides — a comprehensive thesis defense presentation.

### Required New Slides

#### 1. Research Methodology Overview Slide
- Design-Science Research framework visualization (Hevner et al. 2004, Peffers et al. 2007)
- Show the DSR cycle: Problem Identification → Objectives → Design & Development → Demonstration → Evaluation → Communication
- Map each DSR phase to specific thesis chapters and milestones
- Bento grid with each phase as a frosted glass card

#### 2. Literature Positioning Map
- Visual taxonomy of where this work sits in the literature landscape
- Four research streams as bento panels: Human-in/on-the-loop AI, Explainable AI (XAI), AI-Assisted Modeling, Human–AI Co-Reasoning
- Show the gap this thesis fills at the intersection
- Include key authors/papers for each stream (from Chapter 2)

#### 3. Detailed Data Flow Diagram (Full Pipeline)
- End-to-end flow from Student Model Input → Agent 1 → Agent 2 → Agent 3 → Agent 4 → M1 → Expert → M2 → M3 → M4A → M4B-1 → Output
- Show data artifacts produced at each stage (files, schemas, counts)
- Use connected flow with labeled arrows showing data types passed between components
- Color-code: baseline components (gray/blue), artifact extensions (purple/neon)

#### 4. Schema Dependency Chain Diagram
- Six JSON schemas as connected nodes showing how they validate data at each layer
- Show const-enforced fields (`ai_classification_changed = false`, `ai_behavior_changed_in_baseline = false`, `mode = "experimental"`)
- Highlight that non-destruction is machine-verified, not convention
- Reference Appendix A.2 schema table for field details

#### 5. Evaluation Conditions Matrix (C0–C4B)
- Professional research matrix showing all 6 conditions:
  - C0: Original VEGO-AI (baseline)
  - C1: Review Queue (M1)
  - C2: Structured Feedback (M2)
  - C3: Reusable Memory (M3)
  - C4A: Advisory Layer (M4A)
  - C4B: Memory-Informed Comparison (M4B-1)
- For each condition show: what changes, primary evidence, current status (✓ mechanism verified / ⏳ awaiting labels)
- Layer progression should be visually clear (each condition adds to the previous)

#### 6. Metrics Framework Slide
- Two-tier metrics visualization:
  - **Tier 1 — Primary (empirical effect):** Accuracy, Macro-F1 (against expert gold labels, generalization-safe rows only)
  - **Tier 2 — Secondary (mechanism validity):** Organized by condition:
    - C1 Targeting: queue count, targeting rate (40.7%), trigger distribution, coverage
    - C2 Capture: schema validity rate, rationale completeness, signature-mismatch rate
    - C3/C4A Retrieval: match count, advice-strength distribution, conflict rate
    - C4B Comparison: differs count, paired correctness table, McNemar test, escalation precision/recall
    - Reliability: Cohen's κ, adjudication rate
- Show which metrics are currently measurable vs. blocked on labels

#### 7. Current Evidence Dashboard (Detailed)
- Professional research dashboard showing ALL quantitative evidence currently available:
  - 179 student models across 2 domains × 2 diagram types
  - 27 recurring variability patterns (9 Substantial, 18 Occasional)
  - M1: 11/27 flagged (40.7% targeting rate), trigger distribution breakdown
  - M2: 4 feedback entries, 100% schema valid, 0 signature mismatches
  - M3: 3 memory entries with provenance chains
  - M4A: 8 advisory items, advice strength distribution (none/weak/moderate)
  - M4B-1: 27 comparison rows, 0 differ, 2 review-after-memory flags
  - 94 passing tests, 18/18 evidence-consistency invariants
  - 0/24 expert labels (blocked gate)
- Use large stat callouts with supporting detail

#### 8. Blind Annotation Protocol Sequence Diagram
- Detailed UML-style sequence showing the annotation workflow:
  - Researcher prepares blind sheets (strips AI fields)
  - Randomizes row order (different per reviewer)
  - Assigns anonymous IDs
  - Reviewer 1 labels independently
  - Reviewer 2 labels independently
  - Cohen's κ computed
  - Adjudication for disagreements (third reviewer if needed)
  - Gold labels frozen
  - Single evaluation run executed
- Show what's anonymized vs. visible to reviewers
- Reference the blind annotation sheet columns from Appendix A.3

#### 9. Leakage Control & Evidence Gate Flow
- Visualization of the leakage discipline:
  - Per-row `evaluation_leakage_status` tags: `no_memory_used`, `cross_pattern_memory_used`, `same_pattern_memory_used`
  - Show how same-pattern rows are isolated from generalization-safe metrics
  - 24 generalization-safe candidates vs. 3 mechanism-only rows
- Evidence gate flow:
  - 0 labels → Not evaluable (current state, highlighted)
  - 1–19 labels → Qualitative/pilot only
  - ≥20 labels → Quantitative allowed
  - + Reviewer-2/adjudication → Reliability strengthened
- Connect gates to what claims are permitted at each level

#### 10. EXP-001 through EXP-006 Experiment Registry
- One comprehensive slide showing all 6 experiments in a research-grade format:
  - EXP-001: Mechanism & Readiness (COMPLETE) — 27 rows, full coverage, 0 differ
  - EXP-002: Annotation Readiness (COMPLETE) — blind sheets prepared, leakage controls ready
  - EXP-003: Accuracy Evaluation (BLOCKED) — harness built, awaiting labels
  - EXP-004: Policy-Risk Screening (COMPLETE) — synthetic-only, Δ=0.00pp under conservative policy
  - EXP-005: Real-Label Gate (BLOCKED) — 0/24 labels, gate closed
  - EXP-006: Leakage Audit (COMPLETE) — per-row tags verified
- For each: hypothesis, method, key result, status badge

#### 11. Policy Sensitivity Analysis Slide (EXP-004)
- Visualization of EXP-004 synthetic policy-screening results
- Show the policy table from Appendix A.1 (7 rows mapping advice strength × agreement × conflict → outcome)
- Illustrate how conservative policy changes 0/27 classifications
- Show hypothetical aggressive policies: potential gains AND potential losses
- Clear callout: "Synthetic only — not empirical evidence"

#### 12. Contribution to Knowledge Slide
- Map contributions to Design-Science knowledge types (Gregor & Hevner 2013):
  - Level 1: Situated Implementation (the VEGO-AI artifact)
  - Level 2: Nascent Design Theory (five design principles + evidence)
- Three concrete contributions:
  1. Artifact: M1–M4B-1 co-reasoning layer (mechanism demonstrated)
  2. Methodology: Bias-controlled annotation protocol with leakage discipline
  3. Framework: Five design principles for reusable human judgment in AI assessment
- Connect each contribution to specific RQs and evidence

#### 13. Threats to Validity Summary
- Four categories as bento panels:
  - Internal: same-pattern leakage, synthetic EXP-004 gains, single-reviewer labels, small sample (27 patterns)
  - External: single domain (UML modeling), two domains only (Cheers, ParkWise), single AI pipeline (VEGO-AI)
  - Construct: subjective substantial/occasional distinction, expert disagreement
  - Reliability: LLM non-determinism (mitigated by deterministic M4B-1), data sensitivity
- For each threat show the mitigation strategy implemented

#### 14. PhD Continuation Roadmap
- Future milestones M4B-2 through M6 as a timeline/roadmap:
  - M4B-2: Optional LLM-assisted reclassification (deferred)
  - M5: Human-approved guideline refinement
  - M6: Broader evaluation across additional domains and models
- Show the MSc → PhD transition boundary clearly
- Current MSc scope boxed vs. future PhD scope

#### 15. Key References & Theoretical Foundations
- Visual display of the core theoretical foundations:
  - Hevner et al. 2004 — Design Science in IS Research
  - Peffers et al. 2007 — Design Science Research Methodology
  - Gregor & Hevner 2013 — Positioning Design Science Research
  - Shneiderman 2020 — Human-Centered AI
  - Dellermann et al. 2019 — Hybrid Intelligence
  - Mosqueira-Rey et al. 2023 — Human-in-the-Loop ML taxonomy
  - Batool et al. 2024 — VEGO-AI original
- Show how each reference anchors a specific design decision

## Visual Design Requirements

**Maintain and enhance the current aesthetic:**
- Deep dark background (#0A0A12)
- Translucent frosted glass panels with purple edge lighting (#9333EA borders)
- Neon purple accents (#A855F7, #C084FC)
- Bento box asymmetric grid layouts
- Subtle glow orbs in corners
- Neon badges for labels and status indicators

**For the new diagram slides specifically:**
- Use connected nodes with glowing neon arrows for flow diagrams
- Use numbered step indicators with colored circles for sequences
- Use alternating row shading for tables on dark backgrounds
- Use color-coded status badges: green (#10B981) = complete, red (#EF4444) = blocked, amber (#F59E0B) = next, blue (#3B82F6) = in progress
- Make sequence diagrams with vertical lifelines and horizontal message arrows
- Use large stat callouts (38pt+) for key numbers with small muted labels below

**Slide insertion positions (approximate):**
1. Research Methodology → after slide 3 (The Problem), before slide 4 (Baseline Pipeline)
2. Literature Positioning → after Research Methodology
3. Detailed Data Flow → after slide 6 (Co-Reasoning Artifact)
4. Schema Dependency → after Data Flow
5. Evaluation Conditions → after slide 10 (M4B-1 Policy Engine)
6. Metrics Framework → after Evaluation Conditions
7. Current Evidence Dashboard → after Metrics Framework
8. Blind Annotation Protocol → after slide 16 (Evaluation Methodology)
9. Leakage Control → after Blind Annotation
10. Experiment Registry → after slide 15 (Experiments Dashboard)
11. Policy Sensitivity → after Experiment Registry
12. Contribution to Knowledge → after slide 21 (Research Questions)
13. Threats to Validity → after Contribution to Knowledge
14. PhD Continuation → after slide 22 (Critical Path)
15. Key References → before slide 23 (Thank You)

## Critical Research Constraints (MUST follow)

1. **No accuracy claims.** Zero expert labels exist. Never state or imply that classification accuracy improved. The contribution is mechanism + methodology, not empirical accuracy.
2. **No fabricated data.** All numbers must come from the thesis chapters. Do not invent statistics, percentages, or results.
3. **Evidence boundary.** Always distinguish between "mechanism demonstrated" (supported) and "accuracy improvement" (not yet evaluable).
4. **Synthetic ≠ real.** EXP-004 results are synthetic policy screening, not empirical evidence. Always label as such.
5. **Same-pattern leakage.** The 3 memory labels are same-pattern — they prove mechanism only, not generalization.
6. **Non-destructive guarantee.** `ai_classification_changed = 0` across all runs. The baseline is never modified.
7. **Honest reporting.** The gap between mechanism readiness and empirical proof should be presented as a strength (precisely bounded), not a weakness.

## Build Instructions

Use PptxGenJS (Node.js). Read the existing `build.js` in the outputs folder to understand the current helper functions (`bentoPanel`, `neonBadge`, `slideBase`, color palette `C`). Extend that file — do not rewrite from scratch. Add the new slides using the same helper functions and aesthetic.

After building, do a full visual QA: convert to PDF → images → inspect with a subagent. Fix any overlaps, overflows, or contrast issues. Present the final PPTX.

## Exact Numbers for Reference (from thesis chapters)

| Metric | Value |
|--------|-------|
| Student models | 179 |
| Domains | 2 (Cheers, ParkWise) |
| Diagram types | 2 (use-case, class) |
| Settings | 4 (ucd_ch, ucd_pw, cd_ch, cd_pw) |
| Variability patterns | 27 (9 Substantial, 18 Occasional) |
| M1 review queue items | 11 |
| M1 targeting rate | 40.7% |
| M2 feedback entries | 4 |
| M2 schema validity | 100% |
| M2 signature mismatches | 0 |
| M3 memory entries | 3 |
| M3 promoted from M2 | 3 of 4 |
| M4A advisory items | 8 |
| M4A advice strengths | none to moderate |
| M4A ai_classification_changed | false (all) |
| M4B-1 comparison rows | 27 |
| M4B-1 classifications changed | 0 |
| M4B-1 review-after-memory flags | 2 |
| M4B-1 conflicting memory flags | 0 |
| Tests passing | 94 |
| Evidence-consistency invariants | 18/18 |
| Expert labels supplied | 0 |
| Generalization-safe candidates | 24 |
| Same-pattern mechanism rows | 3 |
| M4B-1 policy rows | 7 |
| Thesis chapters | 10 + appendix |
| References | 37 verified |
| Body word count | ~20,200+ |
| EXP-004 Δ accuracy (synthetic) | 0.00 pp |
| Evaluation conditions | 6 (C0–C4B) |
| Trigger reasons | requires_human_review, undetermined, low_confidence, guidelines_update |
| Running example pattern | "Customer as actor" (ucd_ch P6) |
| Running example AI classification | Occasional (confidence: Medium/0.72) |
| Running example expert override | Substantial ("domain interpretation, not error") |
| Running example M4B-1 policy row | moderate_disagreement_keep_original_require_review |
| Running example leakage status | same_pattern_memory_used |
| Baseline git tag | official-vego-ai-baseline (2eeccb1) |
| Policy version | memory-informed-classifier-v1 |

## Final Deliverable

A single PPTX file at `VEGO-AI-Thesis-Progress.pptx` with 35–38 slides total, visually consistent dark bento-box aesthetic throughout, all research metrics accurate, professional flow and sequence diagrams, and comprehensive coverage suitable for an MSc thesis defense presentation.
