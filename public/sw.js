// pages: network-first (always fresh after an update); data files: cache-first with background refresh
const C = 'shaykhain-v2';
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())
));
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin || u.pathname.startsWith('/api/')) return;
  const isPage = e.request.mode === 'navigate' || /\.(html|js|webmanifest)$/.test(u.pathname) || u.pathname === '/';
  e.respondWith(caches.open(C).then(async c => {
    if (isPage){
      try { const r = await fetch(e.request); if (r.ok) c.put(e.request, r.clone()); return r; }
      catch(err){ return (await c.match(e.request, {ignoreSearch: true})) || Response.error(); }
    }
    const hit = await c.match(e.request, {ignoreSearch: true});
    const net = fetch(e.request).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; }).catch(() => hit);
    return hit || net;
  }));
});
