// Check-in page specific JavaScript

// Global variables
let map;
let marker;
let currentPosition = null;
let currentPhoto = null;
let stream = null;
let currentFacingMode = 'environment'; // 'environment' for back camera, 'user' for front camera

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Checkin page loaded, initializing...');
    initializeMap();
    loadUserInfo();
    setupEventListeners();
    updateSubmitButtonState();
    checkBrowserSupport();
    console.log('Checkin page initialization complete');
});

// Check browser support and show warnings
function checkBrowserSupport() {
    const warnings = [];
    
    // Check HTTPS
    const isSecureContext = window.isSecureContext || location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.hostname === 'reco.local';
    
    if (!isSecureContext) {
        warnings.push('⚠️ Trang web không bảo mật - GPS và Camera có thể không hoạt động');
    }
    
    // Check geolocation support
    if (!navigator.geolocation) {
        warnings.push('❌ Trình duyệt không hỗ trợ GPS');
    }
    
    // Check camera support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        warnings.push('❌ Trình duyệt không hỗ trợ Camera');
    }
    
    if (warnings.length > 0) {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'browser-warnings';
        warningDiv.style.cssText = `
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            color: #856404;
        `;
        warningDiv.innerHTML = `
            <h4>⚠️ Cảnh báo trình duyệt:</h4>
            <ul>
                ${warnings.map(w => `<li>${w}</li>`).join('')}
            </ul>
            <p><strong>Khuyến nghị:</strong> Sử dụng Chrome/Firefox/Edge và truy cập qua <code>reco.local</code></p>
        `;
        
        const container = document.querySelector('.checkin-container');
        if (container) {
            container.insertBefore(warningDiv, container.firstChild);
        }
    }
}

// Initialize map (only if map element exists)
function initializeMap() {
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.log('Map element not found, skipping map initialization');
        return;
    }
    
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
        const response = await api('/checkin/api/user-info/');
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
    console.log('Setting up event listeners...');
    
    // Permission test buttons
    const testGpsBtn = document.getElementById('testGpsBtn');
    const testCameraBtn = document.getElementById('testCameraBtn');
    
    if (testGpsBtn) {
        testGpsBtn.addEventListener('click', testGpsPermission);
    }
    
    if (testCameraBtn) {
        testCameraBtn.addEventListener('click', testCameraPermission);
    }
    
    // Get location button
    const getLocationBtn = document.getElementById('getLocationBtn');
    if (getLocationBtn) {
        console.log('Location button found, adding listener');
        getLocationBtn.addEventListener('click', getCurrentLocation);
    } else {
        console.warn('Location button not found');
    }
    
    // Camera buttons
    const captureBtn = document.getElementById('captureBtn');
    const retakeBtn = document.getElementById('retakeBtn');
    const switchBtn = document.getElementById('switchCameraBtn');
    const cameraPreview = document.getElementById('camera-preview');
    
    if (captureBtn) {
        console.log('Capture button found, adding listener');
        captureBtn.addEventListener('click', function() {
            if (currentPhoto) {
                // If already have photo, retake
                retakePhoto();
            } else if (stream) {
                // If camera is open, capture photo
                capturePhoto();
            } else {
                // If camera is not open, open it
                openCameraHandler();
            }
        });
    } else {
        console.warn('Capture button not found');
    }
    
    if (retakeBtn) {
        console.log('Retake button found, adding listener');
        retakeBtn.addEventListener('click', retakePhoto);
    } else {
        console.warn('Retake button not found');
    }
    
    if (switchBtn) {
        console.log('Switch camera button found, adding listener');
        switchBtn.addEventListener('click', switchCamera);
    } else {
        console.warn('Switch camera button not found');
    }
    
    if (cameraPreview) {
        console.log('Camera preview found, adding listener');
        cameraPreview.addEventListener('click', openCameraHandler);
    } else {
        console.warn('Camera preview not found');
    }
    
    
    // Form submission
    const form = document.getElementById('checkinFormElement');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission
            handleSubmit();
        });
    }
    
    // Note input
    const noteInput = document.getElementById('note');
    if (noteInput) {
        noteInput.addEventListener('input', updateSubmitButtonState);
    }
}

