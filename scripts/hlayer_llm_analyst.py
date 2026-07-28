#!/usr/bin/env python3
"""LLM analyst for the VEGO-AI research program (ADVISORY ONLY).

Reads three generated analysis artifacts - the component contribution report,
the experiment-benchmark analytics report, and the unified program overview -
and produces a narrative that explains the program's logic, what improved,
what broke or stalled, and concrete enhancement suggestions.

Two modes, chosen automatically:
- LLM mode when OPENAI_API_KEY is configured: uses the authorized, hardened
  ``VEGO-AI/framework/llm_client.py`` (plaintext keys rejected, secrets
  redacted, logging policy enforced).
- Deterministic mode otherwise: a rule-based narrative from the same inputs,
  so the pipeline never blocks on the LLM.

Hard boundaries (why this is gate-safe): the analyst READS generated analysis
outputs only, WRITES only under reports/generated/llm_analyst/, never touches
protected paths or controlled data, never feeds anything back into
classification, and every output line of provenance-bearing text carries the
ADVISORY banner. Its words are narrative, never evidence.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from hlayer_harness import (
    REPO,
    experiment_output_dir,
    generated_at,
    output_root,
    read_json,
    sha256_file,
    write_json,
)

OUT = experiment_output_dir("llm_analyst")
BANNER = (
    "ADVISORY ANALYSIS - generated narrative, not evidence. No accuracy, generalization, or "
    "clinical-performance claim. Verify every statement against the cited source artifacts."
)
MAX_INPUT_CHARS = 24000  # keep prompts bounded and deterministic in size


def gather_inputs() -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Collect the three analysis inputs with provenance; missing ones are noted, not fatal."""
    sources: list[dict[str, str]] = []
    bundle: dict[str, Any] = {}

    contribution_path = output_root() / "agent_contribution" / "agent_contribution.json"
    if contribution_path.is_file():
        bundle["agent_contribution"] = read_json(contribution_path)
        sources.append({"path": contribution_path.relative_to(REPO).as_posix(),
                        "sha256": sha256_file(contribution_path)})

    benchmark_path = REPO / "docs" / "research" / "bigui" / "EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md"
    if benchmark_path.is_file():
        bundle["benchmark_report_md"] = benchmark_path.read_text(encoding="utf-8")[:MAX_INPUT_CHARS]
        sources.append({"path": benchmark_path.relative_to(REPO).as_posix(),
                        "sha256": sha256_file(benchmark_path)})

    overview_path = output_root() / "hlayer_program_overview" / "program_overview.json"
    if overview_path.is_file():
        bundle["program_overview"] = read_json(overview_path)
        sources.append({"path": overview_path.relative_to(REPO).as_posix(),
                        "sha256": sha256_file(overview_path)})
    return bundle, sources


def deterministic_analysis(bundle: dict[str, Any]) -> dict[str, Any]:
    """Rule-based narrative from the same inputs; used when no API key is configured."""
    contribution = bundle.get("agent_contribution") or {}
    overview = bundle.get("program_overview") or {}
    components = contribution.get("components") or []
    counts = (contribution.get("overall") or {}).get("component_verdict_counts") or {}
    weakest = (contribution.get("overall") or {}).get("weakest_links") or []

    what_works = [
        f"{c['id']} ({c['name']}): {c['why']}"
        for c in components if str(c.get("verdict", "")).startswith("CONTRIBUTING")
    ]
    what_lags = [
        f"{c['id']} ({c['name']}): {c['why']} -> unlocks when: {c['verdict_would_change_if']}"
        for c in components if not str(c.get("verdict", "")).startswith("CONTRIBUTING")
    ]
    iterations = overview.get("iterations") or []
    enhancements = [
        "Run the 24-row label campaign (two reviewers + adjudication) - it simultaneously unlocks the "
        "Agent 4 quality verdict, the M4A/M4B-1 benefit measurement (EXP-012), and the thesis Chapter-7 "
        "quantitative sections; it is the single highest-leverage action available.",
        "Decide M-03 (dosage default): EXP-007 shows threshold_sev2 meets coverage but not the load "
        "target - either accept a higher load budget or approve case-bundled routing before the pilot.",
        "Approve the M-04 H-Verify source set, then rerun EXP-009 with protocol-valid wrong-expert trials; "
        "fixture-only recall of 1.0 says the rules cover their own fixtures, not that they catch real "
        "expert error.",
        "Strengthen Agent 2: its guideline F1 dips to ~0.55 on some settings and its churn is the largest "
        "human-unobserved surface (EXP-008) - prioritize its outputs in the first labeled review round.",
        "Keep every future run inside the immutable run store so the benchmark's trend analysis stays "
        "byte-verifiable.",
    ]
    return {
        "mode": "deterministic",
        "summary": (
            "The program preserved the paper's four-agent architecture byte-identical while wrapping it in "
            "a measured, fail-closed human-judgment layer. Mechanism, observability, and safety are "
            "demonstrated with cited numbers; classification quality is deliberately unanswered until real "
            f"labels exist. Component verdicts: {counts}. Accepted iterations: {len(iterations)}."
        ),
        "what_works_and_why": what_works,
        "what_lags_and_why": what_lags,
        "weakest_links": weakest,
        "enhancement_suggestions": enhancements,
    }


