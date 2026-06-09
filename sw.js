self.addEventListener("install", e => {
    e.waitUntil(
        caches.open("elli-v1").then(cache => {
            return cache.addAll([
                "index.html",
                "manifest.json",
                "elli_avatar.png",
                "elli_talk.apng",
                "elli_icon_192.png"
            ]);
        })
    );
});

self.addEventListener("fetch", e => {
    e.respondWith(
        caches.match(e.request).then(resp => resp || fetch(e.request))
    );
});