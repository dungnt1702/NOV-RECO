// Users Management JavaScript

let allUsers = [];
let filteredUsers = [];

document.addEventListener('DOMContentLoaded', function () {
    console.log('Users page loaded');

    // Initialize form validation
    initializeFormValidation();

    // Initialize search functionality
    initializeSearch();

    // Initialize confirmation dialogs
    initializeConfirmations();

    // Load users data and initialize pagination
    loadUsers();
});

// Load users from API
async function loadUsers() {
    try {
        const response = await fetch('/users/api/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            allUsers = await response.json();
            filteredUsers = [...allUsers];
            
            // Initialize pagination component
            if (window.paginationComponent) {
                window.paginationComponent.setData(allUsers);
                window.paginationComponent.config.onPageChange = (items) => {
                    renderUsersTable(items);
                };
                window.paginationComponent.config.onPageSizeChange = (items) => {
                    renderUsersTable(items);
                };
                window.paginationComponent.config.onSearch = (filteredItems) => {
                    filteredUsers = filteredItems;
                    renderUsersTable(window.paginationComponent.getCurrentPageItems());
                };
                
                // Render first page immediately
                renderUsersTable(window.paginationComponent.getCurrentPageItems());
            }
        } else {
            console.error('Failed to load users:', response.statusText);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Render users table
function renderUsersTable(users) {
    const tableBody = document.querySelector('.users-table tbody');
    const mobileView = document.querySelector('.mobile-view');
    
    if (!tableBody || !mobileView) return;

    // Clear existing content
    tableBody.innerHTML = '';
    mobileView.innerHTML = '';

    if (users.length === 0) {
        // Show empty state
        const emptyState = `
            <tr>
                <td colspan="6" class="text-center py-8">
                    <div class="empty-state">
                        <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                        </svg>
                        <h3>Không có người dùng nào</h3>
                        <p>Không tìm thấy người dùng nào phù hợp với bộ lọc hiện tại.</p>
                    </div>
                </td>
            </tr>
        `;
        tableBody.innerHTML = emptyState;
        
        const mobileEmptyState = `
            <div class="empty-state">
                <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                </svg>
                <h3>Không có người dùng nào</h3>
                <p>Không tìm thấy người dùng nào phù hợp với bộ lọc hiện tại.</p>
            </div>
        `;
        mobileView.innerHTML = mobileEmptyState;
        return;
    }

    // Render desktop table
    users.forEach(user => {
        const row = createUserRow(user);
        tableBody.appendChild(row);
    });

    // Render mobile cards
    users.forEach(user => {
        const card = createUserCard(user);
        mobileView.appendChild(card);
    });
}

// Create user table row
function createUserRow(user) {
    const row = document.createElement('tr');
    
    const userInfo = `
        <td class="user-info">
            <div class="user-avatar">
                ${(user.first_name || user.username).charAt(0).toUpperCase()}
            </div>
            <div class="user-details">
                <div class="user-name">${user.display_name || user.username}</div>
                <div class="user-email">${user.email || ''}</div>
            </div>
        </td>
    `;
    
    const roleBadge = `
        <td>
            <span class="role-badge role-${user.role}">
                ${getRoleDisplay(user.role)}
            </span>
        </td>
    `;
    
    const department = `
        <td>
            ${user.department_name ? `<span class="department-name">${user.department_name}</span>` : '<span class="text-muted">-</span>'}
        </td>
    `;
    
    const employeeId = `
        <td>${user.employee_id || '-'}</td>
    `;
    
    const status = `
        <td>
            <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                ${user.is_active ? 'Hoạt động' : 'Không hoạt động'}
            </span>
        </td>
    `;
    
    const actions = `
        <td class="actions">
            <a href="/users/${user.id}/update/" class="btn btn-sm btn-edit">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
                Sửa
            </a>
            <a href="/users/${user.id}/delete/" class="btn btn-sm btn-danger">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
                Xóa
            </a>
        </td>
    `;
    
    row.innerHTML = userInfo + roleBadge + department + employeeId + status + actions;
    return row;
}

// Create user mobile card
function createUserCard(user) {
    const card = document.createElement('div');
    card.className = 'user-card';
    
    card.innerHTML = `
        <div class="card-header">
            <div class="user-info">
                <div class="user-avatar">
                    ${(user.first_name || user.username).charAt(0).toUpperCase()}
                </div>
                <div class="user-details">
                    <h3 class="user-name">${user.display_name || user.username}</h3>
                    <p class="user-email">${user.email || ''}</p>
                    ${user.employee_id ? `<p class="user-id">Mã NV: ${user.employee_id}</p>` : ''}
                </div>
            </div>
            <div class="user-status">
                <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                    ${user.is_active ? 'Hoạt động' : 'Không hoạt động'}
                </span>
            </div>
        </div>
        
        <div class="card-body">
            <div class="user-meta">
                <div class="meta-item">
                    <span class="meta-label">Vai trò:</span>
                    <span class="role-badge role-${user.role}">${getRoleDisplay(user.role)}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Phòng ban:</span>
                    <span class="meta-value">
                        ${user.department_name || '<span class="text-muted">Chưa phân công</span>'}
                    </span>
                </div>
            </div>
        </div>
        
        <div class="card-footer">
            <div class="card-actions">
                <a href="/users/${user.id}/update/" class="btn btn-primary">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    Sửa
                </a>
                <a href="/users/${user.id}/delete/" class="btn btn-danger">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                    Xóa
                </a>
            </div>
        </div>
    `;
    
    return card;
}

// Get role display text
function getRoleDisplay(role) {
    const roleMap = {
        'admin': 'Quản trị viên',
        'manager': 'Quản lý',
        'employee': 'Nhân viên',
        'hcns': 'Nhân sự'
    };
    return roleMap[role] || role;
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.user-form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;

    // Clear previous errors
    clearErrors(form);

    // Required fields validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Trường này là bắt buộc');
            isValid = false;
        }
    });

    // Email validation
    const emailField = form.querySelector('input[type="email"]');
    if (emailField && emailField.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value)) {
            showFieldError(emailField, 'Email không hợp lệ');
            isValid = false;
        }
    }

    // Password confirmation validation
    const password1 = form.querySelector('input[name="password1"]');
    const password2 = form.querySelector('input[name="password2"]');
    if (password1 && password2) {
        if (password1.value !== password2.value) {
            showFieldError(password2, 'Mật khẩu không khớp');
            isValid = false;
        }

        if (password1.value.length < 8) {
            showFieldError(password1, 'Mật khẩu phải có ít nhất 8 ký tự');
            isValid = false;
        }
    }

    // Username validation
    const usernameField = form.querySelector('input[name="username"]');
    if (usernameField && usernameField.value) {
        const usernameRegex = /^[a-zA-Z0-9_]+$/;
        if (!usernameRegex.test(usernameField.value)) {
            showFieldError(usernameField, 'Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới');
            isValid = false;
        }
    }

    return isValid;
}

