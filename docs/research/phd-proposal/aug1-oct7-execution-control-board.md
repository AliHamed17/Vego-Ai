# Aug 1-Oct 7 Execution Control Board

The canonical machine-readable program is
[`aug1-oct7-execution-control-board.json`](aug1-oct7-execution-control-board.json).
It controls 29 dependency-ordered work packages from source reconciliation
through authorized submission. It does not replace the historical July 29
registers, the master traceability register, or the closure audit.

The board has explicit, machine-checked coverage maps for the complete current
denominators: `R-01`-`R-19`, `A-01`-`A-15`, `Q-01`-`Q-10`,
`IRIS-EXP-01`-`IRIS-EXP-10`, and canonical `EXP-005` plus
`EXP-019`-`EXP-027`. Removing, adding, or leaving any of those IDs unmapped
fails structure mode.

## Current defensible state

- Structure is expected to pass when IDs, roles, dates, dependencies,
  deliverables, acceptance checks, evidence references, and gates are
  consistent.
- The current PPTX, PDF, and automated visual-QA record are hash-verified local
  evidence, and the proposal v0.2 working draft is recorded as a partial
  deliverable. These files do not satisfy human rehearsal, Ali approval,
  delivery, recipient access, or supervisor gates, so readiness still fails.
- Closure is expected to fail until the complete call is human-adjudicated,
  supervisors explicitly disposition the work, the medical-or-Plan-B route is
  evidenced, the proposal is approved, and an authorized submission receipt
  and issued closure certificate exist.
- EXP-005/EXP-020 remains human-gated. A prepared reviewer package is not an
  expert label, and no accuracy, generalization, or effort claim is released by
  this board.
- Medical work remains blocked at less than six of six gates. No row-level work
  is authorized by a plan, shared-folder link, or metadata audit.

## Validation

Run the validator from the repository root. It is read-only and returns a
non-zero exit code on failure.

```powershell
python scripts\validate_aug1_oct7_execution_program.py --mode structure
python scripts\validate_aug1_oct7_execution_program.py --mode readiness
python scripts\validate_aug1_oct7_execution_program.py --mode closure
```

Use `--json` for automation. Use an aware timestamp to add overdue checks:

```powershell
python scripts\validate_aug1_oct7_execution_program.py `
  --mode readiness `
  --as-of 2026-08-04T18:00:00+03:00 `
  --json
```

## Evidence update rules

1. Preserve stable work-package, deliverable, acceptance, gate, and evidence
   IDs. Add a new sequential work package if review discovers more work.
2. Keep expected artifacts as `pending` or `present_unverified`. Mark evidence
   `verified` only with the current SHA-256, verification timestamp, and a
   filled verifier role.
3. A passed acceptance check must cite hash-verified evidence approved by at
   least one accountable package owner. A satisfied gate must cite the exact
   evidence kinds and approvals listed in `gateEvidenceBindings`. Local tool
   verification proves file integrity only; it is not human approval.
4. Only verified evidence referenced from a deliverable, acceptance check, or
   gate can satisfy a readiness or closure requirement. An unreferenced
   evidence row cannot close a required evidence kind.
5. Human and external gates cannot be satisfied by a template, machine output,
   calendar silence, folder visibility, or an unfilled role. An approved
   not-applicable disposition requires verified `approved_disposition`
   evidence and the gate's named approvers.
6. Dependency edges are typed. `hard` requires an evidence-ready predecessor;
   `conditional` permits either a ready result or an explicitly failed,
   evidence-backed blocked outcome; `status_snapshot` permits downstream
   drafting from a verified referenced status snapshot. Closure still requires
   every predecessor to have an approved final state.
7. Use only the approved final statuses for closure. `Partial`, `blocked`,
   `planned`, and other non-final states keep closure non-zero.
8. At the August 26 checkpoint, record the evidence-backed G1-G6 result. If any
   one of G1-G6 lacks its required control or passed evidence, commit Plan B and
   keep Plan A as a conditional annex.
