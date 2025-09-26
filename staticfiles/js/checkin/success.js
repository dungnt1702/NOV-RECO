// Check-in success page JavaScript

// Get check-in data from template context (passed from Django view)
function getCheckinData() {
  // Data is now passed via template context, not URL parameters
  return window.checkinSuccessData || {
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
});
