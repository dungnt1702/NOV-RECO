// Base JavaScript functionality for all pages

// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navOverlay = document.getElementById('nav-overlay');

    if (navToggle && navMenu) {
        // Toggle mobile menu
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            if (navOverlay) {
                navOverlay.classList.toggle('active');
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                navMenu.classList.remove('active');
                if (navOverlay) {
                    navOverlay.classList.remove('active');
                }
            }
        });

        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                navMenu.classList.remove('active');
                if (navOverlay) {
                    navOverlay.classList.remove('active');
                }
            }
        });

        // Close menu on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navMenu.classList.remove('active');
                if (navOverlay) {
                    navOverlay.classList.remove('active');
                }
            }
        });
    }
});

// Common API function
function api(url, options = {}) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    const headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }
    
    return fetch(url, {
        ...options,
        headers,
        credentials: 'include'
    });
}

// Common alert function
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 18px; cursor: pointer; margin-left: auto;">&times;</button>
        </div>
    `;
    
    // Add alert styles
    alert.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    `;
    
    // Set background color based on type
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    alert.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

// Loading state management
function setLoading(element, loading = true) {
    if (loading) {
        element.disabled = true;
        element.classList.add('loading');
        if (element.querySelector('.btn-text')) {
            element.querySelector('.btn-text').style.display = 'none';
        }
        if (element.querySelector('.loading')) {
            element.querySelector('.loading').style.display = 'flex';
        }
    } else {
        element.disabled = false;
        element.classList.remove('loading');
        if (element.querySelector('.btn-text')) {
            element.querySelector('.btn-text').style.display = 'block';
        }
        if (element.querySelector('.loading')) {
            element.querySelector('.loading').style.display = 'none';
        }
    }
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format distance
function formatDistance(meters) {
    if (meters < 1000) {
        return `${Math.round(meters)}m`;
    } else {
        return `${(meters / 1000).toFixed(1)}km`;
    }
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Check if user is authenticated
function isAuthenticated() {
    return document.body.classList.contains('authenticated') || 
           document.querySelector('[data-user-id]') !== null;
}

// Get user info from data attributes
function getUserInfo() {
    const userElement = document.querySelector('[data-user-id]');
    if (userElement) {
        return {
            id: userElement.dataset.userId,
            name: userElement.dataset.userName,
            email: userElement.dataset.userEmail,
            role: userElement.dataset.userRole
        };
    }
    return null;
}
