// Check-in Success Page JavaScript
// This file handles data and UI for checkin success page

// ===== DATA HANDLING =====

// Global variable to store checkin success data
window.checkinSuccessData = null;

// Function to get checkin success data from data attributes
function getCheckinSuccessDataFromAttributes() {
    const container = document.querySelector('.checkin-success-page');
    if (!container) {
        return getDefaultCheckinSuccessData();
    }
    
    return {
        userName: container.dataset.userName || 'N/A',
        userEmail: container.dataset.userEmail || 'N/A',
        userDepartment: container.dataset.userDepartment || 'N/A',
        userEmployeeId: container.dataset.userEmployeeId || 'N/A',
        locationName: container.dataset.locationName || 'N/A',
        coordinates: container.dataset.coordinates || 'N/A',
        checkinTime: container.dataset.checkinTime || 'N/A',
        note: container.dataset.note || '',
        photoUrl: container.dataset.photoUrl || ''
    };
}

// Function to get default checkin success data
function getDefaultCheckinSuccessData() {
    return {
        userName: 'N/A',
        userEmail: 'N/A',
        userDepartment: 'N/A',
        userEmployeeId: 'N/A',
        locationName: 'N/A',
        coordinates: 'N/A',
        checkinTime: 'N/A',
        note: '',
        photoUrl: ''
    };
}

// Function to get checkin success data with fallback
function getCheckinSuccessData() {
    // Try to get from data attributes first
    const dataFromAttributes = getCheckinSuccessDataFromAttributes();
    
    // If we have valid data from attributes, use it
    if (dataFromAttributes.userName !== 'N/A' || dataFromAttributes.userEmployeeId !== 'N/A') {
        return dataFromAttributes;
    }
    
    // Fallback to global variable or default
    return window.checkinSuccessData || getDefaultCheckinSuccessData();
}

// ===== UI FUNCTIONS =====

// Get check-in data from template context (passed from Django view)
function getCheckinData() {
    return getCheckinSuccessData();
}

// Display check-in data
function displayCheckinData() {
    const data = getCheckinData();
    
    const elUserName = document.getElementById('userName');
    const elUserEmail = document.getElementById('userEmail');
    const elUserDept = document.getElementById('userDepartment');
    const elUserEmpId = document.getElementById('userEmployeeId');
    const elLocationName = document.getElementById('locationName');
    const elCoordinates = document.getElementById('coordinates');
    const elCheckinTime = document.getElementById('checkinTime');

    if (elUserName) elUserName.textContent = data.userName;
    if (elUserEmail) elUserEmail.textContent = data.userEmail;
    if (elUserDept) elUserDept.textContent = data.userDepartment;
    if (elUserEmpId) elUserEmpId.textContent = data.userEmployeeId;
    if (elLocationName) elLocationName.textContent = data.locationName;
    if (elCoordinates) elCoordinates.textContent = data.coordinates;
    if (elCheckinTime) elCheckinTime.textContent = data.checkinTime;
    
    // Show note if exists
    if (data.note && data.note.trim() !== '') {
        const elNote = document.getElementById('note');
        if (elNote) elNote.textContent = data.note;
    }
    
    // Show photo if exists
    if (data.photoUrl && data.photoUrl.trim() !== '') {
        const img = document.querySelector('.checkin-photo');
        if (img) img.src = data.photoUrl;
    }
}

// Quick check-in function
function quickCheckin() {
    // Get current check-in data from URL
    const data = getUrlParams();
    
    // Redirect to quick check-in with current data
    const quickData = {
        lat: data.coordinates.split(',')[0]?.trim() || '',
        lng: data.coordinates.split(',')[1]?.trim() || '',
        location_name: data.locationName,
        note: data.note
    };
    
    const params = new URLSearchParams(quickData);
    window.location.href = `/action/?${params.toString()}`;
}

// View history function
function viewHistory() {
    window.location.href = '/history/';
}

// Go to dashboard function
function goToDashboard() {
    window.location.href = '/dashboard/';
}

// Print check-in details
function printCheckin() {
    window.print();
}

