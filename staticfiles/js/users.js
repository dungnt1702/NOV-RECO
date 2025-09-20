// Users Management JavaScript

document.addEventListener('DOMContentLoaded', function () {
    console.log('Users page loaded');

    // Initialize form validation
    initializeFormValidation();

    // Initialize search functionality
    initializeSearch();

    // Initialize confirmation dialogs
    initializeConfirmations();
});

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

    if (searchInput) {
        // Auto-submit on Enter
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                this.closest('form').submit();
            }
        });
    }

    if (roleSelect) {
        // Auto-submit on change
        roleSelect.addEventListener('change', function () {
            this.closest('form').submit();
        });
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
