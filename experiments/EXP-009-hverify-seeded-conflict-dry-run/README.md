# EXP-009 - H-Verify Seeded-Conflict Dry Run

Status: **Provisional synthetic prototype run complete (2026-07-10); protocol unapproved.** Claim scope: assumption-driven synthetic rule test, never validation evidence.

Question: Under its encoded assumptions, does the draft S5 rule set flag seeded conflicts and produce bounded dialogue traces?

Method: Inject clearly-labeled SYNTHETIC wrong feedback into an isolated copy of the feedback stream; run S5 checker offline; measure caught/missed.

Run: Executed as part of the research loop suite via `scripts/exp009_seeded_conflict.py`. Outputs (ignored): `reports/generated/exp009/`.

Interpretation notes: Seeded wrong feedback lives only under `reports/generated/exp009/`, is marked `SYNTHETIC_NOT_HUMAN`, and is never merged into real memory/feedback stores. The run does not establish a catch rate for real expert mistakes, approve the four-source set, or validate semantic checking. M-04 remains unrecorded.
