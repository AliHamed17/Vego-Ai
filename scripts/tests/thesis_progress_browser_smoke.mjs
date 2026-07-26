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
const qaDir = path.join(repoRoot, "tmp", "thesis-progress-qa");
fs.mkdirSync(qaDir, { recursive: true });

const server = http.createServer((request, response) => {
  const requested = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
  const filePath = path.resolve(repoRoot, `.${requested === "/" ? "/VEGO-AI-Thesis-Baseline-Progress.html" : requested}`);
  if (!filePath.startsWith(repoRoot) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    response.writeHead(404);
    response.end("Not found");
    return;
  }
  const type = filePath.endsWith(".html") ? "text/html; charset=utf-8" : "application/octet-stream";
  response.writeHead(200, { "Content-Type": type, "Cache-Control": "no-store" });
  fs.createReadStream(filePath).pipe(response);
});

await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const address = server.address();
const baseUrl = `http://127.0.0.1:${address.port}`;
const browser = await chromium.launch({ headless: true });
const failures = [];

try {
  for (const viewport of [
    { width: 320, height: 568 },
    { width: 390, height: 844 },
    { width: 768, height: 1024 },
    { width: 1024, height: 768 },
    { width: 1440, height: 900 },
  ]) {
    const page = await browser.newPage({ viewport });
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
    await page.goto(`${baseUrl}/VEGO-AI-Thesis-Baseline-Progress.html#B0`, {
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
            return { tag: element.tagName, id: element.id, cls: element.className, left: rect.left, right: rect.right, width: rect.width };
          })
          .filter((item) => item.right > document.documentElement.clientWidth + 1 || item.left < -1)
          .sort((a, b) => b.right - a.right)
          .slice(0, 5),
      );
      failures.push(`${viewport.width}px: horizontal overflow ${overflow}px; ${JSON.stringify(wide)}`);
    }
    if ((await page.locator("#baseline-steps button").count()) !== 6) {
      failures.push(`${viewport.width}px: expected six baseline steps`);
    }
    if ((await page.locator("#experiment-roadmap .exp").count()) !== 9) {
      failures.push(`${viewport.width}px: expected nine roadmap experiments`);
    }
    if ((await page.locator("#model-protocols .protocol").count()) !== 2) {
      failures.push(`${viewport.width}px: expected two model protocols`);
    }
    if ((await page.locator("#rq-traceability .trace-row").count()) !== 7) {
      failures.push(`${viewport.width}px: expected seven RQ/hypothesis traceability rows`);
    }
    if ((await page.locator("#decision-dependencies .decision").count()) !== 6) {
      failures.push(`${viewport.width}px: expected six decision dependencies`);
    }
    if ((await page.locator("#risk-path .risk").count()) !== 4) {
      failures.push(`${viewport.width}px: expected four research risk gates`);
    }
    if ((await page.locator("#label-funnel .funnel-stage").count()) !== 4) {
      failures.push(`${viewport.width}px: expected four label-gate funnel stages`);
    }
    if ((await page.locator(".matrix .empty").count()) !== 4) {
      failures.push(`${viewport.width}px: paired matrix should contain four empty cells`);
    }
    await page.locator('[data-id="B5"]').click();
    if (!(await page.locator("#baseline-detail").textContent())?.includes("target 48")) {
      failures.push(`${viewport.width}px: B5 detail did not update`);
    }
    await page.locator('#decision-dependencies [data-id="M-05"]').click();
    if ((await page.locator('#experiment-roadmap [data-id="EXP-020"]').getAttribute("class"))?.includes("is-related") !== true) {
      failures.push(`${viewport.width}px: M-05 did not cross-highlight EXP-020`);
    }
    await page.locator('#rq-traceability [data-id="E-RQ2"]').focus();
    await page.keyboard.press("Enter");
    if (!(await page.locator("#context-detail").textContent())?.includes("E-RQ2")) {
      failures.push(`${viewport.width}px: keyboard activation did not update the evidence context`);
    }
    if (errors.length) failures.push(`${viewport.width}px: console errors: ${errors.join(" | ")}`);
    if (external.length) failures.push(`${viewport.width}px: external requests: ${external.join(" | ")}`);
    if ([390, 1440].includes(viewport.width)) {
      await page.screenshot({
        path: path.join(qaDir, `thesis-progress-${viewport.width}.png`),
        fullPage: true,
      });
    }
    await page.close();
  }

  const direct = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await direct.goto(`${baseUrl}/VEGO-AI-Thesis-Baseline-Progress.html#B3`, {
    waitUntil: "networkidle",
  });
  if ((await direct.locator('[data-id="B3"]').getAttribute("aria-pressed")) !== "true") {
    failures.push("direct #B3 route failed");
  }
  await direct.emulateMedia({ media: "print", reducedMotion: "reduce" });
  const printOverflow = await direct.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  if (printOverflow > 1) failures.push(`print: horizontal overflow ${printOverflow}px`);
  await direct.close();

  const experimentRoute = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await experimentRoute.goto(`${baseUrl}/VEGO-AI-Thesis-Baseline-Progress.html#EXP-023`, {
    waitUntil: "networkidle",
  });
  if ((await experimentRoute.locator('#experiment-roadmap [data-id="EXP-023"]').getAttribute("aria-pressed")) !== "true") {
    failures.push("direct #EXP-023 route failed");
  }
  if ((await experimentRoute.locator('#baseline-steps [data-id="B3"]').getAttribute("class"))?.includes("is-related") !== true) {
    failures.push("EXP-023 route did not cross-highlight B3");
  }
  await experimentRoute.close();

  const modelRoute = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await modelRoute.goto(`${baseUrl}/VEGO-AI-Thesis-Baseline-Progress.html#EXP-029`, {
    waitUntil: "networkidle",
  });
  if ((await modelRoute.locator('#model-protocols [data-id="EXP-029"]').getAttribute("aria-pressed")) !== "true") {
    failures.push("direct #EXP-029 route failed");
  }
  if ((await modelRoute.locator('#baseline-steps [data-id="B0"]').getAttribute("class"))?.includes("is-related") !== true) {
    failures.push("EXP-029 route did not cross-highlight B0");
  }
  await modelRoute.close();

  for (const entry of ["VEGO-AI-Research-Hub.html", "visualizations-gallery/index.html"]) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(`${baseUrl}/${entry}`, { waitUntil: "networkidle" });
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    if (overflow > 1) failures.push(`${entry}: horizontal overflow ${overflow}px`);
    if ((await page.locator('a[href*="VEGO-AI-Thesis-Baseline-Progress.html"]').count()) < 1) {
      failures.push(`${entry}: thesis evidence entry missing`);
    }
    await page.close();
  }
} finally {
  await browser.close();
  await new Promise((resolve) => server.close(resolve));
}

if (failures.length) {
  for (const failure of failures) console.error(`FAIL: ${failure}`);
  process.exit(1);
}
console.log("thesis progress browser smoke: PASS");
