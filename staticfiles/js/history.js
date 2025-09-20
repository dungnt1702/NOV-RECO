// History page specific JavaScript

let allCheckins = [];
let filteredCheckins = [];
let currentPage = 1;
let totalPages = 1;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadCheckins();
    setupEventListeners();
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
    const locationFilter = document.getElementById('location-filter');
    if (locationFilter) {
        locationFilter.addEventListener('change', applyFilters);
    }
}

// Load check-ins
async function loadCheckins() {
    try {
        const response = await api('/checkin/user-history/?page=1');
        if (response.ok) {
            const data = await response.json();
            allCheckins = data.results || [];
            filteredCheckins = [...allCheckins];
            
            updatePagination(data);
            renderCheckins();
            loadLocations();
        } else {
            showError('Không thể tải dữ liệu check-in');
        }
    } catch (error) {
        console.error('Error loading checkins:', error);
        showError('Lỗi tải dữ liệu check-in');
    }
}

// Load locations for filter
async function loadLocations() {
    try {
        const response = await api('/checkin/locations/');
        if (response.ok) {
            const data = await response.json();
            const allLocations = [...(data.areas || []), ...(data.locations || [])];
            
            const locationSelect = document.getElementById('location-filter');
            if (locationSelect) {
                // Clear existing options except first one
                locationSelect.innerHTML = '<option value="">Tất cả địa điểm</option>';
                
                allLocations.forEach(location => {
                    const option = document.createElement('option');
                    option.value = location.name;
                    option.textContent = location.name;
                    locationSelect.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading locations:', error);
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
        prevBtn.disabled = currentPage === 1;
        prevBtn.addEventListener('click', () => loadPage(currentPage - 1));
        paginationContainer.appendChild(prevBtn);
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.className = i === currentPage ? 'current' : '';
            pageBtn.addEventListener('click', () => loadPage(i));
            paginationContainer.appendChild(pageBtn);
        }
        
        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Sau →';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.addEventListener('click', () => loadPage(currentPage + 1));
        paginationContainer.appendChild(nextBtn);
    }
}

// Load specific page
async function loadPage(page) {
    if (page < 1 || page > totalPages) return;
    
    try {
        const response = await api(`/checkin/user-history/?page=${page}`);
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
    const location = document.getElementById('location-filter')?.value || '';
    
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
        if (location && checkin.location_name !== location) {
            return false;
        }
        
        return true;
    });
    
    renderCheckins();
}

// Render check-ins
function renderCheckins() {
    const container = document.getElementById('checkin-list');
    if (!container) return;
    
    if (filteredCheckins.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <h3>Không có check-in nào</h3>
                <p>Chưa có dữ liệu check-in phù hợp với bộ lọc.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = filteredCheckins.map(checkin => `
        <div class="checkin-item">
            <div class="checkin-header">
                <div class="user-info">
                    <div class="user-avatar">
                        ${checkin.user_name ? checkin.user_name.charAt(0).toUpperCase() : 'U'}
                    </div>
                    <div class="user-details">
                        <h3>${checkin.user_name || 'N/A'}</h3>
                        <p>${checkin.user_email || 'N/A'}</p>
                    </div>
                </div>
                <div class="checkin-time">
                    ${formatDate(checkin.created_at)}
                </div>
            </div>
            
            <div class="checkin-content">
                <div class="checkin-details">
                    <div class="detail-row">
                        <span class="detail-icon">📍</span>
                        <span class="detail-label">Địa điểm:</span>
                        <span class="detail-value location-badge">${checkin.location_name || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-icon">📏</span>
                        <span class="detail-label">Khoảng cách:</span>
                        <span class="detail-value distance-badge">${formatDistance(checkin.distance_m || 0)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-icon">🌐</span>
                        <span class="detail-label">Tọa độ:</span>
                        <span class="detail-value">${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}, ${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}</span>
                    </div>
                    ${checkin.note ? `
                        <div class="note">
                            <strong>Ghi chú:</strong> ${checkin.note}
                        </div>
                    ` : ''}
                </div>
                ${checkin.photo ? `
                    <img src="${checkin.photo}" alt="Check-in photo" class="checkin-photo">
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Show error message
function showError(message) {
    const container = document.getElementById('checkin-list');
    if (container) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">❌</div>
                <h3>Lỗi tải dữ liệu</h3>
                <p>${message}</p>
            </div>
        `;
    }
}
