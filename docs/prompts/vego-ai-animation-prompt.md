# VEGO-AI Pipeline Animation — Complete Prompt for Claude

> **Purpose:** Give this entire prompt to Claude (in a fresh session with canvas/artifact capabilities) to produce a fully animated, interactive HTML visualization of the VEGO-AI four-agent pipeline and Human–AI Co-Reasoning Artifact. The animation traces the "Customer as actor" running example through every stage with real thesis data.

---

## 1. WHAT TO BUILD

Build a single self-contained HTML file (no external dependencies except CDN fonts) that renders:

1. **A cinematic, step-by-step animation** of data flowing through the VEGO-AI pipeline — from raw inputs through 4 AI agents, into the 5-layer Human–AI Co-Reasoning Artifact (M1 → Expert → M2 → M3 → M4A → M4B-1), and ending at the Evidence Gate.
2. **Interactive controls**: Play / Pause / Step Forward / Step Back / Reset / Speed slider (0.5×, 1×, 2×).
3. **A live data panel** that shows the actual JSON payload at each stage (real thesis data, not placeholders).
4. **A flow log** that accumulates a timeline of completed steps.
5. The animation must be **beautiful, polished, and thesis-presentation-quality** — dark theme, glowing edges, smooth transitions, particle trails along data paths.

---

## 2. VISUAL DESIGN SPECIFICATION

### 2.1 Color Palette (dark bento / frosted glass aesthetic)

```
Background:        #0A0A12 (near-black indigo)
Panel surface:     #14141F (dark panel)
Glass overlay:     #1A1A2F (frosted glass)
Glass border:      rgba(147, 51, 234, 0.45) (purple edge)
Neon primary:      #A855F7 (purple)
Neon secondary:    #C084FC (lighter purple)
Neon glow:         #9333EA (saturated purple, for glows/shadows)
Text primary:      #F6F3FF (near-white lavender)
Text secondary:    #D8D3EA (muted lavender)
Text tertiary:     #9A93B4 (faint)
Text dim:          #6E6786 (very faint)
```

### 2.2 Agent Colors

```
Agent 1 (Language Advisor):    #3B82F6 (blue)     — bg: #1e3a5f
Agent 2 (Domain Advisor):      #10B981 (green)    — bg: #134e3a
Agent 3 (Model Inspector):     #A855F7 (purple)   — bg: #2e1065
Agent 4 (Variability Explorer):#F59E0B (amber)    — bg: #451a03
```

### 2.3 Artifact Colors

```
M1 (Review Queue):     #06B6D4 (cyan)     — bg: #164e63
M2 (Feedback):         #10B981 (green)    — bg: #134e3a
M3 (Memory Store):     #818CF8 (indigo)   — bg: #312e81
M4A (Advisory):        #3B82F6 (blue)     — bg: #1e3a5f
M4B-1 (Comparison):    #F59E0B (amber)    — bg: #451a03
Human Expert:          #C084FC (light purple) — bg: #4c1d95
Evidence Gate:         #EF4444 (red)      — bg: #3b1029
```

### 2.4 Typography

```
Font:       'Inter', system-ui, sans-serif  (import from Google Fonts CDN)
Monospace:  'JetBrains Mono', 'Fira Code', monospace  (for JSON data)
```

### 2.5 Visual Effects

- **Glowing edges**: Each active node pulses with a `box-shadow: 0 0 20px <agent-color>40` glow when data is flowing through it.
- **Particle trails**: When data moves between nodes, render 3–5 small luminous dots traveling along the connection path (use CSS animations or canvas).
- **Frosted glass panels**: All panels use `backdrop-filter: blur(12px)` with semi-transparent backgrounds.
- **Node pulse animation**: Active nodes scale up 1.03× and pulse their border brightness.
- **Data cascade**: When the JSON data panel updates, new fields should "typewriter" in character by character (or fade-slide in line by line).
- **Connection lines**: SVG paths between nodes, default color `rgba(147, 51, 234, 0.2)`, glow to full neon purple `#A855F7` when data is traversing them.
- **Step counter badge**: Floating pill badge "Step 3/14" with gradient background.

---

## 3. ARCHITECTURE LAYOUT

