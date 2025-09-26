// Location Form JavaScript
let map;
let currentLocation = null;
let isEditing = false;
let editingMarker = null;
let editingCircle = null;
let currentAddress = null;

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    console.log('Location form page loaded');
    
    // Check if we're editing an existing location
    const pathParts = window.location.pathname.split('/');
    const locationId = pathParts[pathParts.length - 2];
    
    if (locationId && !isNaN(locationId)) {
        isEditing = true;
        loadLocation(parseInt(locationId));
    }
    
    initializeMap();
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
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        document.getElementById('lat').value = lat.toFixed(6);
        document.getElementById('lng').value = lng.toFixed(6);

        // Update map marker
        updateMapMarker(lat, lng);
        
        // Get address from coordinates
        reverseGeocode(lat, lng);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('saveLocationBtn').addEventListener('click', handleFormSubmit);

    // Get current location button
    document.getElementById('getCurrentLocationBtn').addEventListener('click', getCurrentLocation);

    // Coordinate input changes
    document.getElementById('lat').addEventListener('input', updateMapFromInputs);
    document.getElementById('lng').addEventListener('input', updateMapFromInputs);
    document.getElementById('radius_m').addEventListener('input', updateMapFromInputs);
    
    // Address field manual edit tracking
    document.getElementById('address').addEventListener('input', function() {
        this.dataset.autoFilled = 'false';
    });
}

// Load location data for editing
async function loadLocation(locationId) {
    try {
        const response = await fetch(`/location/api/${locationId}/`);
        const location = await response.json();

        currentLocation = location;

        // Fill form
        document.getElementById('name').value = location.name;
        document.getElementById('description').value = location.description || '';
        document.getElementById('address').value = location.address || '';
        document.getElementById('lat').value = location.lat;
        document.getElementById('lng').value = location.lng;
        document.getElementById('radius_m').value = location.radius_m;
        document.getElementById('is_active').checked = location.is_active;

        // Update map
        updateMapMarker(location.lat, location.lng);
        map.setView([location.lat, location.lng], 15);

        showAlert('Đang chỉnh sửa địa điểm', 'info');
    } catch (error) {
        console.error('Error loading location:', error);
        showAlert('Lỗi khi tải thông tin địa điểm', 'danger');
    }
}

// Update map marker for editing
function updateMapMarker(lat, lng) {
    // Remove existing editing markers
    if (editingMarker) {
        map.removeLayer(editingMarker);
    }
    if (editingCircle) {
        map.removeLayer(editingCircle);
    }

    // Add new editing marker
    editingMarker = L.marker([lat, lng], {
        draggable: true
    }).addTo(map);

    // Add circle for radius visualization
    const radius = parseInt(document.getElementById('radius_m').value) || 100;
    editingCircle = L.circle([lat, lng], {
        color: '#dc3545',
        fillColor: '#dc3545',
        fillOpacity: 0.2,
        radius: radius
    }).addTo(map);

    // Add drag event to marker
    editingMarker.on('drag', function(e) {
        const newLat = e.target.getLatLng().lat;
        const newLng = e.target.getLatLng().lng;
        
        document.getElementById('lat').value = newLat.toFixed(6);
        document.getElementById('lng').value = newLng.toFixed(6);
        
        // Update circle position
        editingCircle.setLatLng([newLat, newLng]);
    });
}

// Update map from coordinate inputs
function updateMapFromInputs() {
    const lat = parseFloat(document.getElementById('lat').value);
    const lng = parseFloat(document.getElementById('lng').value);
    const radius = parseInt(document.getElementById('radius_m').value) || 100;

    if (!isNaN(lat) && !isNaN(lng)) {
        updateMapMarker(lat, lng);
        
        // Update circle radius
        if (editingCircle) {
            editingCircle.setRadius(radius);
        }
        
        // Get address from coordinates (only if both lat and lng are valid)
        if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
            reverseGeocode(lat, lng);
        }
    }
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
            map.setView([lat, lng], 15);
            
            // Get address from coordinates
            reverseGeocode(lat, lng);
            
            // Show success message
            showAlert('Đã lấy vị trí hiện tại thành công!', 'success');
            
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
            
            showAlert(errorMessage, 'danger');
            
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

