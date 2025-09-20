// Authentication Pages JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Auth page loaded

    // Initialize form validation
    initializeFormValidation();

    // Initialize password visibility toggle
    initializePasswordToggle();

    // Initialize form animations
    initializeFormAnimations();
});

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.auth-form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function () {
                validateField(this);
            });

            input.addEventListener('input', function () {
                clearFieldError(this);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;

    // Clear previous errors
    clearAllErrors(form);

    // Required fields validation
    const requiredFields = form.querySelectorAll('input[required]');
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

    // Password validation
    const passwordField = form.querySelector('input[name="password1"]');
    const confirmPasswordField = form.querySelector('input[name="password2"]');

    if (passwordField && passwordField.value) {
        if (passwordField.value.length < 8) {
            showFieldError(passwordField, 'Mật khẩu phải có ít nhất 8 ký tự');
            isValid = false;
        }
    }

    if (passwordField && confirmPasswordField && passwordField.value && confirmPasswordField.value) {
        if (passwordField.value !== confirmPasswordField.value) {
            showFieldError(confirmPasswordField, 'Mật khẩu không khớp');
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

function validateField(field) {
    clearFieldError(field);

    if (field.hasAttribute('required') && !field.value.trim()) {
        showFieldError(field, 'Trường này là bắt buộc');
        return false;
    }

    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            showFieldError(field, 'Email không hợp lệ');
            return false;
        }
    }

    return true;
}

function showFieldError(field, message) {
    const formGroup = field.closest('.form-group');
    if (formGroup) {
        let errorDiv = formGroup.querySelector('.field-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'field-error';
            formGroup.appendChild(errorDiv);
        }

        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            color: #e53e3e;
            font-size: 12px;
            margin-top: 5px;
            display: flex;
            align-items: center;
            gap: 5px;
        `;

        field.style.borderColor = '#e53e3e';
        field.style.background = '#fef5f5';
    }
}

function clearFieldError(field) {
    const formGroup = field.closest('.form-group');
    if (formGroup) {
        const errorDiv = formGroup.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }

        field.style.borderColor = '#e2e8f0';
        field.style.background = '#f8f9fa';
    }
}

function clearAllErrors(form) {
    const errorDivs = form.querySelectorAll('.field-error');
    errorDivs.forEach(div => div.remove());

    const fields = form.querySelectorAll('input');
    fields.forEach(field => {
        field.style.borderColor = '#e2e8f0';
        field.style.background = '#f8f9fa';
    });
}

// Password visibility toggle
function initializePasswordToggle() {
    const passwordFields = document.querySelectorAll('input[type="password"]');

    passwordFields.forEach(field => {
        const formGroup = field.closest('.form-group');
        if (formGroup) {
            // Create toggle button
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'password-toggle';
            toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
            toggleBtn.style.cssText = `
                position: absolute;
                right: 12px;
                top: 50%;
                transform: translateY(-50%);
                background: none;
                border: none;
                color: #718096;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: color 0.3s ease;
            `;

            // Make form group relative
            formGroup.style.position = 'relative';

            // Add toggle button
            formGroup.appendChild(toggleBtn);

            // Toggle functionality
            toggleBtn.addEventListener('click', function () {
                const isPassword = field.type === 'password';
                field.type = isPassword ? 'text' : 'password';

                const icon = this.querySelector('i');
                icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';

                this.style.color = isPassword ? '#0A5597' : '#718096';
            });
        }
    });
}

// Form animations
function initializeFormAnimations() {
    const inputs = document.querySelectorAll('.form-group input');

    inputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function () {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });

        // Check if input has value on load
        if (input.value) {
            input.parentElement.classList.add('focused');
        }
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert-toast');
    existingAlerts.forEach(alert => alert.remove());

    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert-toast alert-${type}`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 10px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
    
    .form-group.focused label {
        color: #0A5597;
    }
    
    .form-group.focused input {
        border-color: #0A5597;
        background: white;
    }
`;
document.head.appendChild(style);
