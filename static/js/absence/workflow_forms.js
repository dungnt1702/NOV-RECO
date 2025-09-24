// Workflow Forms JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
    
    function initializePage() {
        setupCheckboxHandlers();
        setupFormValidation();
    }
    
    function setupCheckboxHandlers() {
        const checkboxes = [
            'requires_department_manager',
            'requires_department_deputy',
            'requires_office_director',
            'requires_office_deputy',
            'requires_hr_approval'
        ];

        checkboxes.forEach(checkboxId => {
            const checkbox = document.getElementById(checkboxId);
            if (checkbox) {
                checkbox.addEventListener('change', function() {
                    const stepSettings = this.closest('.approval-step').querySelector('.step-settings');
                    if (this.checked) {
                        stepSettings.classList.add('show');
                    } else {
                        stepSettings.classList.remove('show');
                    }
                });
            }
        });
    }
    
    function setupFormValidation() {
        const form = document.querySelector('form[id$="Form"]');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (!validateForm()) {
                    e.preventDefault();
                }
            });
        }
    }
    
    function validateForm() {
        const department = document.getElementById('department').value;
        const absenceType = document.getElementById('absence_type').value;
        
        if (!department) {
            showNotification('Vui lòng chọn phòng ban', 'error');
            document.getElementById('department').focus();
            return false;
        }
        
        if (!absenceType) {
            showNotification('Vui lòng chọn loại vắng mặt', 'error');
            document.getElementById('absence_type').focus();
            return false;
        }
        
        // Check if at least one approval step is selected
        const checkboxes = [
            'requires_department_manager',
            'requires_department_deputy',
            'requires_office_director',
            'requires_office_deputy',
            'requires_hr_approval'
        ];
        
        const hasApprovalStep = checkboxes.some(id => {
            const checkbox = document.getElementById(id);
            return checkbox && checkbox.checked;
        });
        
        if (!hasApprovalStep) {
            showNotification('Vui lòng chọn ít nhất một bước phê duyệt', 'error');
            return false;
        }
        
        return true;
    }
    
    // Utility functions
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
