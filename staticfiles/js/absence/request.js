// Absence Request Form JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('absenceRequestForm');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    const totalDaysDisplay = document.getElementById('total_days');
    const absenceTypeSelect = document.getElementById('absence_type');
    const workflowInfo = document.getElementById('workflowInfo');
    const workflowDetails = document.getElementById('workflowDetails');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('attachment');
    const filePreview = document.getElementById('filePreview');

    // Initialize form
    initializeForm();

    // Event listeners
    startDateInput.addEventListener('change', calculateTotalDays);
    endDateInput.addEventListener('change', calculateTotalDays);
    startTimeInput.addEventListener('change', calculateTotalDays);
    endTimeInput.addEventListener('change', calculateTotalDays);
    absenceTypeSelect.addEventListener('change', loadWorkflowInfo);
    
    // File upload events
    fileUploadArea.addEventListener('click', () => fileInput.click());
    fileUploadArea.addEventListener('dragover', handleDragOver);
    fileUploadArea.addEventListener('dragleave', handleDragLeave);
    fileUploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);

    // Form submission
    form.addEventListener('submit', handleFormSubmit);

    function initializeForm() {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        endDateInput.min = today;

        // Load absence types
        loadAbsenceTypes();

        // Set initial end date to start date
        startDateInput.addEventListener('change', function() {
            if (!endDateInput.value || endDateInput.value < this.value) {
                endDateInput.value = this.value;
            }
            endDateInput.min = this.value;
        });
    }

    async function loadAbsenceTypes() {
        try {
            const response = await fetch('/absence/api/types/');
            const data = await response.json();
            
            if (data.success) {
                absenceTypeSelect.innerHTML = '<option value="">-- Chọn loại vắng mặt --</option>';
                data.types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.id;
                    option.textContent = type.name;
                    option.dataset.maxDays = type.max_days_per_year || '';
                    option.dataset.requiresApproval = type.requires_approval;
                    absenceTypeSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading absence types:', error);
            showNotification('Lỗi khi tải danh sách loại vắng mặt', 'error');
        }
    }

    async function loadWorkflowInfo() {
        const selectedType = absenceTypeSelect.value;
        if (!selectedType) {
            workflowDetails.innerHTML = '<p>Workflow sẽ được hiển thị sau khi chọn loại vắng mặt</p>';
            return;
        }

        try {
            const response = await fetch(`/absence/api/workflow/?type_id=${selectedType}`);
            const data = await response.json();
            
            if (data.success && data.workflow) {
                displayWorkflowInfo(data.workflow);
            } else {
                workflowDetails.innerHTML = '<p>Không tìm thấy workflow cho loại vắng mặt này</p>';
            }
        } catch (error) {
            console.error('Error loading workflow:', error);
            workflowDetails.innerHTML = '<p>Lỗi khi tải thông tin workflow</p>';
        }
    }

    function displayWorkflowInfo(workflow) {
        const steps = [];
        
        if (workflow.requires_department_manager) {
            steps.push({
                icon: 'fas fa-user-tie',
                title: 'Trưởng phòng',
                timeout: workflow.department_manager_timeout_hours
            });
        }
        
        if (workflow.requires_department_deputy) {
            steps.push({
                icon: 'fas fa-user-friends',
                title: 'Phó phòng',
                timeout: workflow.department_deputy_timeout_hours
            });
        }
        
        if (workflow.requires_office_director) {
            steps.push({
                icon: 'fas fa-crown',
                title: 'Giám đốc Văn phòng',
                timeout: workflow.office_director_timeout_hours
            });
        }
        
        if (workflow.requires_office_deputy) {
            steps.push({
                icon: 'fas fa-user-shield',
                title: 'Phó Giám đốc',
                timeout: workflow.office_deputy_timeout_hours
            });
        }
        
        if (workflow.requires_hr_approval) {
            steps.push({
                icon: 'fas fa-user-check',
                title: 'HR',
                timeout: workflow.hr_timeout_hours
            });
        }

        let workflowHTML = '<div class="workflow-steps">';
        steps.forEach((step, index) => {
            workflowHTML += `
                <div class="workflow-step">
                    <i class="${step.icon}"></i>
                    <span>${step.title}</span>
                </div>
            `;
            if (index < steps.length - 1) {
                workflowHTML += '<div class="workflow-arrow"><i class="fas fa-arrow-right"></i></div>';
            }
        });
        workflowHTML += '</div>';

        workflowHTML += `
            <div class="workflow-details">
                <p><strong>Thời gian phê duyệt:</strong></p>
                <ul>
        `;
        
        steps.forEach(step => {
            workflowHTML += `<li>${step.title}: ${step.timeout} giờ</li>`;
        });
        
        workflowHTML += `
                </ul>
                <p><strong>Nhắc nhở:</strong> ${workflow.send_reminder_before_hours} giờ trước khi hết hạn</p>
            </div>
        `;

        workflowDetails.innerHTML = workflowHTML;
    }

    function calculateTotalDays() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const startTime = startTimeInput.value;
        const endTime = endTimeInput.value;

        if (!startDate || !endDate) {
            totalDaysDisplay.textContent = '0';
            return;
        }

        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (end < start) {
            totalDaysDisplay.textContent = '0';
            return;
        }

        let totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;

        // If times are specified, calculate partial days
        if (startTime && endTime) {
            const startTimeParts = startTime.split(':');
            const endTimeParts = endTime.split(':');
            const startHour = parseInt(startTimeParts[0]) + parseInt(startTimeParts[1]) / 60;
            const endHour = parseInt(endTimeParts[0]) + parseInt(endTimeParts[1]) / 60;
            
            const workHours = endHour - startHour;
            const workDayFraction = workHours / 8; // Assuming 8-hour work day
            
            totalDays = workDayFraction;
        }

        totalDaysDisplay.textContent = totalDays.toFixed(2);
    }

    function handleDragOver(e) {
        e.preventDefault();
        fileUploadArea.classList.add('dragover');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
    }

    function handleDrop(e) {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    }

    function handleFile(file) {
        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            showNotification('Tệp quá lớn. Kích thước tối đa là 10MB.', 'error');
            return;
        }

        // Validate file type
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/jpg',
            'image/png'
        ];

        if (!allowedTypes.includes(file.type)) {
            showNotification('Loại tệp không được hỗ trợ. Chỉ chấp nhận PDF, DOC, DOCX, JPG, PNG.', 'error');
            return;
        }

        // Display file preview
        displayFilePreview(file);
    }

    function displayFilePreview(file) {
        const fileSize = formatFileSize(file.size);
        const fileType = getFileTypeIcon(file.type);
        
        filePreview.innerHTML = `
            <div class="file-preview-item">
                <i class="file-preview-icon ${fileType.icon}"></i>
                <div class="file-preview-info">
                    <div class="file-preview-name">${file.name}</div>
                    <div class="file-preview-size">${fileSize}</div>
                </div>
                <i class="file-preview-remove fas fa-times" onclick="removeFile()"></i>
            </div>
        `;
        
        filePreview.classList.add('show');
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function getFileTypeIcon(type) {
        if (type.includes('pdf')) return { icon: 'fas fa-file-pdf', color: '#dc3545' };
        if (type.includes('word')) return { icon: 'fas fa-file-word', color: '#007bff' };
        if (type.includes('image')) return { icon: 'fas fa-file-image', color: '#28a745' };
        return { icon: 'fas fa-file', color: '#6c757d' };
    }

    window.removeFile = function() {
        fileInput.value = '';
        filePreview.classList.remove('show');
        filePreview.innerHTML = '';
    };

    async function handleFormSubmit(e) {
        e.preventDefault();
        
        // Validate form
        if (!validateForm()) {
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang gửi...';
        submitBtn.disabled = true;

        try {
            const formData = new FormData(form);
            
            const response = await fetch('/absence/api/create/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                showNotification('Đơn vắng mặt đã được gửi thành công!', 'success');
                setTimeout(() => {
                    window.location.href = '/absence/list/';
                }, 2000);
            } else {
                showNotification(data.message || 'Có lỗi xảy ra khi gửi đơn vắng mặt', 'error');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            showNotification('Có lỗi xảy ra khi gửi đơn vắng mặt', 'error');
        } finally {
            // Reset button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    function validateForm() {
        const absenceType = absenceTypeSelect.value;
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const reason = document.getElementById('reason').value;

        if (!absenceType) {
            showNotification('Vui lòng chọn loại vắng mặt', 'error');
            absenceTypeSelect.focus();
            return false;
        }

        if (!startDate) {
            showNotification('Vui lòng chọn ngày bắt đầu', 'error');
            startDateInput.focus();
            return false;
        }

        if (!endDate) {
            showNotification('Vui lòng chọn ngày kết thúc', 'error');
            endDateInput.focus();
            return false;
        }

        if (new Date(endDate) < new Date(startDate)) {
            showNotification('Ngày kết thúc không thể trước ngày bắt đầu', 'error');
            endDateInput.focus();
            return false;
        }

        if (!reason.trim()) {
            showNotification('Vui lòng nhập lý do vắng mặt', 'error');
            document.getElementById('reason').focus();
            return false;
        }

        // Check if absence type has max days limit
        const selectedOption = absenceTypeSelect.options[absenceTypeSelect.selectedIndex];
        const maxDays = selectedOption.dataset.maxDays;
        const totalDays = parseFloat(totalDaysDisplay.textContent);

        if (maxDays && totalDays > parseFloat(maxDays)) {
            showNotification(`Số ngày vắng mặt (${totalDays}) vượt quá giới hạn cho phép (${maxDays} ngày)`, 'error');
            return false;
        }

        return true;
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
            color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
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