function showFieldError(field, message) {
    const formGroup = field.closest('.form-group');
    if (formGroup) {
        let errorDiv = formGroup.querySelector('.error-messages');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-messages';
            formGroup.appendChild(errorDiv);
        }

        const errorSpan = document.createElement('span');
        errorSpan.className = 'error';
        errorSpan.textContent = message;
        errorDiv.appendChild(errorSpan);

        field.style.borderColor = '#e53e3e';
    }
}

function clearErrors(form) {
    const errorMessages = form.querySelectorAll('.error-messages');
    errorMessages.forEach(errorDiv => {
        errorDiv.remove();
    });

    const fields = form.querySelectorAll('.form-control');
    fields.forEach(field => {
        field.style.borderColor = '#e2e8f0';
    });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const roleSelect = document.querySelector('.role-select');
    const departmentSelect = document.querySelector('.department-select');

    if (searchInput) {
        // Debounce search input
        let searchTimeout;
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                applyFilters();
            }, 300);
        });
    }

    if (roleSelect) {
        roleSelect.addEventListener('change', function () {
            applyFilters();
        });
    }

    if (departmentSelect) {
        departmentSelect.addEventListener('change', function () {
            applyFilters();
        });
    }
}

// Apply filters and update pagination
function applyFilters() {
    const searchQuery = document.querySelector('.search-input')?.value || '';
    const roleFilter = document.querySelector('.role-select')?.value || '';
    const departmentFilter = document.querySelector('.department-select')?.value || '';

    // Filter users based on current filters
    filteredUsers = allUsers.filter(user => {
        // Search filter
        const matchesSearch = !searchQuery || 
            user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
            user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (user.first_name && user.first_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
            (user.last_name && user.last_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
            (user.employee_id && user.employee_id.toLowerCase().includes(searchQuery.toLowerCase()));

        // Role filter
        const matchesRole = !roleFilter || user.role === roleFilter;

        // Department filter
        const matchesDepartment = !departmentFilter || 
            (departmentFilter === 'null' && !user.department_name) ||
            user.department_name === departmentFilter;

        return matchesSearch && matchesRole && matchesDepartment;
    });

    // Update pagination component with filtered data
    if (window.paginationComponent) {
        window.paginationComponent.setData(filteredUsers);
        renderUsersTable(window.paginationComponent.getCurrentPageItems());
    }
}

// Confirmation dialogs
function initializeConfirmations() {
    const deleteButtons = document.querySelectorAll('.btn-danger');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            const userName = this.closest('tr').querySelector('.user-name').textContent;
            if (!confirm(`Bạn có chắc chắn muốn xóa người dùng "${userName}" không?`)) {
                e.preventDefault();
            }
        });
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideInRight 0.3s ease;
    `;

    // Set background color based on type
    const colors = {
        'success': '#48bb78',
        'error': '#f56565',
        'warning': '#ed8936',
        'info': '#4299e1'
    };
    alert.style.backgroundColor = colors[type] || colors.info;

    alert.textContent = message;

    // Add to page
    document.body.appendChild(alert);

    // Remove after 5 seconds
    setTimeout(() => {
        alert.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 300);
    }, 5000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