// Share check-in (copy to clipboard)
function shareCheckin() {
    const data = getUrlParams();
    const shareText = `Check-in thành công!\nNgười dùng: ${data.userName}\nĐịa điểm: ${data.locationName}\nThời gian: ${data.checkinTime}\nTọa độ: ${data.coordinates}`;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareText).then(() => {
            alert('Đã copy thông tin check-in vào clipboard!');
        }).catch(err => {
            console.error('Copy failed:', err);
            alert('Không thể copy thông tin');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = shareText;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            alert('Đã copy thông tin check-in vào clipboard!');
        } catch (err) {
            alert('Không thể copy thông tin');
        }
        document.body.removeChild(textArea);
    }
}

// ===== INITIALIZATION =====

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Canonicalize URL: if query param exists, redirect to pretty URL once
    const params = new URLSearchParams(window.location.search);
    const qId = params.get('checkin_id');
    if (qId) {
        const pretty = `/checkin/success/checkin_id/${qId}/`;
        if (window.location.pathname !== pretty) {
            window.location.replace(pretty);
            return; // Stop further execution; page will reload at pretty URL
        }
    }

    displayCheckinData();
    
    // Add event listeners for action buttons
    const quickCheckinBtn = document.getElementById('quick-checkin-btn');
    const historyBtn = document.getElementById('history-btn');
    const dashboardBtn = document.getElementById('dashboard-btn');
    const printBtn = document.getElementById('print-btn');
    const shareBtn = document.getElementById('share-btn');
    
    if (quickCheckinBtn) quickCheckinBtn.addEventListener('click', quickCheckin);
    if (historyBtn) historyBtn.addEventListener('click', viewHistory);
    if (dashboardBtn) dashboardBtn.addEventListener('click', goToDashboard);
    if (printBtn) printBtn.addEventListener('click', printCheckin);
    if (shareBtn) shareBtn.addEventListener('click', shareCheckin);
    
    // Initialize overlay and share features
    initializeOverlayFeatures();
});

// ===== OVERLAY AND SHARE FUNCTIONALITY =====

// Global variables for overlay
let overlayCanvas = null;
let overlayCtx = null;
let originalImage = null;
let overlayImageData = null;

// Function to initialize overlay functionality
function initializeOverlayFeatures() {
    const downloadBtn = document.getElementById('downloadBtn');
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadOverlayImage);
    }
    
    // Initialize share buttons
    initializeShareButtons();
    
    // Automatically create overlay when page loads
    setTimeout(() => {
        addOverlayToImage();
    }, 500); // Small delay to ensure image is loaded
}

// Function to add overlay to image
function addOverlayToImage() {
    const originalPhoto = document.getElementById('originalPhoto');
    const overlayPreview = document.getElementById('overlayPreview');
    
    if (!originalPhoto || !overlayPreview) {
        console.error('Required elements not found');
        return;
    }
    
    // Show overlay preview (original photo will be updated with overlay)
    overlayPreview.style.display = 'block';
    
    // Create canvas
    overlayCanvas = document.getElementById('overlayCanvas');
    if (!overlayCanvas) {
        console.error('Canvas not found');
        return;
    }
    
    overlayCtx = overlayCanvas.getContext('2d');
    
    // Load and draw image with overlay
    originalImage = new Image();
    originalImage.crossOrigin = 'anonymous';
    
    originalImage.onload = function() {
        // Set canvas size to match image - maintain aspect ratio
        const maxWidth = 400;
        const maxHeight = 600;
        let { width, height } = originalImage;
        
        // Calculate aspect ratio and resize if needed
        if (width > maxWidth || height > maxHeight) {
            const ratio = Math.min(maxWidth / width, maxHeight / height);
            width *= ratio;
            height *= ratio;
        }
        
        // Set canvas size to maintain aspect ratio
        overlayCanvas.width = width;
        overlayCanvas.height = height;
        
        // Clear canvas and set background
        overlayCtx.clearRect(0, 0, width, height);
        
        // Draw original image with proper scaling
        overlayCtx.drawImage(originalImage, 0, 0, width, height);
        
        // Add overlay text
        addOverlayText(width, height);
        
        // Store image data for sharing - this is the final image with overlay
        overlayImageData = overlayCanvas.toDataURL('image/jpeg', 0.9);
        
        // Show the final image with overlay
        const finalImage = document.getElementById('finalImage');
        if (finalImage) {
            finalImage.src = overlayImageData;
            finalImage.style.display = 'block';
        }
        
        // Hide canvas and show final image
        overlayCanvas.style.display = 'none';
    };
    
    originalImage.onerror = function() {
        console.error('Failed to load image');
        // Fallback: show original image
        originalPhoto.style.display = 'block';
        overlayPreview.style.display = 'none';
    };
    
    originalImage.src = originalPhoto.src;
}

