import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const artifacts = path.join(root, ".temp/report-browser");
let fixture;
let server;
let browser;
let origin;

before(async () => {
  fs.mkdirSync(artifacts, { recursive: true });
  fixture = fs.mkdtempSync(path.join(root, ".temp/report-"));
  const generated = spawnSync("python3", ["-m", "tools.fleet_street", "report", "--input", "examples/report.json", "--budget", "examples/budget.json", "--directory", path.join(fixture, "report")], { cwd: root, encoding: "utf8", timeout: 10000 });
  assert.equal(generated.status, 0, generated.stderr);
  const files = new Map([["/", ["index.html", "text/html"]], ["/assets/report.css", ["assets/report.css", "text/css"]], ["/assets/proscenium.svg", ["assets/proscenium.svg", "image/svg+xml"]], ["/assets/LICENSE.txt", ["assets/LICENSE.txt", "text/plain"]], ["/data/budget.json", ["data/budget.json", "application/json"]]]);
  server = http.createServer((request, response) => {
    const file = files.get(new URL(request.url, "http://localhost").pathname);
    if (!file) { response.writeHead(404); response.end(); return; }
    response.writeHead(200, { "Content-Type": file[1], "Content-Security-Policy": "default-src 'none'; style-src 'self'; img-src 'self'; sandbox allow-scripts; base-uri 'none'; form-action 'none'", "Referrer-Policy": "no-referrer", "X-Content-Type-Options": "nosniff" });
    response.end(fs.readFileSync(path.join(fixture, "report", file[0])));
  });
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  origin = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch({ executablePath: process.env.BROWSER_EXECUTABLE ?? "/usr/bin/google-chrome", args: ["--no-sandbox", "--disable-dev-shm-usage", "--disable-breakpad", "--disable-crash-reporter"], env: { ...process.env, TMPDIR: path.join(root, ".temp"), XDG_CONFIG_HOME: path.join(artifacts, "config"), XDG_CACHE_HOME: path.join(artifacts, "cache") } });
});

after(async () => {
  if (browser) await browser.close();
  if (server) await new Promise(resolve => server.close(resolve));
  if (fixture) fs.rmSync(fixture, { recursive: true, force: true });
});

test("report uses local assets and readable figures inside an opaque publication sandbox", async context => {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  context.after(() => page.close());
  const errors = [];
  const outside = [];
  page.on("pageerror", error => errors.push(error.message));
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("request", request => { if (!request.url().startsWith(origin)) outside.push(request.url()); });
  await page.goto(origin, { waitUntil: "networkidle" });
  assert.equal(await page.getByRole("heading", { level: 1 }).innerText(), "The River Bell");
  assert.deepEqual(await page.locator(".total strong").allTextContents(), ["GBP 4,745.25", "GBP 5,203.00", "GBP -457.75"]);
  assert.equal(await page.locator(".notice").innerText().then(text => text.includes("Fictional example")), true);
  assert.equal(await page.locator("img").evaluate(image => image.complete && image.naturalWidth > 0), true);
  assert.equal(await page.evaluate(() => { try { localStorage.getItem("not-available"); return false; } catch { return true; } }), true);
  await page.screenshot({ path: path.join(artifacts, "desktop.png"), fullPage: true });
  assert.deepEqual(errors, []);
  assert.deepEqual(outside, []);
});

test("report is usable at phone widths and its JSON link resolves", async context => {
  const page = await browser.newPage();
  context.after(() => page.close());
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(origin);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth <= 1), true, `${width}px page width`);
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: path.join(artifacts, "mobile.png"), fullPage: true });
  const response = await page.request.get(`${origin}/data/budget.json`);
  assert.equal(response.status(), 200);
  assert.equal((await response.json()).break_even_paid_tickets, 297);
});
