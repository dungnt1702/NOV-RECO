// Absence Detail JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const urlParts = window.location.pathname.split('/');
    const requestId = urlParts[urlParts.length - 2];
    
    let requestData = null;

    // Initialize
    initializePage();

    function initializePage() {
        loadRequestDetail();
        setupApprovalModal();
    }

    async function loadRequestDetail() {
        try {
            showLoading(true);
            const response = await fetch(`/absence/api/requests/${requestId}/`);
            const data = await response.json();
            
            if (data.success) {
                requestData = data.request;
                populateRequestInfo();
                loadWorkflowTimeline();
                loadApprovalHistory();
                setupActionButtons();
            } else {
                showNotification('Không tìm thấy đơn vắng mặt', 'error');
                setTimeout(() => {
                    window.location.href = '/absence/list/';
                }, 2000);
            }
        } catch (error) {
            console.error('Error loading request detail:', error);
            showNotification('Lỗi khi tải chi tiết đơn vắng mặt', 'error');
        } finally {
            showLoading(false);
        }
    }

    function populateRequestInfo() {
        if (!requestData) return;

        // Basic info
        document.getElementById('employeeName').textContent = requestData.user_name || 'N/A';
        document.getElementById('departmentName').textContent = requestData.user_department_name || 'N/A';
        document.getElementById('absenceType').textContent = requestData.absence_type_name || 'N/A';
        document.getElementById('createdAt').textContent = formatDateTime(requestData.created_at);
        document.getElementById('startDate').textContent = formatDate(requestData.start_date);
        document.getElementById('endDate').textContent = formatDate(requestData.end_date);
        document.getElementById('totalDays').textContent = requestData.total_days || '0';
        document.getElementById('updatedAt').textContent = formatDateTime(requestData.updated_at);
        document.getElementById('reason').textContent = requestData.reason || 'N/A';

        // Status badge
        const statusBadge = document.getElementById('statusBadge');
        statusBadge.className = `status-badge status-${requestData.status}`;
        statusBadge.textContent = getStatusText(requestData.status);

        // Current status info
        document.getElementById('currentStatus').textContent = getStatusText(requestData.status);
        document.getElementById('currentLevel').textContent = getApprovalLevelText(requestData.approval_level);
        document.getElementById('currentApprover').textContent = requestData.current_approver_name || 'N/A';

        // Timeout info
        if (requestData.status === 'pending' && requestData.current_approver) {
            const timeoutSection = document.getElementById('timeoutSection');
            timeoutSection.style.display = 'block';
            document.getElementById('timeoutInfo').textContent = getTimeoutInfo(requestData);
        }

        // Attachment
        if (requestData.attachment) {
            const attachmentSection = document.getElementById('attachmentSection');
            attachmentSection.style.display = 'block';
            document.getElementById('attachmentInfo').innerHTML = `
                <div class="attachment-info">
                    <i class="attachment-icon fas fa-file"></i>
                    <div class="attachment-details">
                        <div class="attachment-name">${requestData.attachment_name || 'Tệp đính kèm'}</div>
                        <div class="attachment-size">${formatFileSize(requestData.attachment_size || 0)}</div>
                    </div>
                    <a href="${requestData.attachment_url}" class="attachment-download" target="_blank">
                        <i class="fas fa-download"></i> Tải xuống
                    </a>
                </div>
            `;
        }

        // Related info
        document.getElementById('workflowInfo').textContent = requestData.workflow_name || 'N/A';
        document.getElementById('waitingTime').textContent = getWaitingTime(requestData.created_at);
        document.getElementById('reminderCount').textContent = requestData.reminder_count || '0';
    }

    async function loadWorkflowTimeline() {
        try {
            const response = await fetch(`/absence/api/workflow/${requestData.id}/`);
            const data = await response.json();
            
            if (data.success && data.workflow) {
                displayWorkflowTimeline(data.workflow);
            }
        } catch (error) {
            console.error('Error loading workflow timeline:', error);
        }
    }

    function displayWorkflowTimeline(workflow) {
        const timeline = document.getElementById('workflowTimeline');
        const steps = [];

        // Build workflow steps
        if (workflow.requires_department_manager) {
            steps.push({
                level: 'department_manager',
                title: 'Trưởng phòng',
                icon: 'fas fa-user-tie',
                timeout: workflow.department_manager_timeout_hours,
                priority: workflow.department_manager_priority
            });
        }

        if (workflow.requires_department_deputy) {
            steps.push({
                level: 'department_deputy',
                title: 'Phó phòng',
                icon: 'fas fa-user-friends',
                timeout: workflow.department_deputy_timeout_hours,
                priority: workflow.department_deputy_priority
            });
        }

        if (workflow.requires_office_director) {
            steps.push({
                level: 'office_director',
                title: 'Giám đốc Văn phòng',
                icon: 'fas fa-crown',
                timeout: workflow.office_director_timeout_hours,
                priority: workflow.office_director_priority
            });
        }

        if (workflow.requires_office_deputy) {
            steps.push({
                level: 'office_deputy',
                title: 'Phó Giám đốc',
                icon: 'fas fa-user-shield',
                timeout: workflow.office_deputy_timeout_hours,
                priority: workflow.office_deputy_priority
            });
        }

        if (workflow.requires_hr_approval) {
            steps.push({
                level: 'hr_approval',
                title: 'HR',
                icon: 'fas fa-user-check',
                timeout: workflow.hr_timeout_hours,
                priority: 99
            });
        }

        // Sort by priority
        steps.sort((a, b) => a.priority - b.priority);

        // Generate timeline HTML
        let timelineHTML = '';
        steps.forEach((step, index) => {
            const isCompleted = isStepCompleted(step.level);
            const isCurrent = step.level === requestData.approval_level;
            const isRejected = requestData.status === 'rejected' && isCurrent;

            timelineHTML += `
                <div class="workflow-step ${isCompleted ? 'completed' : isCurrent ? (isRejected ? 'rejected' : 'current') : ''}">
                    <div class="workflow-step-content">
                        <div class="workflow-step-title">
                            <i class="${step.icon}"></i>
                            ${step.title}
                        </div>
                        <div class="workflow-step-details">
                            Thời gian phê duyệt: ${step.timeout} giờ
                        </div>
                        <div class="workflow-step-time">
                            ${getStepTimeInfo(step.level)}
                        </div>
                    </div>
                </div>
            `;
        });

        timeline.innerHTML = timelineHTML;
    }

    async function loadApprovalHistory() {
        try {
            const response = await fetch(`/absence/api/history/${requestData.id}/`);
            const data = await response.json();
            
            if (data.success) {
                displayApprovalHistory(data.history);
            }
        } catch (error) {
            console.error('Error loading approval history:', error);
        }
    }

    function displayApprovalHistory(history) {
        const historyContainer = document.getElementById('approvalHistory');
        
        if (history.length === 0) {
            historyContainer.innerHTML = '<p class="text-muted">Chưa có lịch sử phê duyệt</p>';
            return;
        }

        historyContainer.innerHTML = history.map(item => `
            <div class="history-item ${item.action}">
                <div class="history-header">
                    <div class="history-action">
                        <i class="fas fa-${getActionIcon(item.action)}"></i>
                        ${getActionText(item.action)}
                    </div>
                    <div class="history-time">${formatDateTime(item.created_at)}</div>
                </div>
                <div class="history-details">
                    <div class="info-item">
                        <span class="info-label">Người thực hiện:</span>
                        <span class="info-value">${item.approver_name}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Cấp độ:</span>
                        <span class="info-value">${getApprovalLevelText(item.level)}</span>
                    </div>
                </div>
                ${item.comment ? `
                    <div class="history-comment">
                        <strong>Bình luận:</strong> ${item.comment}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    function setupActionButtons() {
        const actionButtons = document.getElementById('actionButtons');
        let buttonsHTML = '';

        // View buttons (always available)
        buttonsHTML += `
            <a href="/absence/list/" class="btn btn-outline-primary">
                <i class="fas fa-list"></i>
                Danh sách đơn
            </a>
        `;

        // Approval buttons (if user can approve)
        if (requestData.can_approve && requestData.status === 'pending') {
            buttonsHTML += `
                <button class="btn btn-success" onclick="openApprovalModal('approved')">
                    <i class="fas fa-check"></i>
                    Phê duyệt
                </button>
                <button class="btn btn-danger" onclick="openApprovalModal('rejected')">
                    <i class="fas fa-times"></i>
                    Từ chối
                </button>
                <button class="btn btn-warning" onclick="openApprovalModal('delegated')">
                    <i class="fas fa-user-friends"></i>
                    Ủy quyền
                </button>
            `;
        }

        // Cancel button (if user is the requester)
        if (requestData.can_cancel && requestData.status === 'pending') {
            buttonsHTML += `
                <button class="btn btn-secondary" onclick="cancelRequest()">
                    <i class="fas fa-ban"></i>
                    Hủy đơn
                </button>
            `;
        }

        actionButtons.innerHTML = buttonsHTML;
    }

    function setupApprovalModal() {
        const modal = document.getElementById('approvalModal');
        const approvalButtons = modal.querySelectorAll('.approval-btn');
        const delegationSection = document.getElementById('delegationSection');
        const submitBtn = document.getElementById('submitApproval');

        approvalButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.dataset.action;
                
                // Update button states
                approvalButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Show/hide delegation section
                delegationSection.style.display = action === 'delegated' ? 'block' : 'none';
                
                // Update submit button
                submitBtn.dataset.action = action;
            });
        });

        submitBtn.addEventListener('click', handleApprovalSubmit);
    }

    function openApprovalModal(action) {
        const modal = document.getElementById('approvalModal');
        
        // Set action
        const actionBtn = modal.querySelector(`[data-action="${action}"]`);
        if (actionBtn) {
            actionBtn.click();
        }

        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    async function handleApprovalSubmit() {
        const action = document.getElementById('submitApproval').dataset.action;
        const comment = document.getElementById('approvalComment').value;
        const delegateTo = document.getElementById('delegateTo').value;

        if (!action) {
            showNotification('Thiếu thông tin cần thiết', 'error');
            return;
        }

        if (action === 'delegated' && !delegateTo) {
            showNotification('Vui lòng chọn người ủy quyền', 'error');
            return;
        }

        try {
            const submitBtn = document.getElementById('submitApproval');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
            submitBtn.disabled = true;

            const response = await fetch(`/absence/api/approve/${requestData.id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    action: action,
                    comment: comment,
                    delegate_to: delegateTo
                })
            });

            const data = await response.json();

            if (data.success) {
                showNotification(`Đơn vắng mặt đã được ${getActionText(action)} thành công`, 'success');
                
                // Hide modal
                const modal = document.getElementById('approvalModal');
                const bsModal = bootstrap.Modal.getInstance(modal);
                bsModal.hide();
                
                // Reload data
                loadRequestDetail();
            } else {
                showNotification(data.message || 'Có lỗi xảy ra', 'error');
            }
        } catch (error) {
            console.error('Error submitting approval:', error);
            showNotification('Có lỗi xảy ra khi xử lý phê duyệt', 'error');
        } finally {
            const submitBtn = document.getElementById('submitApproval');
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Gửi quyết định';
            submitBtn.disabled = false;
        }
    }

    // Global functions
    window.cancelRequest = async function() {
        if (confirm('Bạn có chắc chắn muốn hủy đơn vắng mặt này?')) {
            try {
                const response = await fetch(`/absence/api/approve/${requestData.id}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        action: 'cancelled',
                        comment: 'Người dùng hủy đơn'
                    })
                });

                const data = await response.json();
                if (data.success) {
                    showNotification('Đơn vắng mặt đã được hủy', 'success');
                    loadRequestDetail();
                } else {
                    showNotification(data.message || 'Có lỗi xảy ra', 'error');
                }
            } catch (error) {
                console.error('Error cancelling request:', error);
                showNotification('Có lỗi xảy ra khi hủy đơn', 'error');
            }
        }
    };

    // Utility functions
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
    }

    function formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('vi-VN');
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function getStatusText(status) {
        const statusMap = {
            'pending': 'Đang chờ phê duyệt',
            'approved': 'Đã phê duyệt',
            'rejected': 'Đã từ chối',
            'cancelled': 'Đã hủy',
            'auto_approved': 'Tự động phê duyệt',
            'auto_rejected': 'Tự động từ chối'
        };
        return statusMap[status] || status;
    }

    function getApprovalLevelText(level) {
        const levelMap = {
            'employee': 'Nhân viên',
            'department_manager': 'Trưởng phòng',
            'department_deputy': 'Phó phòng',
            'office_director': 'Giám đốc Văn phòng',
            'office_deputy': 'Phó Giám đốc',
            'hr_approval': 'HR',
            'final_approved': 'Phê duyệt cuối cùng'
        };
        return levelMap[level] || level;
    }

    function getTimeoutInfo(request) {
        const created = new Date(request.created_at);
        const now = new Date();
        const diffMs = now - created;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        
        // This would need to be calculated based on workflow timeout
        return `Đã chờ ${diffHours} giờ`;
    }

    function getWaitingTime(createdAt) {
        const created = new Date(createdAt);
        const now = new Date();
        const diffMs = now - created;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        
        if (diffDays > 0) {
            return `${diffDays} ngày ${diffHours} giờ`;
        } else if (diffHours > 0) {
            return `${diffHours} giờ`;
        } else {
            return 'Vừa tạo';
        }
    }

    function isStepCompleted(level) {
        // This would need to be determined based on approval history
        return false;
    }

    function getStepTimeInfo(level) {
        // This would need to be determined based on approval history
        return 'Chưa xử lý';
    }

    function getActionIcon(action) {
        const iconMap = {
            'submitted': 'paper-plane',
            'approved': 'check-circle',
            'rejected': 'times-circle',
            'delegated': 'user-friends',
            'cancelled': 'ban',
            'commented': 'comment'
        };
        return iconMap[action] || 'info-circle';
    }

    function getActionText(action) {
        const actionMap = {
            'submitted': 'Đã gửi',
            'approved': 'Đã phê duyệt',
            'rejected': 'Đã từ chối',
            'delegated': 'Đã ủy quyền',
            'cancelled': 'Đã hủy',
            'commented': 'Đã bình luận'
        };
        return actionMap[action] || action;
    }

    function getActionText(action) {
        const actionMap = {
            'approved': 'phê duyệt',
            'rejected': 'từ chối',
            'delegated': 'ủy quyền',
            'cancelled': 'hủy'
        };
        return actionMap[action] || action;
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function showLoading(show) {
        const loadingElements = document.querySelectorAll('.detail-card');
        loadingElements.forEach(el => {
            el.classList.toggle('loading', show);
        });
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
