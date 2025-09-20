// Check-in list JavaScript
let allCheckins = [];
let filteredCheckins = [];
let currentPage = 1;
let totalPages = 1;

async function loadCheckins() {
  try {
    console.log('Loading checkins...');
    const response = await api('/checkin/list/');
    console.log('Response status:', response.status);
    if (response.ok) {
      const data = await response.json();
      console.log('Data received:', data);
      allCheckins = data.results || [];
      filteredCheckins = [...allCheckins];
      console.log('Checkins loaded:', allCheckins.length);
      renderCheckinsTable();
      loadUsers();
    } else {
      console.error('API error:', response.status, response.statusText);
    }
  } catch (error) {
    console.error('Error loading checkins:', error);
    showAlert('Lỗi tải danh sách check-in', 'error');
  }
}

function renderCheckinsTable() {
  const tbody = document.getElementById('checkins-table');
  tbody.innerHTML = filteredCheckins.map(checkin => `
    <tr>
      <td>${checkin.id}</td>
      <td>${checkin.user_name}</td>
      <td>${checkin.location_name}</td>
      <td>${checkin.lat ? checkin.lat.toFixed(6) : 'N/A'}, ${checkin.lng ? checkin.lng.toFixed(6) : 'N/A'}</td>
      <td>${formatDistance(checkin.distance_m || 0)}</td>
      <td>${formatDate(checkin.created_at)}</td>
      <td>${checkin.note || 'N/A'}</td>
      <td>
        ${checkin.photo ? `<img src="${checkin.photo}" alt="Check-in photo" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;">` : 'N/A'}
      </td>
    </tr>
  `).join('');
}

async function loadUsers() {
  try {
    const response = await api('/checkin/users-api/');
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
  const searchTerm = document.getElementById('search-input').value.toLowerCase();
  const dateFrom = document.getElementById('date-from').value;
  const dateTo = document.getElementById('date-to').value;
  const userId = document.getElementById('user-filter').value;

  filteredCheckins = allCheckins.filter(checkin => {
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

  renderCheckinsTable();
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
  loadCheckins();
  
  // Add event listeners
  document.getElementById('search-input').addEventListener('input', debounce(applyFilters, 300));
  document.getElementById('date-from').addEventListener('change', applyFilters);
  document.getElementById('date-to').addEventListener('change', applyFilters);
  document.getElementById('user-filter').addEventListener('change', applyFilters);
});
