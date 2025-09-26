// Base JavaScript functionality for all pages

// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navOverlay = document.getElementById('nav-overlay');

    if (navToggle && navMenu) {
        // Toggle mobile menu with dropdown slide animation
        navToggle.addEventListener('click', function(e) {
            e.preventDefault();
            navMenu.classList.toggle('active');
            if (navOverlay) {
                navOverlay.classList.toggle('active');
            }
            
            // Trigger dropdown slide animation when menu opens
            if (navMenu.classList.contains('active')) {
                setTimeout(() => {
                    slideInDropdowns();
                }, 100); // Small delay for menu to appear first
            } else {
                slideOutDropdowns();
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                navMenu.classList.remove('active');
                slideOutDropdowns(); // Hide dropdowns when menu closes
                if (navOverlay) {
                    navOverlay.classList.remove('active');
                }
            }
        });

        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                navMenu.classList.remove('active');
                slideOutDropdowns(); // Hide dropdowns when menu closes
                if (navOverlay) {
                    navOverlay.classList.remove('active');
                }
            }
        });

        // Close menu on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navMenu.classList.remove('active');
                slideOutDropdowns(); // Hide dropdowns when switching to desktop
                if (navOverlay) {
                    navOverlay.classList.remove('active');
                }
            }
        });
    }

    // Dropdown slide animation functions
    function slideInDropdowns() {
        if (window.innerWidth <= 768) {
            const dropdownMenus = document.querySelectorAll('.dropdown-menu');
            dropdownMenus.forEach((menu, index) => {
                setTimeout(() => {
                    menu.classList.add('active');
                }, index * 100); // Staggered animation
            });
        }
    }
    
    function slideOutDropdowns() {
        const dropdownMenus = document.querySelectorAll('.dropdown-menu');
        dropdownMenus.forEach(menu => {
            menu.classList.remove('active');
        });
    }
    
    // Handle dropdown toggle on mobile
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                // On mobile: prevent default click behavior
                // Dropdowns are controlled by menu open/close
                e.preventDefault();
                return false;
            }
            // On desktop: normal dropdown behavior
        });
    });
    
    // Reset dropdown state on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            slideOutDropdowns();
        } else if (navMenu && navMenu.classList.contains('active')) {
            // If mobile menu is open, show dropdowns
            slideInDropdowns();
        }
    });
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
        warning: '#fd7e14',
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

// Format date for display - Global function
window.formatDate = function(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        let date;
        
        // Check if it's ISO format with timezone
        if (dateString.includes('T') && dateString.includes('+')) {
            // ISO format: 2025-09-20T05:27:43.642447+00:00
            date = new Date(dateString);
        } else if (dateString.includes(' ')) {
            // Format: YYYY-MM-DD HH:MM:SS
            const [datePart, timePart] = dateString.split(' ');
            const [year, month, day] = datePart.split('-');
            const [hour, minute, second] = timePart.split(':');
            date = new Date(year, month - 1, day, hour, minute, second);
        } else {
            // Try to parse as date directly
            date = new Date(dateString);
        }
        
        // Check if date is valid
        if (isNaN(date.getTime())) {
            console.warn('Invalid date string:', dateString);
            return 'Ngày không hợp lệ';
        }
        
        // Format the date in Vietnamese format
        return date.toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZone: 'Asia/Ho_Chi_Minh'
        });
    } catch (error) {
        console.error('Error formatting date:', error, 'Input:', dateString);
        return 'Lỗi định dạng ngày';
    }
}

// Format distance
function formatDistance(meters) {
    if (meters < 1000) {
        return `${Math.round(meters)}m`;
    } else {
        return `${(meters / 1000).toFixed(1)}km`;
    }
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        const date = new Date(dateString);
        return date.toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        console.error('Error formatting date:', error);
        return dateString;
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

// User Menu Dropdown functionality
document.addEventListener('DOMContentLoaded', function() {
    const userMenuToggle = document.getElementById('userMenuToggle');
    const userMenuContent = document.getElementById('userMenuContent');
    
    if (userMenuToggle && userMenuContent) {
        // Toggle user menu dropdown
        userMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            userMenuContent.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userMenuContent.contains(e.target) && !userMenuToggle.contains(e.target)) {
                userMenuContent.classList.remove('show');
            }
        });
        
        // Close dropdown when pressing Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                userMenuContent.classList.remove('show');
            }
        });
        
        // Handle menu item clicks
        const menuItems = userMenuContent.querySelectorAll('.menu-item');
        menuItems.forEach(item => {
            item.addEventListener('click', function() {
                // Close dropdown after clicking a menu item
                userMenuContent.classList.remove('show');
            });
        });
    }
});
