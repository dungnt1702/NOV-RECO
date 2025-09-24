// Absence List JavaScript
document.addEventListener('DOMContentLoaded', function() {
    let currentPage = 1;
    let currentFilters = {};
    let currentView = 'table';
    let allData = [];
    let filteredData = [];

    // Initialize
    initializePage();

    function initializePage() {
        setupEventListeners();
        loadInitialData();
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

        // View toggle
        document.getElementById('tableViewBtn').addEventListener('click', () => switchView('table'));
        document.getElementById('cardViewBtn').addEventListener('click', () => switchView('card'));

        // Filter actions
        document.getElementById('applyFilters').addEventListener('click', applyFilters);
        document.getElementById('resetFilters').addEventListener('click', resetFilters);

        // Export button
        document.getElementById('exportBtn').addEventListener('click', exportToExcel);
    }

    async function loadInitialData() {
        try {
            showLoading(true);
            const response = await fetch('/absence/api/requests/');
            const data = await response.json();
            
            if (data.success) {
                allData = data.requests;
                filteredData = [...allData];
                renderData();
                updatePagination();
            } else {
                showEmptyState();
            }
        } catch (error) {
            console.error('Error loading data:', error);
            showNotification('Lỗi khi tải dữ liệu', 'error');
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

            // Load users
            const usersResponse = await fetch('/users/api/list/');
            const usersData = await usersResponse.json();
            
            if (usersData.success) {
                const userFilter = document.getElementById('userFilter');
                userFilter.innerHTML = '<option value="">Tất cả nhân viên</option>';
                usersData.users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = user.get_full_name || user.first_name + ' ' + user.last_name;
                    userFilter.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error setting up filters:', error);
        }
    }

    function applyFilters() {
        currentFilters = {
            status: document.getElementById('statusFilter').value,
            type: document.getElementById('typeFilter').value,
            department: document.getElementById('departmentFilter').value,
            user: document.getElementById('userFilter').value,
            startDate: document.getElementById('startDateFilter').value,
            endDate: document.getElementById('endDateFilter').value
        };

        filteredData = allData.filter(item => {
            if (currentFilters.status && item.status !== currentFilters.status) return false;
            if (currentFilters.type && item.absence_type_id !== parseInt(currentFilters.type)) return false;
            if (currentFilters.department && item.user_department_id !== parseInt(currentFilters.department)) return false;
            if (currentFilters.user && item.user_id !== parseInt(currentFilters.user)) return false;
            if (currentFilters.startDate && new Date(item.start_date) < new Date(currentFilters.startDate)) return false;
            if (currentFilters.endDate && new Date(item.end_date) > new Date(currentFilters.endDate)) return false;
            return true;
        });

        currentPage = 1;
        renderData();
        updatePagination();
    }

    function resetFilters() {
        document.getElementById('statusFilter').value = '';
        document.getElementById('typeFilter').value = '';
        document.getElementById('departmentFilter').value = '';
        document.getElementById('userFilter').value = '';
        document.getElementById('startDateFilter').value = '';
        document.getElementById('endDateFilter').value = '';
        
        currentFilters = {};
        filteredData = [...allData];
        currentPage = 1;
        renderData();
        updatePagination();
    }

    function switchView(view) {
        currentView = view;
        
        // Update button states
        document.getElementById('tableViewBtn').classList.toggle('active', view === 'table');
        document.getElementById('cardViewBtn').classList.toggle('active', view === 'card');
        
        // Show/hide views
        document.getElementById('tableView').style.display = view === 'table' ? 'block' : 'none';
        document.getElementById('cardView').style.display = view === 'card' ? 'block' : 'none';
        
        renderData();
    }

    function renderData() {
        if (currentView === 'table') {
            renderTableView();
        } else {
            renderCardView();
        }
    }

    function renderTableView() {
        const tbody = document.getElementById('absenceTableBody');
        const startIndex = (currentPage - 1) * 10;
        const endIndex = Math.min(startIndex + 10, filteredData.length);
        const pageData = filteredData.slice(startIndex, endIndex);

        if (pageData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" class="text-center">Không có dữ liệu</td></tr>';
            return;
        }

        tbody.innerHTML = pageData.map((item, index) => `
            <tr>
                <td class="text-center">${startIndex + index + 1}</td>
                <td>${item.user_name || 'N/A'}</td>
                <td>${item.absence_type_name || 'N/A'}</td>
                <td class="text-center">${formatDate(item.start_date)}</td>
                <td class="text-center">${formatDate(item.end_date)}</td>
                <td class="text-center">${item.total_days || '0'}</td>
                <td class="text-center">
                    <span class="status-badge status-${item.status}">${getStatusText(item.status)}</span>
                </td>
                <td class="text-center">${getApprovalLevelText(item.approval_level)}</td>
                <td>${item.current_approver_name || 'N/A'}</td>
                <td class="text-center">
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewDetail(${item.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${getActionButtons(item)}
                    </div>
                </td>
            </tr>
        `).join('');
    }

    function renderCardView() {
        const cardGrid = document.getElementById('absenceCardGrid');
        const startIndex = (currentPage - 1) * 12;
        const endIndex = Math.min(startIndex + 12, filteredData.length);
        const pageData = filteredData.slice(startIndex, endIndex);

        if (pageData.length === 0) {
            cardGrid.innerHTML = '<div class="col-12 text-center">Không có dữ liệu</div>';
            return;
        }

        cardGrid.innerHTML = pageData.map((item, index) => `
            <div class="absence-card">
                <div class="card-header">
                    <h3 class="card-title">Đơn #${item.id}</h3>
                    <span class="status-badge status-${item.status}">${getStatusText(item.status)}</span>
                </div>
                <div class="card-body">
                    <div class="card-info">
                        <div class="info-row">
                            <span class="info-label">Nhân viên:</span>
                            <span class="info-value">${item.user_name || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Loại vắng mặt:</span>
                            <span class="info-value">${item.absence_type_name || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Thời gian:</span>
                            <span class="info-value">${formatDate(item.start_date)} - ${formatDate(item.end_date)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Số ngày:</span>
                            <span class="info-value">${item.total_days || '0'} ngày</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Cấp độ phê duyệt:</span>
                            <span class="info-value">${getApprovalLevelText(item.approval_level)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Người phê duyệt:</span>
                            <span class="info-value">${item.current_approver_name || 'N/A'}</span>
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn btn-outline-primary btn-sm" onclick="viewDetail(${item.id})">
                            <i class="fas fa-eye"></i> Xem chi tiết
                        </button>
                        ${getActionButtons(item)}
                    </div>
                </div>
            </div>
        `).join('');
    }

    function getActionButtons(item) {
        let buttons = '';
        
        if (item.status === 'pending' && item.can_approve) {
            buttons += `
                <button class="btn btn-success btn-sm" onclick="approveRequest(${item.id})">
                    <i class="fas fa-check"></i>
                </button>
                <button class="btn btn-danger btn-sm" onclick="rejectRequest(${item.id})">
                    <i class="fas fa-times"></i>
                </button>
            `;
        }
        
        if (item.status === 'pending' && item.user_id === getCurrentUserId()) {
            buttons += `
                <button class="btn btn-warning btn-sm" onclick="cancelRequest(${item.id})">
                    <i class="fas fa-ban"></i>
                </button>
            `;
        }
        
        return buttons;
    }

    function updatePagination() {
        const totalPages = Math.ceil(filteredData.length / (currentView === 'table' ? 10 : 12));
        const pagination = document.getElementById('pagination');
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let paginationHTML = '';
        
        // Previous button
        if (currentPage > 1) {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">
                        <i class="fas fa-chevron-left"></i>
                    </a>
                </li>
            `;
        }

        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
                </li>
            `;
        }

        // Next button
        if (currentPage < totalPages) {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">
                        <i class="fas fa-chevron-right"></i>
                    </a>
                </li>
            `;
        }

        pagination.innerHTML = paginationHTML;
    }

    function showEmptyState() {
        document.getElementById('tableView').style.display = 'none';
        document.getElementById('cardView').style.display = 'none';
        document.getElementById('emptyState').style.display = 'block';
    }

    function showLoading(show) {
        const loadingElements = document.querySelectorAll('.table-responsive, .card-grid');
        loadingElements.forEach(el => {
            el.classList.toggle('loading', show);
        });
    }

    // Global functions
    window.changePage = function(page) {
        currentPage = page;
        renderData();
        updatePagination();
        window.scrollTo(0, 0);
    };

    window.viewDetail = function(id) {
        window.location.href = `/absence/detail/${id}/`;
    };

    window.approveRequest = async function(id) {
        if (confirm('Bạn có chắc chắn muốn phê duyệt đơn vắng mặt này?')) {
            try {
                const response = await fetch(`/absence/api/approve/${id}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        action: 'approved',
                        comment: ''
                    })
                });

                const data = await response.json();
                if (data.success) {
                    showNotification('Đơn vắng mặt đã được phê duyệt', 'success');
                    loadInitialData();
                } else {
                    showNotification(data.message || 'Có lỗi xảy ra', 'error');
                }
            } catch (error) {
                console.error('Error approving request:', error);
                showNotification('Có lỗi xảy ra khi phê duyệt', 'error');
            }
        }
    };

    window.rejectRequest = async function(id) {
        const comment = prompt('Nhập lý do từ chối:');
        if (comment === null) return;

        try {
            const response = await fetch(`/absence/api/approve/${id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    action: 'rejected',
                    comment: comment
                })
            });

            const data = await response.json();
            if (data.success) {
                showNotification('Đơn vắng mặt đã bị từ chối', 'success');
                loadInitialData();
            } else {
                showNotification(data.message || 'Có lỗi xảy ra', 'error');
            }
        } catch (error) {
            console.error('Error rejecting request:', error);
            showNotification('Có lỗi xảy ra khi từ chối', 'error');
        }
    };

    window.cancelRequest = async function(id) {
        if (confirm('Bạn có chắc chắn muốn hủy đơn vắng mặt này?')) {
            try {
                const response = await fetch(`/absence/api/approve/${id}/`, {
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
                    loadInitialData();
                } else {
                    showNotification(data.message || 'Có lỗi xảy ra', 'error');
                }
            } catch (error) {
                console.error('Error cancelling request:', error);
                showNotification('Có lỗi xảy ra khi hủy', 'error');
            }
        }
    };

    window.exportToExcel = function() {
        if (filteredData.length === 0) {
            showNotification('Không có dữ liệu để xuất', 'warning');
            return;
        }

        // Create CSV content
        const headers = [
            'ID', 'Nhân viên', 'Loại vắng mặt', 'Ngày bắt đầu', 'Ngày kết thúc',
            'Số ngày', 'Trạng thái', 'Cấp độ phê duyệt', 'Người phê duyệt', 'Ngày tạo'
        ];

        const csvContent = [
            headers.join(','),
            ...filteredData.map(item => [
                item.id,
                `"${item.user_name || 'N/A'}"`,
                `"${item.absence_type_name || 'N/A'}"`,
                formatDate(item.start_date),
                formatDate(item.end_date),
                item.total_days || '0',
                `"${getStatusText(item.status)}"`,
                `"${getApprovalLevelText(item.approval_level)}"`,
                `"${item.current_approver_name || 'N/A'}"`,
                formatDate(item.created_at)
            ].join(','))
        ].join('\n');

        // Download file
        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `absence_requests_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Utility functions
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
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

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function getCurrentUserId() {
        // This should be set from the template or API
        return window.currentUserId || null;
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
