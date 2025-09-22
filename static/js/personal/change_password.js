// Change Password JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const newPasswordField = document.getElementById('new_password');
    const confirmPasswordField = document.getElementById('confirm_password');
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    const passwordMatch = document.getElementById('passwordMatch');
    const submitBtn = document.getElementById('submitBtn');
    
    // Password strength checker
    if (newPasswordField) {
        newPasswordField.addEventListener('input', function() {
            const password = this.value;
            const strength = calculatePasswordStrength(password);
            updateStrengthIndicator(strength);
            updateRequirements(password);
            checkFormValidity();
        });
    }
    
    // Password confirmation checker
    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', function() {
            checkPasswordMatch();
            checkFormValidity();
        });
    }
    
    // Password toggle functionality
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetField = document.getElementById(targetId);
            const icon = this.querySelector('i');
            
            if (targetField.type === 'password') {
                targetField.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                targetField.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Form submission
    const form = document.querySelector('.password-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!checkFormValidity()) {
                e.preventDefault();
                alert('Vui lòng kiểm tra lại thông tin mật khẩu.');
            } else {
                // Show loading state
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
                    submitBtn.disabled = true;
                }
            }
        });
    }
});

function calculatePasswordStrength(password) {
    let score = 0;
    let feedback = [];
    
    // Length check
    if (password.length >= 8) {
        score += 1;
    } else {
        feedback.push('Cần ít nhất 8 ký tự');
    }
    
    // Uppercase check
    if (/[A-Z]/.test(password)) {
        score += 1;
    } else {
        feedback.push('Cần có chữ hoa');
    }
    
    // Lowercase check
    if (/[a-z]/.test(password)) {
        score += 1;
    } else {
        feedback.push('Cần có chữ thường');
    }
    
    // Number check
    if (/\d/.test(password)) {
        score += 1;
    } else {
        feedback.push('Cần có số');
    }
    
    // Special character check
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        score += 1;
    } else {
        feedback.push('Cần có ký tự đặc biệt');
    }
    
    return { score, feedback };
}

function updateStrengthIndicator(strength) {
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    
    if (!strengthFill || !strengthText) return;
    
    // Remove existing classes
    strengthFill.className = 'strength-fill';
    strengthText.className = 'strength-text';
    
    if (strength.score === 0) {
        strengthText.textContent = 'Nhập mật khẩu mới';
    } else if (strength.score <= 1) {
        strengthFill.classList.add('weak');
        strengthText.classList.add('weak');
        strengthText.textContent = 'Rất yếu';
    } else if (strength.score <= 2) {
        strengthFill.classList.add('fair');
        strengthText.classList.add('fair');
        strengthText.textContent = 'Yếu';
    } else if (strength.score <= 3) {
        strengthFill.classList.add('good');
        strengthText.classList.add('good');
        strengthText.textContent = 'Trung bình';
    } else if (strength.score <= 4) {
        strengthFill.classList.add('strong');
        strengthText.classList.add('strong');
        strengthText.textContent = 'Mạnh';
    } else {
        strengthFill.classList.add('strong');
        strengthText.classList.add('strong');
        strengthText.textContent = 'Rất mạnh';
    }
}

function updateRequirements(password) {
    const requirements = {
        'req-length': password.length >= 8,
        'req-uppercase': /[A-Z]/.test(password),
        'req-lowercase': /[a-z]/.test(password),
        'req-number': /\d/.test(password),
        'req-special': /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };
    
    Object.keys(requirements).forEach(reqId => {
        const element = document.getElementById(reqId);
        if (element) {
            const icon = element.querySelector('i');
            if (requirements[reqId]) {
                element.classList.add('valid');
                if (icon) {
                    icon.classList.remove('fa-circle');
                    icon.classList.add('fa-check-circle');
                }
            } else {
                element.classList.remove('valid');
                if (icon) {
                    icon.classList.remove('fa-check-circle');
                    icon.classList.add('fa-circle');
                }
            }
        }
    });
}

function checkPasswordMatch() {
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const passwordMatch = document.getElementById('passwordMatch');
    
    if (!passwordMatch) return false;
    
    if (confirmPassword && newPassword === confirmPassword) {
        passwordMatch.classList.add('show');
        return true;
    } else {
        passwordMatch.classList.remove('show');
        return false;
    }
}

function checkFormValidity() {
    const currentPassword = document.getElementById('current_password').value;
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const submitBtn = document.getElementById('submitBtn');
    
    const isValid = currentPassword && 
                   newPassword && 
                   confirmPassword && 
                   newPassword === confirmPassword && 
                   newPassword.length >= 8;
    
    if (submitBtn) {
        submitBtn.disabled = !isValid;
    }
    
    return isValid;
}

// Add animation to form elements
document.addEventListener('DOMContentLoaded', function() {
    const formGroups = document.querySelectorAll('.form-group');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    formGroups.forEach(group => {
        group.style.opacity = '0';
        group.style.transform = 'translateY(20px)';
        group.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(group);
    });
});
