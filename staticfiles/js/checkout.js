/**
 * Checkout JavaScript - Simplified version
 * Xử lý logic checkout dựa trên checkin hiện tại
 */

console.log('Checkout JS loaded');

// Global variables
let checkoutCurrentLocation = null;
let checkoutIsSubmitting = false;
let checkoutMap = null;
let checkoutMarker = null;
let checkoutStream = null;
let checkoutCurrentFacingMode = 'environment';
let checkoutCurrentPhoto = null; // Store captured photo

// DOM elements
const checkoutFormElement = document.getElementById('checkoutFormElement');
const checkoutGetLocationBtn = document.getElementById('checkoutGetLocationBtn');
const checkoutSubmitBtn = document.getElementById('submitBtn');
const checkoutLocationInfo = document.getElementById('locationInfo');
const checkoutCurrentAddress = document.getElementById('checkoutCurrentAddress');
const checkoutCurrentLat = document.getElementById('checkoutCurrentLat');
const checkoutCurrentLng = document.getElementById('checkoutCurrentLng');
const checkoutLocationAccuracy = document.getElementById('checkoutLocationAccuracy');
const checkoutAddressDisplay = document.getElementById('checkoutAddressDisplay');
const checkoutLocationDetails = document.getElementById('checkoutLocationDetails');

// Camera elements
const checkoutCameraPreview = document.getElementById('checkoutCameraPreview');
const checkoutVideo = document.getElementById('checkoutVideo');
const checkoutCanvas = document.getElementById('checkoutCanvas');
const checkoutCaptureBtn = document.getElementById('checkoutCaptureBtn');
const checkoutSwitchCameraBtn = document.getElementById('checkoutSwitchCameraBtn');
const checkoutRetakeBtn = document.getElementById('checkoutRetakeBtn');
const checkoutPhotoPreview = document.getElementById('checkoutPhotoPreview');

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Checkout page DOM loaded, initializing...');
    
    if (checkoutFormElement) {
        initializeCheckoutForm();
    } else {
        console.log('No checkout form found');
    }
});

function initializeCheckoutForm() {
    console.log('Initializing checkout form...');
    
    // Initialize map
    initializeCheckoutMap();
    
    // Setup camera
    setupCheckoutCamera();
    
    // Event listeners
    if (checkoutGetLocationBtn) {
        checkoutGetLocationBtn.addEventListener('click', checkoutGetCurrentLocation);
    }
    if (checkoutFormElement) {
        checkoutFormElement.addEventListener('submit', checkoutHandleFormSubmit);
    }
    
    console.log('Checkout form initialized');
}

function initializeCheckoutMap() {
    console.log('Initializing checkout map...');
    
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.log('Map element not found');
        return;
    }
    
    // Initialize map with default center (Hanoi)
    checkoutMap = L.map('map').setView([21.0285, 105.8542], 13);
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(checkoutMap);
    
    console.log('Checkout map initialized');
}

function updateCheckoutMap(lat, lng) {
    if (!checkoutMap) return;
    
    console.log('Updating checkout map with location:', lat, lng);
    
    // Remove existing marker
    if (checkoutMarker) {
        checkoutMap.removeLayer(checkoutMarker);
    }
    
    // Add new marker
    checkoutMarker = L.marker([lat, lng]).addTo(checkoutMap);
    
    // Center map on location
    checkoutMap.setView([lat, lng], 16);
    
    // Add popup
    checkoutMarker.bindPopup(`
        <div>
            <strong>Vị trí Checkout</strong><br>
            <small>Lat: ${lat.toFixed(6)}<br>
            Lng: ${lng.toFixed(6)}</small>
        </div>
    `).openPopup();
}

function setupCheckoutCamera() {
    console.log('Setting up checkout camera...');
    
    // Camera preview click handler
    if (checkoutCameraPreview) {
        checkoutCameraPreview.addEventListener('click', startCheckoutCamera);
    }
    
    // Capture button handler
    if (checkoutCaptureBtn) {
        checkoutCaptureBtn.addEventListener('click', captureCheckoutPhoto);
    }
    
    // Switch camera button handler
    if (checkoutSwitchCameraBtn) {
        checkoutSwitchCameraBtn.addEventListener('click', switchCheckoutCamera);
    }
    
    // Retake button handler
    if (checkoutRetakeBtn) {
        checkoutRetakeBtn.addEventListener('click', retakeCheckoutPhoto);
    }
    
    console.log('Checkout camera setup complete');
}

function startCheckoutCamera() {
    console.log('Starting checkout camera...');
    
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Camera không được hỗ trợ trên thiết bị này');
        return;
    }
    
    const constraints = {
        video: {
            facingMode: checkoutCurrentFacingMode,
            width: { ideal: 1280 },
            height: { ideal: 720 }
        }
    };
    
    navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            checkoutStream = stream;
            if (checkoutVideo) {
                checkoutVideo.srcObject = stream;
                checkoutVideo.style.display = 'block';
            }
            if (checkoutCameraPreview) {
                checkoutCameraPreview.style.display = 'none';
            }
            if (checkoutCaptureBtn) {
                checkoutCaptureBtn.style.display = 'block';
            }
            if (checkoutSwitchCameraBtn) {
                checkoutSwitchCameraBtn.style.display = 'block';
            }
            console.log('Checkout camera started');
        })
        .catch(error => {
            console.error('Camera error:', error);
            alert('Không thể truy cập camera: ' + error.message);
        });
}

