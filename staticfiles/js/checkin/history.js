function normalizePhotoSrc(photoUrl, photoField) {
    if (photoUrl) return photoUrl;
    if (!photoField) return null;
    const val = String(photoField);
    if (val.startsWith('http') || val.startsWith('/media/')) return val;
    return `/media/${val.replace(/^\/+/, '')}`;
}

// Format distance number to "000.00 mét" format
function formatDistanceNumber(distance) {
    if (!distance || distance === null || distance === undefined) {
        return 'N/A';
    }
    const num = parseFloat(distance);
    if (isNaN(num)) return 'N/A';
    return `${num.toFixed(2)} mét`;
}
// History page specific JavaScript

let allCheckins = [];
let filteredCheckins = [];
let currentPage = 1;
let totalPages = 1;
const itemsPerPage = 20;
let currentSort = { field: 'created_at', direction: 'desc' };

// Update view visibility based on screen size
function updateViewVisibility() {
    const desktopTable = document.getElementById('desktopTable');
    const mobileCards = document.getElementById('mobileCards');
    
    if (window.innerWidth > 768) {
        if (desktopTable) desktopTable.style.display = 'block';
        if (mobileCards) mobileCards.style.display = 'none';
    } else {
        if (desktopTable) desktopTable.style.display = 'none';
        if (mobileCards) mobileCards.style.display = 'block';
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('History page DOM loaded, initializing...');
    
    // Check if elements exist
    const checkinList = document.getElementById('checkinList');
    const desktopTable = document.getElementById('desktopTable');
    const mobileCards = document.getElementById('mobileCards');
    console.log('Checkin list container found:', !!checkinList);
    console.log('Desktop table found:', !!desktopTable);
    console.log('Mobile cards found:', !!mobileCards);
    
    // Show appropriate view based on screen size
    updateViewVisibility();
    
    // Collapse filters by default
    const filtersPanel = document.getElementById('filtersPanel');
    const filterToggle = document.getElementById('filterToggle');
    const filterToggleIcon = document.getElementById('filterToggleIcon');
    if (filtersPanel) {
        filtersPanel.classList.add('collapsed');
    }
    if (filterToggle && filtersPanel) {
        filterToggle.addEventListener('click', function() {
            const isCollapsed = filtersPanel.classList.toggle('collapsed');
            if (filterToggleIcon) {
                filterToggleIcon.className = isCollapsed ? 'fas fa-chevron-down' : 'fas fa-chevron-up';
            }
        });
    }

    loadCheckins();
    setupEventListeners();
    
    // Add event listeners for sorting
    document.querySelectorAll('.checkin-table th.sortable').forEach(th => {
        th.addEventListener('click', function() {
            const field = this.getAttribute('data-sort');
            if (field) {
                handleSort(field);
            }
        });
    });
    
    // Listen for window resize to update view
    window.addEventListener('resize', updateViewVisibility);
    
    // Handle window resize for responsive layout
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Re-render checkins on resize to switch between mobile/desktop layout
            renderCheckins();
        }, 250);
    });
});

// Setup event listeners
function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(applyFilters, 300));
    }
    
    // Date filters
    const dateFrom = document.getElementById('dateFrom');
    const dateTo = document.getElementById('dateTo');
    
    if (dateFrom) {
        dateFrom.addEventListener('change', applyFilters);
    }
    
    if (dateTo) {
        dateTo.addEventListener('change', applyFilters);
    }
    
    // Location filter
    const locationFilter = document.getElementById('locationFilter');
    if (locationFilter) {
        locationFilter.addEventListener('change', applyFilters);
    }

    const checkinTypeFilter = document.getElementById('checkinTypeFilter');
    if (checkinTypeFilter) {
        checkinTypeFilter.addEventListener('change', applyFilters);
    }

    // Apply Filters button
    const applyBtn = document.getElementById('applyFilters');
    if (applyBtn) {
        applyBtn.addEventListener('click', applyFilters);
    }
}

