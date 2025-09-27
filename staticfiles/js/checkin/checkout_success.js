// Checkout Success Page JavaScript
// This file handles data and UI for checkout success page

// ===== DATA HANDLING =====

// Global variable to store checkout success data
window.checkoutSuccessData = null;

// Function to get checkout success data from data attributes
function getCheckoutSuccessDataFromAttributes() {
    const container = document.querySelector('.checkin-success-page');
    if (!container) {
        return getDefaultCheckoutSuccessData();
    }
    
    return {
        userName: container.dataset.userName || 'N/A',
        userEmail: container.dataset.userEmail || 'N/A',
        userDepartment: container.dataset.userDepartment || 'N/A',
        userEmployeeId: container.dataset.userEmployeeId || 'N/A',
        locationName: container.dataset.locationName || 'N/A',
        coordinates: container.dataset.coordinates || 'N/A',
        checkoutTime: container.dataset.checkoutTime || 'N/A',
        note: container.dataset.note || '',
        photoUrl: container.dataset.photoUrl || '',
        checkinId: container.dataset.checkinId || 'N/A',
        checkoutId: container.dataset.checkoutId || 'N/A'
    };
}

// Function to get default checkout success data
function getDefaultCheckoutSuccessData() {
    return {
        userName: 'N/A',
        userEmail: 'N/A',
        userDepartment: 'N/A',
        userEmployeeId: 'N/A',
        locationName: 'N/A',
        coordinates: 'N/A',
        checkoutTime: 'N/A',
        note: '',
        photoUrl: '',
        checkinId: 'N/A',
        checkoutId: 'N/A'
    };
}

// Function to get checkout success data with fallback
function getCheckoutSuccessData() {
    // Try to get from data attributes first
    const dataFromAttributes = getCheckoutSuccessDataFromAttributes();
    
    // If we have valid data from attributes, use it
    if (dataFromAttributes.userName !== 'N/A' || dataFromAttributes.userEmployeeId !== 'N/A') {
        return dataFromAttributes;
    }
    
    // Fallback to global variable or default
    return window.checkoutSuccessData || getDefaultCheckoutSuccessData();
}

// ===== UI FUNCTIONS =====

// Get checkout data from template context (passed from Django view)
function getCheckoutData() {
    return getCheckoutSuccessData();
}

// Display checkout data
function displayCheckoutData() {
    const data = getCheckoutData();
    
    const elUserName = document.getElementById('userName');
    const elUserEmail = document.getElementById('userEmail');
    const elUserDept = document.getElementById('userDepartment');
    const elUserEmpId = document.getElementById('userEmployeeId');
    const elLocationName = document.getElementById('locationName');
    const elCoordinates = document.getElementById('coordinates');
    const elCheckoutTime = document.getElementById('checkoutTime');
    const elCheckinId = document.getElementById('checkinId');
    const elCheckoutId = document.getElementById('checkoutId');

    if (elUserName) elUserName.textContent = data.userName;
    if (elUserEmail) elUserEmail.textContent = data.userEmail;
    if (elUserDept) elUserDept.textContent = data.userDepartment;
    if (elUserEmpId) elUserEmpId.textContent = data.userEmployeeId;
    if (elLocationName) elLocationName.textContent = data.locationName;
    if (elCoordinates) elCoordinates.textContent = data.coordinates;
    if (elCheckoutTime) elCheckoutTime.textContent = data.checkoutTime;
    if (elCheckinId) elCheckinId.textContent = data.checkinId;
    if (elCheckoutId) elCheckoutId.textContent = data.checkoutId;
    
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

// Quick checkout function
function quickCheckout() {
    window.location.href = '/checkin/checkout/';
}

// View checkout history function
function viewCheckoutHistory() {
    window.location.href = '/checkin/checkout/history/';
}

// Go to dashboard function
function goToDashboard() {
    window.location.href = '/dashboard/';
}

// Print checkout details
function printCheckout() {
    window.print();
}

// Share checkout (copy to clipboard)
function shareCheckout() {
    const data = getCheckoutData();
    const shareText = `Check-out thành công!\nNgười dùng: ${data.userName}\nĐịa điểm: ${data.locationName}\nThời gian: ${data.checkoutTime}\nTọa độ: ${data.coordinates}\nCheck-in ID: ${data.checkinId}\nCheck-out ID: ${data.checkoutId}`;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareText).then(() => {
            alert('Đã copy thông tin check-out vào clipboard!');
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
            alert('Đã copy thông tin check-out vào clipboard!');
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
    const qId = params.get('checkout_id');
    if (qId) {
        const pretty = `/checkin/checkout/success/checkout_id/${qId}/`;
        if (window.location.pathname !== pretty) {
            window.location.replace(pretty);
            return; // Stop further execution; page will reload at pretty URL
        }
    }

    displayCheckoutData();
    
    // Add event listeners for action buttons
    const quickCheckoutBtn = document.getElementById('quick-checkout-btn');
    const historyBtn = document.getElementById('history-btn');
    const dashboardBtn = document.getElementById('dashboard-btn');
    const printBtn = document.getElementById('print-btn');
    const shareBtn = document.getElementById('share-btn');
    
    if (quickCheckoutBtn) quickCheckoutBtn.addEventListener('click', quickCheckout);
    if (historyBtn) historyBtn.addEventListener('click', viewCheckoutHistory);
    if (dashboardBtn) dashboardBtn.addEventListener('click', goToDashboard);
    if (printBtn) printBtn.addEventListener('click', printCheckout);
    if (shareBtn) shareBtn.addEventListener('click', shareCheckout);
});