function captureCheckoutPhoto() {
    console.log('Capturing checkout photo...');
    
    if (!checkoutVideo || !checkoutCanvas) return;
    
    const context = checkoutCanvas.getContext('2d');
    checkoutCanvas.width = checkoutVideo.videoWidth;
    checkoutCanvas.height = checkoutVideo.videoHeight;
    
    context.drawImage(checkoutVideo, 0, 0);
    
    // Convert to blob and set to file input
    checkoutCanvas.toBlob(blob => {
        if (blob) {
            // Create File object with proper extension
            const file = new File([blob], 'checkout_photo.jpg', { type: 'image/jpeg' });
            checkoutCurrentPhoto = file; // Store globally
            
            // Update preview
            if (checkoutPhotoPreview) {
                const previewImg = document.getElementById('checkoutPreviewImg');
                if (previewImg) {
                    previewImg.src = URL.createObjectURL(blob);
                    previewImg.style.width = '100%';
                    previewImg.style.height = '100%';
                    previewImg.style.objectFit = 'cover';
                    previewImg.style.borderRadius = '8px';
                    
                    checkoutPhotoPreview.style.display = 'block';
                }
            }
            
            // Stop camera
            stopCheckoutCamera();
            
            // Enable submit button
            enableCheckoutSubmit();
            
            console.log('Photo captured successfully');
        }
    }, 'image/jpeg', 0.8);
}

function switchCheckoutCamera() {
    console.log('Switching checkout camera...');
    
    checkoutCurrentFacingMode = checkoutCurrentFacingMode === 'environment' ? 'user' : 'environment';
    
    if (checkoutStream) {
        checkoutStream.getTracks().forEach(track => track.stop());
    }
    
    startCheckoutCamera();
}

function retakeCheckoutPhoto() {
    console.log('Retaking checkout photo...');
    
    // Clear photo
    checkoutCurrentPhoto = null;
    
    // Clear preview image
    const previewImg = document.getElementById('checkoutPreviewImg');
    if (previewImg) {
        previewImg.src = '';
    }
    
    // Disable submit button
    disableCheckoutSubmit();
    
    // Hide preview
    if (checkoutPhotoPreview) {
        checkoutPhotoPreview.style.display = 'none';
    }
    
    // Show camera preview
    if (checkoutCameraPreview) {
        checkoutCameraPreview.style.display = 'block';
    }
    
    // Hide video
    if (checkoutVideo) {
        checkoutVideo.style.display = 'none';
    }
    
    // Hide camera controls
    if (checkoutCaptureBtn) {
        checkoutCaptureBtn.style.display = 'none';
    }
    if (checkoutSwitchCameraBtn) {
        checkoutSwitchCameraBtn.style.display = 'none';
    }
    
    // Stop any existing stream
    if (checkoutStream) {
        checkoutStream.getTracks().forEach(track => track.stop());
        checkoutStream = null;
    }
}

function stopCheckoutCamera() {
    console.log('Stopping checkout camera...');
    
    if (checkoutStream) {
        checkoutStream.getTracks().forEach(track => track.stop());
        checkoutStream = null;
    }
    
    if (checkoutVideo) {
        checkoutVideo.style.display = 'none';
    }
    
    if (checkoutCaptureBtn) {
        checkoutCaptureBtn.style.display = 'none';
    }
    
    if (checkoutSwitchCameraBtn) {
        checkoutSwitchCameraBtn.style.display = 'none';
    }
}

