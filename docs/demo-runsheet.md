# VEGO-AI — Demo Runsheet (≈ 7 minutes)

**What you're showing:** how reusable human judgment flows through VEGO-AI end-to-end, on one real example
("Customer as actor", ucd_ch P6). **Tool:** open `VEGO-AI-Demo-Flow.html` full-screen (F11). Backup:
`VEGO-AI-Research-Hub.html` (everything) and the 38-slide deck. **To record a video:** start screen capture,
press **Auto-play** (6s/step), let it run once (~50s), then talk over a second manual pass.

> **Golden rule for the room:** this demo shows the **mechanism working together**, *not* an accuracy gain.
> If asked "did it get more accurate?" use the boundary answer at the bottom.

## Beats

| # | On screen (step) | Say (≈) | Time |
| --- | --- | --- | --- |
| 0 | Title slide / step 1 | "VEGO-AI assesses student domain models and decides whether a deviation is a *valid alternative* or an *error*. I'll follow one pattern through the whole system." | 0:40 |
| 1 | Step 1 — Input | "Across 179 models we get 27 recurring patterns. Here: a student modelled *Customer* as an actor." | 0:30 |
| 2 | Step 2 — Agent 4 | "The baseline calls it *Occasional* — medium confidence, 0.72 — and raises its own review flag. Note: this output is frozen; nothing downstream ever changes it." | 0:50 |
| 3 | Step 3 — M1 | "We don't review everything — only where the AI is unsure. 11 of 27 are queued; this one enters on the medium-confidence trigger." | 0:45 |
| 4 | Step 4 — Expert/M2 | "The expert disagrees: *Customer placing orders is a legitimate alternative, not an error* — captured as schema-validated feedback with a rationale, not a sticky note." | 0:55 |
| 5 | Step 5 — M3 | "That judgment is stored with full provenance so it can be reused — the point of the whole thesis: judgment as a durable asset, not a one-off fix." | 0:45 |
| 6 | Step 6 — M4A | "Next time the pattern appears, the memory is retrieved as *graded advice*. Critically, the AI label is preserved — advice sits beside it, never overwrites it." | 0:45 |
| 7 | Step 7 — M4B-1 | "The deterministic policy compares the two. Advice is moderate and disagrees, so it *keeps the original and escalates* for another human look — it never silently relabels. Zero of 27 baseline labels changed." | 0:55 |
| 8 | Step 8 — Output/boundary | "End to end: flagged, captured, stored, reused, governed — baseline untouched, every step reproducible. What I'm *not* claiming is an accuracy gain — that's gated on independent labels, which is exactly the next step." | 0:55 |

**Opening line:** "Let me show you how a single human judgment travels through VEGO-AI — and why nothing it does can corrupt the system it's assessing."

**Closing line:** "So the system demonstrably works *together*; the honest open question — does it improve accuracy — is one approval away from being answerable."

## Anticipated questions (short answers)

- **"Did accuracy improve?"** → "Not claimed. We've proven the mechanism and built the bias-controlled
  evaluation; the accuracy question needs 24 independent expert labels we don't have yet. The gap is
  deliberate and bounded."
- **"Why did it keep the 'wrong' label?"** → "By design — the policy is conservative and non-destructive. It
  escalates rather than silently overriding; a label change would require justified, held-out evidence."
- **"Is this just human-in-the-loop?"** → "No — the judgment is *persisted, reused, and governed* (advise /
  decide / escalate), not consumed once."
- **"How do I know the baseline wasn't tampered with?"** → "It's machine-enforced: `ai_classification_changed
  = false` is a const schema field, and an 18-invariant guard checks it every run."

## Fallback if the HTML won't open
Use deck slides: Co-Reasoning Artifact → Running Example → Interaction Sequence → M4B-1 → Evidence Dashboard.
