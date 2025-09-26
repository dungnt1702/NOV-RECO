// Absence History JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

function initializePage() {
    initializeFilters();
    initializeCollapse();
}

function initializeFilters() {
    // Auto-submit form when filter values change
    const statusSelect = document.getElementById('status');
    const typeSelect = document.getElementById('type');
    
    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            // Optional: Auto-submit on change
            // this.form.submit();
        });
    }
    
    if (typeSelect) {
        typeSelect.addEventListener('change', function() {
            // Optional: Auto-submit on change
            // this.form.submit();
        });
    }
}

function initializeCollapse() {
    // Handle filter collapse animation
    const filterToggle = document.querySelector('[data-bs-target="#filterBody"]');
    const filterBody = document.getElementById('filterBody');
    
    if (filterToggle && filterBody) {
        filterToggle.addEventListener('click', function() {
            const icon = this.querySelector('i');
            
            // Toggle icon rotation
            if (filterBody.classList.contains('show')) {
                icon.style.transform = 'rotate(0deg)';
            } else {
                icon.style.transform = 'rotate(180deg)';
            }
        });
        
        // Listen for Bootstrap collapse events
        filterBody.addEventListener('show.bs.collapse', function() {
            const icon = filterToggle.querySelector('i');
            icon.style.transform = 'rotate(180deg)';
        });
        
        filterBody.addEventListener('hide.bs.collapse', function() {
            const icon = filterToggle.querySelector('i');
            icon.style.transform = 'rotate(0deg)';
        });
    }
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN');
}

// Status helpers
function getStatusText(status) {
    const statusMap = {
        'pending': 'Chờ phê duyệt',
        'approved': 'Đã phê duyệt',
        'rejected': 'Đã từ chối',
        'cancelled': 'Đã hủy'
    };
    return statusMap[status] || status;
}

function getStatusClass(status) {
    return `status-${status}`;
}

function getStatusIcon(status) {
    const iconMap = {
        'pending': 'fas fa-clock',
        'approved': 'fas fa-check',
        'rejected': 'fas fa-times',
        'cancelled': 'fas fa-ban'
    };
    return iconMap[status] || 'fas fa-question';
}

// Export functions for potential use in other scripts
window.AbsenceHistory = {
    formatDate,
    formatDateTime,
    getStatusText,
    getStatusClass,
    getStatusIcon
};
