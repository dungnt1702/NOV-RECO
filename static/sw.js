// Service Worker for NOV-RECO PWA
const CACHE_NAME = 'nov-reco-v1.0.0';
const urlsToCache = [
  '/',
  '/static/css/base.css',
  '/static/css/dashboard/main.css',
  '/static/css/notifications.css',
  '/static/css/footer.css',
  '/static/js/base.js',
  '/static/js/dashboard/main.js',
  '/static/js/notifications.js',
  '/static/js/icons.js',
  '/static/js/vendor/bootstrap.bundle.min.js',
  '/static/css/vendor/bootstrap.min.css',
  '/static/css/vendor/inter-fonts.css',
  '/static/css/vendor/fontawesome.css',
  '/static/logo.svg',
  '/static/favicon.png'
];

// Install event - cache resources
self.addEventListener('install', function(event) {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .catch(function(error) {
        console.error('Cache installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', function(event) {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip external requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Return cached version or fetch from network
        if (response) {
          console.log('Serving from cache:', event.request.url);
          return response;
        }

        console.log('Fetching from network:', event.request.url);
        return fetch(event.request).then(function(response) {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response
          const responseToCache = response.clone();

          caches.open(CACHE_NAME)
            .then(function(cache) {
              cache.put(event.request, responseToCache);
            });

          return response;
        }).catch(function(error) {
          console.error('Fetch failed:', error);
          // Return offline page if available
          return caches.match('/offline/');
        });
      })
  );
});

// Background sync for check-in data
self.addEventListener('sync', function(event) {
  if (event.tag === 'checkin-sync') {
    console.log('Background sync for check-in data');
    event.waitUntil(syncCheckinData());
  }
});

// Push notification handling
self.addEventListener('push', function(event) {
  console.log('Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'Bạn có thông báo mới từ NOV-RECO',
    icon: '/static/logo-192.png',
    badge: '/static/logo-96.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Xem chi tiết',
        icon: '/static/icon-view.png'
      },
      {
        action: 'close',
        title: 'Đóng',
        icon: '/static/icon-close.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('NOV-RECO', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', function(event) {
  console.log('Notification clicked');
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/notifications/')
    );
  } else if (event.action === 'close') {
    // Just close the notification
    return;
  } else {
    // Default action - open app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Helper function for background sync
function syncCheckinData() {
  return new Promise(function(resolve, reject) {
    // Implement check-in data synchronization
    console.log('Syncing check-in data...');
    resolve();
  });
}

// Message handling from main thread
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
