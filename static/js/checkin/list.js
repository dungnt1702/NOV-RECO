// Check-in list JavaScript
let allCheckins = [];
let currentPage = 1;
let totalPages = 1;
let itemsPerPage = 25;

console.log('Checkin list JS loaded');

// Sample data for testing when API is not available
const sampleCheckins = [
  {
    id: 1,
    user_name: 'Nguyễn Văn A',
    area_name: 'Văn phòng chính',
    lat: 10.7769,
    lng: 106.7009,
    distance_m: 15,
    created_at: '2025-09-20T08:30:00',
    note: 'Check-in buổi sáng',
    photo: null
  },
  {
    id: 2,
    user_name: 'Trần Thị B',
    area_name: 'Chi nhánh Quận 1',
    lat: 10.7831,
    lng: 106.6957,
    distance_m: 8,
    created_at: '2025-09-20T09:15:00',
    note: 'Họp khách hàng',
    photo: null
  }
];

async function loadCheckins() {
  try {
    console.log('Loading checkins...');
    console.log('API function available:', typeof api);
    
    let response;
    if (typeof api === 'function') {
      response = await api('/checkin/api/list/');
    } else {
      // Fallback to fetch if api() not available
      console.warn('api() function not found, using fetch fallback');
      response = await fetch('/checkin/api/list/', {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      });
    }
    console.log('Response status:', response.status);
    if (response.ok) {
      const data = await response.json();
      console.log('Data received:', data);
      allCheckins = data.results || [];
      
      // Render checkins with pagination
      renderCheckinsTable(allCheckins);
      updatePagination();
      
      console.log('Checkins loaded:', allCheckins.length);
      loadUsers();
    } else {
      console.error('API error:', response.status, response.statusText);
      // Use sample data for demonstration when API fails
      console.log('Using sample data for demonstration');
      allCheckins = sampleCheckins;
      renderCheckinsTable(allCheckins);
      showAlert('Đang sử dụng dữ liệu mẫu. Vui lòng đăng nhập để xem dữ liệu thực.', 'warning');
    }
  } catch (error) {
    console.error('Error loading checkins:', error);
    // Use sample data for demonstration when API fails
    console.log('Using sample data for demonstration');
    allCheckins = sampleCheckins;
    renderCheckinsTable(allCheckins);
    showAlert('Đang sử dụng dữ liệu mẫu. Vui lòng kiểm tra kết nối mạng.', 'warning');
  }
}

function renderCheckinsTable(items = null) {
  // Calculate pagination
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const checkinsToRender = items ? items.slice(startIndex, endIndex) : allCheckins.slice(startIndex, endIndex);
  
  console.log('Rendering checkins table, count:', checkinsToRender.length);
  
  // Render desktop table
  const tbody = document.getElementById('checkins-table');
  if (tbody) {
    if (checkinsToRender.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px; color: #6c757d;">Không có dữ liệu check-in</td></tr>';
    } else {
      tbody.innerHTML = checkinsToRender.map(checkin => `
        <tr>
          <td>${checkin.id}</td>
          <td>
            <div class="user-info">
              <div class="user-name">${checkin.user_name || 'N/A'}</div>
              <div class="user-email">${checkin.user_email || ''}</div>
            </div>
          </td>
          <td>
            <span class="area-badge">${checkin.area_name || 'N/A'}</span>
          </td>
          <td class="location-cell">
            ${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}, ${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}
          </td>
          <td>
            <span class="distance-badge">${formatDistance(checkin.distance_m || 0)}</span>
          </td>
          <td>${formatDate(checkin.created_at)}</td>
          <td>${checkin.note || '-'}</td>
          <td>
            ${checkin.photo_url ? `
              <img src="${checkin.photo_url}" alt="Check-in photo" class="photo-thumbnail" onclick="openPhotoModal('${checkin.photo_url}')">
            ` : `
              <div class="photo-placeholder">
                <i class="fas fa-camera"></i>
              </div>
            `}
          </td>
        </tr>
      `).join('');
    }
  }
  
  // Render mobile cards
  renderMobileCards(checkinsToRender);
}