Arrange the nodes in a top-to-bottom flow with the following spatial groups. Use CSS Grid or absolute positioning. The layout should feel like a blueprint/schematic.

```
ROW 1 — INPUTS (left-aligned cluster)
  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
  │ Language Manual  │  │ Domain          │  │ Case Models     │
  │ + Definition     │  │ Description     │  │ (179 students)  │
  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
           │                    │                     │
ROW 2 — BASELINE AGENTS (horizontal band, connected)
  ┌────────▼────────┐  ┌───────▼─────────┐
  │  ① Agent 1      │  │  ② Agent 2      │
  │  Language Advisor│  │  Domain Advisor  │
  └────────┬────────┘  └───────┬─────────┘
           │         Q&A ↕     │
           └──────┐  ┌────────┘
                  ▼  ▼
           ┌──────────────┐
           │  ③ Agent 3    │
           │ Model Inspector│
           └──────┬───────┘
                  │
                  ▼
           ┌──────────────┐
           │  ④ Agent 4    │      ← guideline-update loop back to Agent 2
           │ Variability   │
           │ Explorer      │
           └──────┬───────┘
                  │
═══════════════════════════════════════════════════
   ▼  HUMAN–AI CO-REASONING ARTIFACT (thesis)  ▼
═══════════════════════════════════════════════════
                  │
ROW 3 — ARTIFACT CHAIN
  ┌───────▼───────┐  ┌──────────────┐  ┌──────────────┐
  │  M1 Review    │→ │ 👤 Human     │→ │  M2 Feedback │
  │  Queue        │  │ Expert       │  │              │
  └───────────────┘  └──────────────┘  └──────┬───────┘
                                              │
                     ┌──────────────┐  ┌──────▼───────┐
                     │  M4A Advisory│← │  M3 Memory   │
                     │  Layer       │  │  Store       │
                     └──────┬───────┘  └──────────────┘
                            │
                     ┌──────▼───────┐
                     │  M4B-1       │
                     │  Comparison  │
                     └──────┬───────┘
                            │
ROW 4 — EVIDENCE GATE
  ┌─────────────────────────▼─────────────────────────────┐
  │  🔒 Evidence Gate — 0/24 expert labels — CLOSED       │
  └───────────────────────────────────────────────────────┘
```

Draw SVG arrow paths between nodes. Use curved bezier paths, not straight lines. Each path should have a small arrowhead at the destination end.

---

## 4. ANIMATION SEQUENCE (14 STEPS)

Each step highlights the active node(s), animates particles along the incoming connection, updates the data panel with real JSON, and appends to the flow log. Pause ~2.5 seconds between steps at 1× speed.

### Step 1: Language Manual → Agent 1
**Active node:** Language Manual (lights up) → Agent 1 (lights up)
**Narration:** "Agent 1 receives the UML Use-Case Diagram specification"
**Data panel:**
```json
{
  "agent": "Agent 1 — Language Advisor",
  "input": "UML 2.x Use-Case Diagram specification",
  "task": "Build Language Template",
  "output_preview": "Enumerating: Actor, UseCase, Association, SystemBoundary, Include, Extend..."
}
```

### Step 2: Agent 1 produces Language Template
**Active node:** Agent 1 (pulses)
**Narration:** "Agent 1 produces the Language Template — a fixed enumeration of valid UML constructs"
**Data panel:**
```json
{
  "artifact": "#1 — Language Template",
  "constructs": ["Actor", "UseCase", "Association", "SystemBoundary", "Include", "Extend", "Generalization"],
  "language": "UML Use-Case Diagram",
  "runs": "Once per language-diagram-type pair",
  "consumed_by": ["Agent 2", "Agent 3"]
}
```

### Step 3: Domain Description → Agent 2
**Active node:** Domain Description → Agent 2
**Narration:** "Domain Description loaded: Cheers cinema-booking system"
**Data panel:**
```json
{
  "agent": "Agent 2 — Domain Advisor",
  "domain": "Cheers — cinema chain booking system",
  "input": "Natural-language specification describing business rules, entities, and relationships",
  "domain_excerpt": "Cheers is a cinema chain. Customers can book tickets, browse the catalog, order food and beverages..."
}
```

