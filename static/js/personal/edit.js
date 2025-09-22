// Personal Edit JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Avatar preview functionality
    const avatarInput = document.getElementById('avatar');
    const avatarPreview = document.querySelector('.avatar-preview');
    const avatarPlaceholder = document.querySelector('.avatar-placeholder');
    
    if (avatarInput) {
        avatarInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Chỉ chấp nhận file ảnh JPG, PNG, GIF.');
                    this.value = '';
                    return;
                }
                
                // Validate file size (5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('Kích thước ảnh không được vượt quá 5MB.');
                    this.value = '';
                    return;
                }
                
                // Create preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (avatarPreview) {
                        avatarPreview.src = e.target.result;
                        avatarPreview.style.display = 'block';
                        if (avatarPlaceholder) {
                            avatarPlaceholder.style.display = 'none';
                        }
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Form validation
    const form = document.querySelector('.edit-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('input[required], select[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                } else {
                    field.style.borderColor = '#e9ecef';
                }
            });
            
            // Email validation
            const emailField = document.getElementById('email');
            if (emailField && emailField.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailField.value)) {
                    emailField.style.borderColor = '#dc3545';
                    isValid = false;
                }
            }
            
            // Phone validation
            const phoneField = document.getElementById('phone');
            if (phoneField && phoneField.value) {
                const phoneRegex = /^[0-9+\-\s()]+$/;
                if (!phoneRegex.test(phoneField.value)) {
                    phoneField.style.borderColor = '#dc3545';
                    isValid = false;
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                alert('Vui lòng kiểm tra lại thông tin đã nhập.');
            } else {
                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lưu...';
                    submitBtn.disabled = true;
                }
            }
        });
    }
    
    // Real-time validation
    const emailField = document.getElementById('email');
    if (emailField) {
        emailField.addEventListener('blur', function() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                this.style.borderColor = '#dc3545';
                showFieldError(this, 'Email không hợp lệ');
            } else {
                this.style.borderColor = '#e9ecef';
                hideFieldError(this);
            }
        });
    }
    
    const phoneField = document.getElementById('phone');
    if (phoneField) {
        phoneField.addEventListener('blur', function() {
            const phoneRegex = /^[0-9+\-\s()]+$/;
            if (this.value && !phoneRegex.test(this.value)) {
                this.style.borderColor = '#dc3545';
                showFieldError(this, 'Số điện thoại không hợp lệ');
            } else {
                this.style.borderColor = '#e9ecef';
                hideFieldError(this);
            }
        });
    }
    
    // Date validation
    const dateField = document.getElementById('date_of_birth');
    if (dateField) {
        dateField.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const today = new Date();
            
            if (selectedDate > today) {
                this.style.borderColor = '#dc3545';
                showFieldError(this, 'Ngày sinh không thể là ngày trong tương lai');
            } else {
                this.style.borderColor = '#e9ecef';
                hideFieldError(this);
            }
        });
    }
    
    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'character-counter';
            counter.style.cssText = 'font-size: 0.8rem; color: #6c757d; text-align: right; margin-top: 0.25rem;';
            textarea.parentNode.appendChild(counter);
            
            const updateCounter = () => {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${textarea.value.length}/${maxLength} ký tự`;
                counter.style.color = remaining < 50 ? '#dc3545' : '#6c757d';
            };
            
            textarea.addEventListener('input', updateCounter);
            updateCounter();
        }
    });
    
    // Add animation to form sections
    const sections = document.querySelectorAll('.form-section');
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
    
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
});

// Helper functions
function showFieldError(field, message) {
    hideFieldError(field);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = 'color: #dc3545; font-size: 0.8rem; margin-top: 0.25rem;';
    field.parentNode.appendChild(errorDiv);
}

function hideFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}
