// Check-in page specific JavaScript

// Global variables
let map;
let marker;
let currentPosition = null;
let currentPhoto = null;
let stream = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadUserInfo();
    setupEventListeners();
    updateSubmitButtonState();
});

// Initialize map
function initializeMap() {
    map = L.map('map').setView([10.8231, 106.6297], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Disable map interaction
    map.dragging.disable();
    map.touchZoom.disable();
    map.doubleClickZoom.disable();
    map.scrollWheelZoom.disable();
    map.boxZoom.disable();
    map.keyboard.disable();
    
    if (map.tap) map.tap.disable();
}

// Load user information
async function loadUserInfo() {
    try {
        const response = await api('/checkin/user-info/');
        if (response.ok) {
            const userData = await response.json();
            updateUserInfo(userData);
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Update user info display
function updateUserInfo(userData) {
    const nameElement = document.getElementById('user-name');
    const emailElement = document.getElementById('user-email');
    const departmentElement = document.getElementById('user-department');
    const roleElement = document.getElementById('user-role');
    
    if (nameElement) nameElement.textContent = userData.display_name || 'N/A';
    if (emailElement) emailElement.textContent = userData.email || 'N/A';
    if (departmentElement) departmentElement.textContent = userData.department || 'N/A';
    if (roleElement) roleElement.textContent = userData.role_display || 'N/A';
}

// Setup event listeners
function setupEventListeners() {
    // Get location button
    const getLocationBtn = document.getElementById('btn-get-location');
    if (getLocationBtn) {
        getLocationBtn.addEventListener('click', getCurrentLocation);
    }
    
    // Camera buttons
    const captureBtn = document.getElementById('btn-capture');
    const retakeBtn = document.getElementById('btn-retake');
    const cameraPreview = document.getElementById('camera-preview');
    
    if (captureBtn) {
        captureBtn.addEventListener('click', openCameraHandler);
    }
    
    if (retakeBtn) {
        retakeBtn.addEventListener('click', retakePhoto);
    }
    
    if (cameraPreview) {
        cameraPreview.addEventListener('click', openCameraHandler);
    }
    
    // Form submission
    const form = document.getElementById('checkin-form');
    if (form) {
        form.addEventListener('submit', handleSubmit);
    }
    
    // Note input
    const noteInput = document.getElementById('note');
    if (noteInput) {
        noteInput.addEventListener('input', updateSubmitButtonState);
    }
}

// Get current location
function getCurrentLocation() {
    const btn = document.getElementById('btn-get-location');
    if (!btn) return;
    
    setLoading(btn, true);
    
    if (!navigator.geolocation) {
        showAlert('Trình duyệt không hỗ trợ định vị GPS', 'error');
        setLoading(btn, false);
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            currentPosition = { lat, lng };
            
            // Update map
            map.setView([lat, lng], 16);
            if (marker) {
                map.removeLayer(marker);
            }
            marker = L.marker([lat, lng]).addTo(map);
            
            // Update coordinates display
            const coordsElement = document.getElementById('coordinates');
            if (coordsElement) {
                coordsElement.textContent = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
            }
            
            updateSubmitButtonState();
            showAlert('Đã lấy vị trí thành công!', 'success');
            setLoading(btn, false);
        },
        function(error) {
            let message = 'Không thể lấy vị trí GPS';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message = 'Bị từ chối quyền truy cập vị trí';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = 'Vị trí không khả dụng';
                    break;
                case error.TIMEOUT:
                    message = 'Hết thời gian chờ lấy vị trí';
                    break;
            }
            showAlert(message, 'error');
            setLoading(btn, false);
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        }
    );
}

// Open camera handler
function openCameraHandler() {
    if (currentPhoto) {
        retakePhoto();
        return;
    }
    
    openCamera();
}

// Open camera
async function openCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { 
                facingMode: 'environment',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        
        const video = document.createElement('video');
        video.srcObject = stream;
        video.play();
        
        const cameraPreview = document.getElementById('camera-preview');
        if (cameraPreview) {
            cameraPreview.innerHTML = '';
            cameraPreview.appendChild(video);
            cameraPreview.classList.add('has-photo');
        }
        
        // Show capture button
        const captureBtn = document.getElementById('btn-capture');
        const retakeBtn = document.getElementById('btn-retake');
        
        if (captureBtn) captureBtn.textContent = '📷 Chụp ảnh';
        if (retakeBtn) retakeBtn.style.display = 'none';
        
    } catch (error) {
        console.error('Camera error:', error);
        showAlert('Không thể mở camera. Vui lòng kiểm tra quyền truy cập.', 'error');
    }
}

// Capture photo
function capturePhoto() {
    const video = document.querySelector('#camera-preview video');
    if (!video) return;
    
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    canvas.toBlob(function(blob) {
        // Create File object with proper extension
        const file = new File([blob], 'checkin_photo.jpg', { type: 'image/jpeg' });
        currentPhoto = file;
        
        // Update preview
        const cameraPreview = document.getElementById('camera-preview');
        if (cameraPreview) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(blob);
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '8px';
            
            cameraPreview.innerHTML = '';
            cameraPreview.appendChild(img);
            cameraPreview.classList.add('has-photo');
        }
        
        // Update buttons
        const captureBtn = document.getElementById('btn-capture');
        const retakeBtn = document.getElementById('btn-retake');
        
        if (captureBtn) captureBtn.textContent = '✅ Đã chụp';
        if (retakeBtn) retakeBtn.style.display = 'inline-block';
        
        // Stop camera
        stopCamera();
        updateSubmitButtonState();
        
    }, 'image/jpeg', 0.8);
}

