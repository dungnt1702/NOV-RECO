// Location List JavaScript
let locations = [];
let currentPage = 1;
let itemsPerPage = 25;
let totalPages = 1;
let statusFilter = '';
let searchQuery = '';

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    console.log('Location list page loaded');
    loadLocations();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Add new location button - check if element exists
    const addLocationBtn = document.querySelector('a[href*="location:create"]');
    if (addLocationBtn) {
        addLocationBtn.addEventListener('click', function(e) {
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
            loadLocations();
        });
    }

    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            searchQuery = this.value;
            currentPage = 1;
            loadLocations();
        });
    }

    const itemsPerPageSelect = document.getElementById('itemsPerPage');
    if (itemsPerPageSelect) {
        itemsPerPageSelect.addEventListener('change', function() {
            itemsPerPage = parseInt(this.value);
            currentPage = 1;
            loadLocations();
        });
    }
}

// Load locations from API
async function loadLocations() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            page_size: itemsPerPage,
            status: statusFilter,
            search: searchQuery
        });

        const response = await fetch(`/location/api/?${params}`);
        const data = await response.json();
        
        locations = data.results || data;
        totalPages = Math.ceil((data.count || locations.length) / itemsPerPage);
        
        displayLocations();
        updatePagination();
    } catch (error) {
        console.error('Error loading locations:', error);
        showAlert('Lỗi khi tải danh sách khu vực', 'danger');
    }
}

// Display locations in the list
function displayLocations() {
    // Display desktop table
    displayLocationsTable();
    
    // Display mobile cards
    displayLocationsCards();
}

// Display locations in table format (desktop)
function displayLocationsTable() {
    const tableBody = document.getElementById('locationsTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';

    if (locations.length === 0) {
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

    locations.forEach(location => {
        const row = createLocationTableRow(location);
        tableBody.appendChild(row);
    });
}

// Display locations in card format (mobile)
function displayLocationsCards() {
    const locationsList = document.getElementById('locationsList');
    if (!locationsList) return;
    
    locationsList.innerHTML = '';

    if (locations.length === 0) {
        locationsList.innerHTML = `
            <div class="loading">
                <i class="fas fa-inbox"></i>
                <p>Không có khu vực nào</p>
            </div>
        `;
        return;
    }

    locations.forEach(location => {
        const locationItem = createLocationItem(location);
        locationsList.appendChild(locationItem);
    });
}

// Create location table row element
function createLocationTableRow(location) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${location.id}</td>
        <td><strong>${location.name}</strong></td>
        <td>${location.description || 'Không có mô tả'}</td>
        <td>${location.lat.toFixed(6)}, ${location.lng.toFixed(6)}</td>
        <td>${location.radius_m}m</td>
        <td>
            <span class="badge ${location.is_active ? 'badge-success' : 'badge-secondary'}">
                ${location.is_active ? 'Hoạt động' : 'Tạm dừng'}
            </span>
        </td>
        <td>${new Date(location.created_at).toLocaleDateString('vi-VN')}</td>
        <td>
            <button class="btn btn-primary btn-sm me-1" onclick="editLocation(${location.id})">
                <i class="fas fa-edit"></i> Sửa
            </button>
            <button class="btn btn-danger btn-sm" onclick="deleteLocation(${location.id})">
                <i class="fas fa-trash"></i> Xóa
            </button>
        </td>
    `;
    return tr;
}

// Create location item element (mobile cards)
function createLocationItem(location) {
    const div = document.createElement('div');
    div.className = 'location-item';
    div.innerHTML = `
        <div class="location-item-header">
            <div class="location-name">${location.name}</div>
            <div class="location-status ${location.is_active ? 'active' : 'inactive'}">
                ${location.is_active ? 'Hoạt động' : 'Tạm dừng'}
            </div>
        </div>
        <div class="location-details">
            <div><strong>Mô tả:</strong> ${location.description || 'Không có mô tả'}</div>
            <div><strong>Tọa độ:</strong> ${location.lat.toFixed(6)}, ${location.lng.toFixed(6)}</div>
            <div><strong>Bán kính:</strong> ${location.radius_m}m</div>
            <div><strong>Ngày tạo:</strong> ${new Date(location.created_at).toLocaleDateString('vi-VN')}</div>
        </div>
        <div class="location-actions">
            <button class="btn btn-primary btn-sm" onclick="editLocation(${location.id})">
                <i class="fas fa-edit"></i> Sửa
            </button>
            <button class="btn btn-danger btn-sm" onclick="deleteLocation(${location.id})">
                <i class="fas fa-trash"></i> Xóa
            </button>
        </div>
    `;
    return div;
}

// Edit location
function editLocation(locationId) {
    window.location.href = `/location/update/${locationId}/`;
}

// Delete location
async function deleteLocation(locationId) {
    if (!confirm('Bạn có chắc chắn muốn xóa khu vực này?')) {
        return;
    }

    try {
        const response = await fetch(`/location/api/${locationId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            showAlert('Xóa khu vực thành công', 'success');
            loadLocations();
        } else {
            throw new Error('Failed to delete location');
        }
    } catch (error) {
        console.error('Error deleting location:', error);
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
            loadLocations();
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

    const container = document.querySelector('.location-list-content');
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
