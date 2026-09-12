/* Local-only browser migration regression. Requires Playwright and installed Edge.
   Run: node tests/browser/provenance.cjs
   Override SAFETASK_TEST_BROWSER for another Chromium executable. */
const {chromium} = require("playwright");
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const root = path.resolve(__dirname, "../..");
const app = path.join(root, "safetask/apps/legacy_scc");
let upgraded = false;
const oldWorker = `
self.addEventListener('install', e => e.waitUntil((async () => {
 const c = await caches.open('safetask-ai-v1');
 await c.put('/policy-packs/gaming/regulations.json', new Response('[{"code":"OBSOLETE"}]'));
 await self.skipWaiting();
})()));
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
`;
const oldPage = `<html><body><input id="unsaved"><script>
navigator.serviceWorker.register('/sw.js');
</script></body></html>`;
const server = http.createServer((req, res) => {
  res.setHeader("Cache-Control", "no-store");
  const url = new URL(req.url, "http://localhost");
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/policy-packs/")) {
    res.setHeader("Content-Type", "application/json");
    return res.end('{"entries":[],"status":"test-network-response"}');
  }
  const file = url.pathname === "/" ? "index.html" : url.pathname.slice(1);
  if (file === "sw.js") {
    res.setHeader("Content-Type", "application/javascript");
    return res.end(upgraded ? fs.readFileSync(path.join(app, file)) : oldWorker);
  }
  if (file === "index.html" && !upgraded) {
    res.setHeader("Content-Type", "text/html");
    return res.end(oldPage);
  }
  const full = path.resolve(app, file);
  if (!full.startsWith(app + path.sep) || !fs.existsSync(full)) {
    res.statusCode = 404; return res.end();
  }
  res.setHeader("Content-Type", file.endsWith(".js") ? "application/javascript" :
    file.endsWith(".css") ? "text/css" : file.endsWith(".json") ? "application/json" : "text/html");
  res.end(fs.readFileSync(full));
});

