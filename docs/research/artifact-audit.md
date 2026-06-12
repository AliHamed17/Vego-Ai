# Artifact Audit

Metadata-only audit for artifacts that are ignored, deferred, generated, or potentially sensitive. Do not paste controlled artifact contents here.

## Default Rule

Unless an artifact has an explicit publish decision, treat it as `Controlled / do not publish`.

## Deferred Artifact Register

| Artifact | Type | Current Location | Git Status | Sensitivity Default | Publishability | Next Action |
| --- | --- | --- | --- | --- | --- | --- |
| IRB / paper PDF | Research document | Repository root, `*.pdf` | Ignored | Controlled | Do not publish | Review protocol, consent, anonymization, and sharing terms. |
| Source delivery archive | Archive | Repository root, `*.zip` | Ignored | Controlled | Do not publish | Keep local backup; publish only if audited and needed. |
| Nested UI archive | Archive | `VEGO-AI/VEGO-AI-UI.zip` | Ignored | Controlled | Do not publish | Audit contents before any release decision. |
| Case models | Research data | `VEGO-AI/models/` | Ignored | Controlled | Do not publish | Audit provenance, anonymization, and permission. |
| Expert analysis | Research analysis | `VEGO-AI/analysis/` | Ignored | Controlled | Do not publish | Map to `EXP-000` with metadata only. |
| Evaluation outputs | Generated results | `VEGO-AI/eval_output/` | Ignored | Controlled | Do not publish | Record provenance and selected evidence after audit. |
| Human review outputs | Generated review queue | `VEGO-AI/human_review_output/` | Ignored | Controlled | Do not publish | Regenerate through documented commands when needed. |
| Visualizer bundled models | Research data | `VEGO-AI/vego_visualizer_delivery/models/` | Ignored | Controlled | Do not publish | Audit with case models. |
| Visualizer compliance vectors | Generated outputs | `VEGO-AI/vego_visualizer_delivery/compliance_vectors/` | Ignored | Controlled | Do not publish | Link only summarized results after audit. |
| Visualizer bundled guidelines | Generated/reference outputs | `VEGO-AI/vego_visualizer_delivery/guidelines/` | Ignored | Controlled | Do not publish | Audit provenance before publishing. |
| Bundled executable | Binary package | `VEGO-AI/vego_visualizer_delivery/VEGO-AI.exe` | Ignored | Controlled | Do not publish | Rebuild from source if a release is needed. |
| Local milestone change archive | Archive | `artifacts/vego-ai-M1-M2-changes.zip` | Ignored | Controlled | Do not publish | Keep local only unless explicitly audited and needed. |
| Local Claude settings | Local tool state | `.claude/*.local.json` | Ignored | Local-only | Do not publish | Keep machine-specific permissions out of Git. |
| Compiled memory | Generated context | `docs/agent-memory/compiled-memory.md` | Ignored | Internal | Do not publish | Regenerate per prompt. |
| Confluence outbox | Generated wiki draft | `docs/confluence/outbox/` | Ignored | Internal | Do not publish | Regenerate after memory updates. |

## Audit Status

- Current status: in progress.
- Last metadata pass: 2026-06-12.
- Content audit status: not completed.
- IRB review status: not completed.
