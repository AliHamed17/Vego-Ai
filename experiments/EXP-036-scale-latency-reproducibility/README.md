# EXP-036 — Scale, latency, and reproducibility

## Purpose

Measure legacy, unified, and parity operational overhead over the current
fixture corpus and explicitly synthetic 5× and 10× replications.

## Measures

p50 and p95 latency, throughput, peak memory, disk output, normalized output
hash, and replay determinism. Record machine and runtime provenance with every
run.

## Targets

- Unified p95 overhead at most 15% relative to legacy.
- Unified peak memory at most 1.5× legacy.
- Parity runtime at most 2.25× legacy.

Targets are engineering thresholds, not empirical performance claims. Timing
results remain machine-specific and accuracy remains out of scope.
