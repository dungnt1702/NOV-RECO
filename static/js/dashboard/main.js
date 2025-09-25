// Dashboard Main JavaScript
let attendanceChart = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard Main loaded');
    
    // Initialize dashboard
    initializeDashboard();
    
    // Setup real-time updates
    setupRealTimeUpdates();
    
    // Setup interactive elements
    setupInteractiveElements();
    
    // Initialize charts
    initializeCharts();
});

function initializeDashboard() {
    // Add loading states to cards
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach(card => {
        card.classList.add('loading');
    });
    
    // Remove loading states after a short delay
    setTimeout(() => {
        cards.forEach(card => {
            card.classList.remove('loading');
        });
    }, 500);
}

function setupRealTimeUpdates() {
    // Update stats every 30 seconds
    setInterval(updateStats, 30000);
    
    // Update activity every 60 seconds
    setInterval(updateActivity, 60000);
}

function setupInteractiveElements() {
    // Add hover effects to stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add click effects to action buttons
    const actionBtns = document.querySelectorAll('.action-btn');
    actionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

function initializeCharts() {
    // Initialize attendance chart
    createAttendanceChart();
    
    // Add color coding to stat cards
    addColorCodingToStats();
}

function createAttendanceChart() {
    const ctx = document.getElementById('attendanceChart');
    if (!ctx) return;
    
    // Sample data - in real implementation, this would come from API
    const chartData = {
        labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
        datasets: [{
            label: 'Check-in tuần này',
            data: [12, 19, 15, 25, 22, 8, 3],
            borderColor: 'rgb(102, 126, 234)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: 'rgb(102, 126, 234)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
        }]
    };
    
    const config = {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgb(102, 126, 234)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#718096',
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(113, 128, 150, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#718096',
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    },
                    beginAtZero: true
                }
            },
            elements: {
                point: {
                    hoverBackgroundColor: 'rgb(102, 126, 234)'
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };
    
    attendanceChart = new Chart(ctx, config);
}

function addColorCodingToStats() {
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        const valueElement = card.querySelector('h3');
        if (valueElement) {
            const value = parseInt(valueElement.textContent);
            
            // Remove existing classes
            card.classList.remove('high-value', 'medium-value', 'low-value');
            
            // Add appropriate class based on value
            if (value >= 20) {
                card.classList.add('high-value');
            } else if (value >= 10) {
                card.classList.add('medium-value');
            } else {
                card.classList.add('low-value');
            }
        }
    });
}

function updateStats() {
    // Fetch updated stats from API
    fetch('/dashboard/api/stats/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatCards(data.stats);
            }
        })
        .catch(error => {
            console.error('Error updating stats:', error);
        });
}

function updateStatCards(stats) {
    // Update today checkins
    const todayCheckins = document.querySelector('.stat-card:nth-child(1) h3');
    if (todayCheckins) {
        animateNumber(todayCheckins, stats.today_checkins);
    }
    
    // Update week checkins
    const weekCheckins = document.querySelector('.stat-card:nth-child(2) h3');
    if (weekCheckins) {
        animateNumber(weekCheckins, stats.week_checkins);
    }
    
    // Update month checkins
    const monthCheckins = document.querySelector('.stat-card:nth-child(3) h3');
    if (monthCheckins) {
        animateNumber(monthCheckins, stats.month_checkins);
    }
    
    // Update total employees (if exists)
    const totalEmployees = document.querySelector('.stat-card:nth-child(4) h3');
    if (totalEmployees && stats.total_employees) {
        animateNumber(totalEmployees, stats.total_employees);
    }
}

function updateActivity() {
    // Fetch updated activity from API
    fetch('/dashboard/api/activity/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateActivityList(data.activities);
            }
        })
        .catch(error => {
            console.error('Error updating activity:', error);
        });
}

function updateActivityList(activities) {
    const activityList = document.querySelector('.activity-list');
    if (!activityList) return;
    
    // Clear existing activities
    activityList.innerHTML = '';
    
    if (activities.length === 0) {
        activityList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>Chưa có hoạt động nào</p>
            </div>
        `;
        return;
    }
    
    // Add new activities
    activities.forEach(activity => {
        const activityItem = createActivityItem(activity);
        activityList.appendChild(activityItem);
    });
}

function createActivityItem(activity) {
    const item = document.createElement('div');
    item.classList.add('activity-item');
    
    if (activity.type === 'checkin') {
        item.innerHTML = `
            <div class="activity-avatar">
                ${activity.user.avatar ? 
                    `<img src="${activity.user.avatar}" alt="${activity.user.name}">` :
                    activity.user.name.charAt(0).toUpperCase()
                }
            </div>
            <div class="activity-content">
                <p><strong>${activity.user.name}</strong> đã check-in tại <strong>${activity.area.name}</strong></p>
                <span class="activity-time">${activity.time_ago}</span>
            </div>
        `;
    } else {
        item.innerHTML = `
            <div class="activity-icon">
                <i class="fas fa-map-marker-alt"></i>
            </div>
            <div class="activity-content">
                <p>Check-in tại <strong>${activity.area.name}</strong></p>
                <span class="activity-time">${activity.time_ago}</span>
            </div>
        `;
    }
    
    return item;
}

function animateNumber(element, newValue) {
    const currentValue = parseInt(element.textContent);
    const increment = (newValue - currentValue) / 20;
    let current = currentValue;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= newValue) || (increment < 0 && current <= newValue)) {
            current = newValue;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 50);
}

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .dashboard-card.loading {
        opacity: 0.7;
        pointer-events: none;
    }
    
    .dashboard-card.loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin: -10px 0 0 -10px;
        border: 2px solid #667eea;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
`;
document.head.appendChild(style);