function checkoutGetCurrentLocation() {
    console.log('Getting current location...');
    
    if (!navigator.geolocation) {
        showCheckoutError('Trình duyệt không hỗ trợ định vị GPS');
        return;
    }
    
    // Show loading state
    if (checkoutGetLocationBtn) {
        checkoutGetLocationBtn.disabled = true;
        checkoutGetLocationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lấy vị trí...';
    }
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            console.log('Location obtained:', position.coords);
            
            checkoutCurrentLocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
            };
            
            // Update form fields
            document.getElementById('lat').value = position.coords.latitude;
            document.getElementById('lng').value = position.coords.longitude;
            
            // Update UI
            updateCheckoutLocationInfo();
            getCheckoutAddress(position.coords.latitude, position.coords.longitude);
            
            // Enable submit button
            enableCheckoutSubmit();
            
            // Reset button
            if (checkoutGetLocationBtn) {
                checkoutGetLocationBtn.disabled = false;
                checkoutGetLocationBtn.innerHTML = '<i class="fas fa-location-arrow"></i> Lấy vị trí';
            }
        },
        function(error) {
            console.error('Location error:', error);
            showCheckoutError('Không thể lấy vị trí: ' + error.message);
            
            // Reset button
            if (checkoutGetLocationBtn) {
                checkoutGetLocationBtn.disabled = false;
                checkoutGetLocationBtn.innerHTML = '<i class="fas fa-location-arrow"></i> Lấy vị trí';
            }
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

function updateCheckoutLocationInfo() {
    if (checkoutCurrentLocation) {
        // Update coordinates display
        if (checkoutCurrentLat) {
            checkoutCurrentLat.textContent = checkoutCurrentLocation.latitude.toFixed(6);
        }
        if (checkoutCurrentLng) {
            checkoutCurrentLng.textContent = checkoutCurrentLocation.longitude.toFixed(6);
        }
        if (checkoutLocationAccuracy) {
            checkoutLocationAccuracy.textContent = checkoutCurrentLocation.accuracy.toFixed(0) + 'm';
        }
        
        // Show location details
        if (checkoutLocationDetails) {
            checkoutLocationDetails.style.display = 'block';
        }
        
        // Update map
        updateCheckoutMap(checkoutCurrentLocation.latitude, checkoutCurrentLocation.longitude);
    }
}

function getCheckoutAddress(lat, lng) {
    console.log('Getting address for:', lat, lng);
    
    fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`)
        .then(response => response.json())
        .then(data => {
            console.log('Address data:', data);
            
            let address = 'Địa chỉ không xác định';
            if (data.display_name) {
                address = data.display_name;
            }
            
            document.getElementById('address').value = address;
            if (checkoutCurrentAddress) {
                checkoutCurrentAddress.textContent = address;
            }
            
            // Show address display
            if (checkoutAddressDisplay) {
                checkoutAddressDisplay.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Address lookup error:', error);
            document.getElementById('address').value = 'Địa chỉ không xác định';
            if (checkoutCurrentAddress) {
                checkoutCurrentAddress.textContent = 'Địa chỉ không xác định';
            }
            
            // Show address display anyway
            if (checkoutAddressDisplay) {
                checkoutAddressDisplay.style.display = 'block';
            }
        });
}

function enableCheckoutSubmit() {
    // Enable submit button when we have both photo and location
    if (checkoutSubmitBtn && checkoutCurrentPhoto && checkoutCurrentLocation) {
        checkoutSubmitBtn.disabled = false;
        checkoutSubmitBtn.classList.remove('btn-disabled');
        checkoutSubmitBtn.classList.add('btn-enabled');
    }
}

function disableCheckoutSubmit() {
    // Disable submit button when missing required data
    if (checkoutSubmitBtn) {
        checkoutSubmitBtn.disabled = true;
        checkoutSubmitBtn.classList.add('btn-disabled');
        checkoutSubmitBtn.classList.remove('btn-enabled');
    }
}

function checkoutHandleFormSubmit(event) {
    event.preventDefault();
    
    if (checkoutIsSubmitting) {
        return;
    }
    
    console.log('Submitting checkout form...');
    
    // Validate required fields
    if (!document.getElementById('lat').value || !document.getElementById('lng').value) {
        showCheckoutError('Vui lòng lấy vị trí trước khi checkout');
        return;
    }
    
    if (!checkoutCurrentPhoto) {
        showCheckoutError('Vui lòng chụp ảnh checkout');
        return;
    }
    
    checkoutIsSubmitting = true;
    
    // Disable submit button
    if (checkoutSubmitBtn) {
        checkoutSubmitBtn.disabled = true;
        checkoutSubmitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
    }
    
    // Submit form
    const formData = new FormData(checkoutFormElement);
    
    // Add photo to form data
    if (checkoutCurrentPhoto) {
        formData.append('photo', checkoutCurrentPhoto);
    }
    
    fetch('/checkin/checkout/submit/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Checkout response:', data);
        
        if (data.success) {
            // Redirect to success page with checkout_id
            window.location.href = `/checkin/checkout/success/checkout_id/${data.data.checkout_id}/`;
        } else {
            showCheckoutError(data.error || 'Có lỗi xảy ra khi checkout');
        }
    })
    .catch(error => {
        console.error('Checkout error:', error);
        showCheckoutError('Có lỗi xảy ra khi checkout');
    })
    .finally(() => {
        checkoutIsSubmitting = false;
        
        // Re-enable submit button
        if (checkoutSubmitBtn) {
            checkoutSubmitBtn.disabled = false;
            checkoutSubmitBtn.innerHTML = '<i class="fas fa-check"></i> Hoàn thành Check-out';
        }
    });
}

function showCheckoutError(message) {
    console.error('Checkout error:', message);
    
    // Create error alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of form
    if (checkoutFormElement) {
        checkoutFormElement.insertBefore(alertDiv, checkoutFormElement.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Auto-get location on page load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        if (checkoutGetLocationBtn && !checkoutCurrentLocation) {
            console.log('Auto-getting location...');
            checkoutGetCurrentLocation();
        }
    }, 1000);
});