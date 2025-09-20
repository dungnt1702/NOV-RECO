// Quick check-in JavaScript
let lastCheckinData = null;

// Get URL parameters
function getUrlParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    lat: params.get('lat'),
    lng: params.get('lng'),
    location_name: params.get('location_name'),
    note: params.get('note')
  };
}

// Load last check-in data
async function loadLastCheckin() {
  try {
    // Check if we have data from URL parameters (from success page)
    const urlData = getUrlParams();
    if (urlData.lat && urlData.lng) {
      lastCheckinData = {
        lat: parseFloat(urlData.lat),
        lng: parseFloat(urlData.lng),
        location_name: urlData.location_name || 'Vị trí hiện tại',
        coordinates: `${urlData.lat}, ${urlData.lng}`,
        checkin_time: 'Vừa xong',
        note: urlData.note || ''
      };
      
      // Update UI
      document.getElementById('last-location').textContent = lastCheckinData.location_name;
      document.getElementById('last-coordinates').textContent = lastCheckinData.coordinates;
      document.getElementById('last-time').textContent = lastCheckinData.checkin_time;
      document.getElementById('last-note').textContent = lastCheckinData.note || 'Không có ghi chú';
      
      // Pre-fill note if available
      if (lastCheckinData.note) {
        document.getElementById('note').value = lastCheckinData.note;
      }
      
      return;
    }
    
    // Otherwise, fetch from API
    const response = await fetch('/checkin/last-checkin/', {
      credentials: 'include'
    });
    
    if (response.ok) {
      lastCheckinData = await response.json();
      
      // Update UI with last check-in data
      document.getElementById('last-location').textContent = lastCheckinData.location_name || 'N/A';
      document.getElementById('last-coordinates').textContent = lastCheckinData.coordinates || 'N/A';
      document.getElementById('last-time').textContent = formatDate(lastCheckinData.created_at);
      document.getElementById('last-note').textContent = lastCheckinData.note || 'Không có ghi chú';
    } else {
      // No previous check-in found
      document.getElementById('last-location').textContent = 'Chưa có check-in nào';
      document.getElementById('last-coordinates').textContent = 'N/A';
      document.getElementById('last-time').textContent = 'N/A';
      document.getElementById('last-note').textContent = 'N/A';
    }
  } catch (error) {
    console.error('Error loading last check-in:', error);
    document.getElementById('last-location').textContent = 'Lỗi tải dữ liệu';
    document.getElementById('last-coordinates').textContent = 'N/A';
    document.getElementById('last-time').textContent = 'N/A';
    document.getElementById('last-note').textContent = 'N/A';
  }
}

// Get current location
function getCurrentLocation() {
  if (!navigator.geolocation) {
    showAlert('Trình duyệt không hỗ trợ định vị', 'error');
    return;
  }

  showAlert('Đang lấy vị trí...', 'info');
  
  navigator.geolocation.getCurrentPosition(
    function(position) {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;
      
      // Update coordinates display
      document.getElementById('coordinates').textContent = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
      
      // Reverse geocoding to get location name
      reverseGeocode(lat, lng);
      
      showAlert('Đã lấy vị trí thành công!', 'success');
    },
    function(error) {
      console.error('Geolocation error:', error);
      let errorMessage = 'Lỗi lấy vị trí: ';
      switch(error.code) {
        case error.PERMISSION_DENIED:
          errorMessage += 'Người dùng từ chối quyền truy cập vị trí';
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
      showAlert(errorMessage, 'error');
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000
    }
  );
}

// Reverse geocoding to get location name
function reverseGeocode(lat, lng) {
  // Using OpenStreetMap Nominatim API
  fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`)
    .then(response => response.json())
    .then(data => {
      if (data && data.display_name) {
        document.getElementById('location').textContent = data.display_name;
      }
    })
    .catch(error => {
      console.error('Reverse geocoding error:', error);
      document.getElementById('location').textContent = 'Vị trí hiện tại';
    });
}

// Submit quick check-in
async function submitQuickCheckin() {
  const note = document.getElementById('note').value.trim();
  const coordinates = document.getElementById('coordinates').textContent;
  const location = document.getElementById('location').textContent;
  
  if (coordinates === 'Chưa lấy vị trí') {
    showAlert('Vui lòng lấy vị trí trước khi check-in', 'error');
    return;
  }
  
  const [lat, lng] = coordinates.split(',').map(coord => parseFloat(coord.trim()));
  
  try {
    showAlert('Đang xử lý check-in...', 'info');
    
    const formData = new FormData();
    formData.append('lat', lat);
    formData.append('lng', lng);
    formData.append('location_name', location);
    formData.append('note', note);
    
    const response = await fetch('/checkin/quick-checkin/', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    });
    
    if (response.ok) {
      const data = await response.json();
      showAlert('Check-in thành công!', 'success');
      
      // Redirect to success page with data
      const successUrl = `/checkin/success/?user_name=${encodeURIComponent(data.user_name)}&user_email=${encodeURIComponent(data.user_email)}&user_department=${encodeURIComponent(data.user_department)}&user_employee_id=${encodeURIComponent(data.user_employee_id)}&location_name=${encodeURIComponent(location)}&coordinates=${encodeURIComponent(coordinates)}&checkin_time=${encodeURIComponent(new Date().toLocaleString('vi-VN'))}&note=${encodeURIComponent(note)}&photo_url=${encodeURIComponent(data.photo_url || '')}`;
      
      setTimeout(() => {
        window.location.href = successUrl;
      }, 1500);
    } else {
      const errorData = await response.json();
      showAlert(errorData.error || 'Lỗi check-in', 'error');
    }
  } catch (error) {
    console.error('Check-in error:', error);
    showAlert('Lỗi kết nối server', 'error');
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  loadLastCheckin();
  
  // Add event listeners
  document.getElementById('get-location-btn').addEventListener('click', getCurrentLocation);
  document.getElementById('submit-btn').addEventListener('click', submitQuickCheckin);
});
