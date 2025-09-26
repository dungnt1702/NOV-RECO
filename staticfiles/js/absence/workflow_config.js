// Workflow Config JavaScript
document.addEventListener('DOMContentLoaded', function() {
    let currentWorkflowId = null;

    // Initialize
    initializePage();

    function initializePage() {
        setupEventListeners();
    }

    function setupEventListeners() {
        // Add workflow button
        document.getElementById('addWorkflowBtn').addEventListener('click', addWorkflow);
        
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', refreshPage);
        
        // Save workflow button
        document.getElementById('saveWorkflowBtn').addEventListener('click', saveWorkflow);
        
        // Checkbox change handlers
        setupCheckboxHandlers();
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

    function addWorkflow() {
        currentWorkflowId = null;
        resetForm();
        showModal('Thêm Workflow');
    }

    function editWorkflow(workflowId) {
        currentWorkflowId = workflowId;
        loadWorkflowData(workflowId);
        showModal('Sửa Workflow');
    }

    async function loadWorkflowData(workflowId) {
        try {
            const response = await fetch(`/absence/api/workflow/${workflowId}/`);
            const data = await response.json();
            
            if (data.success) {
                const workflow = data.workflow;
                
                // Populate form
                document.getElementById('department').value = workflow.department_id;
                document.getElementById('absence_type').value = workflow.absence_type_id;
                
                // Checkboxes
                document.getElementById('requires_department_manager').checked = workflow.requires_department_manager;
                document.getElementById('requires_department_deputy').checked = workflow.requires_department_deputy;
                document.getElementById('requires_office_director').checked = workflow.requires_office_director;
                document.getElementById('requires_office_deputy').checked = workflow.requires_office_deputy;
                document.getElementById('requires_hr_approval').checked = workflow.requires_hr_approval;
                
                // Timeout hours
                document.getElementById('department_manager_timeout_hours').value = workflow.department_manager_timeout_hours;
                document.getElementById('department_deputy_timeout_hours').value = workflow.department_deputy_timeout_hours;
                document.getElementById('office_director_timeout_hours').value = workflow.office_director_timeout_hours;
                document.getElementById('office_deputy_timeout_hours').value = workflow.office_deputy_timeout_hours;
                document.getElementById('hr_timeout_hours').value = workflow.hr_timeout_hours;
                
                // Settings
                document.getElementById('send_reminder_before_hours').value = workflow.send_reminder_before_hours;
                document.getElementById('max_reminders').value = workflow.max_reminders;
                document.getElementById('is_active').checked = workflow.is_active;
                
                // Show/hide step settings
                setupCheckboxHandlers();
                updateStepSettingsVisibility();
            } else {
                showNotification('Lỗi khi tải dữ liệu workflow', 'error');
            }
        } catch (error) {
            console.error('Error loading workflow data:', error);
            showNotification('Có lỗi xảy ra khi tải dữ liệu', 'error');
        }
    }

    function updateStepSettingsVisibility() {
        const checkboxes = [
            'requires_department_manager',
            'requires_department_deputy',
            'requires_office_director',
            'requires_office_deputy',
            'requires_hr_approval'
        ];

        checkboxes.forEach(checkboxId => {
            const checkbox = document.getElementById(checkboxId);
            const stepSettings = checkbox.closest('.approval-step').querySelector('.step-settings');
            
            if (checkbox.checked) {
                stepSettings.classList.add('show');
            } else {
                stepSettings.classList.remove('show');
            }
        });
    }

    async function saveWorkflow() {
        const form = document.getElementById('workflowForm');
        const formData = new FormData(form);
        
        // Validate form
        if (!validateForm()) {
            return;
        }

        try {
            const submitBtn = document.getElementById('saveWorkflowBtn');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lưu...';
            submitBtn.disabled = true;

            const url = currentWorkflowId ? 
                `/absence/api/workflow/${currentWorkflowId}/` : 
                '/absence/api/workflow/';
            
            const method = currentWorkflowId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                showNotification(
                    currentWorkflowId ? 'Workflow đã được cập nhật' : 'Workflow đã được tạo', 
                    'success'
                );
                
                // Hide modal
                const modal = document.getElementById('workflowModal');
                const bsModal = bootstrap.Modal.getInstance(modal);
                bsModal.hide();
                
                // Refresh page
                refreshPage();
            } else {
                showNotification(data.message || 'Có lỗi xảy ra', 'error');
            }
        } catch (error) {
            console.error('Error saving workflow:', error);
            showNotification('Có lỗi xảy ra khi lưu workflow', 'error');
        } finally {
            const submitBtn = document.getElementById('saveWorkflowBtn');
            submitBtn.innerHTML = '<i class="fas fa-save"></i> Lưu Workflow';
            submitBtn.disabled = false;
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
        
        const hasApprovalStep = checkboxes.some(id => document.getElementById(id).checked);
        
        if (!hasApprovalStep) {
            showNotification('Vui lòng chọn ít nhất một bước phê duyệt', 'error');
            return false;
        }
        
        return true;
    }

    function resetForm() {
        document.getElementById('workflowForm').reset();
        
        // Hide all step settings
        document.querySelectorAll('.step-settings').forEach(settings => {
            settings.classList.remove('show');
        });
        
        // Show HR step settings by default
        document.getElementById('requires_hr_approval').checked = true;
        document.querySelector('#requires_hr_approval').closest('.approval-step').querySelector('.step-settings').classList.add('show');
    }

    function showModal(title) {
        document.getElementById('workflowModalTitle').innerHTML = `<i class="fas fa-cogs"></i> ${title}`;
        
        const modal = document.getElementById('workflowModal');
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    function refreshPage() {
        window.location.reload();
    }

    // Global functions
    window.deleteWorkflow = async function(workflowId) {
        if (!confirm('Bạn có chắc chắn muốn xóa workflow này?')) {
            return;
        }

        try {
            const response = await fetch(`/absence/api/workflow/${workflowId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();
            if (data.success) {
                showNotification('Workflow đã được xóa', 'success');
                refreshPage();
            } else {
                showNotification(data.message || 'Có lỗi xảy ra', 'error');
            }
        } catch (error) {
            console.error('Error deleting workflow:', error);
            showNotification('Có lỗi xảy ra khi xóa workflow', 'error');
        }
    };

    // Utility functions
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

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
