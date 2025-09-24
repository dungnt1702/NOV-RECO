// Check-in list JavaScript
let allCheckins = [];
let currentPage = 1;
let totalPages = 1;
let itemsPerPage = 25;
let currentSort = { field: 'created_at', direction: 'desc' };

console.log('Checkin list JS loaded');

// Export current filtered data to CSV (Excel-compatible)
function exportCurrentToCSV() {
  // Use the filtered data if available; otherwise use allCheckins
  const data = (typeof window !== 'undefined' && window.paginationComponent && typeof window.paginationComponent.getAllItems === 'function')
    ? window.paginationComponent.getAllItems()
    : (window.originalCheckins && allCheckins.length && allCheckins.length <= (window.originalCheckins.length))
      ? allCheckins
      : (window.originalCheckins || allCheckins);

  const rows = [];
  // Header
  rows.push(['Số thứ tự', 'Nhân viên', 'Khu vực', 'Tọa độ (lat)', 'Tọa độ (lng)', 'Khoảng cách (mét)', 'Loại checkin', 'Thời gian', 'Ghi chú']);
  
  // Data rows
  data.forEach((c, index) => {
    rows.push([
      String(index + 1),
      c.user_name || '',
      c.area_name || '',
      c.lat != null ? (Number(c.lat).toFixed(6)) : '',
      c.lng != null ? (Number(c.lng).toFixed(6)) : '',
      c.distance_m != null ? (Number(c.distance_m).toFixed(2)) : '',
      c.checkin_type_display || '',
      c.created_at || '',
      c.note || ''
    ]);
  });

  // Convert to CSV string
  const csv = rows.map(r => r.map(field => {
    const s = String(field ?? '');
    if (s.includes(',') || s.includes('"') || s.includes('\n')) {
      return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
  }).join(',')).join('\n');

  // Download as .csv (Excel opens fine)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `checkins_export_${new Date().toISOString().slice(0,19).replace(/[:T]/g,'-')}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function normalizePhotoSrc(photoUrl, photoField) {
  if (photoUrl) return photoUrl;
  if (!photoField) return null;
  const val = String(photoField);
  if (val.startsWith('http') || val.startsWith('/media/')) return val;
  return `/media/${val.replace(/^\/+/, '')}`;
}

function formatDistanceNumber(meters) {
  const n = parseFloat(meters) || 0;
  return `${n.toFixed(2)} mét`;
}

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
      response = await api('/checkin/api/?per_page=1000');
    } else {
      // Fallback to fetch if api() not available
      console.warn('api() function not found, using fetch fallback');
      response = await fetch('/checkin/api/?per_page=1000', {
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
      allCheckins = data.checkins || data.results || [];
      window.originalCheckins = allCheckins; // Store original data for filtering
      
      // Initialize sort icons
      updateSortIcons(currentSort.field, currentSort.direction);
      
      // Render checkins with pagination
      renderCheckinsTable(allCheckins);
      updatePagination();
      
      console.log('Checkins loaded:', allCheckins.length);
      loadDepartments();
      loadAreas();
      loadAllUsers();
      initializeDepartmentFilter();
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

// Sorting functions
function sortCheckins(checkins, field, direction) {
  return [...checkins].sort((a, b) => {
    let aVal = a[field];
    let bVal = b[field];
    
    // Handle different data types
    if (field === 'created_at') {
      aVal = new Date(aVal);
      bVal = new Date(bVal);
    } else if (field === 'id' || field === 'distance_m' || field === 'lat' || field === 'lng') {
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
  renderCheckinsTable(sortedCheckins);
  updatePagination();
}

function renderCheckinsTable(items = null) {
  // Use provided items or sort allCheckins
  const dataToRender = items || sortCheckins(allCheckins, currentSort.field, currentSort.direction);
  
  // Calculate pagination
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const checkinsToRender = dataToRender.slice(startIndex, endIndex);
  
  console.log('Rendering checkins table, count:', checkinsToRender.length);
  
  // Render desktop table
  const tbody = document.getElementById('checkins-table');
  if (tbody) {
    if (checkinsToRender.length === 0) {
      tbody.innerHTML = `
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
    } else {
      tbody.innerHTML = checkinsToRender.map((checkin, idx) => `
        <tr>
          <td>${startIndex + idx + 1}</td>
          <td>${checkin.user_name || 'N/A'}</td>
          <td class="area-cell">
            <i class="fas fa-map-marker-alt"></i>${checkin.area_name || 'N/A'}
          </td>
          <td class="location-cell">
            ${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}, ${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}
          </td>
          <td>
            <span class="distance-cell">${formatDistanceNumber(checkin.distance_m || 0)}</span>
          </td>
          <td>
            <span class="checkin-type-badge ${checkin.checkin_type === '1' ? 'work' : 'visitor'}">
              ${checkin.checkin_type_display || 'N/A'}
            </span>
          </td>
          <td>${formatDate(checkin.created_at)}</td>
          <td>${checkin.note || '-'}</td>
          <td>
            ${(() => {
              const src = normalizePhotoSrc(checkin.photo_url, checkin.photo);
              if (src) {
                return `<img src="${src}" alt="Check-in photo" class="photo-thumbnail" onclick="openPhotoModal('${src}')" onerror="this.style.display='none'">`;
              }
              return `<div class=\"photo-placeholder\"><i class=\"fas fa-camera\"></i></div>`;
            })()}
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
    mobileCards.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-inbox"></i>
        <h3>Không có check-in nào</h3>
        <p>Chưa có dữ liệu check-in phù hợp với bộ lọc.</p>
      </div>
    `;
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
            <span class="mobile-card-label">📏 Khoảng cách:</span>
            <span class="mobile-card-value">${formatDistanceNumber(checkin.distance_m || 0)}</span>
          </div>
          
          <div class="mobile-card-row">
            <span class="mobile-card-label">🏷️ Loại checkin:</span>
            <span class="mobile-card-value">${checkin.checkin_type_display || 'N/A'}</span>
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
          ${(function(){
            const src = normalizePhotoSrc(checkin.photo_url, checkin.photo);
            if (src) {
              return `<img src="${src}" alt="Check-in photo" class="mobile-card-photo" onclick="openPhotoModal('${src}')" onerror="this.style.display='none'">`;
            }
            return `<div class=\"mobile-card-photo-placeholder\">📷</div>`;
          })()}
        </div>
      </div>
        
        <div class="mobile-card-badges"></div>
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

async function loadDepartments() {
  try {
    let response;
    if (typeof api === 'function') {
      response = await api('/users/api/departments/');
    } else {
      response = await fetch('/users/api/departments/', {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      });
    }
    if (response.ok) {
      const departments = await response.json();
      populateDepartmentFilter(departments);
    }
  } catch (error) {
    console.error('Error loading departments:', error);
  }
}

async function loadAllUsers() {
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
      const data = await response.json();
      const users = Array.isArray(data) ? data : data.results || [];
      populateUserFilter(users);
    }
  } catch (error) {
    console.error('Error loading all users:', error);
  }
}

async function loadUsersByDepartment(departmentId) {
  try {
    console.log('Loading users for department:', departmentId);
    let response;
    if (typeof api === 'function') {
      response = await api(`/users/api/?department=${departmentId}`);
    } else {
      response = await fetch(`/users/api/?department=${departmentId}`, {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      });
    }
    console.log('API response status:', response.status);
    if (response.ok) {
      const data = await response.json();
      console.log('API response data:', data);
      const users = Array.isArray(data) ? data : data.results || [];
      console.log('Users found:', users.length);
      populateUserFilter(users);
    }
  } catch (error) {
    console.error('Error loading users by department:', error);
  }
}

async function loadAreas() {
  try {
    let response;
    if (typeof api === 'function') {
      response = await api('/area/api/');
    } else {
      response = await fetch('/area/api/', {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      });
    }
    if (response.ok) {
      const data = await response.json();
      const areas = data.results || data; // Handle both paginated and direct array responses
      populateAreaFilter(areas);
    }
  } catch (error) {
    console.error('Error loading areas:', error);
  }
}

function populateDepartmentFilter(departments) {
  const departmentFilter = document.getElementById('departmentFilter');
  if (departmentFilter) {
    departmentFilter.innerHTML = '<option value="">Tất cả phòng ban</option>' +
      departments.map(dept => `<option value="${dept.id}">${dept.name}</option>`).join('');
  }
}

// Initialize department filter event listener once
function initializeDepartmentFilter() {
  const departmentFilter = document.getElementById('departmentFilter');
  if (departmentFilter && !departmentFilter.hasAttribute('data-initialized')) {
    departmentFilter.setAttribute('data-initialized', 'true');
    departmentFilter.addEventListener('change', function() {
      console.log('Department changed to:', this.value);
      const departmentId = this.value;
      if (departmentId) {
        loadUsersByDepartment(departmentId);
      } else {
        loadAllUsers();
      }
    });
  }
}

function populateUserFilter(users) {
  console.log('Populating user filter with users:', users);
  const userFilter = document.getElementById('userFilter');
  if (userFilter) {
    if (users.length === 0) {
      console.log('No users found, showing "Không có nhân viên"');
      userFilter.innerHTML = '<option value="">Không có nhân viên</option>';
    } else {
      console.log('Found users, showing user list');
      userFilter.innerHTML = '<option value="">Tất cả nhân viên</option>' +
        users.map(user => {
          // Use full_name from API, otherwise construct from first_name and last_name
          const fullName = user.full_name || 
            (user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : 
             user.first_name || user.last_name || user.username || 'Unknown User');
          return `<option value="${user.id}">${fullName}</option>`;
        }).join('');
    }
  } else {
    console.error('User filter element not found');
  }
}

function populateAreaFilter(areas) {
  const areaFilter = document.getElementById('areaFilter');
  if (areaFilter) {
    areaFilter.innerHTML = '<option value="">Tất cả khu vực</option>' +
      areas.map(area => `<option value="${area.id}">${area.name}</option>`).join('');
  }
}

function applyFilters() {
  const dateFrom = document.getElementById('dateFrom')?.value || '';
  const dateTo = document.getElementById('dateTo')?.value || '';
  const departmentId = document.getElementById('departmentFilter')?.value || '';
  const userId = document.getElementById('userFilter')?.value || '';
  const areaId = document.getElementById('areaFilter')?.value || '';
  const checkinType = document.getElementById('checkinTypeFilter')?.value || '';

  // Get original data (not filtered data)
  const originalData = window.originalCheckins || allCheckins;
  
  const filtered = originalData.filter(checkin => {
    // Date filter
    if (dateFrom && checkin.created_at < dateFrom) return false;
    if (dateTo && checkin.created_at > dateTo + 'T23:59:59') return false;

    // Department filter
    if (departmentId && checkin.user_department_id !== parseInt(departmentId)) return false;

    // User filter
    if (userId && checkin.user_id !== parseInt(userId)) return false;

    // Area filter
    if (areaId && checkin.area_id !== parseInt(areaId)) return false;

    // Checkin type filter
    if (checkinType && checkin.checkin_type !== checkinType) return false;

    return true;
  });

  // Update current page to 1 and re-render
  currentPage = 1;
  allCheckins = filtered;
  renderCheckinsTable();
  updatePagination();
}

// Clear all filters
function clearFilters() {
  const searchInput = document.getElementById('search-input');
  const dateFrom = document.getElementById('date-from');
  const dateTo = document.getElementById('date-to');
  const userFilter = document.getElementById('user-filter');
  const checkinTypeFilter = document.getElementById('checkinTypeFilter');
  
  if (searchInput) searchInput.value = '';
  if (dateFrom) dateFrom.value = '';
  if (dateTo) dateTo.value = '';
  if (userFilter) userFilter.value = '';
  if (checkinTypeFilter) checkinTypeFilter.value = '';
  
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
  const totalItems = allCheckins.length;
  totalPages = Math.ceil(totalItems / itemsPerPage) || 1;
  
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
    
    // Add pagination info with counts
    const start = totalItems === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, totalItems);
    const info = document.createElement('div');
    info.className = 'pagination-info';
    info.textContent = `Trang ${currentPage}/${totalPages} • Hiển thị ${start}–${end} / ${totalItems}`;
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
  
  // Add event listeners for sorting
  document.querySelectorAll('.checkin-table th.sortable').forEach(th => {
    th.addEventListener('click', function() {
      const field = this.getAttribute('data-sort');
      if (field) {
        handleSort(field);
      }
    });
  });
  
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

  // Export Excel (CSV) button
  const exportBtn = document.getElementById('exportExcelBtn');
  if (exportBtn) {
    exportBtn.addEventListener('click', function() {
      exportCurrentToCSV();
    });
  }

  // Department filter change - handled in populateDepartmentFilter

  // User filter change
  const userFilter = document.getElementById('userFilter');
  if (userFilter) {
    userFilter.addEventListener('change', applyFilters);
  }

  // Area filter change
  const areaFilter = document.getElementById('areaFilter');
  if (areaFilter) {
    areaFilter.addEventListener('change', applyFilters);
  }

  // Date filters
  const dateFrom = document.getElementById('dateFrom');
  if (dateFrom) {
    dateFrom.addEventListener('change', applyFilters);
  }

  const dateTo = document.getElementById('dateTo');
  if (dateTo) {
    dateTo.addEventListener('change', applyFilters);
  }

  // Checkin type filter
  const checkinTypeFilter = document.getElementById('checkinTypeFilter');
  if (checkinTypeFilter) {
    checkinTypeFilter.addEventListener('change', applyFilters);
  }
});
