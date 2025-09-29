const CACHE = "pc-hopkins-v1";
const ASSETS = [
  "/", "/index.html", "/style.css", "/script.js",
  "/assets/logo.jpg", "/assets/hero.jpg",
  "/manifest.json"
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

self.addEventListener("fetch", e => {
  const { request } = e;
  // Network-first for HTML, cache-first for assets
  if (request.mode === "navigate") {
    e.respondWith(
      fetch(request).catch(() => caches.match("/index.html"))
    );
  } else {
    e.respondWith(
      caches.match(request).then(res => res || fetch(request))
    );
  }
});
