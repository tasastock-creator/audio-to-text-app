self.addEventListener('install',e=>e.waitUntil(caches.open('tasa-audio-v12').then(c=>c.addAll(['/','/index.html','/manifest.webmanifest','/sw.js','/transcription-worker.js','/icon-192.png','/icon-512.png']))));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!=='tasa-audio-v12').map(k=>caches.delete(k))))));
self.addEventListener('fetch',e=>e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))));