// Get current location
async function getCurrentLocation() {
    const btn = document.getElementById('getLocationBtn');
    if (!btn) return;
    
    setLoading(btn, true);
    
    // Check if running on HTTPS or localhost
    const isSecureContext = window.isSecureContext || location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.hostname === 'reco.local';
    
    if (!isSecureContext) {
        showAlert('⚠️ GPS chỉ hoạt động trên HTTPS hoặc localhost.\n\nVui lòng truy cập qua:\n• https:// (bảo mật)\n• localhost\n• reco.local', 'error');
        setLoading(btn, false);
        return;
    }
    
    if (!navigator.geolocation) {
        showAlert('❌ Trình duyệt không hỗ trợ định vị GPS', 'error');
        setLoading(btn, false);
        return;
    }
    
    try {
        // First check permissions if supported
        if (navigator.permissions) {
            const permission = await navigator.permissions.query({ name: 'geolocation' });
            console.log('Geolocation permission:', permission.state);
            
            if (permission.state === 'denied') {
                showAlert('🚫 Quyền truy cập vị trí bị từ chối!\n\n📋 Cách khắc phục:\n1️⃣ Nhấp vào biểu tượng 🔒 bên trái thanh địa chỉ\n2️⃣ Chọn "Vị trí" → "Cho phép"\n3️⃣ Tải lại trang và thử lại', 'error');
                setLoading(btn, false);
                return;
            }
        }
        
    } catch (error) {
        console.log('Permissions API not supported, proceeding with geolocation');
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
            showAlert('✅ Đã lấy vị trí thành công!', 'success');
            setLoading(btn, false);
        },
        function(error) {
            let message = '';
            let suggestion = '';
            
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message = '🚫 Bị từ chối quyền truy cập vị trí';
                    suggestion = '📋 Cách khắc phục:\n1️⃣ Nhấp vào biểu tượng 🔒 bên trái thanh địa chỉ\n2️⃣ Chọn "Vị trí" → "Cho phép"\n3️⃣ Tải lại trang và thử lại';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = '📍 Vị trí không khả dụng';
                    suggestion = '🔧 Kiểm tra:\n• Kết nối mạng\n• GPS đã bật\n• Thử lại sau vài giây';
                    break;
                case error.TIMEOUT:
                    message = '⏰ Hết thời gian chờ lấy vị trí';
                    suggestion = '🔄 Vui lòng thử lại (có thể do tín hiệu GPS yếu)';
                    break;
                default:
                    message = '❌ Lỗi không xác định khi lấy vị trí';
                    suggestion = '🔄 Vui lòng thử lại hoặc kiểm tra cài đặt vị trí';
                    break;
            }
            
            console.error('Geolocation error:', error);
            showAlert(`${message}\n\n${suggestion}`, 'error');
            setLoading(btn, false);
        },
        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 30000
        }
    );
}

// Open camera handler
function openCameraHandler() {
    console.log('Camera button clicked');
    if (currentPhoto) {
        console.log('Retaking photo');
        retakePhoto();
        return;
    }
    
    console.log('Opening camera...');
    openCamera();
}

