# Confluence Wiki Sync

The Confluence wiki is the external, curated view of the VEGO-AI research workspace. The repository and `docs/agent-memory/` remain the source of truth.

## Current Mode

- Live Confluence target: not configured.
- Default behavior: generate local Markdown page bodies in `docs/confluence/outbox/`.
- Generated outbox files are ignored by Git.

## End-Of-Prompt Order

For every meaningful prompt:

1. Run `.\scripts\agent-memory-start.ps1` at the beginning.
2. Do the requested work.
3. Update memory files and run `.\scripts\agent-memory-finish.ps1`.
4. Run `.\scripts\build-confluence-wiki.ps1`.
5. If `docs/confluence/wiki-sync-config.local.json` has real Confluence IDs, update the configured Confluence pages with Atlassian Rovo using `contentFormat: markdown`.
6. If IDs are missing, leave the generated outbox as the pending wiki update and mention that live Confluence sync is pending.

## Curated Pages

| Page | Generated File | Purpose |
| --- | --- | --- |
| VEGO-AI Wiki Home | `vego-ai-wiki-home.md` | Project overview and navigation. |
| VEGO-AI Current State | `vego-ai-current-state.md` | Latest status, active risks, and next steps. |
| VEGO-AI Update Changelog | `vego-ai-update-changelog.md` | Recent prompt/update history. |
| VEGO-AI Research Operations | `vego-ai-research-operations.md` | Roadmap, risks, experiment registry, audit posture. |

## Configuration

Copy `docs/confluence/wiki-sync-config.template.json` to `docs/confluence/wiki-sync-config.local.json` and fill:

- `cloudId`
- `spaceId`
- `parentId`, optional
- `pages.home.pageId`
- `pages.currentState.pageId`
- `pages.changelog.pageId`
- `pages.researchOperations.pageId`

Do not commit the local config.

## Safety Rules

- Do not mirror ignored artifacts or controlled contents.
- Do not paste PDF, model, analysis, eval output, or raw data contents into Confluence.
- Use metadata-only summaries until `docs/research/publishability-register.md` says otherwise.
- Confluence updates are agent-enforced workflow, not a background service.
