# H-Layer Advancement Phase 0 Boundary Record

Captured: 2026-07-10. Branch: `main`. HEAD: `c72b845`.

Status: the worktree was already dirty at entry and remains intentionally dirty (124 porcelain status rows at this checkpoint). This record does not claim a clean, merged, finalized, or release-ready state. Unrelated changes must be preserved.

## Deliberate File Boundary

Allowed during the offline phases:

- `docs/` research, architecture, governance, dashboard, and progress sources;
- `experiments/` registry and experiment protocols;
- `scripts/` offline contracts, replay, harness, and validation tooling;
- generated/ignored outputs under `reports/generated/` and iteration scratch directories.

Protected until M-05 and a separate implementation authorization:

- `VEGO-AI/framework/`, `VEGO-AI/schemas/`, `VEGO-AI/tests/`, `VEGO-AI/eval/`, and `VEGO-AI/inputs/`;
- baseline outputs under `VEGO-AI/eval_output/`;
- all Agent 1-4 modules, Agent 4 policy, existing runtime/output/evaluation schemas, active correction, and automatic memory reuse.

At this checkpoint, `git diff --name-only` over the protected paths is empty.

## Reproducible Protected-Path Fingerprints

For tracked directories, each fingerprint is SHA-256 over UTF-8 lines of `repo-relative/path<TAB>file_sha256`. Repo-relative paths are ordered by the ordinal value of `ToLowerInvariant()` (the PowerShell equivalent of Python `sorted(key=str.lower)`), then joined by LF with no trailing LF. These fingerprints describe current working-tree content at HEAD `c72b845`; rerun the exact command below before and after offline work.

| Path | Tracked files | Tree SHA-256 |
| --- | ---: | --- |
| `VEGO-AI/framework` | 17 | `de4749aa39aef4e0ea02b3e24f8ec8174ed46ec0806e92c5778f980077cde8df` |
| `VEGO-AI/schemas` | 6 | `7dfdea2552ac1f12ea0370263151056e01b5c18c1cd1a2890188fb48efa43455` |
| `VEGO-AI/tests` | 8 | `1766a596d0c54c94ed83e72693884301d5ba98e973947b4fde1cc777ff032a2c` |
| `VEGO-AI/eval` | 7 | `f62c34f9f30558269eaa8fdb7b3f96e656f91a5fffc7ee79990234ec4d48e3ec` |
| `VEGO-AI/inputs` | 10 | `ce6baead0fb775ca926f2fdfe6578aafcc3d603db1785ea8cb2ca6b7d2d3f356` |

`VEGO-AI/eval_output` contains no tracked files, so a tracked-file hash would be the empty SHA-256 and is not useful. For this local checkpoint only, hashing all 241 files with the same relative-path/content-hash algorithm produced `12368093fdc7ae8c69eb99e1dc3534f69c5a7a0cf79fcf9345437d1f587d1f12`. Treat that as a local baseline-preservation check, not a tracked evidence artifact.

Compact verification command for the tracked fingerprints:

```powershell
$root=(Resolve-Path '.').Path; 'VEGO-AI/framework','VEGO-AI/schemas','VEGO-AI/tests','VEGO-AI/eval','VEGO-AI/inputs' | ForEach-Object { $d=$_; $files=[string[]]@(git ls-files -- $d); [Array]::Sort($files,[System.Comparison[string]]{param($a,$b)[string]::CompareOrdinal($a.ToLowerInvariant(),$b.ToLowerInvariant())}); $lines=@($files | ForEach-Object { $rel=$_; $hash=(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $rel)).Hash.ToLowerInvariant(); "$($rel.Replace('\','/'))`t$hash" }); $bytes=[Text.Encoding]::UTF8.GetBytes([string]::Join("`n",$lines)); $sha=[Security.Cryptography.SHA256]::Create(); "$d`t$(($sha.ComputeHash($bytes)|ForEach-Object ToString x2)-join '')`t$($lines.Count)" }
```

## Advancement Gates

- Phase 0 documentation reconciliation may finish inside the allowed boundary.
- Phase 1 remains `Awaiting decision record`: M-02 through M-05 have no recorded outcome.
- Offline contract/harness work may continue without selecting unapproved defaults or changing protected paths.
- Phase 4 live shadow-listener work remains `Blocked`: both M-05 and a separate authorization generated from `allowed-touch-authorization.template.json` are required.
- EXP-005 remains human-gated at 0 supplied generalization-safe real labels. Do not invent or prefill labels.
