// Notification System - Database Polling Method
// Fetches notifications every 10 seconds

let notificationCheckInterval;

// Initialize notification system when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Only run if user is logged in (check if notification bell exists)
    if (document.getElementById('notification-bell')) {
        fetchNotifications(); // Fetch immediately on load
        startNotificationPolling(); // Then poll every 10 seconds
    }
});

// Start polling for notifications
function startNotificationPolling() {
    // Fetch every 10 seconds
    notificationCheckInterval = setInterval(fetchNotifications, 10000);
}

// Stop polling (useful if user logs out)
function stopNotificationPolling() {
    if (notificationCheckInterval) {
        clearInterval(notificationCheckInterval);
    }
}

// Fetch notifications from server
function fetchNotifications() {
    fetch('/api/get_notifications')
        .then(response => response.json())
        .then(data => {
            updateNotificationUI(data);
        })
        .catch(error => {
            console.error('Error fetching notifications:', error);
        });
}

// Update the notification UI
function updateNotificationUI(data) {
    const badge = document.getElementById('notification-badge');
    const dropdown = document.getElementById('notification-dropdown');
    const count = data.count;

    // Update badge
    if (count > 0) {
        badge.textContent = count > 9 ? '9+' : count;
        badge.style.display = 'inline-block';
    } else {
        badge.style.display = 'none';
    }

    // Update dropdown content
    if (count === 0) {
        dropdown.innerHTML = `
            <div class="notification-item no-notifications">
                <p>No new notifications</p>
            </div>
        `;
    } else {
        dropdown.innerHTML = '';
        data.notifications.forEach(notif => {
            const notifElement = createNotificationElement(notif);
            dropdown.appendChild(notifElement);
        });

        // Add "Clear All" button
        const clearAllBtn = document.createElement('div');
        clearAllBtn.className = 'notification-item clear-all';
        clearAllBtn.innerHTML = '<button onclick="clearAllNotifications()">Clear All</button>';
        dropdown.appendChild(clearAllBtn);
    }
}

// Create a notification element
function createNotificationElement(notif) {
    const div = document.createElement('div');
    div.className = 'notification-item';
    div.setAttribute('data-id', notif.id);
    
    const content = `
        <div class="notif-content">
            <strong>${notif.title}</strong>
            <p>${notif.message}</p>
            <small>${notif.created_at}</small>
        </div>
    `;
    
    div.innerHTML = content;
    
    // Add click handler
    div.addEventListener('click', function() {
        markAsRead(notif.id);
        if (notif.link) {
            window.location.href = notif.link;
        }
    });
    
    return div;
}

// Mark a notification as read
function markAsRead(notificationId) {
    fetch(`/api/mark_notification_read/${notificationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fetchNotifications(); // Refresh the list
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

// Clear all notifications
function clearAllNotifications() {
    fetch('/api/mark_all_notifications_read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fetchNotifications(); // Refresh the list
        }
    })
    .catch(error => {
        console.error('Error clearing notifications:', error);
    });
}

// Toggle notification dropdown
function toggleNotificationDropdown() {
    const dropdown = document.getElementById('notification-dropdown');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const bell = document.getElementById('notification-bell');
    const dropdown = document.getElementById('notification-dropdown');
    
    if (bell && dropdown) {
        if (!bell.contains(event.target) && !dropdown.contains(event.target)) {
            dropdown.classList.remove('show');
        }
    }
});