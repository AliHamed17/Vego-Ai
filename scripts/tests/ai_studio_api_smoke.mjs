#!/usr/bin/env node
import assert from "node:assert/strict";
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const repoRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
);
process.env.VEGO_REPO_ROOT = repoRoot;
const catalog = JSON.parse(
  fs.readFileSync(
    path.join(
      repoRoot,
      "docs",
      "research",
      "bigui",
      "experiment-catalog-snapshot-v1.json",
    ),
    "utf8",
  ),
);
const app = require(path.join(repoRoot, "deploy", "ai-studio", "server.js"));
const server = await new Promise((resolve) => {
  const listener = app.listen(0, "127.0.0.1", () => resolve(listener));
});
const address = server.address();
const baseUrl = `http://127.0.0.1:${address.port}`;

async function json(pathname, expectedStatus = 200) {
  const response = await fetch(`${baseUrl}${pathname}`);
  assert.equal(
    response.status,
    expectedStatus,
    `${pathname} returned ${response.status}`,
  );
  return response.json();
}

function runKeyForTest(observation) {
  return `${observation.metricId}|${JSON.stringify(
    observation.dimensions || {},
    Object.keys(observation.dimensions || {}).sort(),
  )}`;
}

try {
  const health = await json("/api/health");
  assert.equal(health.status, "ok");
  assert.equal(health.apiVersion, "v1");
  assert.equal(health.experimentCount, 41);

  const program = await json("/api/v1/program");
  assert.equal(program.experimentCount, 41);
  assert.equal(program.currentAcceptedRunCount, 26);
  assert.equal(
    program.historicalAcceptedRunCount,
    catalog.runStoreSummary.bundleCount,
  );
  assert.equal(
    program.metricObservationCount,
    catalog.runStoreSummary.metricObservationCount,
  );
  assert.match(program.claimBoundary, /0\/24 safe labels/);

  const index = await json("/api/v1/experiments");
  assert.equal(index.count, 41);
  assert.equal(index.data.length, 41);
  assert.equal(new Set(index.data.map((item) => item.experimentId)).size, 41);

  const exp003 = await json("/api/v1/experiments/EXP-003");
  assert.equal(exp003.data.measurementState.status, "observed_null");
  assert.equal(exp003.data.measurementState.nonNullMetricCount, 0);
  assert.equal(exp003.data.measurementState.claimEligibleMetricCount, 0);
  assert.match(exp003.data.currentRun.runId, /^EXP-003-/);

  const exp039Runs = await json("/api/v1/experiments/EXP-039/runs");
  assert.ok(exp039Runs.count >= 2);
  const leftRunId = exp039Runs.data[0].envelope.runId;
  const rightRunId = exp039Runs.data[1].envelope.runId;
  const eligible = await json(
    `/api/v1/comparisons/eligibility?leftRunId=${encodeURIComponent(leftRunId)}&rightRunId=${encodeURIComponent(rightRunId)}`,
  );
  assert.equal(eligible.eligible, true);
  assert.equal(eligible.status, "Eligible");

  const exp038Runs = await json("/api/v1/experiments/EXP-038/runs");
  const ineligible = await json(
    `/api/v1/comparisons/eligibility?leftRunId=${encodeURIComponent(leftRunId)}&rightRunId=${encodeURIComponent(exp038Runs.data[0].envelope.runId)}`,
  );
  assert.equal(ineligible.eligible, false);
  assert.equal(ineligible.status, "Not directly comparable");
  assert.ok(ineligible.mismatches.some((item) => item.field === "experimentId"));
  assert.equal(ineligible.deltas.length, 0);

  const exp030Runs = await json("/api/v1/experiments/EXP-030/runs");
  let definitionMismatchPair = null;
  for (let leftIndex = 0; leftIndex < exp030Runs.data.length; leftIndex += 1) {
    for (
      let rightIndex = leftIndex + 1;
      rightIndex < exp030Runs.data.length;
      rightIndex += 1
    ) {
      const leftRun = exp030Runs.data[leftIndex];
      const rightRun = exp030Runs.data[rightIndex];
      const leftDefinitions = new Map(
        leftRun.metricObservations.map((item) => [
          runKeyForTest(item),
          item.metricDefinitionSha256,
        ]),
      );
      const differs = rightRun.metricObservations.some(
        (item) =>
          leftDefinitions.has(runKeyForTest(item)) &&
          leftDefinitions.get(runKeyForTest(item)) !==
            item.metricDefinitionSha256,
      );
      if (differs) {
        definitionMismatchPair = [
          leftRun.envelope.runId,
          rightRun.envelope.runId,
        ];
        break;
      }
    }
    if (definitionMismatchPair) break;
  }
  assert.ok(definitionMismatchPair);
  const definitionMismatch = await json(
    `/api/v1/comparisons/eligibility?leftRunId=${encodeURIComponent(definitionMismatchPair[0])}&rightRunId=${encodeURIComponent(definitionMismatchPair[1])}`,
  );
  assert.equal(definitionMismatch.eligible, false);
  assert.ok(
    definitionMismatch.mismatches.some(
      (item) => item.field === "metricDefinitionSha256",
    ),
  );
  assert.equal(definitionMismatch.deltas.length, 0);

  const missing = await json(
    "/api/v1/comparisons/eligibility?leftRunId=missing&rightRunId=missing-too",
    404,
  );
  assert.equal(missing.eligible, false);
  assert.equal(missing.status, "run_not_found");

  const paper = await json("/api/v1/paper-baseline");
  assert.equal(paper.mappings.length, 4);
  assert.deepEqual(
    paper.mappings.map((item) => item.paperPhase),
    ["A", "B", "C", "D"],
  );
  assert.ok(
    paper.mappings.every((item) => item.directComparisonEligible === false),
  );

  const deployment = await json("/api/v1/deployment");
  assert.equal(deployment.experimentCount, 41);
  assert.equal(deployment.liveObservation.experimentCount, 28);
  assert.equal(deployment.liveObservation.status, "stale");

  const root = await fetch(`${baseUrl}/`);
  assert.equal(root.status, 200);
  assert.match(await root.text(), /VEGO-AI Research Observatory/);
  assert.match(
    root.headers.get("content-security-policy") || "",
    /default-src 'self'/,
  );

  const archive = await fetch(`${baseUrl}/archive/workspace-v1`);
  assert.equal(archive.status, 200);
  assert.match(await archive.text(), /Historical BigUI deployment/);

  process.stdout.write("AI Studio read-only API smoke: PASS\n");
} finally {
  await new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}