### Step 4: Agent 2 builds Reference Guidelines
**Active node:** Agent 2 (pulses, shows evolving output)
**Narration:** "Agent 2 builds evolving Reference Guidelines with mapping certainty scores"
**Data panel:**
```json
{
  "artifact": "#2 — Reference Guidelines",
  "sample_guideline": {
    "element": "Customer actor",
    "description": "Customer who interacts with cinema system",
    "mapping_certainty": 0.85,
    "valid_alternatives": ["Single 'Customer' actor", "Split into 'Registered' and 'Walk-In'"],
    "note": "Both representations are valid design choices"
  },
  "total_guidelines": 14
}
```

### Step 5: Case Models → Agent 3
**Active node:** Case Models → Agent 3 (particles showing many models flowing in)
**Narration:** "179 student models loaded — Agent 3 inspects each one against the Reference Guidelines"
**Data panel:**
```json
{
  "agent": "Agent 3 — Model Inspector",
  "setting": "ucd_ch (Use-Case Diagram, Cheers)",
  "models_to_inspect": 179,
  "inputs": ["Language Template (from Agent 1)", "Reference Guidelines (from Agent 2)", "Student models"],
  "task": "Per-model compliance scoring",
  "focus": "5 models show 'Customer' as a direct actor"
}
```

### Step 6: Agent 3 scores models
**Active node:** Agent 3 (pulses with results flowing out)
**Narration:** "Agent 3 produces per-guideline compliance vectors and flags recurring deviations"
**Data panel:**
```json
{
  "artifact": "#3 — Identified Variability",
  "example_model": "Model #34",
  "compliance_vector": {
    "Customer_actor": "Alternative",
    "Booking_usecase": "Satisfied",
    "Payment_usecase": "Partially-Satisfied"
  },
  "recurring_deviation": "'Customer' as actor — seen in models 12, 34, 67, 89, 112",
  "severity": "Medium"
}
```

### Step 7: Agent 4 classifies patterns (THE KEY MOMENT)
**Active node:** Agent 4 (large pulse, glowing amber)
**Narration:** "Agent 4 aggregates into Pattern P6: 'Customer as actor' — classifies as OCCASIONAL (error)"
**Data panel — highlight this as the critical decision:**
```json
{
  "agent": "Agent 4 — Variability Explorer",
  "pattern_id": "P6",
  "setting": "ucd_ch",
  "description": "Customer modeled as actor by 5 students",
  "classification": "Occasional Variability ⚠️",
  "confidence": 0.72,
  "justification": "Consistent representation suggests error, not valid alternative",
  "requires_human_review": false,
  "flag_for_guidelines_update": false,
  "LATENT_HOOKS": "⚡ These fields exist but are NEVER ACTED UPON in baseline"
}
```
**Visual note:** Flash "LATENT HOOKS — unused in baseline!" badge near Agent 4.

### Step 8: M1 — Selective Review Queue (ARTIFACT BEGINS)
**Active node:** Agent 4 → M1 (cross the separator line with dramatic particle burst)
**Narration:** "M1 flags P6 — medium confidence triggers selective review despite requires_human_review=false"
**Data panel:**
```json
{
  "layer": "M1 — Selective Review Queue",
  "action": "COMPLETING the latent hook Agent 4 left behind",
  "pattern_id": "P6",
  "review_id": "HRQ-ucd_ch-P6",
  "trigger": "medium_confidence (0.72 < threshold)",
  "review_signature": "sha256(ucd_ch + P6 + Occasional + justification_hash)",
  "queue_status": "11 of 27 patterns flagged (40.7% reduction)",
  "SQ1": "Where is human judgment needed? → HERE"
}
```
**Visual:** The separator line between baseline and artifact should glow and pulse as data crosses it.

