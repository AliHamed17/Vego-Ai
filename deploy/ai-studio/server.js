"use strict";

const express = require("express");
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");

const app = express();
app.disable("x-powered-by");
app.use((request, response, next) => {
  response.setHeader("X-Content-Type-Options", "nosniff");
  response.setHeader("Referrer-Policy", "no-referrer");
  response.setHeader("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
  response.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
  );
  next();
});

const bundledRoot = path.resolve(__dirname);
const repositoryRoot = path.resolve(
  process.env.VEGO_REPO_ROOT || path.join(__dirname, "..", "..")
);
const bundledData = path.join(bundledRoot, "data");
const isBundled = fs.existsSync(path.join(bundledData, "catalog.json"));
const fileMap = isBundled
  ? {
      html: path.join(bundledRoot, "public", "index.html"),
      catalog: path.join(bundledData, "catalog.json"),
      results: path.join(bundledData, "result-views.json"),
      paper: path.join(bundledData, "paper-baseline.json"),
      deployment: path.join(bundledData, "deployment.json"),
      archive: path.join(bundledRoot, "public", "archive", "workspace-v1", "index.html"),
    }
  : {
      html: path.join(repositoryRoot, "VEGO-AI-Research-Hub.html"),
      catalog: path.join(
        repositoryRoot,
        "docs",
        "research",
        "bigui",
        "experiment-catalog-snapshot-v1.json"
      ),
      results: path.join(
        repositoryRoot,
        "docs",
        "research",
        "bigui",
        "experiment-result-views-v1.json"
      ),
      paper: path.join(
        repositoryRoot,
        "docs",
        "research",
        "bigui",
        "paper-baseline-snapshot-v1.json"
      ),
      deployment: path.join(
        repositoryRoot,
        "docs",
        "research",
        "bigui",
        "deployment-snapshot-v1.json"
      ),
      archive: path.join(__dirname, "archive", "workspace-v1.html"),
    };

function loadJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function hashFile(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function dataState() {
  const catalog = loadJson(fileMap.catalog);
  const results = loadJson(fileMap.results);
  const paper = loadJson(fileMap.paper);
  const deployment = loadJson(fileMap.deployment);
  const resultById = new Map(
    results.resultViews.map((item) => [item.experimentId, item])
  );
  const bundlesById = new Map();
  for (const bundle of catalog.acceptedRunBundles) {
    const id = bundle.envelope.experimentId;
    if (!bundlesById.has(id)) bundlesById.set(id, []);
    bundlesById.get(id).push(bundle);
  }
  return { catalog, results, paper, deployment, resultById, bundlesById };
}

function sendJson(response, value, status = 200) {
  response.status(status).type("application/json").send(
    JSON.stringify(value)
  );
}

function experimentId(value) {
  return typeof value === "string" && /^EXP-\d{3}$/.test(value);
}

function runKey(observation) {
  return `${observation.metricId}|${JSON.stringify(
    observation.dimensions || {},
    Object.keys(observation.dimensions || {}).sort()
  )}`;
}

app.get("/api/health", (_request, response) => {
  try {
    const { catalog, deployment } = dataState();
    sendJson(response, {
      status: "ok",
      apiVersion: "v1",
      experimentCount: catalog.experiments.length,
      catalogSha256: hashFile(fileMap.catalog),
      publicationState: deployment.publicationState,
    });
  } catch (error) {
    sendJson(response, { status: "error", detail: error.message }, 503);
  }
});

app.get("/api/v1/program", (_request, response) => {
  const { catalog, results, deployment } = dataState();
  sendJson(response, {
    schemaVersion: "BigUIProgramView-v1",
    programState: catalog.programState,
    experimentCount: catalog.experiments.length,
    currentAcceptedRunCount: results.summary.currentAcceptedRunCount,
    historicalAcceptedRunCount: results.summary.historicalAcceptedRunCount,
    metricObservationCount: catalog.runStoreSummary.metricObservationCount,
    catalogSha256: deployment.catalogSha256,
    claimBoundary: results.claimBoundary,
  });
});

app.get("/api/v1/experiments", (_request, response) => {
  const { results, deployment } = dataState();
  sendJson(response, {
    schemaVersion: "ExperimentResultIndex-v1",
    count: results.resultViews.length,
    catalogSha256: deployment.catalogSha256,
    data: results.resultViews.map((item) => ({
      experimentId: item.experimentId,
      title: item.title,
      status: item.status,
      evidenceClass: item.evidenceClass,
      measurementState: item.measurementState,
      progressStatus: item.conclusion.progressStatus,
      currentRunId: item.currentRun?.runId || null,
      nextAction: item.nextAction,
      claimBoundary: item.claimBoundary,
    })),
  });
});

app.get("/api/v1/experiments/:id", (request, response) => {
  if (!experimentId(request.params.id)) {
    return sendJson(response, { status: "invalid_experiment_id" }, 400);
  }
  const { resultById, deployment } = dataState();
  const item = resultById.get(request.params.id);
  if (!item) return sendJson(response, { status: "not_found" }, 404);
  return sendJson(response, {
    catalogSha256: deployment.catalogSha256,
    data: item,
  });
});

app.get("/api/v1/experiments/:id/runs", (request, response) => {
  if (!experimentId(request.params.id)) {
    return sendJson(response, { status: "invalid_experiment_id" }, 400);
  }
  const { bundlesById, deployment } = dataState();
  const runs = bundlesById.get(request.params.id) || [];
  return sendJson(response, {
    schemaVersion: "AcceptedRunBundleIndex-v1",
    experimentId: request.params.id,
    count: runs.length,
    catalogSha256: deployment.catalogSha256,
    data: runs,
  });
});

app.get("/api/v1/paper-baseline", (_request, response) => {
  const { paper, results, deployment } = dataState();
  sendJson(response, {
    schemaVersion: "PaperBaselineView-v1",
    catalogSha256: deployment.catalogSha256,
    paper,
    mappings: results.paperMetricMappings,
  });
});

app.get("/api/v1/comparisons/eligibility", (request, response) => {
  const leftRunId = String(request.query.leftRunId || "");
  const rightRunId = String(request.query.rightRunId || "");
  const { catalog, deployment } = dataState();
  const bundles = catalog.acceptedRunBundles;
  const left = bundles.find((item) => item.envelope.runId === leftRunId);
  const right = bundles.find((item) => item.envelope.runId === rightRunId);
  if (!left || !right) {
    return sendJson(
      response,
      {
        eligible: false,
        status: "run_not_found",
        mismatches: [],
        deltas: [],
        catalogSha256: deployment.catalogSha256,
      },
      404
    );
  }
  const fields = [
    "datasetHash",
    "partitionHash",
    "baselineRevision",
    "policyVersion",
    "promptVersion",
    "modelIdentifier",
    "metricSchemaVersion",
    "labelEligibility",
    "leakageClass",
    "evidenceClass",
  ];
  const mismatches = [];
  if (left.envelope.experimentId !== right.envelope.experimentId) {
    mismatches.push({
      field: "experimentId",
      left: left.envelope.experimentId,
      right: right.envelope.experimentId,
    });
  }
  for (const field of fields) {
    const leftValue = left.envelope.comparisonContext[field];
    const rightValue = right.envelope.comparisonContext[field];
    if (leftValue == null || rightValue == null || leftValue !== rightValue) {
      mismatches.push({ field, left: leftValue, right: rightValue });
    }
  }
  const leftMetrics = new Map(
    left.metricObservations.map((item) => [runKey(item), item])
  );
  for (const item of right.metricObservations) {
    const previous = leftMetrics.get(runKey(item));
    if (
      previous &&
      previous.metricDefinitionSha256 !== item.metricDefinitionSha256
    ) {
      mismatches.push({
        field: "metricDefinitionSha256",
        metricId: item.metricId,
        dimensions: item.dimensions || {},
        left: previous.metricDefinitionSha256,
        right: item.metricDefinitionSha256,
      });
    }
  }
  const eligible = mismatches.length === 0 && leftRunId !== rightRunId;
  const deltas = eligible
    ? right.metricObservations.flatMap((item) => {
        const previous = leftMetrics.get(runKey(item));
        if (
          !previous ||
          typeof previous.value !== "number" ||
          typeof item.value !== "number"
        ) {
          return [];
        }
        return [
          {
            metricId: item.metricId,
            dimensions: item.dimensions || {},
            left: previous.value,
            right: item.value,
            absoluteDelta: item.value - previous.value,
            unit: item.unit,
          },
        ];
      })
    : [];
  return sendJson(response, {
    eligible,
    status: eligible ? "Eligible" : "Not directly comparable",
    mismatches,
    deltas,
    catalogSha256: deployment.catalogSha256,
  });
});

app.get("/api/v1/deployment", (_request, response) => {
  sendJson(response, dataState().deployment);
});

app.get("/archive/workspace-v1", (_request, response) => {
  response.sendFile(fileMap.archive);
});

app.get("/", (_request, response) => {
  response.sendFile(fileMap.html);
});

app.use((_request, response) => {
  sendJson(response, { status: "not_found" }, 404);
});

const port = Number(process.env.PORT || 8080);
if (require.main === module) {
  app.listen(port, "0.0.0.0", () => {
    process.stdout.write(`VEGO-AI BigUI listening on ${port}\n`);
  });
}

module.exports = app;