// Open camera
async function openCamera() {
    try {
        console.log('Requesting camera access...');
        
        // Check if running on HTTPS or localhost
        const isSecureContext = window.isSecureContext || location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.hostname === 'reco.local';
        
        if (!isSecureContext) {
            showAlert('⚠️ Camera chỉ hoạt động trên HTTPS hoặc localhost.\n\nVui lòng truy cập qua:\n• https:// (bảo mật)\n• localhost\n• reco.local', 'error');
            return;
        }
        
        // Check if getUserMedia is supported
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('📷 Camera không được hỗ trợ trên trình duyệt này');
        }
        
        // Check camera permission first if supported
        if (navigator.permissions) {
            try {
                const permission = await navigator.permissions.query({ name: 'camera' });
                console.log('Camera permission:', permission.state);
                
                if (permission.state === 'denied') {
                    showAlert('🚫 Quyền truy cập camera bị từ chối!\n\n📋 Cách khắc phục:\n1️⃣ Nhấp vào biểu tượng 🔒 bên trái thanh địa chỉ\n2️⃣ Chọn "Camera" → "Cho phép"\n3️⃣ Tải lại trang và thử lại', 'error');
                    return;
                }
            } catch (permError) {
                console.log('Camera permission check not supported, proceeding...');
            }
        }
        
        stream = await navigator.mediaDevices.getUserMedia({
            video: { 
                facingMode: currentFacingMode,
                width: { ideal: 720 }, // Portrait width (smaller)
                height: { ideal: 960 } // Portrait height (larger) - 3:4 ratio
            }
        });
        
        console.log('Camera access granted, creating video element...');
        
        const video = document.createElement('video');
        video.id = 'video';
        video.srcObject = stream;
        video.autoplay = true;
        video.muted = true;
        video.playsInline = true;
        
        // Wait for video to be ready
        video.onloadedmetadata = function() {
            console.log('Video metadata loaded, playing...');
            video.play().catch(e => console.error('Error playing video:', e));
        };
        
        const cameraPreview = document.getElementById('camera-preview');
        if (cameraPreview) {
            console.log('Updating camera preview...');
            cameraPreview.innerHTML = '';
            cameraPreview.appendChild(video);
            cameraPreview.classList.add('has-photo', 'showing-video');
        }
        
        // Show capture and switch camera buttons
        const captureBtn = document.getElementById('captureBtn');
        const retakeBtn = document.getElementById('retakeBtn');
        const switchBtn = document.getElementById('switchCameraBtn');
        
        console.log('Camera buttons found:', {
            capture: !!captureBtn,
            retake: !!retakeBtn,
            switch: !!switchBtn
        });
        
        if (captureBtn) captureBtn.textContent = '📷 Chụp ảnh';
        if (retakeBtn) retakeBtn.style.display = 'none';
        if (switchBtn) {
            // Always show switch button on mobile, let user decide
            const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            
            if (isMobile) {
                // On mobile, always show the button since most phones have front+back cameras
                switchBtn.style.display = 'inline-block';
                switchBtn.textContent = '🔄 Đổi camera';
                console.log('Switch camera button shown - mobile device detected');
            } else {
                // On desktop, check for multiple cameras
                checkMultipleCameras().then(hasMultiple => {
                    if (hasMultiple) {
                        switchBtn.style.display = 'inline-block';
                        switchBtn.textContent = '🔄 Đổi camera';
                        console.log('Switch camera button shown - multiple cameras detected');
                    } else {
                        switchBtn.style.display = 'none';
                        console.log('Switch camera button hidden - only one camera detected');
                    }
                }).catch(error => {
                    console.warn('Could not detect camera count, showing switch button anyway:', error);
                    switchBtn.style.display = 'inline-block';
                    switchBtn.textContent = '🔄 Đổi camera';
                });
            }
        } else {
            console.error('Switch camera button not found!');
        }
        
        updateSubmitButtonState();
        console.log('Camera opened successfully');
        showAlert('✅ Camera đã sẵn sàng!', 'success');
        
    } catch (error) {
        console.error('Error opening camera:', error);
        let errorMessage = '';
        let suggestion = '';
        
        if (error.name === 'NotAllowedError') {
            errorMessage = '🚫 Bị từ chối quyền truy cập camera';
            suggestion = '📋 Cách khắc phục:\n1️⃣ Nhấp vào biểu tượng 🔒 bên trái thanh địa chỉ\n2️⃣ Chọn "Camera" → "Cho phép"\n3️⃣ Tải lại trang và thử lại';
        } else if (error.name === 'NotFoundError') {
            errorMessage = '📷 Không tìm thấy camera';
            suggestion = '🔧 Kiểm tra:\n• Camera đã kết nối\n• Không có ứng dụng nào khác đang sử dụng camera';
        } else if (error.name === 'NotSupportedError') {
            errorMessage = '❌ Camera không được hỗ trợ trên trình duyệt này';
            suggestion = '🌐 Thử với trình duyệt khác (Chrome, Firefox, Edge)';
        } else if (error.name === 'NotReadableError') {
            errorMessage = '⚠️ Camera đang được sử dụng bởi ứng dụng khác';
            suggestion = '🔄 Đóng các ứng dụng camera khác và thử lại';
        } else {
            errorMessage = '❌ Lỗi không xác định với camera';
            suggestion = `🔧 Chi tiết: ${error.message}`;
        }
        
        showAlert(`${errorMessage}\n\n${suggestion}`, 'error');
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
            cameraPreview.classList.remove('showing-video');
        }
        
        // Update buttons
        const captureBtn = document.getElementById('captureBtn');
        const retakeBtn = document.getElementById('retakeBtn');
        const switchBtn = document.getElementById('switchCameraBtn');
        
        if (captureBtn) captureBtn.textContent = '✅ Đã chụp';
        if (retakeBtn) retakeBtn.style.display = 'inline-block';
        if (switchBtn) switchBtn.style.display = 'none';
        
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
        cameraPreview.classList.remove('has-photo', 'showing-video');
    }
    
    // Update buttons
    const captureBtn = document.getElementById('captureBtn');
    const retakeBtn = document.getElementById('retakeBtn');
    
    if (captureBtn) captureBtn.textContent = '📷 Chụp ảnh';
    if (retakeBtn) retakeBtn.style.display = 'none';
    
    // Hide switch camera button when retaking
    const switchBtn = document.getElementById('switchCameraBtn');
    if (switchBtn) switchBtn.style.display = 'none';
    
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

