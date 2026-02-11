// Service Worker caching strategy tuned for "latest" freshness ✅
// - UI/core: cache-first
// - /latest/*.json and /latest/*.bin: network-first (avoid stale time_index/meta)
// - tiles: stale-while-revalidate (fast + keeps updating)
const CACHE = "seydyaar-v0.3.0";
const CORE = [
  "./",
  "./index.html",
  "./app.html",
  "./styles.css",
  "./home.js",
  "./app.js",
  "./manifest.json",
  "./assets/logo.png",
  "./latest/meta_index.json",
  "./latest/preview.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(k => (k === CACHE) ? null : caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  const path = url.pathname;
  const isLatest = path.includes("/latest/");
  const isJson = path.endsWith(".json") || path.endsWith(".geojson");
  const isBin = path.endsWith(".bin") || path.endsWith(".tif") || path.endsWith(".pmtiles") || path.endsWith(".png");
  const isTile = path.includes("/tiles/") || path.match(/\/(\d+)\/(\d+)\/(\d+)\.(png|jpg|webp)$/);

  // Network-first for latest metadata and binary layers to avoid stale runs/times
  if (isLatest && (isJson || isBin) && !isTile) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE);
      try {
        const fresh = await fetch(req, {cache: "no-store"});
        if (fresh && fresh.status === 200 && req.method === "GET") {
          cache.put(req, fresh.clone());
        }
        return fresh;
      } catch (err) {
        const cached = await cache.match(req);
        return cached || new Response("Offline", {status: 503});
      }
    })());
    return;
  }

  // Stale-while-revalidate for tiles (fast + keeps updating)
  if (isTile) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const cached = await cache.match(req);
      const network = fetch(req).then((fresh) => {
        if (fresh && fresh.status === 200 && req.method === "GET") cache.put(req, fresh.clone());
        return fresh;
      }).catch(() => null);
      return cached || (await network) || new Response("Offline", {status: 503});
    })());
    return;
  }

  // Core assets: cache-first
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(req);
    if (cached) return cached;
    try {
      const fresh = await fetch(req);
      if (fresh && fresh.status === 200 && req.method === "GET") cache.put(req, fresh.clone());
      return fresh;
    } catch (err) {
      return cached || new Response("Offline", {status: 503});
    }
  })());
});