// Retake photo
function retakePhoto() {
    currentPhoto = null;
    
    const cameraPreview = document.getElementById('camera-preview');
    if (cameraPreview) {
        cameraPreview.innerHTML = `
            <div class="camera-icon">📷</div>
            <div class="camera-text">Chạm để chụp ảnh</div>
        `;
        cameraPreview.classList.remove('has-photo');
    }
    
    // Update buttons
    const captureBtn = document.getElementById('btn-capture');
    const retakeBtn = document.getElementById('btn-retake');
    
    if (captureBtn) captureBtn.textContent = '📷 Chụp ảnh';
    if (retakeBtn) retakeBtn.style.display = 'none';
    
    updateSubmitButtonState();
}

// Stop camera
function stopCamera() {
    if (stream) {
        try {
            stream.getTracks().forEach(track => track.stop());
        } catch (error) {
            console.error('Error stopping camera:', error);
        }
        stream = null;
    }
}

// Update submit button state
function updateSubmitButtonState() {
    const submitBtn = document.getElementById('btn-checkin');
    if (!submitBtn) return;
    
    const hasLocation = currentPosition !== null;
    const hasPhoto = currentPhoto !== null;
    
    if (hasLocation && hasPhoto) {
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
    } else {
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
    }
}

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();
    
    // Check if we have required data
    if (!currentPosition || !currentPhoto) {
        showAlert('Vui lòng lấy vị trí và chụp ảnh trước khi gửi check-in', 'error');
        return;
    }
    
    const submitBtn = document.getElementById('btn-checkin');
    setLoading(submitBtn, true);
    
    try {
        const formData = new FormData();
        formData.append('lat', currentPosition.lat);
        formData.append('lng', currentPosition.lng);
        formData.append('photo', currentPhoto);
        
        const note = document.getElementById('note').value;
        if (note) {
            formData.append('note', note);
        }
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        formData.append('csrfmiddlewaretoken', csrfToken);
        
        const response = await fetch('/checkin/submit/', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        
        if (response.ok) {
            if (response.url.includes('/checkin/success/')) {
                window.location.href = response.url;
            } else {
                const result = await response.json();
                if (result.success) {
                    showAlert('Check-in thành công!', 'success');
                    // Reset form
                    resetForm();
                } else {
                    showAlert(result.message || 'Có lỗi xảy ra', 'error');
                }
            }
        } else if (response.status === 302) {
            // Redirect to login
            window.location.href = '/accounts/login/';
        } else {
            showAlert('Có lỗi xảy ra khi gửi check-in', 'error');
        }
        
    } catch (error) {
        console.error('Submit error:', error);
        showAlert(`Lỗi: ${error.message}`, 'error');
    } finally {
        setLoading(submitBtn, false);
    }
}

// Reset form
function resetForm() {
    currentPosition = null;
    currentPhoto = null;
    
    // Reset map
    if (marker) {
        map.removeLayer(marker);
        marker = null;
    }
    
    // Reset coordinates
    const coordsElement = document.getElementById('coordinates');
    if (coordsElement) {
        coordsElement.textContent = 'Chưa lấy vị trí';
    }
    
    // Reset camera
    retakePhoto();
    
    // Reset note
    const noteInput = document.getElementById('note');
    if (noteInput) {
        noteInput.value = '';
    }
    
    updateSubmitButtonState();
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopCamera();
});