// Check if device has multiple cameras
async function checkMultipleCameras() {
    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
            console.log('enumerateDevices not supported');
            return true; // Assume multiple cameras if we can't check
        }
        
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        
        console.log('Video devices found:', videoDevices.length, videoDevices);
        
        // Check if we have at least 2 cameras or if we can't determine (return true to be safe)
        return videoDevices.length >= 2 || videoDevices.length === 0;
        
    } catch (error) {
        console.error('Error checking camera devices:', error);
        return true; // If we can't check, assume multiple cameras
    }
}

// Switch camera (front/back)
async function switchCamera() {
    try {
        // Stop current camera
        stopCamera();
        
        // Switch facing mode
        currentFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
        
        // Show loading state
        const switchBtn = document.getElementById('switchCameraBtn');
        if (switchBtn) {
            switchBtn.textContent = '🔄 Đang chuyển...';
            switchBtn.disabled = true;
        }
        
        // Open camera with new facing mode
        await openCamera();
        
        // Update button text and re-enable
        if (switchBtn) {
            switchBtn.textContent = currentFacingMode === 'environment' ? '🤳 Camera trước' : '📷 Camera sau';
            switchBtn.disabled = false;
        }
        
        const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        if (isMobile) {
            showAlert('✅ Đã chuyển camera!', 'success');
        }
        
        console.log(`Switched to ${currentFacingMode === 'environment' ? 'back' : 'front'} camera`);
        
    } catch (error) {
        console.error('Error switching camera:', error);
        
        // Reset button state
        const switchBtn = document.getElementById('switchCameraBtn');
        if (switchBtn) {
            switchBtn.textContent = '🔄 Đổi camera';
            switchBtn.disabled = false;
        }
        
        showAlert('❌ Không thể chuyển đổi camera. Vui lòng thử lại.', 'error');
    }
}

