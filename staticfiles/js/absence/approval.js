// Absence Approval JavaScript
document.addEventListener('DOMContentLoaded', function() {
    let currentFilters = {};
    let approvalData = [];

    // Initialize
    initializePage();

    function initializePage() {
        setupEventListeners();
        loadApprovalData();
        setupFilters();
    }

    function setupEventListeners() {
        // Filter toggle
        const filterToggle = document.getElementById('filterToggle');
        const filterBody = document.getElementById('filterBody');
        
        filterToggle.addEventListener('click', function() {
            filterBody.classList.toggle('collapsed');
            const icon = filterToggle.querySelector('i');
            icon.classList.toggle('fa-chevron-down');
            icon.classList.toggle('fa-chevron-up');
        });

        // Filter actions
        document.getElementById('applyFilters').addEventListener('click', applyFilters);
        document.getElementById('resetFilters').addEventListener('click', resetFilters);

        // Approval modal events
        setupApprovalModal();
    }

    async function loadApprovalData() {
        try {
            showLoading(true);
            const response = await fetch('/absence/api/requests/?pending=true');
            const data = await response.json();
            
            if (data.success) {
                approvalData = data.requests;
                renderApprovalList();
                updateStats();
            } else {
                showEmptyState();
            }
        } catch (error) {
            console.error('Error loading approval data:', error);
            showNotification('Lỗi khi tải dữ liệu phê duyệt', 'error');
        } finally {
            showLoading(false);
        }
    }

    async function setupFilters() {
        try {
            // Load absence types
            const typesResponse = await fetch('/absence/api/types/');
            const typesData = await typesResponse.json();
            
            if (typesData.success) {
                const typeFilter = document.getElementById('typeFilter');
                typeFilter.innerHTML = '<option value="">Tất cả loại</option>';
                typesData.types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.id;
                    option.textContent = type.name;
                    typeFilter.appendChild(option);
                });
            }

            // Load departments
            const deptResponse = await fetch('/users/api/departments/');
            const deptData = await deptResponse.json();
            
            if (deptData.success) {
                const deptFilter = document.getElementById('departmentFilter');
                deptFilter.innerHTML = '<option value="">Tất cả phòng ban</option>';
                deptData.departments.forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept.id;
                    option.textContent = dept.full_name || dept.name;
                    deptFilter.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error setting up filters:', error);
        }
    }

    function applyFilters() {
        currentFilters = {
            level: document.getElementById('levelFilter').value,
            type: document.getElementById('typeFilter').value,
            department: document.getElementById('departmentFilter').value,
            priority: document.getElementById('priorityFilter').value
        };

        const filteredData = approvalData.filter(item => {
            if (currentFilters.level && item.approval_level !== currentFilters.level) return false;
            if (currentFilters.type && item.absence_type_id !== parseInt(currentFilters.type)) return false;
            if (currentFilters.department && item.user_department_id !== parseInt(currentFilters.department)) return false;
            if (currentFilters.priority) {
                const isUrgent = isUrgentRequest(item);
                const isOverdue = isOverdueRequest(item);
                
                if (currentFilters.priority === 'urgent' && !isUrgent) return false;
                if (currentFilters.priority === 'overdue' && !isOverdue) return false;
                if (currentFilters.priority === 'normal' && (isUrgent || isOverdue)) return false;
            }
            return true;
        });

        renderApprovalList(filteredData);
    }

    function resetFilters() {
        document.getElementById('levelFilter').value = '';
        document.getElementById('typeFilter').value = '';
        document.getElementById('departmentFilter').value = '';
        document.getElementById('priorityFilter').value = '';
        
        currentFilters = {};
        renderApprovalList();
    }

    function renderApprovalList(data = approvalData) {
        const approvalList = document.getElementById('approvalList');
        
        if (data.length === 0) {
            showEmptyState();
            return;
        }

        // Hide empty state
        document.getElementById('emptyState').style.display = 'none';

        approvalList.innerHTML = data.map(item => {
            const isUrgent = isUrgentRequest(item);
            const isOverdue = isOverdueRequest(item);
            const priorityClass = isUrgent ? 'urgent' : isOverdue ? 'overdue' : '';
            const priorityBadge = isUrgent ? 'urgent' : isOverdue ? 'overdue' : 'normal';

            return `
                <div class="approval-item ${priorityClass}">
                    <div class="approval-header">
                        <h3 class="approval-title">Đơn vắng mặt #${item.id}</h3>
                        <div class="approval-priority">
                            <span class="priority-badge priority-${priorityBadge}">
                                ${priorityBadge === 'urgent' ? 'Khẩn cấp' : priorityBadge === 'overdue' ? 'Quá hạn' : 'Bình thường'}
                            </span>
                        </div>
                    </div>
                    <div class="approval-body">
                        <div class="approval-info">
                            <div class="info-item">
                                <span class="info-label">Nhân viên</span>
                                <span class="info-value">${item.user_name || 'N/A'}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Loại vắng mặt</span>
                                <span class="info-value">${item.absence_type_name || 'N/A'}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Thời gian</span>
                                <span class="info-value">${formatDate(item.start_date)} - ${formatDate(item.end_date)}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Số ngày</span>
                                <span class="info-value">${item.total_days || '0'} ngày</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Cấp độ phê duyệt</span>
                                <span class="info-value">${getApprovalLevelText(item.approval_level)}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Thời gian chờ</span>
                                <span class="info-value">${getWaitingTime(item.created_at)}</span>
                            </div>
                        </div>
                        <div class="approval-actions">
                            <button class="btn btn-outline-primary btn-sm" onclick="viewDetail(${item.id})">
                                <i class="fas fa-eye"></i> Xem chi tiết
                            </button>
                            <button class="btn btn-success btn-sm" onclick="openApprovalModal(${item.id}, 'approved')">
                                <i class="fas fa-check"></i> Phê duyệt
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="openApprovalModal(${item.id}, 'rejected')">
                                <i class="fas fa-times"></i> Từ chối
                            </button>
                            <button class="btn btn-warning btn-sm" onclick="openApprovalModal(${item.id}, 'delegated')">
                                <i class="fas fa-user-friends"></i> Ủy quyền
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    function updateStats() {
        const pendingCount = approvalData.length;
        const urgentCount = approvalData.filter(isUrgentRequest).length;
        const overdueCount = approvalData.filter(isOverdueRequest).length;
        const todayCount = approvalData.filter(item => {
            const createdDate = new Date(item.created_at);
            const today = new Date();
            return createdDate.toDateString() === today.toDateString();
        }).length;

        document.getElementById('pendingCount').textContent = pendingCount;
        document.getElementById('urgentCount').textContent = urgentCount;
        document.getElementById('overdueCount').textContent = overdueCount;
        document.getElementById('todayCount').textContent = todayCount;
    }

    function isUrgentRequest(item) {
        // Consider urgent if created more than 2 days ago and still pending
        const createdDate = new Date(item.created_at);
        const now = new Date();
        const daysDiff = (now - createdDate) / (1000 * 60 * 60 * 24);
        return daysDiff > 2;
    }

    function isOverdueRequest(item) {
        // Consider overdue if created more than 5 days ago and still pending
        const createdDate = new Date(item.created_at);
        const now = new Date();
        const daysDiff = (now - createdDate) / (1000 * 60 * 60 * 24);
        return daysDiff > 5;
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

    function openApprovalModal(requestId, action) {
        const modal = document.getElementById('approvalModal');
        const requestDetails = document.getElementById('requestDetails');
        
        // Find request data
        const request = approvalData.find(item => item.id === requestId);
        if (!request) return;

        // Populate request details
        requestDetails.innerHTML = `
            <div class="detail-title">Chi tiết đơn vắng mặt #${request.id}</div>
            <div class="detail-info">
                <div class="info-item">
                    <span class="info-label">Nhân viên:</span>
                    <span class="info-value">${request.user_name || 'N/A'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Loại vắng mặt:</span>
                    <span class="info-value">${request.absence_type_name || 'N/A'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Thời gian:</span>
                    <span class="info-value">${formatDate(request.start_date)} - ${formatDate(request.end_date)}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Số ngày:</span>
                    <span class="info-value">${request.total_days || '0'} ngày</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Lý do:</span>
                    <span class="info-value">${request.reason || 'N/A'}</span>
                </div>
            </div>
        `;

        // Set action
        const actionBtn = modal.querySelector(`[data-action="${action}"]`);
        if (actionBtn) {
            actionBtn.click();
        }

        // Store request ID
        modal.dataset.requestId = requestId;

        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    async function handleApprovalSubmit() {
        const modal = document.getElementById('approvalModal');
        const requestId = modal.dataset.requestId;
        const action = document.getElementById('submitApproval').dataset.action;
        const comment = document.getElementById('approvalComment').value;
        const delegateTo = document.getElementById('delegateTo').value;

        if (!requestId || !action) {
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

            const response = await fetch(`/absence/api/approve/${requestId}/`, {
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
                const bsModal = bootstrap.Modal.getInstance(modal);
                bsModal.hide();
                
                // Reload data
                loadApprovalData();
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

    function showEmptyState() {
        document.getElementById('approvalList').innerHTML = '';
        document.getElementById('emptyState').style.display = 'block';
    }

    function showLoading(show) {
        const loadingElements = document.querySelectorAll('.approval-list');
        loadingElements.forEach(el => {
            el.classList.toggle('loading', show);
        });
    }

    // Global functions
    window.viewDetail = function(id) {
        window.location.href = `/absence/detail/${id}/`;
    };

    // Utility functions
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
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
