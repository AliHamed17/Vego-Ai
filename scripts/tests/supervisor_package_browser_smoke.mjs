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

function contentType(filePath) {
  if (filePath.endsWith(".html")) return "text/html; charset=utf-8";
  if (filePath.endsWith(".json")) return "application/json; charset=utf-8";
  if (filePath.endsWith(".js") || filePath.endsWith(".mjs")) return "text/javascript; charset=utf-8";
  return "application/octet-stream";
}

const server = http.createServer((request, response) => {
  const rawPath = new URL(request.url, "http://127.0.0.1").pathname;
  const requested = rawPath === "/" ? "/VEGO-AI-July1-PointByPoint-EN-HE.html" : rawPath;
  const filePath = path.resolve(repoRoot, `.${decodeURIComponent(requested)}`);
  if (!filePath.startsWith(repoRoot) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    response.writeHead(404);
    response.end("Not found");
    return;
  }
  response.writeHead(200, { "Content-Type": contentType(filePath), "Cache-Control": "no-store" });
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
    const consoleErrors = [];
    const externalRequests = [];
    page.on("console", (message) => {
      if (message.type() === "error") consoleErrors.push(message.text());
    });
    page.on("pageerror", (error) => consoleErrors.push(error.message));
    page.on("request", (request) => {
      const url = new URL(request.url());
      if (url.origin !== baseUrl) externalRequests.push(request.url());
    });
    await page.goto(`${baseUrl}/VEGO-AI-July1-PointByPoint-EN-HE.html#story-1`, {
      waitUntil: "networkidle",
    });
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    if (overflow > 1) failures.push(`${viewport.width}px: horizontal overflow ${overflow}px`);
    if ((await page.locator(".puzzle-piece").count()) !== 6) failures.push(`${viewport.width}px: expected 6 puzzle pieces`);
    if ((await page.locator("#stepCount").textContent())?.trim() !== "Step 1 of 6") {
      failures.push(`${viewport.width}px: initial story step mismatch`);
    }
    await page.locator('[data-action="complete"]').click();
    if (!(await page.locator("#stepCount").textContent())?.includes("Complete")) {
      failures.push(`${viewport.width}px: complete-system action failed`);
    }
    await page.locator('[data-lang="he"]').click();
    if ((await page.locator("html").getAttribute("dir")) !== "rtl") failures.push(`${viewport.width}px: Hebrew RTL failed`);
    await page.locator('[data-mode="explore"]').click();
    if (!(await page.locator("#exploreView").isVisible())) failures.push(`${viewport.width}px: Explore mode remained hidden`);
    if ((await page.locator('[id^="directive-D"]').count()) !== 12) failures.push(`${viewport.width}px: directive count mismatch`);
    if ((await page.locator('[id^="experiment-EXP-"]').count()) !== 19) failures.push(`${viewport.width}px: experiment count mismatch`);
    if ((await page.locator('[id^="decision-M-"]').count()) !== 6) failures.push(`${viewport.width}px: decision count mismatch`);
    if (consoleErrors.length) failures.push(`${viewport.width}px: console errors: ${consoleErrors.join(" | ")}`);
    if (externalRequests.length) failures.push(`${viewport.width}px: external requests: ${externalRequests.join(" | ")}`);
    await page.close();
  }

  const direct = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await direct.goto(`${baseUrl}/VEGO-AI-July1-PointByPoint-EN-HE.html#story-6`, { waitUntil: "networkidle" });
  if ((await direct.locator("#stepCount").textContent())?.trim() !== "Step 6 of 6") failures.push("direct #story-6 route failed");
  if (!(await direct.locator("#guidedView").isVisible())) failures.push("direct #story-6 did not force Guided mode");
  await direct.close();

  const gallery = await browser.newPage({ viewport: { width: 390, height: 844 } });
  for (const file of ["visualizations-gallery/index.html", "VEGO-AI-Research-Hub.html"]) {
    await gallery.goto(`${baseUrl}/${file}`, { waitUntil: "networkidle" });
    const overflow = await gallery.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    if (overflow > 1) failures.push(`${file}: horizontal overflow ${overflow}px`);
  }
  await gallery.close();
} finally {
  await browser.close();
  await new Promise((resolve) => server.close(resolve));
}

if (failures.length) {
  for (const failure of failures) console.error(`FAIL: ${failure}`);
  process.exit(1);
}
console.log("supervisor package browser smoke: PASS");