// Load check-ins
async function loadCheckins() {
    try {
        const response = await api('/checkin/api/history/?page=1');
        if (response.ok) {
            const data = await response.json();
            allCheckins = data.checkins || data.results || [];
            filteredCheckins = [...allCheckins];
            
            // Initialize sort icons
            updateSortIcons(currentSort.field, currentSort.direction);
            
            renderCheckins();
            updatePagination();
            loadAreas();
            updateFilterCount();
        } else {
            console.error('API error loading checkins:', response.status, response.statusText);
            // Show error but still try to render empty state
            renderCheckins([]);
            showAlert('Lỗi tải lịch sử check-in. Vui lòng đăng nhập để xem dữ liệu.', 'error');
        }
    } catch (error) {
        console.error('Error loading checkins:', error);
        // Show error but still try to render empty state
        renderCheckins([]);
        showAlert('Lỗi tải lịch sử check-in. Vui lòng kiểm tra kết nối mạng.', 'error');
    }
}

// Sorting functions
function sortCheckins(checkins, field, direction) {
    return [...checkins].sort((a, b) => {
        let aVal = a[field];
        let bVal = b[field];
        
        // Handle different data types
        if (field === 'created_at') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        } else if (field === 'lat' || field === 'lng') {
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
        } else {
            aVal = String(aVal || '').toLowerCase();
            bVal = String(bVal || '').toLowerCase();
        }
        
        if (direction === 'asc') {
            return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
        } else {
            return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
        }
    });
}

function updateSortIcons(field, direction) {
    // Remove active class from all sortable headers
    document.querySelectorAll('.checkin-table th.sortable').forEach(th => {
        th.classList.remove('active');
        const icon = th.querySelector('.sort-icon');
        if (icon) {
            icon.className = 'fas fa-sort sort-icon';
        }
    });
    
    // Add active class to current sort field
    const activeTh = document.querySelector(`.checkin-table th[data-sort="${field}"]`);
    if (activeTh) {
        activeTh.classList.add('active');
        const icon = activeTh.querySelector('.sort-icon');
        if (icon) {
            icon.className = `fas fa-sort-${direction === 'asc' ? 'up' : 'down'} sort-icon`;
        }
    }
}

function handleSort(field) {
    // Toggle direction if same field, otherwise set to desc
    if (currentSort.field === field) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.direction = 'desc';
    }
    currentSort.field = field;
    
    // Update icons
    updateSortIcons(field, currentSort.direction);
    
    // Sort and re-render
    const sortedCheckins = sortCheckins(allCheckins, field, currentSort.direction);
    filteredCheckins = sortedCheckins;
    renderCheckins();
    updatePagination();
}

