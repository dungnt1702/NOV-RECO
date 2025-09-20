// Area Management JavaScript
let map;
let areas = [];
let currentArea = null;
let isEditing = false;

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    console.log('Area management page loaded');
    initializeMap();
    loadAreas();
    setupEventListeners();
});

// Initialize Leaflet map
function initializeMap() {
    // Default to Ho Chi Minh City
    map = L.map('map').setView([10.8231, 106.6297], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add click event to map
    map.on('click', function (e) {
        if (!isEditing) return;

        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        document.getElementById('lat').value = lat.toFixed(6);
        document.getElementById('lng').value = lng.toFixed(6);

        // Update map marker
        updateMapMarker(lat, lng);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('areaForm').addEventListener('submit', handleFormSubmit);

    // Add new area button
    document.getElementById('addAreaBtn').addEventListener('click', addNewArea);

    // Update check-ins button
    document.getElementById('updateCheckinsBtn').addEventListener('click', updateAllCheckins);

    // Get current location button
    document.getElementById('getCurrentLocationBtn').addEventListener('click', getCurrentLocation);
}

// Load areas from API
async function loadAreas() {
    try {
        const response = await fetch('/checkin/areas/');
        const data = await response.json();
        areas = data;
        displayAreas();
        updateMapMarkers();
    } catch (error) {
        console.error('Error loading areas:', error);
        showAlert('Lỗi khi tải danh sách khu vực', 'danger');
    }
}

// Display areas in the list
function displayAreas() {
    const areasList = document.getElementById('areasList');
    areasList.innerHTML = '';

    if (areas.length === 0) {
        areasList.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Đang tải...</div>';
        return;
    }

    areas.forEach(area => {
        const areaItem = createAreaItem(area);
        areasList.appendChild(areaItem);
    });
}

// Create area item element
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

// Update map markers
function updateMapMarkers() {
    // Clear existing markers
    map.eachLayer(layer => {
        if (layer instanceof L.CircleMarker || layer instanceof L.Circle) {
            map.removeLayer(layer);
        }
    });

    // Add markers for each area
    areas.forEach(area => {
        if (area.is_active) {
            const marker = L.circleMarker([area.lat, area.lng], {
                color: '#667eea',
                fillColor: '#667eea',
                fillOpacity: 0.7,
                radius: 8
            });

            const circle = L.circle([area.lat, area.lng], {
                color: '#667eea',
                fillColor: '#667eea',
                fillOpacity: 0.2,
                radius: area.radius_m
            });

            marker.bindPopup(`
                <strong>${area.name}</strong><br>
                Bán kính: ${area.radius_m}m<br>
                ${area.description || ''}
            `);

            marker.addTo(map);
            circle.addTo(map);
        }
    });
}

// Update map marker for editing
function updateMapMarker(lat, lng) {
    // Remove existing editing marker
    map.eachLayer(layer => {
        if (layer.options && layer.options.isEditing) {
            map.removeLayer(layer);
        }
    });

    // Add new editing marker
    const marker = L.marker([lat, lng], {
        isEditing: true
    }).addTo(map);

    const radius = parseInt(document.getElementById('radius_m').value) || 100;
    const circle = L.circle([lat, lng], {
        color: '#dc3545',
        fillColor: '#dc3545',
        fillOpacity: 0.2,
        radius: radius,
        isEditing: true
    }).addTo(map);
}

// Add new area
function addNewArea() {
    isEditing = true;
    currentArea = null;

    // Reset form
    document.getElementById('areaForm').reset();
    document.getElementById('areaForm').style.display = 'block';

    // Clear map markers
    map.eachLayer(layer => {
        if (layer instanceof L.CircleMarker || layer instanceof L.Circle) {
            map.removeLayer(layer);
        }
    });

    showAlert('Nhấp vào bản đồ để chọn vị trí khu vực', 'info');
}

// Edit area
async function editArea(areaId) {
    try {
        const response = await fetch(`/checkin/areas/${areaId}/`);
        const area = await response.json();

        currentArea = area;
        isEditing = true;

        // Fill form
        document.getElementById('name').value = area.name;
        document.getElementById('description').value = area.description || '';
        document.getElementById('lat').value = area.lat;
        document.getElementById('lng').value = area.lng;
        document.getElementById('radius_m').value = area.radius_m;
        document.getElementById('is_active').checked = area.is_active;

        // Show form
        document.getElementById('areaForm').style.display = 'block';

        // Update map
        updateMapMarker(area.lat, area.lng);

        showAlert('Đang chỉnh sửa khu vực', 'info');
    } catch (error) {
        console.error('Error loading area:', error);
        showAlert('Lỗi khi tải thông tin khu vực', 'danger');
    }
}

// Delete area
async function deleteArea(areaId) {
    if (!confirm('Bạn có chắc chắn muốn xóa khu vực này?')) {
        return;
    }

    try {
        const response = await fetch(`/checkin/areas/${areaId}/`, {
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

// Cancel edit
function cancelEdit() {
    document.getElementById('areaForm').style.display = 'none';
    isEditing = false;
    currentArea = null;
    
    // Clear map editing markers
    map.eachLayer(layer => {
        if (layer.options && layer.options.isEditing) {
            map.removeLayer(layer);
        }
    });
    
    // Reload areas to show all markers
    loadAreas();
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Convert boolean
    data.is_active = data.is_active === 'on';

    try {
        let response;
        if (currentArea) {
            // Update existing area
            response = await fetch(`/checkin/areas/${currentArea.id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });
        } else {
            // Create new area
            response = await fetch('/checkin/areas/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });
        }

        if (response.ok) {
            const message = currentArea ? 'Cập nhật khu vực thành công' : 'Tạo khu vực thành công';
            showAlert(message, 'success');

            // Hide form
            document.getElementById('areaForm').style.display = 'none';

            // Reset state
            isEditing = false;
            currentArea = null;

            // Reload areas
            loadAreas();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save area');
        }
    } catch (error) {
        console.error('Error saving area:', error);
        showAlert('Lỗi khi lưu khu vực: ' + error.message, 'danger');
    }
}

// Update all check-ins
async function updateAllCheckins() {
    if (!confirm('Bạn có chắc chắn muốn cập nhật tất cả check-in? Thao tác này có thể mất vài phút.')) {
        return;
    }

    const btn = document.getElementById('updateCheckinsBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang cập nhật...';
    btn.disabled = true;

    try {
        const response = await fetch('/checkin/update-checkins-areas/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            const result = await response.json();
            showAlert(`Cập nhật thành công! ${result.updated_count} check-in đã được cập nhật.`, 'success');
        } else {
            throw new Error('Failed to update check-ins');
        }
    } catch (error) {
        console.error('Error updating check-ins:', error);
        showAlert('Lỗi khi cập nhật check-in', 'danger');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Show alert message
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;

    const container = document.querySelector('.area-management-content');
    container.insertBefore(alertDiv, container.firstChild);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Get current location using GPS
function getCurrentLocation() {
    if (!navigator.geolocation) {
        alert('Trình duyệt không hỗ trợ định vị GPS');
        return;
    }

    const button = document.getElementById('getCurrentLocationBtn');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lấy vị trí...';
    button.disabled = true;

    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            // Update form fields
            document.getElementById('lat').value = lat.toFixed(6);
            document.getElementById('lng').value = lng.toFixed(6);
            
            // Update map marker
            updateMapMarker(lat, lng);
            
            // Show success message
            showMessage('Đã lấy vị trí hiện tại thành công!', 'success');
            
            // Restore button
            button.innerHTML = originalText;
            button.disabled = false;
        },
        function(error) {
            let errorMessage = 'Không thể lấy vị trí hiện tại: ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage += 'Bạn đã từ chối quyền truy cập vị trí';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage += 'Thông tin vị trí không khả dụng';
                    break;
                case error.TIMEOUT:
                    errorMessage += 'Hết thời gian chờ lấy vị trí';
                    break;
                default:
                    errorMessage += 'Lỗi không xác định';
                    break;
            }
            
            showMessage(errorMessage, 'error');
            
            // Restore button
            button.innerHTML = originalText;
            button.disabled = false;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        }
    );
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
