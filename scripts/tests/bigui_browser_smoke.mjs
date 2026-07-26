#!/usr/bin/env node
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const moduleRoot = process.env.PLAYWRIGHT_MODULE_DIR;
const { chromium } = require(moduleRoot ? path.join(moduleRoot, "playwright") : "playwright");
const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const qaDir = path.join(repoRoot, "tmp", "bigui-qa");
fs.mkdirSync(qaDir, { recursive: true });

const server = http.createServer((request, response) => {
  const requested = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
  const relative = requested === "/" ? "/VEGO-AI-Research-Hub.html" : requested;
  const filePath = path.resolve(repoRoot, `.${relative}`);
  if (!filePath.startsWith(repoRoot) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    response.writeHead(404);
    response.end("Not found");
    return;
  }
  const type = filePath.endsWith(".html")
    ? "text/html; charset=utf-8"
    : filePath.endsWith(".json")
      ? "application/json; charset=utf-8"
      : "application/octet-stream";
  response.writeHead(200, { "Content-Type": type, "Cache-Control": "no-store" });
  fs.createReadStream(filePath).pipe(response);
});

await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const address = server.address();
const baseUrl = `http://127.0.0.1:${address.port}`;
const browser = await chromium.launch({ headless: true });
const failures = [];

async function verifyPage(viewport) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const errors = [];
  const external = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.origin !== baseUrl) external.push(request.url());
  });
  await page.goto(`${baseUrl}/VEGO-AI-Research-Hub.html#overview`, {
    waitUntil: "networkidle",
  });
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  if (overflow > 1) {
    const wide = await page.evaluate(() =>
      [...document.querySelectorAll("body *")]
        .map((element) => {
          const rect = element.getBoundingClientRect();
          return {
            tag: element.tagName,
            id: element.id,
            cls: typeof element.className === "string" ? element.className : "",
            left: rect.left,
            right: rect.right,
            width: rect.width,
          };
        })
        .filter((item) => item.right > document.documentElement.clientWidth + 1 || item.left < -1)
        .sort((a, b) => b.right - a.right)
        .slice(0, 6),
    );
    failures.push(`${viewport.width}px: overflow ${overflow}px ${JSON.stringify(wide)}`);
  }
  const assertions = [
    ["#experiment-grid .experiment-card", 41, "experiment cards"],
    ["#comparison-lanes .evidence-lane", 5, "baseline comparison lanes"],
    ["#capability-matrix > div:not(.metric-meta)", 24, "capability matrix cells"],
    ["#capability-matrix > .metric-meta", 1, "capability claim boundary"],
    ["#runtime-cards .arch-card", 3, "runtime cards"],
    ["#topology-cards .arch-card", 3, "topology cards"],
    ["#label-funnel .funnel-stage", 4, "label stages"],
    ["#accuracy-panels .empty-result", 4, "blank performance cards"],
    ["#paired-matrix .matrix-empty", 4, "blank paired cells"],
    ["#source-grid .source-card", 9, "source cards"],
  ];
  for (const [selector, expected, label] of assertions) {
    const actual = await page.locator(selector).count();
    if (actual !== expected) failures.push(`${viewport.width}px: expected ${expected} ${label}, got ${actual}`);
  }
  if (!(await page.locator("#gate-summary").textContent())?.includes("0/24")) {
    failures.push(`${viewport.width}px: zero-label gate is not visible`);
  }
  if (!(await page.locator("#overview-kpis").textContent())?.includes("NOT YET COMPUTABLE")) {
    failures.push(`${viewport.width}px: not-computable result is not visible`);
  }
  const embeddedRunCount = await page.evaluate(
    () => new Set(JSON.parse(document.getElementById("bigui-catalog").textContent).acceptedRunBundles.map((bundle) => bundle.envelope.experimentId)).size,
  );
  const renderedRunCount = await page.locator("#run-grid .run-card").count();
  if (renderedRunCount !== embeddedRunCount) {
    failures.push(`${viewport.width}px: expected ${embeddedRunCount} run cards, got ${renderedRunCount}`);
  }
  if (!(await page.locator("#executed-kpis").textContent())?.includes("Measured observations")) {
    failures.push(`${viewport.width}px: executed metric summary is missing`);
  }
  if (errors.length) failures.push(`${viewport.width}px: console errors: ${errors.join(" | ")}`);
  if (external.length) failures.push(`${viewport.width}px: external requests: ${external.join(" | ")}`);
  if ([390, 1440].includes(viewport.width)) {
    await page.screenshot({
      path: path.join(qaDir, `bigui-${viewport.width}.png`),
      fullPage: true,
    });
  }
  await context.close();
}