// Load areas for filter
async function loadAreas() {
    try {
        const response = await api('/location/api/');
        if (response.ok) {
            const data = await response.json();
            const areas = Array.isArray(data) ? data : (data.areas || data.results || []);
            
            const locationSelect = document.getElementById('locationFilter');
            if (locationSelect) {
                // Clear existing options except first one
                locationSelect.innerHTML = '<option value="">Tất cả địa điểm</option>';
                
                areas.forEach(area => {
                    const option = document.createElement('option');
                    option.value = area.id;
                    option.textContent = area.name;
                    locationSelect.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading areas:', error);
    }
}

// Update pagination
function updatePagination() {
    const paginationContainer = document.getElementById('pagination');
    if (paginationContainer) {
        paginationContainer.innerHTML = '';
        
        const totalItems = filteredCheckins?.length || allCheckins.length || 0;
        totalPages = Math.ceil(totalItems / itemsPerPage) || 1;

        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '← Trước';
        prevBtn.className = 'pagination-btn';
        prevBtn.disabled = currentPage === 1;
        prevBtn.addEventListener('click', () => loadPage(currentPage - 1));
        paginationContainer.appendChild(prevBtn);
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.className = `pagination-btn ${i === currentPage ? 'active' : ''}`;
            pageBtn.addEventListener('click', () => loadPage(i));
            paginationContainer.appendChild(pageBtn);
        }
        
        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Sau →';
        nextBtn.className = 'pagination-btn';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.addEventListener('click', () => loadPage(currentPage + 1));
        paginationContainer.appendChild(nextBtn);
        
        // Add pagination info with counts
        const start = totalItems === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1;
        const end = Math.min(currentPage * itemsPerPage, totalItems);
        const info = document.createElement('div');
        info.className = 'pagination-info';
        info.textContent = `Trang ${currentPage}/${totalPages} • Hiển thị ${start}–${end} / ${totalItems}`;
        paginationContainer.appendChild(info);
    }
}

// Load specific page
function loadPage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    renderCheckins();
    updatePagination();
}

// Apply filters
function applyFilters() {
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
    const dateFrom = document.getElementById('dateFrom')?.value || '';
    const dateTo = document.getElementById('dateTo')?.value || '';
    const location = document.getElementById('locationFilter')?.value || '';
    const checkinType = document.getElementById('checkinTypeFilter')?.value || '';
    
    filteredCheckins = allCheckins.filter(checkin => {
        // Search filter
        if (searchTerm && !checkin.location_name.toLowerCase().includes(searchTerm) &&
            !(checkin.note && checkin.note.toLowerCase().includes(searchTerm))) {
            return false;
        }
        
        // Date filter
        if (dateFrom) {
            const checkinDate = new Date(checkin.created_at);
            const fromDate = new Date(dateFrom);
            if (checkinDate < fromDate) return false;
        }
        
        if (dateTo) {
            const checkinDate = new Date(checkin.created_at);
            const toDate = new Date(dateTo);
            toDate.setHours(23, 59, 59, 999);
            if (checkinDate > toDate) return false;
        }
        
        // Location filter
        if (location && checkin.location && checkin.location.toString() !== location) {
            return false;
        }
        
        // Checkin type filter
        if (checkinType && checkin.checkin_type !== checkinType) {
            return false;
        }
        
        return true;
    });
    
    renderCheckins();
    updateFilterCount();
}

// Clear all filters
function clearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('date-from').value = '';
    document.getElementById('date-to').value = '';
    document.getElementById('locationFilter').value = '';
    document.getElementById('checkinTypeFilter').value = '';
    
    // Reset to all check-ins
    filteredCheckins = [...allCheckins];
    renderCheckins();
    updateFilterCount();
    
    // Show success message
    showAlert('Đã xóa tất cả bộ lọc', 'success');
}

// Update filter count display
function updateFilterCount() {
    const searchTerm = document.getElementById('search-input')?.value.trim() || '';
    const dateFrom = document.getElementById('date-from')?.value || '';
    const dateTo = document.getElementById('date-to')?.value || '';
    const location = document.getElementById('locationFilter')?.value || '';
    
    let activeFilters = 0;
    
    if (searchTerm) activeFilters++;
    if (dateFrom) activeFilters++;
    if (dateTo) activeFilters++;
    if (location) activeFilters++;
    
    const filterCountText = document.getElementById('filter-count-text');
    const filterCount = document.getElementById('filter-count');
    
    if (filterCountText) {
        filterCountText.textContent = activeFilters;
    }
    
    if (filterCount) {
        if (activeFilters > 0) {
            filterCount.style.display = 'flex';
            filterCount.style.background = '#0A5597';
        } else {
            filterCount.style.display = 'none';
        }
    }
}

// Render check-ins
function renderCheckins(checkins = null) {
    const mobileContainer = document.getElementById('checkinList');
    const tableBody = document.getElementById('checkinTableBody');
    
    // Use provided checkins or sort filtered checkins
    const dataToRender = checkins || sortCheckins(filteredCheckins, currentSort.field, currentSort.direction);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const checkinsToRender = dataToRender.slice(startIndex, endIndex);
    console.log('Rendering history checkins, count:', checkinsToRender.length);
    
    if (checkinsToRender.length === 0) {
        const emptyState = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>Không có check-in nào</h3>
                <p>Chưa có dữ liệu check-in phù hợp với bộ lọc.</p>
            </div>
        `;
        
        const emptyStateTable = `
            <tr>
                <td colspan="8" class="empty-state-cell">
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <h3>Không có check-in nào</h3>
                        <p>Chưa có dữ liệu check-in phù hợp với bộ lọc.</p>
                    </div>
                </td>
            </tr>
        `;
        
        if (mobileContainer) mobileContainer.innerHTML = emptyState;
        if (tableBody) tableBody.innerHTML = emptyStateTable;
        return;
    }
    
    // Render mobile cards
    if (mobileContainer) {
        mobileContainer.innerHTML = checkinsToRender.map(checkin => `
            <div class="mobile-card">
                <div class="mobile-card-header">
                    <h3 class="mobile-card-title">${checkin.user_name || 'N/A'}</h3>
                    <span class="mobile-card-time">${formatDate(checkin.created_at)}</span>
                </div>
                
                <div class="mobile-card-content">
                    <div class="mobile-card-details">
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">📍 Địa điểm:</span>
                            <span class="mobile-card-value">${checkin.location_name || 'N/A'}</span>
                        </div>
                        
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">🗺️ Tọa độ:</span>
                            <span class="mobile-card-value">${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}, ${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}</span>
                        </div>
                        
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">📏 Khoảng cách:</span>
                            <span class="mobile-card-value">${formatDistanceNumber(checkin.distance_m)}</span>
                        </div>
                        
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">🏷️ Loại checkin:</span>
                            <span class="mobile-card-value">${checkin.checkin_type_display || 'N/A'}</span>
                        </div>
                        
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">📅 Thời gian:</span>
                            <span class="mobile-card-value">${formatDate(checkin.created_at)}</span>
                        </div>
                        
                        ${checkin.note ? `
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">📝 Ghi chú:</span>
                            <span class="mobile-card-value">${checkin.note}</span>
                        </div>
                        ` : ''}
                    </div>
                    
                    <div class="mobile-card-photo-container">
                        ${(() => {
                            const src = normalizePhotoSrc(checkin.photo_url, checkin.photo);
                            if (src) {
                                return `<img src="${src}" alt="Check-in photo" class="mobile-card-photo" onclick="openPhotoModal('${src}')" onerror="this.style.display='none'">`;
                            }
                            return `<div class=\"mobile-card-photo-placeholder\">📷</div>`;
                        })()}
                    </div>
                </div>
                
                <div class="mobile-card-badges">
                    ${(() => {
                        const canCheckoutResult = canCheckout(checkin);
                        
                        if (canCheckoutResult) {
                            return `
                                <button class="btn btn-sm btn-outline-warning checkout-btn" 
                                        onclick="performCheckout(${checkin.id})" 
                                        title="Chờ checkout">
                                    <i class="fas fa-clock"></i>
                                    Chờ checkout
                                </button>
                            `;
                        } else {
                            return `
                                <button class="btn btn-sm btn-outline-success checkout-detail-btn" 
                                        onclick="viewCheckoutDetail(${checkin.id})" 
                                        title="Xem chi tiết checkout">
                                    <i class="fas fa-check-circle"></i>
                                    Đã checkout
                                </button>
                            `;
                        }
                    })()}
                </div>
            </div>
        `).join('');
    }
    
    // Render desktop table
    if (tableBody) {
        tableBody.innerHTML = checkinsToRender.map(checkin => `
            <tr>
                <td>
                    <div class="time-cell">
                        <div class="time-primary">${formatDate(checkin.created_at)}</div>
                        <div class="time-secondary">${formatTime(checkin.created_at)}</div>
                    </div>
                </td>
                <td>
                    <div class="area-cell">
                        <i class="fas fa-map-marker-alt"></i>
                        ${checkin.location_name || 'N/A'}
                    </div>
                </td>
                <td>
                    <div class="location-cell">
                        <div>${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}</div>
                        <div>${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}</div>
                    </div>
                </td>
                <td>
                    <div class="distance-cell">
                        ${formatDistanceNumber(checkin.distance_m)}
                    </div>
                </td>
                <td>
                    <div class="checkin-type-cell">
                        <span class="checkin-type-badge ${checkin.checkin_type === '1' ? 'work' : 'visitor'}">
                            ${checkin.checkin_type_display || 'N/A'}
                        </span>
                    </div>
                </td>
                <td>
                    <div class="note-cell">
                        ${checkin.note || '-'}
                    </div>
                </td>
                <td>
                    ${(() => {
                        const src = normalizePhotoSrc(checkin.photo_url, checkin.photo);
                        if (src) {
                            return `<img src="${src}" alt="Check-in photo" class="photo-thumbnail" onclick="openPhotoModal('${src}')" onerror="this.style.display='none'">`;
                        }
                        return `<div class=\"photo-placeholder\"><i class=\"fas fa-camera\"></i></div>`;
                    })()}
                </td>
                <td>
                    <span class="status-badge status-success">Thành công</span>
                </td>
                <td>
                    <div class="action-buttons">
                        ${(() => {
                            const canCheckoutResult = canCheckout(checkin);
                            
                            if (canCheckoutResult) {
                                return `
                                    <button class="btn btn-sm btn-outline-warning checkout-btn" 
                                            onclick="performCheckout(${checkin.id})" 
                                            title="Chờ checkout">
                                        <i class="fas fa-clock"></i>
                                        Chờ checkout
                                    </button>
                                `;
                            } else {
                                return `
                                    <button class="btn btn-sm btn-outline-success checkout-detail-btn" 
                                            onclick="viewCheckoutDetail(${checkin.id})" 
                                            title="Xem chi tiết checkout">
                                        <i class="fas fa-check-circle"></i>
                                        Đã checkout
                                    </button>
                                `;
                            }
                        })()}
                    </div>
                </td>
            </tr>
        `).join('');
    }
}

// Show error message
function showError(message) {
    const mobileContainer = document.getElementById('checkinList');
    const tableBody = document.getElementById('checkinTableBody');
    
    const errorState = `
        <div class="empty-state">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>Lỗi tải dữ liệu</h3>
            <p>${message}</p>
        </div>
    `;
    
    if (mobileContainer) mobileContainer.innerHTML = errorState;
    if (tableBody) tableBody.innerHTML = errorState;
}

// Check if checkout is allowed for a checkin
function canCheckout(checkin) {
    // Chỉ cần kiểm tra xem đã có checkout chưa
    // Không cần kiểm tra cùng ngày vì có thể checkout vào ngày khác
    const hasCheckout = checkin.has_checkout || false;
    
    return !hasCheckout;
}

// Perform checkout for a specific checkin
async function performCheckout(checkinId) {
    try {
        // Redirect directly to checkout page without confirmation
        window.location.href = `/checkin/checkout/?checkin_id=${checkinId}`;
        
    } catch (error) {
        console.error('Error performing checkout:', error);
        showAlert('Có lỗi xảy ra khi thực hiện checkout', 'error');
    }
}

// View checkout detail for a specific checkin
async function viewCheckoutDetail(checkinId) {
    try {
        // Redirect to checkout detail page with checkin ID
        window.location.href = `/checkin/checkout/detail/${checkinId}/`;
        
    } catch (error) {
        console.error('Error viewing checkout detail:', error);
        showAlert('Có lỗi xảy ra khi xem chi tiết checkout', 'error');
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of page
    const container = document.querySelector('.history-container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// Format time
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format distance
function formatDistance(distance) {
    if (distance < 1000) {
        return `${Math.round(distance)}m`;
    } else {
        return `${(distance / 1000).toFixed(1)}km`;
    }
}

// Open photo modal
function openPhotoModal(photoUrl) {
    const modal = document.createElement('div');
    modal.style.cssText = (
        'position:fixed;top:0;left:0;width:100%;height:100%;' +
        'background:rgba(0,0,0,0.8);display:flex;align-items:center;' +
        'justify-content:center;z-index:1000;cursor:pointer;'
    );

    const img = document.createElement('img');
    img.src = photoUrl;
    img.alt = 'Check-in photo';
    img.style.cssText = (
        'max-width:90%;max-height:90%;border-radius:8px;' +
        'box-shadow:0 8px 32px rgba(0,0,0,0.3);'
    );

    modal.appendChild(img);
    document.body.appendChild(modal);
    modal.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
}
