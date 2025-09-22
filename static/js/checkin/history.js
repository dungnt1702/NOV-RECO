// History page specific JavaScript

let allCheckins = [];
let filteredCheckins = [];
let currentPage = 1;
let totalPages = 1;

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
    
    loadCheckins();
    setupEventListeners();
    
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
    const dateFrom = document.getElementById('date-from');
    const dateTo = document.getElementById('date-to');
    
    if (dateFrom) {
        dateFrom.addEventListener('change', applyFilters);
    }
    
    if (dateTo) {
        dateTo.addEventListener('change', applyFilters);
    }
    
    // Location filter
    const areaFilter = document.getElementById('area-filter');
    if (areaFilter) {
        areaFilter.addEventListener('change', applyFilters);
    }
}

// Load check-ins
async function loadCheckins() {
    try {
        const response = await api('/checkin/api/history/?page=1');
        if (response.ok) {
            const data = await response.json();
            allCheckins = data.results || [];
            filteredCheckins = [...allCheckins];
            
            updatePagination(data);
            renderCheckins();
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

// Load areas for filter
async function loadAreas() {
    try {
        const response = await api('/area/api/');
        if (response.ok) {
            const data = await response.json();
            const areas = data.areas || [];
            
            const areaSelect = document.getElementById('area-filter');
            if (areaSelect) {
                // Clear existing options except first one
                areaSelect.innerHTML = '<option value="">Tất cả khu vực</option>';
                
                areas.forEach(area => {
                    const option = document.createElement('option');
                    option.value = area.id;
                    option.textContent = area.name;
                    areaSelect.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading areas:', error);
    }
}

// Update pagination
function updatePagination(data) {
    currentPage = data.current_page || 1;
    totalPages = data.total_pages || 1;
    
    const paginationContainer = document.getElementById('pagination');
    if (paginationContainer) {
        paginationContainer.innerHTML = '';
        
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
        
        // Add pagination info
        const info = document.createElement('div');
        info.className = 'pagination-info';
        info.textContent = `Trang ${currentPage} / ${totalPages}`;
        paginationContainer.appendChild(info);
    }
}

// Load specific page
async function loadPage(page) {
    if (page < 1 || page > totalPages) return;
    
    try {
        const response = await api(`/checkin/api/history/?page=${page}`);
        if (response.ok) {
            const data = await response.json();
            allCheckins = data.results || [];
            filteredCheckins = [...allCheckins];
            
            updatePagination(data);
            renderCheckins();
        }
    } catch (error) {
        console.error('Error loading page:', error);
        showError('Lỗi tải trang');
    }
}

// Apply filters
function applyFilters() {
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
    const dateFrom = document.getElementById('date-from')?.value || '';
    const dateTo = document.getElementById('date-to')?.value || '';
    const area = document.getElementById('area-filter')?.value || '';
    
    filteredCheckins = allCheckins.filter(checkin => {
        // Search filter
        if (searchTerm && !checkin.area_name.toLowerCase().includes(searchTerm) &&
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
        
        // Area filter
        if (area && checkin.area && checkin.area.toString() !== area) {
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
    document.getElementById('area-filter').value = '';
    
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
    const area = document.getElementById('area-filter')?.value || '';
    
    let activeFilters = 0;
    
    if (searchTerm) activeFilters++;
    if (dateFrom) activeFilters++;
    if (dateTo) activeFilters++;
    if (area) activeFilters++;
    
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
    
    // Use provided checkins or filtered checkins
    const checkinsToRender = checkins || filteredCheckins;
    console.log('Rendering history checkins, count:', checkinsToRender.length);
    
    if (checkinsToRender.length === 0) {
        const emptyState = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>Không có check-in nào</h3>
                <p>Chưa có dữ liệu check-in phù hợp với bộ lọc.</p>
            </div>
        `;
        
        if (mobileContainer) mobileContainer.innerHTML = emptyState;
        if (tableBody) tableBody.innerHTML = emptyState;
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
                            <span class="mobile-card-value">${checkin.area_name || 'N/A'}</span>
                        </div>
                        
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">📏 Khoảng cách:</span>
                            <span class="mobile-card-value">${formatDistance(checkin.distance_m || 0)}</span>
                        </div>
                        
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">🗺️ Tọa độ:</span>
                            <span class="mobile-card-value">${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}, ${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}</span>
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
                        ${checkin.photo_url ? `
                            <img src="${checkin.photo_url}" alt="Check-in photo" class="mobile-card-photo">
                        ` : `
                            <div class="mobile-card-photo-placeholder">📷</div>
                        `}
                    </div>
                </div>
                
                <div class="mobile-card-badges">
                    <span class="mobile-badge area-badge">${checkin.area_name || 'N/A'}</span>
                    <span class="mobile-badge distance-badge">${formatDistance(checkin.distance_m || 0)}</span>
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
                        ${checkin.area_name || 'N/A'}
                    </div>
                </td>
                <td>
                    <div class="location-cell">
                        <div>${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}</div>
                        <div>${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}</div>
                    </div>
                </td>
                <td>
                    <div class="note-cell">
                        ${checkin.note || '-'}
                    </div>
                </td>
                <td>
                    ${checkin.photo_url ? `
                        <img src="${checkin.photo_url}" alt="Check-in photo" class="photo-thumbnail" onclick="openPhotoModal('${checkin.photo_url}')">
                    ` : `
                        <div class="photo-placeholder">
                            <i class="fas fa-camera"></i>
                        </div>
                    `}
                </td>
                <td>
                    <span class="status-badge status-success">Thành công</span>
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
    // Simple implementation - can be enhanced with a proper modal
    window.open(photoUrl, '_blank');
}
