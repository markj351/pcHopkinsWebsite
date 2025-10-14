const CACHE = "pc-hopkins-v1";
const ASSETS = [
  "/pcHopkinsWebsite/",
  "/pcHopkinsWebsite/index.html",
  "/pcHopkinsWebsite/style.css",
  "/pcHopkinsWebsite/script.js",
  "/pcHopkinsWebsite/assets/churchLogo.jpg",
  "/pcHopkinsWebsite/manifest.json",
  "/pcHopkinsWebsite/offline.html"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Network-first for navigations; cache-first for assets
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req).catch(() => caches.match("/pcHopkinsWebsite/offline.html"))
    );
  } else {
    e.respondWith(
      caches.match(req).then(res => res || fetch(req))
    );
  }
});
