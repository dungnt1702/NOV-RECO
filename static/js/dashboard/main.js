// Dashboard Main JavaScript
let attendanceChart = null;
let isMobile = window.innerWidth <= 768;
let updateInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard Main loaded');
    
    // Initialize dashboard
    initializeDashboard();
    
    // Setup real-time updates (only on desktop)
    if (!isMobile) {
        setupRealTimeUpdates();
    }
    
    // Setup interactive elements
    setupInteractiveElements();
    
    // Initialize charts
    initializeCharts();
    
    // Setup mobile-specific optimizations
    if (isMobile) {
        setupMobileOptimizations();
    }
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
    // Update stats every 30 seconds (desktop only)
    updateInterval = setInterval(updateStats, 30000);
    
    // Update activity every 60 seconds (desktop only)
    setInterval(updateActivity, 60000);
}

function setupMobileOptimizations() {
    // Disable real-time updates on mobile to save battery
    console.log('Mobile optimizations enabled');
    
    // Add intersection observer for lazy loading
    setupLazyLoading();
    
    // Optimize chart rendering for mobile
    optimizeChartsForMobile();
    
    // Add performance monitoring
    monitorPerformance();
}

function setupLazyLoading() {
    // Only load charts when they come into view
    const chartContainer = document.querySelector('.charts-container');
    if (chartContainer) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Chart is visible, ensure it's rendered
                    if (attendanceChart) {
                        attendanceChart.resize();
                    }
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(chartContainer);
    }
}

function optimizeChartsForMobile() {
    // Reduce chart complexity on mobile
    if (attendanceChart && isMobile) {
        attendanceChart.options.animation.duration = 0; // Disable animations
        attendanceChart.options.responsive = true;
        attendanceChart.options.maintainAspectRatio = false;
        attendanceChart.update();
    }
}

function monitorPerformance() {
    // Monitor performance and adjust accordingly
    let frameCount = 0;
    let lastTime = performance.now();
    
    function measureFPS() {
        frameCount++;
        const currentTime = performance.now();
        
        if (currentTime - lastTime >= 1000) {
            const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
            
            if (fps < 30) {
                // Low FPS detected, reduce animations
                document.body.classList.add('low-performance');
            } else {
                document.body.classList.remove('low-performance');
            }
            
            frameCount = 0;
            lastTime = currentTime;
        }
        
        requestAnimationFrame(measureFPS);
    }
    
    requestAnimationFrame(measureFPS);
}

function setupInteractiveElements() {
    // Add hover effects to stat cards (desktop only)
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (window.innerWidth > 768) {
                this.style.transform = 'translateY(-5px)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            if (window.innerWidth > 768) {
                this.style.transform = 'translateY(0)';
            }
        });
        
        // Touch interactions for mobile
        card.addEventListener('touchstart', function(e) {
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        card.addEventListener('touchend', function(e) {
            this.style.transform = 'scale(1)';
            this.style.transition = 'transform 0.2s ease';
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
        
        // Touch interactions for mobile
        btn.addEventListener('touchstart', function(e) {
            this.style.transform = 'scale(0.95)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        btn.addEventListener('touchend', function(e) {
            this.style.transform = 'scale(1)';
            this.style.transition = 'transform 0.2s ease';
        });
    });
    
    // Add touch interactions to dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    dashboardCards.forEach(card => {
        card.addEventListener('touchstart', function(e) {
            this.style.transform = 'scale(0.99)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        card.addEventListener('touchend', function(e) {
            this.style.transform = 'scale(1)';
            this.style.transition = 'transform 0.2s ease';
        });
    });
}

function initializeCharts() {
    // Initialize attendance chart
    createAttendanceChart();
    
    // Add color coding to stat cards
    addColorCodingToStats();
    
    // Setup swipe gestures for mobile
    setupSwipeGestures();
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

function setupSwipeGestures() {
    // Only setup swipe gestures on mobile devices
    if (window.innerWidth > 768) return;
    
    let startX = 0;
    let startY = 0;
    let endX = 0;
    let endY = 0;
    
    // Add swipe gesture to stats grid
    const statsGrid = document.querySelector('.stats-grid');
    if (statsGrid) {
        statsGrid.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        statsGrid.addEventListener('touchend', function(e) {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // Check if it's a horizontal swipe
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Swipe left - could be used for next stats view
                    console.log('Swipe left detected');
                } else {
                    // Swipe right - could be used for previous stats view
                    console.log('Swipe right detected');
                }
            }
        });
    }
    
    // Add swipe gesture to activity list
    const activityList = document.querySelector('.activity-list');
    if (activityList) {
        activityList.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        activityList.addEventListener('touchend', function(e) {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // Check if it's a vertical swipe
            if (Math.abs(diffY) > Math.abs(diffX) && Math.abs(diffY) > 50) {
                if (diffY > 0) {
                    // Swipe up - refresh activity
                    refreshActivity();
                } else {
                    // Swipe down - could be used for pull to refresh
                    console.log('Swipe down detected - pull to refresh');
                }
            }
        });
    }
    
    // Add swipe gesture to charts
    const chartContainer = document.querySelector('.charts-container');
    if (chartContainer) {
        chartContainer.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        chartContainer.addEventListener('touchend', function(e) {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // Check if it's a horizontal swipe
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Swipe left - next chart
                    switchToNextChart();
                } else {
                    // Swipe right - previous chart
                    switchToPreviousChart();
                }
            }
        });
    }
}

function refreshActivity() {
    // Add visual feedback
    const activityList = document.querySelector('.activity-list');
    if (activityList) {
        activityList.style.transform = 'translateY(10px)';
        activityList.style.opacity = '0.7';
        
        setTimeout(() => {
            activityList.style.transform = 'translateY(0)';
            activityList.style.opacity = '1';
        }, 300);
    }
    
    // Refresh activity data
    updateActivity();
}

function switchToNextChart() {
    // Add visual feedback
    const chartContainer = document.querySelector('.charts-container');
    if (chartContainer) {
        chartContainer.style.transform = 'translateX(-10px)';
        chartContainer.style.opacity = '0.7';
        
        setTimeout(() => {
            chartContainer.style.transform = 'translateX(0)';
            chartContainer.style.opacity = '1';
        }, 300);
    }
    
    // Switch to next chart (placeholder for future implementation)
    console.log('Switching to next chart');
}

function switchToPreviousChart() {
    // Add visual feedback
    const chartContainer = document.querySelector('.charts-container');
    if (chartContainer) {
        chartContainer.style.transform = 'translateX(10px)';
        chartContainer.style.opacity = '0.7';
        
        setTimeout(() => {
            chartContainer.style.transform = 'translateX(0)';
            chartContainer.style.opacity = '1';
        }, 300);
    }
    
    // Switch to previous chart (placeholder for future implementation)
    console.log('Switching to previous chart');
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
