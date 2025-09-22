// Employee Form JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize employee form
    initializeEmployeeForm();
    
    // Setup avatar upload
    setupAvatarUpload();
    
    // Setup form validation
    setupFormValidation();
    
    // Setup form sections
    setupFormSections();
});

function initializeEmployeeForm() {
    console.log('Employee Form initialized');
    
    // Add animation to form elements
    const formElements = document.querySelectorAll('.form-group');
    formElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function setupAvatarUpload() {
    const avatarInput = document.getElementById('avatar');
    const avatarPreview = document.getElementById('avatarPreview');
    const avatarUploadBtn = document.getElementById('avatarUploadBtn');
    
    if (!avatarInput || !avatarPreview || !avatarUploadBtn) return;
    
    // Handle file selection
    avatarInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file');
                return;
            }
            
            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size must be less than 5MB');
                return;
            }
            
            // Create preview
            const reader = new FileReader();
            reader.onload = function(e) {
                avatarPreview.innerHTML = `<img src="${e.target.result}" alt="Avatar Preview">`;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Handle upload button click
    avatarUploadBtn.addEventListener('click', function() {
        avatarInput.click();
    });
    
    // Handle drag and drop
    avatarPreview.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = '#667eea';
        this.style.backgroundColor = '#f8f9fa';
    });
    
    avatarPreview.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = '#e9ecef';
        this.style.backgroundColor = '#f8f9fa';
    });
    
    avatarPreview.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '#e9ecef';
        this.style.backgroundColor = '#f8f9fa';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                avatarInput.files = files;
                avatarInput.dispatchEvent(new Event('change'));
            } else {
                alert('Please drop an image file');
            }
        }
    });
}

function setupFormValidation() {
    const form = document.getElementById('employeeForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        if (!validateForm()) {
            return;
        }
        
        // Show loading state
        const submitBtn = document.getElementById('saveEmployeeBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        }
        
        // Simulate form submission
        setTimeout(() => {
            console.log('Form submitted successfully');
            // In real implementation, this would submit the form
            alert('Employee saved successfully!');
            
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-save"></i> Save Employee';
            }
        }, 2000);
    });
    
    // Real-time validation
    const requiredFields = form.querySelectorAll('input[required], textarea[required], select[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
        
        field.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                validateField(this);
            }
        });
    });
}

function validateForm() {
    const form = document.getElementById('employeeForm');
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    // Validate email format
    const emailField = document.getElementById('email');
    if (emailField && emailField.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value)) {
            showFieldError(emailField, 'Please enter a valid email address');
            isValid = false;
        } else {
            clearFieldError(emailField);
        }
    }
    
    // Validate phone format
    const phoneField = document.getElementById('phone');
    if (phoneField && phoneField.value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(phoneField.value.replace(/\s/g, ''))) {
            showFieldError(phoneField, 'Please enter a valid phone number');
            isValid = false;
        } else {
            clearFieldError(phoneField);
        }
    }
    
    return isValid;
}

function validateField(field) {
    if (!field) return false;
    
    const value = field.value.trim();
    const isRequired = field.hasAttribute('required');
    
    if (isRequired && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    clearFieldError(field);
    return true;
}

function showFieldError(field, message) {
    if (!field) return;
    
    field.style.borderColor = '#dc3545';
    field.classList.add('error');
    field.classList.remove('success');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    if (!field) return;
    
    field.style.borderColor = '#e9ecef';
    field.classList.remove('error');
    field.classList.add('success');
    
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function setupFormSections() {
    // Add section toggle functionality
    const sectionTitles = document.querySelectorAll('.form-section-title');
    sectionTitles.forEach(title => {
        title.style.cursor = 'pointer';
        title.addEventListener('click', function() {
            const section = this.parentNode;
            const content = section.querySelector('.form-group');
            
            if (content) {
                content.style.display = content.style.display === 'none' ? 'block' : 'none';
            }
        });
    });
}

// Add real-time character counting for textarea fields
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    textareas.forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('maxlength'));
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.style.fontSize = '0.875rem';
        counter.style.color = '#6c757d';
        counter.style.textAlign = 'right';
        counter.style.marginTop = '0.25rem';
        
        textarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${remaining} characters remaining`;
            counter.style.color = remaining < 0 ? '#dc3545' : '#6c757d';
        }
        
        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });
});

// Add form auto-save functionality
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('employeeForm');
    if (!form) return;
    
    const formData = {};
    
    // Load saved data
    const savedData = localStorage.getItem('employeeFormData');
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            });
        } catch (e) {
            console.error('Error loading saved form data:', e);
        }
    }
    
    // Save data on input
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            formData[this.name] = this.value;
            localStorage.setItem('employeeFormData', JSON.stringify(formData));
        });
    });
    
    // Clear saved data on successful submit
    form.addEventListener('submit', function() {
        localStorage.removeItem('employeeFormData');
    });
});