// Function to add overlay text
function addOverlayText(canvasWidth, canvasHeight) {
    if (!overlayCtx) return;
    
    // Get data from page elements
    const userName = document.getElementById('userName')?.textContent || 'N/A';
    const locationName = document.getElementById('locationName')?.textContent || 'N/A';
    const address = document.getElementById('address')?.textContent || 'N/A';
    const checkinTime = document.getElementById('checkinTime')?.textContent || 'N/A';
    
    // Compact overlay in bottom right corner - smaller and closer to edge
    const overlayWidth = Math.min(200, canvasWidth * 0.5);
    const overlayHeight = 80;
    const margin = 8; // Closer to edge
    const x = canvasWidth - overlayWidth - margin;
    const y = canvasHeight - overlayHeight - margin;
    
    // Background with white color
    overlayCtx.fillStyle = 'rgba(255, 255, 255, 0.9)'; // White with slight transparency
    overlayCtx.fillRect(x, y, overlayWidth, overlayHeight);
    
    // Text properties - black text for better contrast
    overlayCtx.fillStyle = '#000000';
    overlayCtx.textAlign = 'left';
    overlayCtx.textBaseline = 'top';
    
    // Calculate available space for text
    const padding = 8;
    const availableWidth = overlayWidth - (padding * 2);
    const availableHeight = overlayHeight - (padding * 2);
    
    // Prepare text lines
    const textLines = [
        'NOV-RECO',
        userName,
        locationName,
        address.length > 25 ? address.substring(0, 22) + '...' : address,
        checkinTime
    ];
    
    // Calculate optimal font size to fit all text
    let fontSize = Math.max(8, Math.min(12, availableWidth / 15));
    let lineHeight = fontSize + 2;
    let totalTextHeight = (textLines.length * lineHeight) - 2; // -2 for last line
    
    // Adjust font size if text doesn't fit
    while (totalTextHeight > availableHeight && fontSize > 6) {
        fontSize -= 0.5;
        lineHeight = fontSize + 2;
        totalTextHeight = (textLines.length * lineHeight) - 2;
    }
    
    // Draw text
    let textY = y + padding;
    const textX = x + padding;
    
    textLines.forEach((line, index) => {
        if (index === 0) {
            // Title with bold font
            overlayCtx.font = `bold ${fontSize}px Arial, sans-serif`;
        } else {
            // Regular text
            overlayCtx.font = `${fontSize}px Arial, sans-serif`;
        }
        
        // Truncate text if too long for available width
        let displayText = line;
        const maxChars = Math.floor(availableWidth / (fontSize * 0.6));
        if (displayText.length > maxChars) {
            displayText = displayText.substring(0, maxChars - 3) + '...';
        }
        
        overlayCtx.fillText(displayText, textX, textY);
        textY += lineHeight;
    });
}

// Function to download overlay image
function downloadOverlayImage() {
    if (!overlayImageData) {
        console.error('No overlay image data available');
        return;
    }
    
    const userEmployeeId = document.getElementById('userEmployeeId')?.textContent || 'unknown';
    const link = document.createElement('a');
    link.download = `checkin_${userEmployeeId}_${new Date().getTime()}.jpg`;
    link.href = overlayImageData;
    link.click();
}

