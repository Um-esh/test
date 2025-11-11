function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = 'notification ' + type + ' show';
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

async function logoutRequest() {
    if (!confirm('Are you sure you want to logout?')) {
        return;
    }
    
    try {
        const response = await fetch('/logout', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Logout failed', 'error');
    }
}

async function initFirebase() {
    try {
        const response = await fetch('/api/firebase-config');
        const config = await response.json();
        
        if (!config.enabled) {
            console.log('Firebase not configured. Set FIREBASE_API_KEY and other Firebase environment variables to enable notifications.');
            return;
        }
        
        if (typeof firebase !== 'undefined') {
            if (!firebase.apps.length) {
                firebase.initializeApp(config.firebaseConfig);
            }
            
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/firebase-messaging-sw.js')
                    .then((registration) => {
                        console.log('Service Worker registered');
                        
                        const messaging = firebase.messaging();
                        
                        messaging.getToken({ 
                            vapidKey: config.vapidKey,
                            serviceWorkerRegistration: registration 
                        }).then((currentToken) => {
                            if (currentToken) {
                                console.log('FCM Token obtained');
                                fetch('/api/save-fcm-token', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ token: currentToken })
                                });
                            } else {
                                console.log('No registration token available.');
                            }
                        }).catch((err) => {
                            console.log('An error occurred while retrieving token:', err);
                        });
                        
                        messaging.onMessage((payload) => {
                            console.log('Message received:', payload);
                            showNotification(payload.notification.body, 'success');
                        });
                    })
                    .catch((err) => {
                        console.log('Service Worker registration failed:', err);
                    });
            }
        }
    } catch (error) {
        console.log('Firebase initialization error:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFirebase);
} else {
    initFirebase();
}
