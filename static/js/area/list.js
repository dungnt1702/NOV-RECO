// Area List JavaScript
let areas = [];
let currentPage = 1;
let itemsPerPage = 25;
let totalPages = 1;
let statusFilter = '';
let searchQuery = '';

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    console.log('Area list page loaded');
    loadAreas();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Add new area button - check if element exists
    const addAreaBtn = document.querySelector('a[href*="area:create"]');
    if (addAreaBtn) {
        addAreaBtn.addEventListener('click', function(e) {
            // Let the link work normally, no need to prevent default
        });
    }

    // Update check-ins button removed - no longer needed

    // Filter controls
    const statusFilterElement = document.getElementById('statusFilter');
    if (statusFilterElement) {
        statusFilterElement.addEventListener('change', function() {
            statusFilter = this.value;
            currentPage = 1;
            loadAreas();
        });
    }

    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            searchQuery = this.value;
            currentPage = 1;
            loadAreas();
        });
    }

    const itemsPerPageSelect = document.getElementById('itemsPerPage');
    if (itemsPerPageSelect) {
        itemsPerPageSelect.addEventListener('change', function() {
            itemsPerPage = parseInt(this.value);
            currentPage = 1;
            loadAreas();
        });
    }
}

// Load areas from API
async function loadAreas() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            page_size: itemsPerPage,
            status: statusFilter,
            search: searchQuery
        });

        const response = await fetch(`/area/api/?${params}`);
        const data = await response.json();
        
        areas = data.results || data;
        totalPages = Math.ceil((data.count || areas.length) / itemsPerPage);
        
        displayAreas();
        updatePagination();
    } catch (error) {
        console.error('Error loading areas:', error);
        showAlert('Lỗi khi tải danh sách khu vực', 'danger');
    }
}

// Display areas in the list
function displayAreas() {
    // Display desktop table
    displayAreasTable();
    
    // Display mobile cards
    displayAreasCards();
}

// Display areas in table format (desktop)
function displayAreasTable() {
    const tableBody = document.getElementById('areasTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';

    if (areas.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center">
                    <i class="fas fa-inbox"></i>
                    <p class="mb-0">Không có khu vực nào</p>
                </td>
            </tr>
        `;
        return;
    }

    areas.forEach(area => {
        const row = createAreaTableRow(area);
        tableBody.appendChild(row);
    });
}

// Display areas in card format (mobile)
function displayAreasCards() {
    const areasList = document.getElementById('areasList');
    if (!areasList) return;
    
    areasList.innerHTML = '';

    if (areas.length === 0) {
        areasList.innerHTML = `
            <div class="loading">
                <i class="fas fa-inbox"></i>
                <p>Không có khu vực nào</p>
            </div>
        `;
        return;
    }

    areas.forEach(area => {
        const areaItem = createAreaItem(area);
        areasList.appendChild(areaItem);
    });
}

// Create area table row element
function createAreaTableRow(area) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${area.id}</td>
        <td><strong>${area.name}</strong></td>
        <td>${area.description || 'Không có mô tả'}</td>
        <td>${area.lat.toFixed(6)}, ${area.lng.toFixed(6)}</td>
        <td>${area.radius_m}m</td>
        <td>
            <span class="badge ${area.is_active ? 'badge-success' : 'badge-secondary'}">
                ${area.is_active ? 'Hoạt động' : 'Tạm dừng'}
            </span>
        </td>
        <td>${new Date(area.created_at).toLocaleDateString('vi-VN')}</td>
        <td>
            <button class="btn btn-primary btn-sm me-1" onclick="editArea(${area.id})">
                <i class="fas fa-edit"></i> Sửa
            </button>
            <button class="btn btn-danger btn-sm" onclick="deleteArea(${area.id})">
                <i class="fas fa-trash"></i> Xóa
            </button>
        </td>
    `;
    return tr;
}

// Create area item element (mobile cards)
function createAreaItem(area) {
    const div = document.createElement('div');
    div.className = 'area-item';
    div.innerHTML = `
        <div class="area-item-header">
            <div class="area-name">${area.name}</div>
            <div class="area-status ${area.is_active ? 'active' : 'inactive'}">
                ${area.is_active ? 'Hoạt động' : 'Tạm dừng'}
            </div>
        </div>
        <div class="area-details">
            <div><strong>Mô tả:</strong> ${area.description || 'Không có mô tả'}</div>
            <div><strong>Tọa độ:</strong> ${area.lat.toFixed(6)}, ${area.lng.toFixed(6)}</div>
            <div><strong>Bán kính:</strong> ${area.radius_m}m</div>
            <div><strong>Ngày tạo:</strong> ${new Date(area.created_at).toLocaleDateString('vi-VN')}</div>
        </div>
        <div class="area-actions">
            <button class="btn btn-primary btn-sm" onclick="editArea(${area.id})">
                <i class="fas fa-edit"></i> Sửa
            </button>
            <button class="btn btn-danger btn-sm" onclick="deleteArea(${area.id})">
                <i class="fas fa-trash"></i> Xóa
            </button>
        </div>
    `;
    return div;
}

// Edit area
function editArea(areaId) {
    window.location.href = `/area/update/${areaId}/`;
}

// Delete area
async function deleteArea(areaId) {
    if (!confirm('Bạn có chắc chắn muốn xóa khu vực này?')) {
        return;
    }

    try {
        const response = await fetch(`/area/api/${areaId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            showAlert('Xóa khu vực thành công', 'success');
            loadAreas();
        } else {
            throw new Error('Failed to delete area');
        }
    } catch (error) {
        console.error('Error deleting area:', error);
        showAlert('Lỗi khi xóa khu vực', 'danger');
    }
}

// Update all check-ins function removed - no longer needed

// Update pagination
function updatePagination() {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    if (totalPages <= 1) return;

    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    // Pagination info
    const info = document.createElement('div');
    info.className = 'pagination-info';
    info.textContent = `Trang ${currentPage} / ${totalPages}`;
    pagination.appendChild(info);

    // Pagination buttons
    const buttons = document.createElement('div');
    buttons.className = 'pagination-buttons';

    // Previous button
    const prevBtn = createPaginationButton('←', currentPage - 1, currentPage === 1);
    buttons.appendChild(prevBtn);

    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = createPaginationButton(i, i, false, i === currentPage);
        buttons.appendChild(pageBtn);
    }

    // Next button
    const nextBtn = createPaginationButton('→', currentPage + 1, currentPage === totalPages);
    buttons.appendChild(nextBtn);

    pagination.appendChild(buttons);
}

// Create pagination button
function createPaginationButton(text, page, disabled, active = false) {
    const button = document.createElement('button');
    button.className = `btn ${active ? 'active' : ''}`;
    button.textContent = text;
    button.disabled = disabled;
    
    if (!disabled) {
        button.addEventListener('click', function() {
            currentPage = page;
            loadAreas();
        });
    }
    
    return button;
}

// Show alert message
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;

    const container = document.querySelector('.area-list-content');
    container.insertBefore(alertDiv, container.firstChild);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
