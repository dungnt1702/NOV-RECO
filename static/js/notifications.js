// Notification Bell JavaScript
class NotificationManager {
    constructor() {
        this.toggle = document.getElementById('notificationToggle');
        this.dropdown = document.getElementById('notificationDropdown');
        this.badge = document.getElementById('notificationBadge');
        this.unreadCount = document.getElementById('unreadCount');
        this.notificationList = document.getElementById('notificationList');
        
        this.init();
    }
    
    init() {
        if (!this.toggle) return;
        
        // Handle click - go to notifications page
        this.toggle.addEventListener('click', (e) => {
            // Let the link work normally to go to notifications page
            // Don't prevent default
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.toggle.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Load notifications
        this.loadNotifications();
        
        // Auto refresh every 30 seconds
        setInterval(() => {
            this.loadNotifications();
        }, 30000);
    }
    
    toggleDropdown() {
        if (this.dropdown.classList.contains('show')) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }
    
    openDropdown() {
        this.dropdown.classList.add('show');
        this.loadNotifications();
    }
    
    closeDropdown() {
        this.dropdown.classList.remove('show');
    }
    
    async loadNotifications() {
        try {
            const response = await fetch('/notifications/api/');
            const data = await response.json();
            
            this.updateBadge(data.unread_count);
            this.renderNotifications(data.notifications);
            
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }
    
    updateBadge(count) {
        // Always show badge with count (0 if no unread notifications)
        this.badge.textContent = count > 99 ? '99+' : count;
        this.badge.setAttribute('data-count', count);
        this.toggle.setAttribute('data-count', count); // Add data-count to toggle for CSS styling
        this.badge.classList.remove('hidden');
        this.unreadCount.textContent = `${count} thông báo chưa đọc`;
    }
    
    renderNotifications(notifications) {
        if (notifications.length === 0) {
            this.notificationList.innerHTML = `
                <div class="empty-notifications">
                    <i class="fas fa-bell-slash"></i>
                    <p>Không có thông báo nào</p>
                </div>
            `;
            return;
        }
        
        this.notificationList.innerHTML = notifications.map(notification => `
            <div class="notification-item ${notification.is_read ? '' : 'unread'} ${notification.is_important ? 'important' : ''}" 
                 data-id="${notification.id}">
                <div class="notification-content">
                    <div class="notification-icon ${notification.type}">
                        <i class="fas ${this.getNotificationIcon(notification.type)}"></i>
                    </div>
                    <div class="notification-text">
                        <div class="notification-title">${notification.title}</div>
                        <div class="notification-message">${notification.message}</div>
                        <div class="notification-time">${this.formatTime(notification.created_at)}</div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Add click handlers
        this.notificationList.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', () => {
                const notificationId = item.dataset.id;
                this.markAsRead(notificationId);
            });
        });
    }
    
    getNotificationIcon(type) {
        const icons = {
            'approval_required': 'fa-clock',
            'approval_completed': 'fa-check',
            'approval_rejected': 'fa-times',
            'reminder': 'fa-bell',
            'system': 'fa-info-circle',
            'checkin': 'fa-map-marker-alt',
            'absence': 'fa-calendar-times'
        };
        return icons[type] || 'fa-bell';
    }
    
    formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Vừa xong';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes} phút trước`;
        } else if (diff < 86400000) { // Less than 1 day
            const hours = Math.floor(diff / 3600000);
            return `${hours} giờ trước`;
        } else {
            const days = Math.floor(diff / 86400000);
            return `${days} ngày trước`;
        }
    }
    
    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/notifications/api/mark-read/${notificationId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // Reload notifications
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }
    
    async markAllAsRead() {
        try {
            const response = await fetch('/notifications/api/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
        }
    }
    
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NotificationManager();
});

// Export for use in other scripts
window.NotificationManager = NotificationManager;