// Function to initialize share buttons
function initializeShareButtons() {
    const shareFacebook = document.getElementById('shareFacebook');
    const shareZalo = document.getElementById('shareZalo');
    const shareWhatsApp = document.getElementById('shareWhatsApp');
    const shareTelegram = document.getElementById('shareTelegram');
    const copyLink = document.getElementById('copyLink');
    const toggleShareBtn = document.getElementById('toggleShareBtn');
    const shareButtons = document.getElementById('shareButtons');
    const shareToggleIcon = document.getElementById('shareToggleIcon');
    
    // Toggle share buttons
    if (toggleShareBtn && shareButtons && shareToggleIcon) {
        toggleShareBtn.addEventListener('click', () => {
            const isVisible = shareButtons.style.display !== 'none';
            
            if (isVisible) {
                shareButtons.style.display = 'none';
                shareToggleIcon.classList.remove('rotated');
            } else {
                shareButtons.style.display = 'flex';
                shareToggleIcon.classList.add('rotated');
            }
        });
    }
    
    if (shareFacebook) {
        shareFacebook.addEventListener('click', () => shareToFacebook());
    }
    
    if (shareZalo) {
        shareZalo.addEventListener('click', () => shareToZalo());
    }
    
    if (shareWhatsApp) {
        shareWhatsApp.addEventListener('click', () => shareToWhatsApp());
    }
    
    if (shareTelegram) {
        shareTelegram.addEventListener('click', () => shareToTelegram());
    }
    
    if (copyLink) {
        copyLink.addEventListener('click', () => copyImageLink());
    }
}

// Share functions
function shareToFacebook() {
    if (!overlayImageData) {
        alert('Vui lòng tạo ảnh overlay trước khi chia sẻ');
        return;
    }
    
    const locationName = document.getElementById('locationName')?.textContent || 'NOV-RECO';
    const text = `Tôi vừa check-in tại ${locationName} - NOV-RECO`;
    const url = encodeURIComponent(window.location.href);
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${encodeURIComponent(text)}`;
    
    window.open(facebookUrl, '_blank', 'width=600,height=400');
}

function shareToZalo() {
    if (!overlayImageData) {
        alert('Vui lòng tạo ảnh overlay trước khi chia sẻ');
        return;
    }
    
    const locationName = document.getElementById('locationName')?.textContent || 'NOV-RECO';
    const text = `Tôi vừa check-in tại ${locationName} - NOV-RECO`;
    const url = encodeURIComponent(window.location.href);
    const zaloUrl = `https://zalo.me/pc?url=${url}&text=${encodeURIComponent(text)}`;
    
    window.open(zaloUrl, '_blank', 'width=600,height=400');
}

function shareToWhatsApp() {
    if (!overlayImageData) {
        alert('Vui lòng tạo ảnh overlay trước khi chia sẻ');
        return;
    }
    
    const locationName = document.getElementById('locationName')?.textContent || 'NOV-RECO';
    const text = `Tôi vừa check-in tại ${locationName} - NOV-RECO\n${window.location.href}`;
    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(text)}`;
    
    window.open(whatsappUrl, '_blank');
}

function shareToTelegram() {
    if (!overlayImageData) {
        alert('Vui lòng tạo ảnh overlay trước khi chia sẻ');
        return;
    }
    
    const locationName = document.getElementById('locationName')?.textContent || 'NOV-RECO';
    const text = `Tôi vừa check-in tại ${locationName} - NOV-RECO`;
    const url = encodeURIComponent(window.location.href);
    const telegramUrl = `https://t.me/share/url?url=${url}&text=${encodeURIComponent(text)}`;
    
    window.open(telegramUrl, '_blank');
}

function copyImageLink() {
    if (!overlayImageData) {
        alert('Vui lòng tạo ảnh overlay trước khi copy link');
        return;
    }
    
    // Create a blob from the image data
    const byteString = atob(overlayImageData.split(',')[1]);
    const mimeString = overlayImageData.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    
    const blob = new Blob([ab], { type: mimeString });
    const url = URL.createObjectURL(blob);
    
    // Copy to clipboard
    navigator.clipboard.writeText(url).then(() => {
        alert('Link ảnh đã được copy vào clipboard!');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Link ảnh đã được copy vào clipboard!');
    });
}