// Handle form submission
async function handleFormSubmit() {
    // Validate form
    if (!validateForm()) {
        return;
    }

    const formData = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value,
        address: document.getElementById('address').value,
        lat: parseFloat(document.getElementById('lat').value),
        lng: parseFloat(document.getElementById('lng').value),
        radius_m: parseInt(document.getElementById('radius_m').value),
        is_active: document.getElementById('is_active').checked
    };

    const btn = document.getElementById('saveLocationBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lưu...';
    btn.disabled = true;

    try {
        let response;
        if (currentLocation) {
            // Update existing location
            response = await fetch(`/location/api/${currentLocation.id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            });
        } else {
            // Create new location
            response = await fetch('/location/api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            });
        }

        if (response.ok) {
            const message = currentLocation ? 'Cập nhật địa điểm thành công' : 'Tạo địa điểm thành công';
            showAlert(message, 'success');
            
            // Redirect to list after 2 seconds
            setTimeout(() => {
                window.location.href = '/location/list/';
            }, 2000);
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save location');
        }
    } catch (error) {
        console.error('Error saving location:', error);
        showAlert('Lỗi khi lưu địa điểm: ' + error.message, 'danger');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Validate form
function validateForm() {
    let isValid = true;
    
    // Clear previous validation
    document.querySelectorAll('.form-control').forEach(input => {
        input.classList.remove('is-invalid', 'is-valid');
    });
    document.querySelectorAll('.invalid-feedback').forEach(feedback => {
        feedback.remove();
    });

    // Validate name
    const name = document.getElementById('name').value.trim();
    if (!name) {
        showFieldError('name', 'Tên địa điểm là bắt buộc');
        isValid = false;
    }

    // Validate coordinates
    const lat = parseFloat(document.getElementById('lat').value);
    const lng = parseFloat(document.getElementById('lng').value);
    
    if (isNaN(lat) || lat < -90 || lat > 90) {
        showFieldError('lat', 'Vĩ độ phải là số từ -90 đến 90');
        isValid = false;
    }
    
    if (isNaN(lng) || lng < -180 || lng > 180) {
        showFieldError('lng', 'Kinh độ phải là số từ -180 đến 180');
        isValid = false;
    }

    // Validate radius
    const radius = parseInt(document.getElementById('radius_m').value);
    if (isNaN(radius) || radius < 10 || radius > 10000) {
        showFieldError('radius_m', 'Bán kính phải từ 10 đến 10000 mét');
        isValid = false;
    }

    return isValid;
}

// Show field error
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    field.classList.add('is-invalid');
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    field.parentNode.appendChild(feedback);
}

// Show alert message
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;

    const container = document.querySelector('.location-form-content');
    container.insertBefore(alertDiv, container.firstChild);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Reverse geocoding function
async function reverseGeocode(lat, lng) {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`);
        const data = await response.json();
        
        if (data && data.display_name) {
            currentAddress = data.display_name;
            
            // Update address field if it's empty or if user hasn't manually edited it
            const addressField = document.getElementById('address');
            if (!addressField.value.trim() || addressField.dataset.autoFilled === 'true') {
                addressField.value = currentAddress;
                addressField.dataset.autoFilled = 'true';
                
                // Add visual indicator that address was auto-filled
                addressField.style.backgroundColor = '#e8f5e8';
                setTimeout(() => {
                    addressField.style.backgroundColor = '';
                }, 2000);
            }
        }
    } catch (error) {
        console.error('Reverse geocoding error:', error);
        // Don't show error to user as this is a background operation
    }
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
