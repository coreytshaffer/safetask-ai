/* Policy migration is independent of the legacy app. Never navigate an open client. */
const VERSION = 2;
const CACHE_NAME = "safetask-ai-provenance-v2";
const ASSETS = ["./", "./index.html", "./styles.css", "./app.js", "./manifest.json", "./provenance-migration.js"];
const assetURLs = new Set(ASSETS.map(path => new URL(path, self.registration.scope).href));
const unavailable = () => new Response(JSON.stringify({
  status: "retrieval_unavailable", entries: [], message: "Policy data unavailable offline"
}), {status: 503, headers: {"Content-Type": "application/json", "Cache-Control": "no-store"}});
const state = {type: "SAFETASK_PROVENANCE_STATE", workerVersion: VERSION, reloadRequired: true};

self.addEventListener("install", event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await cache.addAll(ASSETS.map(path => new Request(new URL(path, self.registration.scope), {cache: "reload"})));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key.startsWith("safetask-ai-") && key !== CACHE_NAME)
      .map(key => caches.delete(key)));
    await self.clients.claim();
    const clients = await self.clients.matchAll({type: "window", includeUncontrolled: true});
    clients.forEach(client => client.postMessage(state));
  })());
});

self.addEventListener("message", event => {
  if (event.data?.type === "SAFETASK_PROVENANCE_STATE_REQUEST") {
    const reply = {...state, reloadRequired: event.data.pageVersion !== VERSION};
    if (event.ports[0]) event.ports[0].postMessage(reply);
    else event.source?.postMessage(reply);
  }
});

self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  const policy = url.pathname.startsWith("/policy-packs/") || url.pathname.endsWith("/regulations.json");
  const api = url.pathname.startsWith("/api/");
  const retired = url.pathname === "/policy-packs/gaming/regulations.json" ||
    url.pathname.endsWith("/domains/gaming/regulations.json") || url.pathname === "/regulations.json";
  if (retired) {
    event.respondWith(Promise.resolve(new Response(JSON.stringify({
      status: "retired", entries: [], message: "Legacy gaming corpus retired"
    }), {status: 410, headers: {"Content-Type": "application/json", "Cache-Control": "no-store"}})));
    return;
  }
  if (policy || api) {
    event.respondWith(fetch(new Request(event.request, {cache: "no-store"})).catch(unavailable));
    return;
  }
  if (event.request.method !== "GET" || !assetURLs.has(url.href)) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    try {
      const response = await fetch(new Request(event.request, {cache: "no-store"}));
      if (response.ok) await cache.put(event.request, response.clone());
      return response;
    } catch {
      return await cache.match(event.request) || new Response("Offline shell unavailable", {status: 503});
    }
  })());
});