try {
  for (const viewport of [
    { width: 320, height: 568 },
    { width: 390, height: 844 },
    { width: 768, height: 1024 },
    { width: 1024, height: 768 },
    { width: 1440, height: 900 },
  ]) {
    await verifyPage(viewport);
  }

  const interaction = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await interaction.goto(`${baseUrl}/VEGO-AI-Research-Hub.html#experiments`, {
    waitUntil: "networkidle",
  });
  await interaction.locator("#filter-evidence").selectOption("synthetic");
  if ((await interaction.locator("#experiment-grid .experiment-card").count()) !== 3) {
    failures.push("synthetic evidence filter did not return three experiments");
  }
  await interaction.locator("#filter-evidence").selectOption("");
  await interaction.locator('#experiment-grid [data-id="EXP-033"]').focus();
  await interaction.keyboard.press("Enter");
  if (!(await interaction.locator("#dialog-title").textContent())?.includes("EXP-033")) {
    failures.push("keyboard activation did not open EXP-033");
  }
  await interaction.locator("#dialog-close").click();
  await interaction.locator("#language-toggle").click();
  if ((await interaction.locator("html").getAttribute("dir")) !== "rtl") {
    failures.push("Hebrew mode did not set RTL");
  }
  if ((await interaction.locator("#language-toggle").textContent()) !== "English") {
    failures.push("language toggle did not preserve the return label");
  }
  await interaction.close();

  const direct = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await direct.goto(`${baseUrl}/VEGO-AI-Research-Hub.html#experiment-EXP-034`, {
    waitUntil: "networkidle",
  });
  if (!(await direct.locator("#dialog-title").textContent())?.includes("EXP-034")) {
    failures.push("direct EXP-034 route failed");
  }
  await direct.locator("#dialog-close").click();
  await direct.close();

  const compare = await browser.newPage({ viewport: { width: 1024, height: 768 } });
  await compare.goto(`${baseUrl}/VEGO-AI-Research-Hub.html#results`, {
    waitUntil: "networkidle",
  });
  const leftReplay = await compare.locator('#compare-left option').evaluateAll((options) =>
    options.find((option) => option.textContent.startsWith("EXP-006"))?.value,
  );
  const rightReplay = await compare.locator('#compare-right option').evaluateAll((options) =>
    options.find((option) => option.textContent.startsWith("EXP-007"))?.value,
  );
  const faultRun = await compare.locator('#compare-right option').evaluateAll((options) =>
    options.find((option) => option.textContent.startsWith("EXP-035"))?.value,
  );
  await compare.locator("#compare-left").selectOption(leftReplay);
  await compare.locator("#compare-right").selectOption(rightReplay);
  await compare.locator("#compare-button").click();
  if (!(await compare.locator("#compare-result").textContent())?.includes("Not directly comparable")) {
    failures.push("unrelated EXP-006 and EXP-007 records were not refused");
  }
  await compare.locator("#compare-right").selectOption(faultRun);
  await compare.locator("#compare-button").click();
  if (!(await compare.locator("#compare-result").textContent())?.includes("Not directly comparable")) {
    failures.push("synthetic fault record was not refused for direct comparison");
  }
  await compare.emulateMedia({ media: "print", reducedMotion: "reduce" });
  const printOverflow = await compare.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  if (printOverflow > 1) failures.push(`print: overflow ${printOverflow}px`);
  await compare.close();
} finally {
  await browser.close();
  await new Promise((resolve) => server.close(resolve));
}

if (failures.length) {
  for (const failure of failures) console.error(`FAIL: ${failure}`);
  process.exit(1);
}
console.log("BigUI browser smoke: PASS");
