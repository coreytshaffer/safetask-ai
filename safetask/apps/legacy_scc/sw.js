/* -------------------------------------------------------------
 * SafeTask AI Service Worker
 * Manages caching and offline availability for field safety operations
 * ------------------------------------------------------------- */

const CACHE_NAME = "safetask-ai-v1";
const ASSETS_TO_CACHE = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "/policy-packs/gaming/regulations.json",
  "./manifest.json"
];

// Install Event - cache core shell assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("SafeTask AI: Caching app assets...");
      return cache.addAll(ASSETS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

// Activate Event - clean up legacy caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log("SafeTask AI: Clearing old cache:", key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event - network-first fallback to cache
self.addEventListener("fetch", (event) => {
  // Do not intercept external API calls to LM Studio
  if (event.request.url.includes("/v1/chat/completions") || event.request.url.includes("/v1/models")) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache new network updates dynamically
        if (response.ok && event.request.method === "GET") {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Fallback to cache when offline
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          // If not in cache, trigger failure gracefully
          return new Response("SafeTask AI Offline Content Unloaded", {
            status: 503,
            statusText: "Service Offline",
            headers: new Headers({ "Content-Type": "text/plain" })
          });
        });
      })
  );
});
