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
  
  document.getElementById('user-name').textContent = data.userName;
  document.getElementById('user-email').textContent = data.userEmail;
  document.getElementById('user-department').textContent = data.userDepartment;
  document.getElementById('user-employee-id').textContent = data.userEmployeeId;
  document.getElementById('location-name').textContent = data.locationName;
  document.getElementById('coordinates').textContent = data.coordinates;
  document.getElementById('checkin-time').textContent = data.checkinTime;
  
  // Show note if exists
  if (data.note && data.note.trim() !== '') {
    document.getElementById('note-text').textContent = data.note;
    document.getElementById('note-item').style.display = 'flex';
  }
  
  // Show photo if exists
  if (data.photoUrl && data.photoUrl.trim() !== '') {
    document.getElementById('photo-preview').src = data.photoUrl;
    document.getElementById('photo-container').style.display = 'block';
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