### Step 9: Human Expert reviews and DISAGREES
**Active node:** M1 → Human Expert (special treatment — human icon glows purple)
**Narration:** "Expert reviews P6 and DISAGREES with the AI — 'Customer as actor is a valid design choice, not an error'"
**Data panel:**
```json
{
  "reviewer": "Domain Expert",
  "pattern": "P6 — Customer as actor",
  "ai_said": "Occasional Variability (error)",
  "expert_says": "Substantial Variability (valid alternative) ✓",
  "decision": "valid_alternative",
  "rationale": "Modeling 'Customer' as an actor who places orders is a legitimate alternative interpretation, not a modeling error. The 5 students made the same valid design choice, not the same mistake.",
  "DISAGREEMENT": "🔴 AI was WRONG — expert overrides"
}
```
**Visual:** Flash a red-to-green transition on the classification badge. Show "AI: Occasional ✗" crossing out and "Expert: Substantial ✓" appearing.

### Step 10: M2 — Structured Feedback captured
**Active node:** Human Expert → M2
**Narration:** "M2 captures structured feedback, validates against schema, verifies review signature"
**Data panel:**
```json
{
  "layer": "M2 — Structured Feedback",
  "feedback_id": "HFB-ucd_ch-P6",
  "review_id": "HRQ-ucd_ch-P6",
  "decision": "valid_alternative",
  "rationale": "Legitimate alternative interpretation, not error",
  "schema_valid": true,
  "signature_match": true,
  "signature_mismatch_count": 0,
  "status": "resolved",
  "reusable": true,
  "output": "human_review_queue_resolved.jsonl"
}
```

### Step 11: M3 — Promoted to reusable memory (CORE CONTRIBUTION)
**Active node:** M2 → M3 (special glow — this is the central contribution)
**Narration:** "M3 promotes to reusable memory — the central thesis contribution: human judgment becomes durable, queryable knowledge"
**Data panel:**
```json
{
  "layer": "M3 — Human Judgment Memory ⭐ CORE CONTRIBUTION",
  "memory_id": "HJM-ucd_ch-P6",
  "memory_signature": "sha256(memory_fields)",
  "source_review_id": "HRQ-ucd_ch-P6",
  "source_feedback_id": "HFB-ucd_ch-P6",
  "decision": "Substantial Variability",
  "rationale": "Customer as actor is a valid design choice",
  "reuse_scope": {
    "domain": "cheers",
    "diagram_type": "UCD",
    "applies_to_future_models": true
  },
  "limitation": "Only when customer is clearly the order initiator",
  "retrieval": "Deterministic keyword matching (no embeddings) — fully auditable",
  "provenance_chain": "memory → feedback → queue → Agent 4 → student models"
}
```
**Visual:** This node should have the strongest glow of all — radiate waves. Show the provenance chain as a visual trail lighting up backward through the previous nodes.

### Step 12: M4A — Advisory retrieval
**Active node:** M3 → M4A
**Narration:** "M4A retrieves memory, generates graded advisory evidence — advice_strength: moderate"
**Data panel:**
```json
{
  "layer": "M4A — Advisory Layer",
  "pattern_assessed": "P6 — Customer as actor",
  "memory_retrieved": "HJM-ucd_ch-P6",
  "match_reasons": ["same domain (Cheers)", "same diagram type (UCD)", "keyword: Customer actor"],
  "advice_strength": "moderate",
  "advice_mode": "advisory_only (schema const — CANNOT be overridden)",
  "ai_classification_changed": "false (schema const — HARD BOUNDARY)",
  "original_preserved": "Occasional Variability — UNTOUCHED"
}
```
**Visual:** Show the "ai_classification_changed = false" as a locked/shield icon.

### Step 13: M4B-1 — Deterministic comparison
**Active node:** M4A → M4B-1
**Narration:** "M4B-1 applies deterministic policy table: moderate disagreement → keep original, flag for review"
**Data panel:**
```json
{
  "layer": "M4B-1 — Deterministic Comparison",
  "policy_version": "memory-informed-classifier-v1",
  "policy_row_applied": "moderate_disagreement → keep_original_require_review",
  "original_classification": "Occasional Variability",
  "memory_informed_classification": "Substantial Variability",
  "memory_informed_differs": true,
  "final_decision": "KEEP ORIGINAL — flag for further review",
  "requires_human_review_after_memory": true,
  "ai_behavior_changed_in_baseline": "false (schema const)",
  "evaluation_leakage_status": "same_pattern_memory_used",
  "total_rows": 27,
  "classifications_changed": "0 (Δ = 0.00pp)"
}
```
**Visual:** Show a side-by-side comparison table: Original vs Memory-Informed, with the policy row highlighted.

