// Notification List JavaScript
document.addEventListener('DOMContentLoaded', function() {
    let currentTab = 'all';
    let notifications = [];
    let filteredNotifications = [];

    // Initialize
    initializePage();

    function initializePage() {
        setupEventListeners();
        loadNotifications();
    }

    function setupEventListeners() {
        // Tab switching
        const tabButtons = document.querySelectorAll('#notificationTabs button[data-bs-toggle="tab"]');
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const target = this.getAttribute('data-bs-target').substring(1);
                switchTab(target);
            });
        });

        // Action buttons
        document.getElementById('markAllReadBtn').addEventListener('click', markAllAsRead);
        document.getElementById('clearReadBtn').addEventListener('click', clearReadNotifications);
        document.getElementById('markAsReadBtn').addEventListener('click', markCurrentAsRead);
    }

    async function loadNotifications() {
        try {
            showLoading(true);
            const response = await fetch('/notifications/api/');
            const data = await response.json();
            
            if (data.success) {
                notifications = data.notifications;
                updateCounts();
                renderNotifications();
            } else {
                showEmptyState();
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
            showNotification('Lỗi khi tải thông báo', 'error');
        } finally {
            showLoading(false);
        }
    }

    function switchTab(tab) {
        currentTab = tab;
        
        // Update active tab
        document.querySelectorAll('#notificationTabs .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.getElementById(`${tab}-tab`).classList.add('active');
        
        // Update active tab pane
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('show', 'active');
        });
        document.getElementById(tab).classList.add('show', 'active');
        
        renderNotifications();
    }

    function updateCounts() {
        const allCount = notifications.length;
        const unreadCount = notifications.filter(n => !n.is_read).length;
        const absenceCount = notifications.filter(n => n.type.includes('absence')).length;
        const systemCount = notifications.filter(n => n.type === 'system_alert').length;

        document.getElementById('allCount').textContent = allCount;
        document.getElementById('unreadCount').textContent = unreadCount;
        document.getElementById('absenceCount').textContent = absenceCount;
        document.getElementById('systemCount').textContent = systemCount;
    }

    function renderNotifications() {
        // Hide global empty state
        document.getElementById('emptyState').style.display = 'none';
        
        // Show notification actions
        document.querySelector('.notification-actions').style.display = 'flex';
        
        // Show current tab content
        document.querySelectorAll('.tab-pane').forEach(tab => {
            tab.classList.remove('show', 'active');
        });
        document.getElementById(currentTab).classList.add('show', 'active');
        
        // Filter notifications based on current tab
        switch (currentTab) {
            case 'unread':
                filteredNotifications = notifications.filter(n => !n.is_read);
                break;
            case 'absence':
                filteredNotifications = notifications.filter(n => n.type.includes('absence'));
                break;
            case 'system':
                filteredNotifications = notifications.filter(n => n.type === 'system_alert');
                break;
            default:
                filteredNotifications = [...notifications];
        }

        const container = document.getElementById(`${currentTab}Notifications`);
        
        if (filteredNotifications.length === 0) {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-bell-slash"></i><h3>Không có thông báo</h3><p>Không tìm thấy thông báo phù hợp.</p></div>';
            return;
        }

        container.innerHTML = filteredNotifications.map(notification => `
            <div class="notification-item ${notification.is_read ? '' : 'unread'} ${notification.is_important ? 'important' : ''} ${notification.type}" 
                 onclick="viewNotification(${notification.id})">
                ${!notification.is_read ? '<div class="unread-indicator"></div>' : ''}
                <div class="notification-header">
                    <h3 class="notification-title">${notification.title}</h3>
                    <span class="notification-time">${formatTime(notification.created_at)}</span>
                </div>
                <div class="notification-body">
                    ${notification.message}
                </div>
                <div class="notification-footer">
                    <span class="notification-type ${notification.type}">${getTypeText(notification.type)}</span>
                    <div class="notification-actions">
                        ${!notification.is_read ? `
                            <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); markAsRead(${notification.id})">
                                <i class="fas fa-check"></i>
                                Đánh dấu đã đọc
                            </button>
                        ` : ''}
                        <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); deleteNotification(${notification.id})">
                            <i class="fas fa-trash"></i>
                            Xóa
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async function markAllAsRead() {
        try {
            const response = await fetch('/notifications/api/mark-all-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();
            if (data.success) {
                showNotification('Đã đánh dấu tất cả thông báo đã đọc', 'success');
                loadNotifications();
            } else {
                showNotification(data.message || 'Có lỗi xảy ra', 'error');
            }
        } catch (error) {
            console.error('Error marking all as read:', error);
            showNotification('Có lỗi xảy ra khi đánh dấu đã đọc', 'error');
        }
    }

    async function clearReadNotifications() {
        if (!confirm('Bạn có chắc chắn muốn xóa tất cả thông báo đã đọc?')) {
            return;
        }

        try {
            const response = await fetch('/notifications/api/clear-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();
            if (data.success) {
                showNotification('Đã xóa thông báo đã đọc', 'success');
                loadNotifications();
            } else {
                showNotification(data.message || 'Có lỗi xảy ra', 'error');
            }
        } catch (error) {
            console.error('Error clearing read notifications:', error);
            showNotification('Có lỗi xảy ra khi xóa thông báo', 'error');
        }
    }

    async function markCurrentAsRead() {
        const modal = document.getElementById('notificationModal');
        const notificationId = modal.dataset.notificationId;
        
        if (notificationId) {
            await markAsRead(notificationId);
            const bsModal = bootstrap.Modal.getInstance(modal);
            bsModal.hide();
        }
    }

    // Global functions
    window.viewNotification = async function(id) {
        try {
            const response = await fetch(`/notifications/api/${id}/`);
            const data = await response.json();
            
            if (data.success) {
                const notification = data.notification;
                
                // Populate modal
                document.getElementById('notificationModalTitle').innerHTML = `
                    <i class="fas fa-bell"></i>
                    ${notification.title}
                `;
                
                document.getElementById('notificationModalBody').innerHTML = `
                    <div class="notification-detail">
                        <div class="detail-header">
                            <span class="notification-type ${notification.type}">${getTypeText(notification.type)}</span>
                            <span class="notification-time">${formatDateTime(notification.created_at)}</span>
                        </div>
                        <div class="detail-body">
                            <p>${notification.message}</p>
                            ${notification.data ? `
                                <div class="detail-data">
                                    <h6>Thông tin bổ sung:</h6>
                                    <pre>${JSON.stringify(notification.data, null, 2)}</pre>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
                
                // Store notification ID
                document.getElementById('notificationModal').dataset.notificationId = id;
                
                // Show/hide mark as read button
                const markAsReadBtn = document.getElementById('markAsReadBtn');
                if (notification.is_read) {
                    markAsReadBtn.style.display = 'none';
                } else {
                    markAsReadBtn.style.display = 'inline-flex';
                }
                
                // Show modal
                const bsModal = new bootstrap.Modal(document.getElementById('notificationModal'));
                bsModal.show();
                
                // Mark as read if not already read
                if (!notification.is_read) {
                    await markAsRead(id);
                }
            } else {
                showNotification('Không tìm thấy thông báo', 'error');
            }
        } catch (error) {
            console.error('Error viewing notification:', error);
            showNotification('Có lỗi xảy ra khi xem thông báo', 'error');
        }
    };

    window.markAsRead = async function(id) {
        try {
            const response = await fetch(`/notifications/api/${id}/mark-read/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();
            if (data.success) {
                // Update local data
                const notification = notifications.find(n => n.id === id);
                if (notification) {
                    notification.is_read = true;
                    notification.read_at = new Date().toISOString();
                }
                
                updateCounts();
                renderNotifications();
                
                // Update notification bell if exists
                updateNotificationBell();
            } else {
                showNotification(data.message || 'Có lỗi xảy ra', 'error');
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
            showNotification('Có lỗi xảy ra khi đánh dấu đã đọc', 'error');
        }
    };

    window.deleteNotification = async function(id) {
        if (!confirm('Bạn có chắc chắn muốn xóa thông báo này?')) {
            return;
        }

        try {
            const response = await fetch(`/notifications/api/${id}/delete/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();
            if (data.success) {
                showNotification('Đã xóa thông báo', 'success');
                
                // Remove from local data
                notifications = notifications.filter(n => n.id !== id);
                updateCounts();
                renderNotifications();
                
                // Update notification bell if exists
                updateNotificationBell();
            } else {
                showNotification(data.message || 'Có lỗi xảy ra', 'error');
            }
        } catch (error) {
            console.error('Error deleting notification:', error);
            showNotification('Có lỗi xảy ra khi xóa thông báo', 'error');
        }
    };

    function updateNotificationBell() {
        // Update notification bell count if it exists
        const bellCount = document.querySelector('.notification-bell .badge');
        if (bellCount) {
            const unreadCount = notifications.filter(n => !n.is_read).length;
            bellCount.textContent = unreadCount;
            bellCount.style.display = unreadCount > 0 ? 'block' : 'none';
        }
    }

    function showLoading(show) {
        const loadingElements = document.querySelectorAll('.notification-list');
        loadingElements.forEach(el => {
            el.classList.toggle('loading', show);
        });
    }

    function showEmptyState() {
        // Hide all tab content
        document.querySelectorAll('.tab-pane').forEach(tab => {
            tab.classList.remove('show', 'active');
        });
        
        // Clear all notification lists
        document.querySelectorAll('.notification-list').forEach(el => {
            el.innerHTML = '';
        });
        
        // Show empty state
        document.getElementById('emptyState').style.display = 'block';
        
        // Hide notification actions
        document.querySelector('.notification-actions').style.display = 'none';
    }

    // Utility functions
    function formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffMinutes < 1) {
            return 'Vừa xong';
        } else if (diffMinutes < 60) {
            return `${diffMinutes} phút trước`;
        } else if (diffHours < 24) {
            return `${diffHours} giờ trước`;
        } else if (diffDays < 7) {
            return `${diffDays} ngày trước`;
        } else {
            return date.toLocaleDateString('vi-VN');
        }
    }

    function formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('vi-VN');
    }

    function getTypeText(type) {
        const typeMap = {
            'absence_request': 'Đơn vắng mặt',
            'absence_approval': 'Phê duyệt vắng mặt',
            'system_alert': 'Cảnh báo hệ thống',
            'reminder': 'Nhắc nhở',
            'other': 'Khác'
        };
        return typeMap[type] || type;
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : type === 'warning' ? '#fff3cd' : '#d1ecf1'};
            color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : type === 'warning' ? '#856404' : '#0c5460'};
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            z-index: 9999;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});
