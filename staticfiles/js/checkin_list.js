// Check-in list JavaScript
let allCheckins = [];

console.log('Checkin list JS loaded');

// Sample data for testing when API is not available
const sampleCheckins = [
  {
    id: 1,
    user_name: 'Nguyễn Văn A',
    location_name: 'Văn phòng chính',
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
    location_name: 'Chi nhánh Quận 1',
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
      response = await api('/checkin/list/');
    } else {
      // Fallback to fetch if api() not available
      console.warn('api() function not found, using fetch fallback');
      response = await fetch('/checkin/list/', {
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
      
      // Initialize pagination component with data
      if (window.paginationComponent) {
        window.paginationComponent.setData(allCheckins);
        window.paginationComponent.config.onPageChange = (items) => {
          renderCheckinsTable(items);
        };
        window.paginationComponent.config.onPageSizeChange = (items) => {
          renderCheckinsTable(items);
        };
        window.paginationComponent.config.onSearch = (filteredItems) => {
          renderCheckinsTable(window.paginationComponent.getCurrentPageItems());
        };
        
        // Render first page immediately
        renderCheckinsTable(window.paginationComponent.getCurrentPageItems());
      } else {
        // Fallback: render without pagination
        renderCheckinsTable(allCheckins.slice(0, 20));
      }
      
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
  
  console.log('Rendering checkins table, count:', checkinsToRender.length);
  
  const tbody = document.getElementById('checkins-table');
  if (!tbody) {
    console.error('checkins-table element not found');
    return;
  }
  
  if (checkinsToRender.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px; color: #6c757d;">Không có dữ liệu check-in</td></tr>';
  } else {
    tbody.innerHTML = checkinsToRender.map(checkin => `
      <tr>
        <td>${checkin.id}</td>
        <td>${checkin.user_name}</td>
        <td>${checkin.location_name}</td>
        <td>${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}, ${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}</td>
        <td>${formatDistance(checkin.distance_m || 0)}</td>
        <td>${formatDate(checkin.created_at)}</td>
        <td>${checkin.note || 'N/A'}</td>
        <td>
          ${checkin.photo_url ? `<img src="${checkin.photo_url}" alt="Check-in photo" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;">` : 'N/A'}
        </td>
      </tr>
    `).join('');
  }
  
  // Also render mobile cards
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
            <span class="mobile-card-value">${checkin.location_name}</span>
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
          <span class="mobile-card-badge location">${checkin.location_name}</span>
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
      response = await api('/checkin/users-api/');
    } else {
      response = await fetch('/checkin/users-api/', {
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
        !checkin.location_name.toLowerCase().includes(searchTerm) &&
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

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing checkin list...');
  
  // Check if elements exist
  const tbody = document.getElementById('checkins-table');
  const mobileCards = document.getElementById('mobile-cards');
  console.log('Table body found:', !!tbody);
  console.log('Mobile cards container found:', !!mobileCards);
  console.log('Pagination component available:', !!window.paginationComponent);
  
  // Load checkins
  loadCheckins();
  
  // Add event listeners
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', debounce(applyFilters, 300));
  }
  
  // Optional: Add other filters if they exist
  const dateFrom = document.getElementById('date-from');
  if (dateFrom) {
    dateFrom.addEventListener('change', applyFilters);
  }
  
  const dateTo = document.getElementById('date-to');
  if (dateTo) {
    dateTo.addEventListener('change', applyFilters);
  }
  
  const userFilter = document.getElementById('user-filter');
  if (userFilter) {
    userFilter.addEventListener('change', applyFilters);
  }
});