### Step 14: Evidence Gate — CLOSED
**Active node:** M4B-1 → Evidence Gate (red glow)
**Narration:** "Evidence Gate: 0/24 expert labels → no accuracy claims permitted. The thesis contribution is the mechanism, not empirical accuracy."
**Data panel:**
```json
{
  "layer": "Evidence Gate — EVALUATION CONTROL",
  "current_labels": "0 / 24",
  "gate_status": "🔒 CLOSED — NOT EVALUABLE",
  "permitted_claims": {
    "0_labels": "Mechanism demonstration only — NO accuracy claims",
    "1_to_19": "Qualitative / pilot only",
    "20_plus": "Quantitative claims allowed",
    "plus_kappa": "Cohen's κ strengthens reliability"
  },
  "thesis_contribution": "The artifact and methodology, not empirical accuracy",
  "honest_reporting": "Claims are tied to evidence that actually exists"
}
```
**Visual:** Gate should slam shut with a brief shake animation. Show "0/24" as a prominent red badge. Display the graduated scale (0 → 20 → 24) as a progress bar that's empty.

---

## 5. INTERACTIVE FEATURES

### 5.1 Controls Bar (fixed at bottom or top)

```
[⏮ Reset] [⏪ Back] [▶ Play / ⏸ Pause] [⏩ Next] [Speed: 0.5× | 1× | 2×]
[Step 7/14 ●●●●●●●○○○○○○○]
```

- **Play** auto-advances through all 14 steps.
- **Pause** stops at the current step.
- **Step Forward/Back** allows manual frame-by-frame navigation.
- **Speed** adjusts the inter-step pause (5s at 0.5×, 2.5s at 1×, 1.25s at 2×).
- **Progress bar** shows dots or a gradient bar with the current position.

### 5.2 Clickable Nodes

When not animating, clicking any node opens its detail panel (same data as during animation) without advancing the sequence.

### 5.3 Flow Log (right sidebar or bottom panel)

Scrolling list of completed steps with colored badges:
```
[1] 🔵 Agent 1 receives UML specification
[2] 🔵 Language Template produced
[3] 🟢 Domain Description → Agent 2
...
[7] 🟠 Agent 4 classifies P6 as OCCASIONAL ⚠️
[8] 🔷 M1 flags for review
[9] 🟣 Expert DISAGREES → Substantial ✓
...
```

---

## 6. SPECIAL VISUAL MOMENTS

These moments deserve extra animation polish:

1. **Step 7 (Agent 4 classification):** The word "Occasional" should appear with an amber flash and a subtle "wrong answer" visual cue (not too harsh — the AI had reasons). Show the confidence gauge at 0.72 (72%).

2. **Step 8 (Crossing into artifact):** The horizontal separator between "Baseline" and "Artifact" sections should explode with particles as data crosses it. Text "THESIS CONTRIBUTION BEGINS" briefly flashes.

3. **Step 9 (Expert disagrees):** The most dramatic moment. The classification badge should morph: "Occasional" (amber) shatters/fades, "Substantial" (green) grows in. Brief dramatic pause.

4. **Step 11 (M3 Memory):** Emanate concentric rings from the M3 node — this is the "knowledge crystallizes" moment. The provenance chain should light up backward (M3 → M2 → Expert → M1 → Agent 4).

5. **Step 14 (Evidence Gate):** Gate slams shut. Everything dims slightly except the gate badge showing "0/24". A note appears: "Honest science: we show what the mechanism does, not accuracy we haven't measured."

---

## 7. DATA PANEL DESIGN

The data panel (right side, ~350px wide) should:

- Have a frosted glass background matching the theme
- Show the current step's JSON with syntax highlighting:
  - Keys: `#C084FC` (light purple)
  - Strings: `#10B981` (green)
  - Numbers: `#F59E0B` (amber)
  - Booleans: `#3B82F6` (blue)
  - Special values (like "false (schema const)"): `#EF4444` (red) with bold
- Animate JSON lines appearing one by one (typewriter or slide-in)
- Show the layer/agent name as a colored header above the JSON
- Show the narration text below the JSON in italic secondary text

