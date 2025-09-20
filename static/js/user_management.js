// User management JavaScript
async function loadUsers() {
  try {
    const response = await api('/checkin/users-api/');
    if (response.ok) {
      const users = await response.json();
      renderUsersTable(users);
    }
  } catch (error) {
    console.error('Error loading users:', error);
    showAlert('Lỗi tải danh sách người dùng', 'error');
  }
}

function renderUsersTable(users) {
  const tbody = document.getElementById('users-table');
  tbody.innerHTML = users.map(user => `
    <tr>
      <td>${user.id}</td>
      <td>${user.display_name}</td>
      <td>${user.email}</td>
      <td>${user.role_display || user.role}</td>
      <td>${user.department || 'N/A'}</td>
      <td>
        <span class="badge ${user.is_active ? 'success' : 'danger'}">
          ${user.is_active ? 'Hoạt động' : 'Không hoạt động'}
        </span>
      </td>
      <td>
        <button onclick="editUser(${user.id})" class="btn btn-sm">Sửa</button>
        <button onclick="deleteUser(${user.id})" class="btn btn-sm danger">Xóa</button>
      </td>
    </tr>
  `).join('');
}

function createUser() {
  // Implementation for creating new user
  showAlert('Tính năng đang phát triển', 'info');
}

function editUser(userId) {
  // Implementation for editing user
  showAlert('Tính năng đang phát triển', 'info');
}

function deleteUser(userId) {
  if (confirm('Bạn có chắc chắn muốn xóa người dùng này?')) {
    // Implementation for deleting user
    showAlert('Tính năng đang phát triển', 'info');
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  loadUsers();
});