(async () => {
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const origin = "http://127.0.0.1:" + server.address().port;
  const browser = await chromium.launch({headless: true,
    executablePath: process.env.SAFETASK_TEST_BROWSER || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    args: ["--disable-background-networking", "--disable-component-update",
      "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1"]});
  try {
    const context = await browser.newContext();
    await context.route("**/*", route => route.request().url().startsWith(origin + "/") ?
      route.continue() : route.abort());
    const page = await context.newPage();
    await page.goto(origin);
    await page.waitForFunction(() => navigator.serviceWorker.controller?.state === "activated");
    await page.fill("#unsaved", "retain this unsaved incident");
    await page.evaluate(async () => { await caches.open("unrelated-app-cache"); });
    upgraded = true;
    await page.evaluate(async () => {
      await new Promise(async resolve => {
        navigator.serviceWorker.addEventListener("controllerchange", resolve, {once: true});
        await (await navigator.serviceWorker.getRegistration()).update();
      });
    });
    await page.waitForFunction(() => navigator.serviceWorker.controller?.state === "activated");
    assert.equal(await page.inputValue("#unsaved"), "retain this unsaved incident");
    assert.equal(await page.locator("[data-provenance-version]").count(), 0);
    let keys = await page.evaluate(() => caches.keys());
    assert(!keys.includes("safetask-ai-v1"));
    assert(keys.includes("safetask-ai-provenance-v2"));
    assert(keys.includes("unrelated-app-cache"));
    assert.equal(await page.evaluate(async () => (await fetch("/policy-packs/gaming/regulations.json")).status), 410);
    console.log("PASS migration preserves unsaved old page; removes only owned obsolete caches; retires gaming");
    // The user chooses when to reload. Only this corrected page can declare migration complete.
    await page.reload();
    await page.waitForFunction(() => document.querySelector("#provenance-migration")?.dataset.complete === "true");
    assert.equal(await page.locator("body").getAttribute("data-provenance-version"), "2");
    assert(!(await page.textContent("body")).includes("NIGC MICS 25 CFR"));
    await page.evaluate(async () => {
      await fetch("/api/test");
      await fetch("/policy-packs/test/regulations.json");
    });
    const cached = await page.evaluate(async () => {
      const cache = await caches.open("safetask-ai-provenance-v2");
      return (await cache.keys()).map(req => new URL(req.url).pathname);
    });
    assert(!cached.some(p => p.startsWith("/api/") || p.startsWith("/policy-packs/")));
    console.log("PASS corrected page + active v2 worker required; no API or policy responses cached");
    await context.setOffline(true);
    const offline = await page.evaluate(async () => {
      const paths = ["/policy-packs/gaming/regulations.json", "/policy-packs/test/regulations.json", "/api/test"];
      return await Promise.all(paths.map(async path => {
        const res = await fetch(path); return {status: res.status, body: await res.json()};
      }));
    });
    assert.deepEqual(offline.map(r => r.status), [410, 503, 503]);
    assert(offline.every(r => r.body.entries.length === 0));
    await page.reload();
    await page.waitForFunction(() => document.querySelector("#provenance-migration")?.dataset.complete === "true");
    assert(!(await page.textContent("body")).includes("NIGC MICS 25 CFR"));
    console.log("PASS migrated offline page remains corrected; retired/uncached policy never falls back");
    await context.setOffline(false);
    const render = await context.newPage();
    await render.setContent('<div id="no-incident-msg"></div><div id="review-packet"></div>' +
      ["packet-id", "packet-status", "packet-location", "packet-desc", "packet-escalation",
       "packet-source-status", "policy-list"].map(id => '<div id="' + id + '"></div>').join(""));
    const ui = fs.readFileSync(path.join(root, "safetask/web_ui/app.js"), "utf8");
    const start = ui.indexOf("    function displayReviewPacket(packet)");
    const body = ui.slice(start, ui.indexOf("    // Epic 16:", start));
    const packet = {incident_id: "TEST", status: "Awaiting Review", details: {location: "Test", description: "Neutral"},
      escalation_prompt: "Human review required", policy_sources_status: "reviewed_sources",
      source_notice: "Test-only source", recommended_review: [{title: "Neutral reviewed test", source: "test.md",
        excerpt: "Neutral text", page: null, provenance_label: "Reviewed external source record - applicability requires human review",
        provenance: {provenance_version: 1, source_kind: "external_source", review_status: "reviewed",
          review_id: "test-review", scope: "Test scope", source_locator: "https://example.org/source"}}]};
    await render.evaluate(({body, packet}) => new Function(body + ";return displayReviewPacket;")()(packet), {body, packet});
    assert((await render.textContent("#policy-list")).includes("applicability requires human review"));
    assert((await render.textContent("#policy-list")).includes("Test scope"));
    assert((await render.textContent("#policy-list")).includes("Page: Not applicable"));
    packet.recommended_review.push({title: "Forged card", excerpt: "Unverified text"});
    await render.evaluate(({body, packet}) => new Function(body + ";return displayReviewPacket;")()(packet), {body, packet});
    assert(!(await render.textContent("#policy-list")).includes("Neutral reviewed test"));
    assert((await render.textContent("#policy-list")).includes("No reviewed sources"));
    console.log("PASS incident renderer preserves provenance and suppresses a malformed/partial source set");
    await render.setContent('<button id="search"></button><input id="query" value="neutral"><div id="results"></div>');
    const field = fs.readFileSync(path.join(root, "src/web/static/app.js"), "utf8");
    const handler = field.slice(field.indexOf('    searchBtn.addEventListener("click"'),
      field.indexOf("    async function loadNotes"));
    await render.evaluate(handler => {
      window.testResponse = {retrieval_status: "ready", results: [{metadata: {title: "Synthetic example", source: "test.md",
        provenance_label: "Synthetic test material - not reviewed authority", provenance: {source_kind: "synthetic"}},
        content: "Neutral synthetic text"}]};
      window.fetch = async () => ({ok: true, json: async () => window.testResponse});
      new Function("searchBtn", "searchInput", "searchResults", "escapeHTML", handler)(
        document.querySelector("#search"), document.querySelector("#query"), document.querySelector("#results"),
        value => String(value ?? "").replaceAll("<", "&lt;").replaceAll(">", "&gt;"));
    }, handler);
    await render.click("#search");
    await render.waitForFunction(() => document.querySelector("#results").textContent.includes("Synthetic test material"));
    await render.evaluate(() => { window.testResponse = {retrieval_status: "index_required", results: []}; });
    await render.click("#search");
    await render.waitForFunction(() => document.querySelector("#results").textContent.includes("index_required"));
    assert(!(await render.textContent("#results")).includes("Neutral synthetic text"));
    console.log("PASS search renderer labels synthetic results and clears stale results on index/error status");
    await context.close();
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