---

## 8. RESPONSIVE BEHAVIOR

- **Desktop (>1200px):** Architecture diagram left (60%), data panel right (40%), flow log below.
- **Tablet (768–1200px):** Architecture full width, data panel slides in from right as an overlay.
- **Mobile (<768px):** Vertical stack — simplified architecture, data panel below, flow log collapsible.

---

## 9. SEPARATOR DESIGN

Between the "Baseline Agents" zone and the "Artifact" zone, render a prominent separator:

```
════════════════════════════════════════════════════════
  ▼  HUMAN–AI CO-REASONING ARTIFACT (thesis contribution)  ▼
════════════════════════════════════════════════════════
```

- Dashed glowing purple line
- Text in `#C084FC` with letter-spacing
- The separator should "break open" when Step 8 sends data across it

---

## 10. TITLE AND HEADER

At the very top:

```
VEGO-AI Pipeline — Live Architecture Animation
Reusable Human Judgment in AI-Assisted Domain Model Assessment
Running Example: "Customer as actor" (Pattern P6, ucd_ch setting)
```

- Title in 24px bold `#F6F3FF`
- Subtitle in 14px `#D8D3EA`
- Running example in 12px italic `#9A93B4` with a small amber badge

---

## 11. CONSTRAINTS AND REQUIREMENTS

- **Single HTML file** — all CSS and JS inline. No frameworks (React, Vue, etc.). Vanilla JS only.
- **CDN allowed** for Google Fonts only (`Inter` and `JetBrains Mono`).
- **No canvas for the main diagram** — use HTML/CSS/SVG so nodes are clickable DOM elements. Canvas is acceptable for particle effects only if overlaid transparently.
- **Smooth animations** — use CSS transitions and `requestAnimationFrame`. Target 60fps.
- **Accessible** — all text readable, sufficient contrast ratios, keyboard navigation for controls.
- **The JSON data must be the REAL thesis data shown above** — do not simplify or placeholder it. Every field, every value matters for thesis accuracy.
- **No audio** — visual only.
- **Total file size** should be manageable (under 50KB of HTML/CSS/JS, excluding font imports).
- **All 14 steps must work correctly** — test the Play, Pause, Step, Reset flow.

---

## 12. THESIS CONTEXT (for accuracy)

This animation is for **Ali Ahmed's MSc thesis**: "Reusable Human Judgment in AI-Assisted Domain Model Assessment: The VEGO-AI Case."

Key facts the animation must correctly represent:

- VEGO-AI uses **gpt-4o** (4 agents, asynchronous pipeline)
- The baseline produces **27 variability patterns** across 4 settings (ucd_ch, ucd_pw, cd_ch, cd_pw)
- Agent 4's **latent hooks** (requires_human_review, confidence) are produced but NEVER acted upon in the baseline — this is the gap the thesis fills
- The artifact is **non-destructive**: `ai_classification_changed = 0`, `ai_behavior_changed_in_baseline = false` — these are **schema-enforced constants**, not just conventions
- M1 reduces review from **27 to 11 patterns** (40.7%)
- M3 stores **3 reusable memory entries** from 4 feedback entries
- M4A generates **8 advisory items** across 27 patterns
- M4B-1 produces **27 comparison rows** with **0 classifications changed**
- Evidence Gate: **0/24 expert labels** → gate is CLOSED → no accuracy claims permitted
- The running example "Customer as actor" (P6, ucd_ch): AI says Occasional (conf 0.72), expert says Substantial — a genuine disagreement where the human is right
- Retrieval in M3 uses **deterministic keyword matching** (no embeddings) — this is a deliberate transparency choice
- The thesis contribution is the **mechanism** (the artifact design), not empirical accuracy (which requires labels that don't exist yet)

---

## 13. QUALITY BAR

The result should look like it belongs in:
- A thesis defense presentation projected on a large screen
- A research conference demo
- A portfolio piece

It should NOT look like:
- A homework assignment
- A basic tutorial diagram
- A flowchart made in 10 minutes

Spend the effort on polish. The animation should make the viewer say "wow, that's a beautiful way to understand this system."