function renderMobileCards(items = null) {
  // Use provided items or get current page items from pagination component or use all checkins
  let checkinsToRender;
  if (items) {
    checkinsToRender = items;
  } else if (window.paginationComponent) {
    checkinsToRender = window.paginationComponent.getCurrentPageItems();
  } else {
    // Fallback: show first 20 items if pagination is not available
    checkinsToRender = allCheckins.slice(0, 20);
  }
  
  console.log('Rendering mobile cards, count:', checkinsToRender.length);
  console.log('Sample checkin data:', checkinsToRender[0]);
  console.log('Screen width:', window.innerWidth);
  console.log('Is mobile view:', window.innerWidth <= 768);
  
  const mobileCards = document.getElementById('mobile-cards');
  if (!mobileCards) {
    console.error('mobile-cards element not found');
    return;
  }
  
  console.log('Mobile cards container found:', mobileCards);
  
  if (checkinsToRender.length === 0) {
    mobileCards.innerHTML = '<div style="text-align: center; padding: 40px; color: #6c757d;">Không có dữ liệu check-in</div>';
  } else {
  mobileCards.innerHTML = checkinsToRender.map(checkin => `
    <div class="mobile-card">
      <div class="mobile-card-header">
        <h3 class="mobile-card-title">${checkin.user_name}</h3>
        <span class="mobile-card-id">#${checkin.id}</span>
      </div>
      
      <div class="mobile-card-content">
        <div class="mobile-card-details">
          <div class="mobile-card-row">
            <span class="mobile-card-label">📍 Địa điểm:</span>
            <span class="mobile-card-value">${checkin.area_name}</span>
          </div>
          
          <div class="mobile-card-row">
            <span class="mobile-card-label">🗺️ Tọa độ:</span>
            <span class="mobile-card-value">${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}, ${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}</span>
          </div>
          
          <div class="mobile-card-row">
            <span class="mobile-card-label">📅 Thời gian:</span>
            <span class="mobile-card-value">${formatDate(checkin.created_at)}</span>
          </div>
          
          ${checkin.note && checkin.note !== 'N/A' ? `
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
          <span class="mobile-card-badge location">${checkin.area_name}</span>
          <span class="mobile-card-badge distance">${formatDistance(checkin.distance_m || 0)}</span>
        </div>
      </div>
    `).join('');
    
    console.log('Mobile cards HTML generated, length:', mobileCards.innerHTML.length);
    console.log('Mobile cards container display:', window.getComputedStyle(mobileCards).display);
    console.log('Mobile cards container visibility:', window.getComputedStyle(mobileCards).visibility);
    
    // Force visibility check
    setTimeout(() => {
      const renderedCards = mobileCards.querySelectorAll('.mobile-card');
      console.log('Rendered mobile cards count:', renderedCards.length);
      if (renderedCards.length > 0) {
        console.log('First card display:', window.getComputedStyle(renderedCards[0]).display);
        console.log('First card visibility:', window.getComputedStyle(renderedCards[0]).visibility);
      }
    }, 100);
  }
}

async function loadUsers() {
  try {
    let response;
    if (typeof api === 'function') {
      response = await api('/users/api/');
    } else {
      response = await fetch('/users/api/', {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      });
    }
    if (response.ok) {
      const users = await response.json();
      populateUserFilter(users);
    }
  } catch (error) {
    console.error('Error loading users:', error);
  }
}

function populateUserFilter(users) {
  const userFilter = document.getElementById('user-filter');
  if (userFilter) {
    userFilter.innerHTML = '<option value="">Tất cả người dùng</option>' +
      users.map(user => `<option value="${user.id}">${user.display_name}</option>`).join('');
  }
}

function applyFilters() {
  const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
  const dateFrom = document.getElementById('date-from')?.value || '';
  const dateTo = document.getElementById('date-to')?.value || '';
  const userId = document.getElementById('user-filter')?.value || '';

  const filtered = allCheckins.filter(checkin => {
    // Search filter
    if (searchTerm && !checkin.user_name.toLowerCase().includes(searchTerm) &&
        !checkin.area_name.toLowerCase().includes(searchTerm) &&
        !(checkin.note && checkin.note.toLowerCase().includes(searchTerm))) {
      return false;
    }

    // Date filter
    if (dateFrom && checkin.created_at < dateFrom) return false;
    if (dateTo && checkin.created_at > dateTo + 'T23:59:59') return false;

    // User filter
    if (userId && checkin.user_id !== parseInt(userId)) return false;

    return true;
  });

  // Update pagination component with filtered data
  if (window.paginationComponent) {
    window.paginationComponent.setData(filtered);
    renderCheckinsTable(window.paginationComponent.getCurrentPageItems());
  }
}

// Clear all filters
function clearFilters() {
  const searchInput = document.getElementById('search-input');
  const dateFrom = document.getElementById('date-from');
  const dateTo = document.getElementById('date-to');
  const userFilter = document.getElementById('user-filter');
  
  if (searchInput) searchInput.value = '';
  if (dateFrom) dateFrom.value = '';
  if (dateTo) dateTo.value = '';
  if (userFilter) userFilter.value = '';
  
  // Reset pagination component with all data
  if (window.paginationComponent) {
    window.paginationComponent.setData(allCheckins);
    renderCheckinsTable(window.paginationComponent.getCurrentPageItems());
  }
}


// Debounce function for search input
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Utility functions
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function formatDistance(meters) {
  if (meters < 1000) {
    return `${meters}m`;
  } else {
    return `${(meters / 1000).toFixed(1)}km`;
  }
}

function openPhotoModal(photoUrl) {
  // Simple modal implementation
  const modal = document.createElement('div');
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    cursor: pointer;
  `;
  
  const img = document.createElement('img');
  img.src = photoUrl;
  img.style.cssText = `
    max-width: 90%;
    max-height: 90%;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  `;
  
  modal.appendChild(img);
  document.body.appendChild(modal);
  
  modal.addEventListener('click', () => {
    document.body.removeChild(modal);
  });
}

// Pagination functions
function updatePagination() {
  totalPages = Math.ceil(allCheckins.length / itemsPerPage);
  
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

function loadPage(page) {
  if (page >= 1 && page <= totalPages) {
    currentPage = page;
    renderCheckinsTable();
    updatePagination();
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing checkin list...');
  
  // Check if elements exist
  const tbody = document.getElementById('checkins-table');
  const mobileCards = document.getElementById('mobile-cards');
  console.log('Table body found:', !!tbody);
  console.log('Mobile cards container found:', !!mobileCards);
  
  // Load checkins
  loadCheckins();
  
  // Add event listeners for filters
  const applyFiltersBtn = document.getElementById('applyFilters');
  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener('click', applyFilters);
  }
  
  const itemsPerPageSelect = document.getElementById('itemsPerPage');
  if (itemsPerPageSelect) {
    itemsPerPageSelect.addEventListener('change', function() {
      itemsPerPage = parseInt(this.value);
      currentPage = 1;
      renderCheckinsTable();
      updatePagination();
    });
  }
});
