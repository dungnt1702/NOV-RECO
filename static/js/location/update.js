(function(){
  // Helper function to parse numbers with comma decimal separator
  function parseNumber(val){
    if (typeof val !== 'string') return Number(val);
    return Number(val.replace(',', '.'));
  }

  // Helper function to format coordinates
  function formatCoordinate(num) {
    return parseFloat(num).toFixed(6);
  }

  // Helper function to show loading state
  function setLoading(element, loading) {
    if (loading) {
      element.disabled = true;
      element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang tải...';
    } else {
      element.disabled = false;
      element.innerHTML = '<i class="fas fa-location-arrow"></i> Lấy vị trí hiện tại';
    }
  }

  // Helper function to show notification
  function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
      ${message}
    `;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 1000;
      animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  // Get DOM elements
  const latInput = document.getElementById('lat');
  const lngInput = document.getElementById('lng');
  const radiusInput = document.getElementById('radius_m');
  const btnCurrent = document.getElementById('btnCurrent');
  const form = document.querySelector('form');
  
  if (!latInput || !lngInput) return;

  // Initialize coordinates
  const startLat = parseNumber(latInput.value) || 10.762622; // Default to HCMC
  const startLng = parseNumber(lngInput.value) || 106.660172; // Default to HCMC

  // Wait for Leaflet to load
  if (!window.L) {
    console.error('Leaflet library not loaded');
    return;
  }

  // Initialize map
  const map = L.map('map', {
    zoomControl: true,
    scrollWheelZoom: true,
    doubleClickZoom: true,
    boxZoom: true,
    keyboard: true,
    dragging: true,
    touchZoom: true
  });

  // Add tile layer
  const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    subdomains: ['a', 'b', 'c']
  });
  tiles.addTo(map);

  // Set initial view
  map.setView([startLat, startLng], 15);

  // Create draggable marker
  const marker = L.marker([startLat, startLng], { 
    draggable: true,
    title: 'Kéo thả để thay đổi vị trí'
  }).addTo(map);

  // Add circle to show radius
  let radiusCircle = null;
  function updateRadiusCircle() {
    if (radiusCircle) {
      map.removeLayer(radiusCircle);
    }
    
    const radius = parseNumber(radiusInput.value) || 100;
    const latLng = marker.getLatLng();
    
    radiusCircle = L.circle(latLng, {
      radius: radius,
      color: '#0A5597',
      fillColor: '#0A5597',
      fillOpacity: 0.2,
      weight: 2
    }).addTo(map);
  }

  // Sync inputs from marker position
  function syncInputsFromMarker(pos) {
    const p = pos || marker.getLatLng();
    latInput.value = formatCoordinate(p.lat);
    lngInput.value = formatCoordinate(p.lng);
    updateRadiusCircle();
  }

  // Move marker from input values
  function moveMarkerFromInputs() {
    const la = parseNumber(latInput.value);
    const ln = parseNumber(lngInput.value);
    
    if (!isFinite(la) || !isFinite(ln)) {
      showNotification('Tọa độ không hợp lệ', 'error');
      return;
    }
    
    if (la < -90 || la > 90) {
      showNotification('Vĩ độ phải từ -90 đến 90', 'error');
      return;
    }
    
    if (ln < -180 || ln > 180) {
      showNotification('Kinh độ phải từ -180 đến 180', 'error');
      return;
    }
    
    marker.setLatLng([la, ln]);
    map.setView([la, ln], map.getZoom());
    updateRadiusCircle();
  }

  // Event listeners
  marker.on('dragstart', function() {
    showNotification('Đang kéo ghim...', 'info');
  });

  marker.on('dragend', function() {
    syncInputsFromMarker();
    showNotification('Vị trí đã được cập nhật', 'success');
  });

  map.on('click', function(e) {
    marker.setLatLng(e.latlng);
    syncInputsFromMarker(e.latlng);
    showNotification('Vị trí đã được chọn', 'success');
  });

  // Input change listeners
  latInput.addEventListener('input', moveMarkerFromInputs);
  lngInput.addEventListener('input', moveMarkerFromInputs);
  radiusInput.addEventListener('input', updateRadiusCircle);

  // Get current location button
  if (btnCurrent && navigator.geolocation) {
    btnCurrent.addEventListener('click', function() {
      setLoading(btnCurrent, true);
      
      navigator.geolocation.getCurrentPosition(
        function(pos) {
          const { latitude, longitude } = pos.coords;
          marker.setLatLng([latitude, longitude]);
          map.setView([latitude, longitude], 17);
          syncInputsFromMarker({ lat: latitude, lng: longitude });
          showNotification('Vị trí hiện tại đã được lấy', 'success');
          setLoading(btnCurrent, false);
        },
        function(error) {
          let message = 'Không lấy được vị trí hiện tại';
          switch(error.code) {
            case error.PERMISSION_DENIED:
              message = 'Bạn đã từ chối quyền truy cập vị trí';
              break;
            case error.POSITION_UNAVAILABLE:
              message = 'Thông tin vị trí không khả dụng';
              break;
            case error.TIMEOUT:
              message = 'Hết thời gian chờ lấy vị trí';
              break;
          }
          showNotification(message, 'error');
          setLoading(btnCurrent, false);
        },
        { 
          enableHighAccuracy: true, 
          timeout: 10000,
          maximumAge: 60000
        }
      );
    });
  }

  // Form validation
  if (form) {
    form.addEventListener('submit', function(e) {
      const name = document.getElementById('name').value.trim();
      const lat = parseNumber(latInput.value);
      const lng = parseNumber(lngInput.value);
      const radius = parseNumber(radiusInput.value);

      if (!name) {
        e.preventDefault();
        showNotification('Vui lòng nhập tên khu vực', 'error');
        return;
      }

      if (!isFinite(lat) || !isFinite(lng)) {
        e.preventDefault();
        showNotification('Vui lòng nhập tọa độ hợp lệ', 'error');
        return;
      }

      if (lat < -90 || lat > 90) {
        e.preventDefault();
        showNotification('Vĩ độ phải từ -90 đến 90', 'error');
        return;
      }

      if (lng < -180 || lng > 180) {
        e.preventDefault();
        showNotification('Kinh độ phải từ -180 đến 180', 'error');
        return;
      }

      if (!isFinite(radius) || radius < 10 || radius > 10000) {
        e.preventDefault();
        showNotification('Bán kính phải từ 10 đến 10000 mét', 'error');
        return;
      }

      showNotification('Đang cập nhật khu vực...', 'info');
    });
  }

  // Initialize radius circle
  updateRadiusCircle();

  // Add CSS for animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }
  `;
  document.head.appendChild(style);

  console.log('Location update page initialized successfully');
})();
