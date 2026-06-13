# Confluence Manual Sync

Use this workflow only when live Atlassian Rovo access is unavailable and the generated wiki outbox needs to be published through another approved route.

## Generated Pack

Run:

```powershell
.\scripts\build-confluence-wiki.ps1
```

This refreshes:

- `docs/confluence/outbox/`
- `docs/dashboards/status-snapshot.generated.md`
- `docs/confluence/manual-sync-pack.generated.md`

The manual sync pack is ignored by Git. It contains the curated page bodies, page titles, target metadata, and SHA-256 hashes for the five wiki pages.

## Pages

| Page | Target |
| --- | --- |
| VEGO-AI Wiki Home | Existing page `294914`. |
| VEGO-AI Current State | Child of page `294914`. |
| VEGO-AI Progress Dashboard | Child of page `294914`. |
| VEGO-AI Update Changelog | Child of page `294914`. |
| VEGO-AI Research Operations | Child of page `294914`. |

## Rules

- Do not publish controlled artifact contents, PDFs, model files, raw analysis outputs, or generated evaluation outputs.
- Use only the generated outbox/manual pack content, which is sanitized by `scripts/build-confluence-wiki.ps1`.
- After child pages are created, store page IDs only in ignored `docs/confluence/wiki-sync-config.local.json`.
- After manual sync, run `.\scripts\dashboard-health.ps1 -RequireOutbox`.