async def llm_analysis(bundle: dict[str, Any]) -> dict[str, Any]:
    framework = REPO / "VEGO-AI" / "framework"
    if str(framework) not in sys.path:
        sys.path.insert(0, str(framework))
    from llm_client import LLMClient  # authorized, hardened client

    client = LLMClient()
    contribution = bundle.get("agent_contribution") or {}
    prompt = {
        "system": (
            "You are the analyst for the VEGO-AI MSc research program. You explain logic and suggest "
            "enhancements. HARD RULES: never claim accuracy, generalization, or clinical performance - "
            "0 independent expert labels exist; every claim must reference the provided data; clearly "
            "separate measured facts from your interpretation. Answer as JSON with keys: summary, "
            "what_works_and_why (list), what_lags_and_why (list), enhancement_suggestions (list), "
            "risks (list)."
        ),
        "user": (
            "Component contribution report (verdicts with sources):\n"
            + str(contribution)[:MAX_INPUT_CHARS // 2]
            + "\n\nBenchmark analytics (excerpt):\n"
            + str(bundle.get("benchmark_report_md", ""))[: MAX_INPUT_CHARS // 2]
        ),
    }
    parsed = await client.call(prompt, label="hlayer_analyst/program_analysis")
    parsed["mode"] = "llm"
    return parsed


def build_markdown(analysis: dict[str, Any], sources: list[dict[str, str]]) -> str:
    lines = [
        "# VEGO-AI Program Analyst Report",
        "",
        f"> {BANNER}",
        "",
        f"Generated: {generated_at()} | mode: {analysis.get('mode')} | "
        "regenerate: `python scripts/hlayer_llm_analyst.py`",
        "",
        "## Summary",
        "",
        str(analysis.get("summary", "")),
        "",
        "## What Works, And Why",
        "",
    ]
    for item in analysis.get("what_works_and_why", []) or []:
        lines.append(f"- {item}")
    lines += ["", "## What Lags, And Why", ""]
    for item in analysis.get("what_lags_and_why", []) or []:
        lines.append(f"- {item}")
    if analysis.get("weakest_links"):
        lines += ["", "## Weakest Links", ""]
        for item in analysis["weakest_links"]:
            lines.append(f"- {item}")
    if analysis.get("risks"):
        lines += ["", "## Risks", ""]
        for item in analysis["risks"]:
            lines.append(f"- {item}")
    lines += ["", "## Enhancement Suggestions (advisory)", ""]
    for item in analysis.get("enhancement_suggestions", []) or []:
        lines.append(f"- {item}")
    lines += ["", "## Input Provenance", ""]
    for src in sources:
        lines.append(f"- `{src['path']}` sha256 `{src['sha256'][:16]}...`")
    lines += ["", f"> {BANNER}"]
    return "\n".join(lines) + "\n"


def main() -> int:
    bundle, sources = gather_inputs()
    if not bundle:
        print("llm analyst: no analysis inputs found; run the contribution report and overview first",
              file=sys.stderr)
        return 2

    use_llm = bool(os.environ.get("OPENAI_API_KEY"))
    if use_llm:
        try:
            analysis = asyncio.run(llm_analysis(bundle))
        except Exception as exc:  # LLM problems must never block the pipeline
            print(f"llm analyst: LLM mode failed ({exc}); falling back to deterministic", file=sys.stderr)
            analysis = deterministic_analysis(bundle)
            analysis["llm_fallback_reason"] = str(exc)
    else:
        analysis = deterministic_analysis(bundle)

    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "generated_at": generated_at(),
        "advisory_banner": BANNER,
        "inputs": sources,
        "analysis": analysis,
    }
    write_json(OUT / "analysis.json", payload)
    (OUT / "analysis.md").write_text(build_markdown(analysis, sources), encoding="utf-8")
    print(f"llm analyst ({analysis.get('mode')}): -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