// Update submit button state
function updateSubmitButtonState() {
    const submitBtn = document.getElementById('submitBtn');
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
    
    const submitBtn = document.getElementById('submitBtn');
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
            // Check if response is a redirect to success page
            if (response.redirected && response.url.includes('/success/')) {
                window.location.href = response.url;
            } else {
                // Try to parse JSON response
                try {
                    const result = await response.json();
                    if (result.success && result.redirect_url) {
                        window.location.href = result.redirect_url;
                    } else if (result.success) {
                        showAlert('Check-in thành công!', 'success');
                        // Reset form
                        resetForm();
                    } else {
                        showAlert(result.message || 'Có lỗi xảy ra', 'error');
                    }
                } catch (e) {
                    // If not JSON, check if it's HTML (success page)
                    const text = await response.text();
                    if (text.includes('Check-in Thành công') || text.includes('success')) {
                        // This is the success page, redirect to it
                        window.location.href = '/success/';
                    } else {
                        showAlert('Check-in thành công!', 'success');
                        resetForm();
                    }
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

// Test GPS permission
async function testGpsPermission() {
    const statusElement = document.getElementById('gps-status');
    const btn = document.getElementById('testGpsBtn');
    
    if (statusElement) statusElement.textContent = 'Đang kiểm tra...';
    if (btn) btn.disabled = true;
    
    try {
        // Check secure context
        const isSecureContext = window.isSecureContext || location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.hostname === 'reco.local';
        
        if (!isSecureContext) {
            if (statusElement) {
                statusElement.textContent = 'Không bảo mật';
                statusElement.className = 'permission-status denied';
            }
            showAlert('⚠️ GPS cần HTTPS hoặc localhost để hoạt động', 'warning');
            return;
        }
        
        if (!navigator.geolocation) {
            if (statusElement) {
                statusElement.textContent = 'Không hỗ trợ';
                statusElement.className = 'permission-status denied';
            }
            return;
        }
        
        // Try to trigger permission request directly
        navigator.geolocation.getCurrentPosition(
            () => {
                if (statusElement) {
                    statusElement.textContent = '✅ Đã cho phép';
                    statusElement.className = 'permission-status granted';
                }
                showAlert('✅ GPS đã được cấp quyền!', 'success');
            },
            (error) => {
                if (statusElement) {
                    statusElement.textContent = '❌ Bị từ chối';
                    statusElement.className = 'permission-status denied';
                }
                
                let message = '❌ GPS bị từ chối';
                if (error.code === error.PERMISSION_DENIED) {
                    message += '\n\n📋 Cách sửa:\n1️⃣ Nhấp 🔒 bên trái thanh địa chỉ\n2️⃣ Chọn "Vị trí" → "Cho phép"\n3️⃣ Tải lại trang';
                }
                showAlert(message, 'error');
            },
            { timeout: 5000 }
        );
        
    } catch (error) {
        console.error('Error testing GPS:', error);
        if (statusElement) {
            statusElement.textContent = '❌ Lỗi';
            statusElement.className = 'permission-status denied';
        }
    } finally {
        if (btn) btn.disabled = false;
    }
}

// Test Camera permission
async function testCameraPermission() {
    const statusElement = document.getElementById('camera-status');
    const btn = document.getElementById('testCameraBtn');
    
    if (statusElement) statusElement.textContent = 'Đang kiểm tra...';
    if (btn) btn.disabled = true;
    
    try {
        // Check secure context
        const isSecureContext = window.isSecureContext || location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.hostname === 'reco.local';
        
        if (!isSecureContext) {
            if (statusElement) {
                statusElement.textContent = 'Không bảo mật';
                statusElement.className = 'permission-status denied';
            }
            showAlert('⚠️ Camera cần HTTPS hoặc localhost để hoạt động', 'warning');
            return;
        }
        
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            if (statusElement) {
                statusElement.textContent = 'Không hỗ trợ';
                statusElement.className = 'permission-status denied';
            }
            return;
        }
        
        // Try to trigger permission request directly
        try {
            const testStream = await navigator.mediaDevices.getUserMedia({ video: true });
            testStream.getTracks().forEach(track => track.stop()); // Stop immediately
            
            if (statusElement) {
                statusElement.textContent = '✅ Đã cho phép';
                statusElement.className = 'permission-status granted';
            }
            showAlert('✅ Camera đã được cấp quyền!', 'success');
        } catch (streamError) {
            if (statusElement) {
                statusElement.textContent = '❌ Bị từ chối';
                statusElement.className = 'permission-status denied';
            }
            
            let message = '❌ Camera bị từ chối';
            if (streamError.name === 'NotAllowedError') {
                message += '\n\n📋 Cách sửa:\n1️⃣ Nhấp 🔒 bên trái thanh địa chỉ\n2️⃣ Chọn "Camera" → "Cho phép"\n3️⃣ Tải lại trang';
            }
            showAlert(message, 'error');
        }
        
    } catch (error) {
        console.error('Error testing camera:', error);
        if (statusElement) {
            statusElement.textContent = '❌ Lỗi';
            statusElement.className = 'permission-status denied';
        }
    } finally {
        if (btn) btn.disabled = false;
    }
}


// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopCamera();
});
