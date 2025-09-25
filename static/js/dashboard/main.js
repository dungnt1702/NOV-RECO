// Dashboard Main JavaScript
let attendanceChart = null;
let departmentChart = null;
let timeChart = null;
let mainChart = null;
let isMobile = window.innerWidth <= 768;

// Update mobile detection on resize
window.addEventListener('resize', function() {
    isMobile = window.innerWidth <= 768;
});
let updateInterval = null;
let currentChartType = 'attendance';
let currentDateRange = '7';
let websocket = null;
let reconnectAttempts = 0;
let maxReconnectAttempts = 5;
let testData = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard Main loaded');
    
    // Initialize test data
    initializeTestData();
    
    // Initialize dashboard
    initializeDashboard();
    
    // Setup real-time updates (disabled for now)
    // if (!isMobile) {
    //     setupRealTimeUpdates();
    //     setupWebSocketConnection();
    // }
    
    // Setup interactive elements
    setupInteractiveElements();
    
    // Initialize charts
    initializeCharts();
    
    // Setup mobile-specific optimizations
    if (isMobile) {
        setupMobileOptimizations();
    }
});

function initializeTestData() {
    // Initialize test data if available
    if (window.DashboardTestData) {
        testData = window.DashboardTestData.exportAllData();
        console.log('Test data initialized:', testData);
    } else {
        console.warn('Test data not available, using fallback data');
        testData = generateFallbackData();
    }
}

function generateFallbackData() {
    return {
        users: [
            { id: 1, full_name: 'Admin User', role: 'admin', department: 'IT' },
            { id: 2, full_name: 'Manager User', role: 'manager', department: 'Sales' },
            { id: 3, full_name: 'Employee User', role: 'employee', department: 'Tech' }
        ],
        checkins: [
            { id: 1, user_name: 'Admin User', area_name: 'Văn phòng chính', checkin_type: 'check-in', created_at: new Date().toISOString() },
            { id: 2, user_name: 'Manager User', area_name: 'Khu vực A', checkin_type: 'check-out', created_at: new Date().toISOString() }
        ],
        dashboard_stats: {
            today_checkins: 15,
            week_checkins: 85,
            month_checkins: 320,
            total_employees: 25,
            total_areas: 4
        }
    };
}

function initializeDashboard() {
    // Add loading states to cards
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach(card => {
        card.classList.add('loading');
    });
    
    // Load real data
    loadDashboardData();
    
    // Remove loading states after a short delay
    setTimeout(() => {
        cards.forEach(card => {
            card.classList.remove('loading');
        });
    }, 500);
}

function loadDashboardData() {
    if (!testData) return;
    
    // Update stat cards with real data
    updateStatCards(testData.dashboard_stats);
    
    // Update activity list
    updateActivityList(testData.checkins.slice(0, 5));
    
    // Update department stats if available
    if (testData.departments) {
        updateDepartmentStats(testData.departments);
    }
}

function updateStatCards(stats) {
    // Update today check-ins
    const todayCheckins = document.querySelector('.stat-card:nth-child(1) h3');
    if (todayCheckins) {
        todayCheckins.textContent = stats.today_checkins || 0;
    }
    
    // Update week check-ins
    const weekCheckins = document.querySelector('.stat-card:nth-child(2) h3');
    if (weekCheckins) {
        weekCheckins.textContent = stats.week_checkins || 0;
    }
    
    // Update month check-ins
    const monthCheckins = document.querySelector('.stat-card:nth-child(3) h3');
    if (monthCheckins) {
        monthCheckins.textContent = stats.month_checkins || 0;
    }
    
    // Update total employees
    const totalEmployees = document.querySelector('.stat-card:nth-child(4) h3');
    if (totalEmployees) {
        totalEmployees.textContent = stats.total_employees || 0;
    }
    
    // Update total areas
    const totalAreas = document.querySelector('.stat-card:nth-child(5) h3');
    if (totalAreas) {
        totalAreas.textContent = stats.total_areas || 0;
    }
}

function updateActivityList(activities) {
    const activityList = document.querySelector('.activity-list');
    if (!activityList || !activities) return;
    
    activityList.innerHTML = '';
    
    activities.forEach(activity => {
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div class="activity-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="activity-content">
                <p><strong>${activity.user_name}</strong> đã ${activity.checkin_type} tại <strong>${activity.area_name}</strong></p>
                <span class="activity-time">${formatDateTime(activity.created_at)}</span>
            </div>
            <div class="activity-icon">
                <i class="fas fa-${activity.checkin_type === 'check-in' ? 'sign-in-alt' : 'sign-out-alt'}"></i>
            </div>
        `;
        activityList.appendChild(activityItem);
    });
}

function updateDepartmentStats(departments) {
    const departmentList = document.querySelector('.department-list');
    if (!departmentList || !departments) return;
    
    departmentList.innerHTML = '';
    
    departments.slice(0, 5).forEach(dept => {
        const deptItem = document.createElement('div');
        deptItem.className = 'department-item';
        deptItem.innerHTML = `
            <div class="department-info">
                <h4>${dept.name}</h4>
                <p>${dept.office}</p>
            </div>
            <div class="department-count">
                <span class="count">${dept.employee_count}</span>
                <span class="label">nhân viên</span>
            </div>
        `;
        departmentList.appendChild(deptItem);
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

function setupRealTimeUpdates() {
    // Update stats every 30 seconds (desktop only)
    updateInterval = setInterval(updateStats, 30000);
    
    // Update activity every 60 seconds (desktop only)
    setInterval(updateActivity, 60000);
}

function setupWebSocketConnection() {
    // Check if WebSocket is supported
    if (!window.WebSocket) {
        console.log('WebSocket not supported, falling back to polling');
        setupWebSocketSimulation();
        return;
    }
    
    // Connect to WebSocket
    connectWebSocket();
}

function setupWebSocketSimulation() {
    // Simulate WebSocket connection for testing
    console.log('Setting up WebSocket simulation for testing');
    
    // Simulate connection after 2 seconds
    setTimeout(() => {
        showConnectionStatus('connected');
        
        // Simulate periodic updates
        setInterval(() => {
            if (testData && testData.realtime_data) {
                const realtimeData = testData.realtime_data;
                
                // Randomly send different types of updates
                const updateTypes = ['stats_update', 'activity_update', 'checkin_alert', 'notification'];
                const randomType = updateTypes[Math.floor(Math.random() * updateTypes.length)];
                
                switch (randomType) {
                    case 'stats_update':
                        handleWebSocketMessage(realtimeData.stats_update);
                        break;
                    case 'activity_update':
                        handleWebSocketMessage(realtimeData.activity_update);
                        break;
                    case 'checkin_alert':
                        handleWebSocketMessage(realtimeData.checkin_alert);
                        break;
                    case 'notification':
                        handleWebSocketMessage(realtimeData.notification);
                        break;
                }
            }
        }, 30000); // Every 30 seconds
        
    }, 2000);
}

function connectWebSocket() {
    try {
        // Use wss:// for production, ws:// for development
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/dashboard/`;
        
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = function(event) {
            console.log('WebSocket connected');
            reconnectAttempts = 0;
            showConnectionStatus('connected');
        };
        
        websocket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        websocket.onclose = function(event) {
            console.log('WebSocket disconnected');
            showConnectionStatus('disconnected');
            
            // Attempt to reconnect
            if (reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                console.log(`Attempting to reconnect... (${reconnectAttempts}/${maxReconnectAttempts})`);
                setTimeout(connectWebSocket, 5000 * reconnectAttempts);
            } else {
                console.log('Max reconnection attempts reached, falling back to polling');
                showConnectionStatus('failed');
            }
        };
        
        websocket.onerror = function(error) {
            console.error('WebSocket error:', error);
            showConnectionStatus('error');
        };
        
    } catch (error) {
        console.error('Error setting up WebSocket:', error);
        showConnectionStatus('error');
    }
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'stats_update':
            updateStatsFromWebSocket(data.data);
            break;
        case 'activity_update':
            updateActivityFromWebSocket(data.data);
            break;
        case 'checkin_alert':
            showCheckinAlert(data.data);
            break;
        case 'notification':
            showDashboardNotification(data.data);
            break;
        default:
            console.log('Unknown WebSocket message type:', data.type);
    }
}

function updateStatsFromWebSocket(stats) {
    // Update stat cards with new data
    updateStatCards(stats);
    
    // Update charts if needed
    if (mainChart) {
        updateMainChart();
    }
}

function updateActivityFromWebSocket(activities) {
    // Update activity list with new data
    updateActivityList(activities);
}

function showCheckinAlert(checkinData) {
    // Show real-time check-in alert
    const alert = document.createElement('div');
    alert.className = 'checkin-alert';
    alert.innerHTML = `
        <div class="alert-content">
            <div class="alert-icon">
                <i class="fas fa-map-marker-alt"></i>
            </div>
            <div class="alert-text">
                <strong>${checkinData.user_name}</strong> vừa check-in tại <strong>${checkinData.area_name}</strong>
            </div>
            <button class="alert-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add styles
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        max-width: 300px;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 300);
        }
    }, 5000);
}

function showDashboardNotification(notification) {
    // Show dashboard-specific notification
    const notificationEl = document.createElement('div');
    notificationEl.className = 'dashboard-notification';
    notificationEl.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">
                <i class="fas fa-${notification.icon || 'bell'}"></i>
            </div>
            <div class="notification-text">
                <strong>${notification.title}</strong>
                <p>${notification.message}</p>
            </div>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add styles
    notificationEl.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: white;
        color: #2d3748;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        max-width: 350px;
        border-left: 4px solid ${notification.color || '#667eea'};
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notificationEl);
    
    // Auto remove after 8 seconds
    setTimeout(() => {
        if (notificationEl.parentElement) {
            notificationEl.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notificationEl.parentElement) {
                    notificationEl.remove();
                }
            }, 300);
        }
    }, 8000);
}

function showConnectionStatus(status) {
    // Remove existing status indicator
    const existingStatus = document.getElementById('connection-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    // Create status indicator
    const statusEl = document.createElement('div');
    statusEl.id = 'connection-status';
    statusEl.className = `connection-status ${status}`;
    
    let statusText, statusIcon, statusColor;
    
    switch (status) {
        case 'connected':
            statusText = 'Kết nối real-time';
            statusIcon = 'fas fa-wifi';
            statusColor = '#48bb78';
            break;
        case 'disconnected':
            statusText = 'Mất kết nối';
            statusIcon = 'fas fa-wifi-slash';
            statusColor = '#ed8936';
            break;
        case 'failed':
            statusText = 'Chế độ offline';
            statusIcon = 'fas fa-exclamation-triangle';
            statusColor = '#e53e3e';
            break;
        case 'error':
            statusText = 'Lỗi kết nối';
            statusIcon = 'fas fa-times-circle';
            statusColor = '#e53e3e';
            break;
    }
    
    statusEl.innerHTML = `
        <i class="${statusIcon}"></i>
        <span>${statusText}</span>
    `;
    
    // Add styles
    statusEl.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${statusColor};
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: slideInUp 0.3s ease;
    `;
    
    document.body.appendChild(statusEl);
    
    // Auto remove after 3 seconds for connected status
    if (status === 'connected') {
        setTimeout(() => {
            if (statusEl.parentElement) {
                statusEl.style.animation = 'slideOutDown 0.3s ease';
                setTimeout(() => {
                    if (statusEl.parentElement) {
                        statusEl.remove();
                    }
                }, 300);
            }
        }, 3000);
    }
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
    console.log('Initializing charts...');
    
    // Wait a bit for Chart.js to be fully loaded
    setTimeout(() => {
        console.log('Chart.js version:', Chart.version);
        console.log('Chart.js available:', typeof Chart);
        
        // Initialize main chart
        createMainChart();
        
        // Initialize additional charts
        console.log('Creating department chart...');
        createDepartmentChart();
        
        console.log('Creating time chart...');
        createTimeChart();
        
        console.log('Charts initialization completed');
        
        // Check if charts were created successfully
        setTimeout(() => {
            console.log('Department chart after creation:', departmentChart);
            console.log('Time chart after creation:', timeChart);
            
            // Check if charts are visible
            const deptCanvas = document.getElementById('departmentChart');
            const timeCanvas = document.getElementById('timeChart');
            
            if (deptCanvas) {
                console.log('Department canvas visible:', deptCanvas.offsetWidth, 'x', deptCanvas.offsetHeight);
                console.log('Department canvas style:', window.getComputedStyle(deptCanvas).display);
            }
            
            if (timeCanvas) {
                console.log('Time canvas visible:', timeCanvas.offsetWidth, 'x', timeCanvas.offsetHeight);
                console.log('Time canvas style:', window.getComputedStyle(timeCanvas).display);
            }
        }, 500);
    }, 100);
    
    // Add color coding to stat cards
    addColorCodingToStats();
    
    // Setup chart controls
    setupChartControls();
    
    // Setup export functionality
    setupExportFunctionality();
    
    // Setup customization system
    setupCustomizationSystem();
    
    // Setup module integration
    setupModuleIntegration();
    
    // Setup swipe gestures for mobile
    setupSwipeGestures();
}

function createMainChart() {
    const ctx = document.getElementById('mainChart');
    if (!ctx) return;
    
    // Create main chart based on current type
    updateMainChart();
}

function updateMainChart() {
    const ctx = document.getElementById('mainChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (mainChart) {
        mainChart.destroy();
    }
    
    let chartData, chartConfig;
    
    switch (currentChartType) {
        case 'attendance':
            chartData = getAttendanceData();
            chartConfig = getAttendanceConfig();
            break;
        case 'department':
            chartData = getDepartmentData();
            chartConfig = getDepartmentConfig();
            break;
        case 'time':
            chartData = getTimeData();
            chartConfig = getTimeConfig();
            break;
        default:
            chartData = getAttendanceData();
            chartConfig = getAttendanceConfig();
    }
    
    const config = {
        ...chartConfig,
        data: chartData
    };
    
    mainChart = new Chart(ctx, config);
    updateChartLegend(chartData);
}

function getAttendanceData() {
    const days = getDateRangeLabels();
    return {
        labels: days,
        datasets: [{
            label: 'Check-in',
            data: generateAttendanceData(days.length),
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
}

function getDepartmentData() {
    return {
        labels: ['Kỹ thuật', 'Kinh doanh', 'Nhân sự', 'Kế toán', 'Marketing'],
        datasets: [{
            label: 'Số lượng check-in',
            data: [45, 38, 42, 35, 28],
            backgroundColor: [
                'rgba(102, 126, 234, 0.8)',
                'rgba(240, 147, 251, 0.8)',
                'rgba(79, 172, 254, 0.8)',
                'rgba(67, 233, 123, 0.8)',
                'rgba(255, 159, 64, 0.8)'
            ],
            borderColor: [
                'rgb(102, 126, 234)',
                'rgb(240, 147, 251)',
                'rgb(79, 172, 254)',
                'rgb(67, 233, 123)',
                'rgb(255, 159, 64)'
            ],
            borderWidth: 2
        }]
    };
}

function getTimeData() {
    return {
        labels: ['6h-8h', '8h-10h', '10h-12h', '12h-14h', '14h-16h', '16h-18h', '18h-20h'],
        datasets: [{
            label: 'Check-in theo giờ',
            data: [5, 25, 15, 8, 20, 18, 3],
            borderColor: 'rgb(67, 233, 123)',
            backgroundColor: 'rgba(67, 233, 123, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: 'rgb(67, 233, 123)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
        }]
    };
}

function getAttendanceConfig() {
    return {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 1,
            layout: {
                padding: {
                    top: 20,
                    bottom: 20,
                    left: 20,
                    right: 20
                }
            },
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
}

function getDepartmentConfig() {
    return {
        type: 'bar',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 1,
            layout: {
                padding: {
                    top: 20,
                    bottom: 20,
                    left: 20,
                    right: 20
                }
            },
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
            }
        }
    };
}

function getTimeConfig() {
    return {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 1,
            layout: {
                padding: {
                    top: 20,
                    bottom: 20,
                    left: 20,
                    right: 20
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgb(67, 233, 123)',
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
                    hoverBackgroundColor: 'rgb(67, 233, 123)'
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };
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

function setupChartControls() {
    const chartTypeSelect = document.getElementById('chartType');
    const dateRangeSelect = document.getElementById('dateRange');
    
    if (chartTypeSelect) {
        chartTypeSelect.addEventListener('change', function() {
            currentChartType = this.value;
            updateMainChart();
        });
    }
    
    if (dateRangeSelect) {
        dateRangeSelect.addEventListener('change', function() {
            currentDateRange = this.value;
            updateMainChart();
        });
    }
}

function getDateRangeLabels() {
    const days = parseInt(currentDateRange);
    const labels = [];
    const today = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('vi-VN', { weekday: 'short', month: 'short', day: 'numeric' }));
    }
    
    return labels;
}

function generateAttendanceData(length) {
    const data = [];
    for (let i = 0; i < length; i++) {
        data.push(Math.floor(Math.random() * 30) + 10);
    }
    return data;
}

function updateChartLegend(chartData) {
    const legendContainer = document.getElementById('chartLegend');
    if (!legendContainer) return;
    
    legendContainer.innerHTML = '';
    
    if (chartData.datasets) {
        chartData.datasets.forEach((dataset, index) => {
            const legendItem = document.createElement('div');
            legendItem.className = 'legend-item';
            
            const color = dataset.borderColor || dataset.backgroundColor;
            legendItem.innerHTML = `
                <div class="legend-color" style="background-color: ${color}"></div>
                <span>${dataset.label}</span>
            `;
            
            legendContainer.appendChild(legendItem);
        });
    }
}

function createDepartmentChart() {
    const ctx = document.getElementById('departmentChart');
    if (!ctx) {
        console.log('departmentChart canvas not found');
        return;
    }
    console.log('Creating department chart...');
    console.log('Canvas element:', ctx);
    console.log('Canvas dimensions:', ctx.width, 'x', ctx.height);
    
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }
    
    // Check if canvas is ready
    if (!ctx.getContext) {
        console.error('Canvas getContext not available');
        return;
    }
    
    const canvasContext = ctx.getContext('2d');
    if (!canvasContext) {
        console.error('Cannot get 2D context from canvas');
        return;
    }
    
    // Get real data from test data or use fallback
    let chartData;
    if (window.DashboardTestData && window.DashboardTestData.exportAllData) {
        const data = window.DashboardTestData.exportAllData();
        if (data.departments && Array.isArray(data.departments)) {
            chartData = data.departments.map(dept => ({
                label: dept.name,
                value: dept.employee_count
            }));
        } else {
            chartData = [
                { label: 'Kỹ thuật', value: 35 },
                { label: 'Kinh doanh', value: 28 },
                { label: 'Nhân sự', value: 22 },
                { label: 'Kế toán', value: 15 }
            ];
        }
    } else {
        chartData = [
            { label: 'Kỹ thuật', value: 35 },
            { label: 'Kinh doanh', value: 28 },
            { label: 'Nhân sự', value: 22 },
            { label: 'Kế toán', value: 15 }
        ];
    }
    
    // Ensure chartData is valid
    if (!chartData || !Array.isArray(chartData) || chartData.length === 0) {
        console.log('Using fallback data for department chart');
        chartData = [
            { label: 'Kỹ thuật', value: 35 },
            { label: 'Kinh doanh', value: 28 },
            { label: 'Nhân sự', value: 22 },
            { label: 'Kế toán', value: 15 }
        ];
    }
    
    console.log('Department chart data:', chartData);
    const total = chartData.reduce((sum, item) => sum + item.value, 0);
    
    const data = {
        labels: chartData.map(item => item.label),
        datasets: [{
            data: chartData.map(item => item.value),
            backgroundColor: [
                'rgba(102, 126, 234, 0.8)',
                'rgba(240, 147, 251, 0.8)',
                'rgba(79, 172, 254, 0.8)',
                'rgba(67, 233, 123, 0.8)',
                'rgba(255, 193, 7, 0.8)',
                'rgba(220, 53, 69, 0.8)'
            ],
            borderColor: [
                'rgb(102, 126, 234)',
                'rgb(240, 147, 251)',
                'rgb(79, 172, 254)',
                'rgb(67, 233, 123)',
                'rgb(255, 193, 7)',
                'rgb(220, 53, 69)'
            ],
            borderWidth: 2
        }]
    };
    
    const config = {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 1,
            layout: {
                padding: {
                    top: 20,
                    bottom: 20,
                    left: 20,
                    right: 20
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: '500'
                        },
                        boxWidth: 14,
                        boxHeight: 14,
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return {
                                        text: `${label}: ${value} (${percentage}%)`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: data.datasets[0].borderColor[i],
                                        lineWidth: 2,
                                        pointStyle: 'circle',
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgb(102, 126, 234)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${value} nhân viên (${percentage}%)`;
                        }
                    }
                }
            },
            elements: {
                arc: {
                    borderWidth: 2
                }
            }
        }
    };
    
    try {
        departmentChart = new Chart(ctx, config);
        console.log('Department chart created successfully');
        console.log('Department chart instance:', departmentChart);
    } catch (error) {
        console.error('Error creating department chart:', error);
        console.error('Chart config:', config);
    }
}

function createTimeChart() {
    const ctx = document.getElementById('timeChart');
    if (!ctx) {
        console.log('timeChart canvas not found');
        return;
    }
    console.log('Creating time chart...');
    console.log('Canvas element:', ctx);
    console.log('Canvas dimensions:', ctx.width, 'x', ctx.height);
    
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }
    
    // Check if canvas is ready
    if (!ctx.getContext) {
        console.error('Canvas getContext not available');
        return;
    }
    
    const canvasContext = ctx.getContext('2d');
    if (!canvasContext) {
        console.error('Cannot get 2D context from canvas');
        return;
    }
    
    // Get real data or use fallback
    let chartData;
    if (window.DashboardTestData && window.DashboardTestData.exportAllData) {
        const data = window.DashboardTestData.exportAllData();
        if (data.chart_data && data.chart_data.time) {
            chartData = data.chart_data.time;
        } else {
            chartData = {
                labels: ['Sáng sớm (6-9h)', 'Buổi sáng (9-12h)', 'Buổi chiều (12-17h)', 'Buổi tối (17-22h)', 'Đêm (22-6h)'],
                data: [45, 120, 85, 30, 15]
            };
        }
    } else {
        chartData = {
            labels: ['Sáng sớm (6-9h)', 'Buổi sáng (9-12h)', 'Buổi chiều (12-17h)', 'Buổi tối (17-22h)', 'Đêm (22-6h)'],
            data: [45, 120, 85, 30, 15]
        };
    }
    
    // Ensure chartData has the correct structure
    if (!chartData || !chartData.labels || !chartData.data) {
        console.log('Using fallback data for time chart');
        chartData = {
            labels: ['Sáng sớm (6-9h)', 'Buổi sáng (9-12h)', 'Buổi chiều (12-17h)', 'Buổi tối (17-22h)', 'Đêm (22-6h)'],
            data: [45, 120, 85, 30, 15]
        };
    }
    
    console.log('Time chart data:', chartData);
    const total = chartData.data.reduce((sum, value) => sum + value, 0);
    
    const data = {
        labels: chartData.labels,
        datasets: [{
            data: chartData.data,
            backgroundColor: [
                'rgba(67, 233, 123, 0.8)',
                'rgba(79, 172, 254, 0.8)',
                'rgba(240, 147, 251, 0.8)',
                'rgba(255, 193, 7, 0.8)',
                'rgba(220, 53, 69, 0.8)'
            ],
            borderColor: [
                'rgb(67, 233, 123)',
                'rgb(79, 172, 254)',
                'rgb(240, 147, 251)',
                'rgb(255, 193, 7)',
                'rgb(220, 53, 69)'
            ],
            borderWidth: 2
        }]
    };
    
    const config = {
        type: 'pie',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 1,
            layout: {
                padding: {
                    top: 20,
                    bottom: 20,
                    left: 20,
                    right: 20
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 11,
                            weight: '500'
                        },
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return {
                                        text: `${label}: ${value} (${percentage}%)`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: data.datasets[0].borderColor[i],
                                        lineWidth: 2,
                                        pointStyle: 'circle',
                                        hidden: false,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgb(67, 233, 123)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${value} lượt (${percentage}%)`;
                        }
                    }
                }
            },
            elements: {
                arc: {
                    borderWidth: 2
                }
            }
        }
    };
    
    try {
        timeChart = new Chart(ctx, config);
        console.log('Time chart created successfully');
        console.log('Time chart instance:', timeChart);
    } catch (error) {
        console.error('Error creating time chart:', error);
        console.error('Chart config:', config);
    }
}

function setupExportFunctionality() {
    // PDF Export
    const exportPDFBtn = document.getElementById('exportPDF');
    if (exportPDFBtn) {
        exportPDFBtn.addEventListener('click', function() {
            exportToPDF();
        });
    }
    
    // Excel Export
    const exportExcelBtn = document.getElementById('exportExcel');
    if (exportExcelBtn) {
        exportExcelBtn.addEventListener('click', function() {
            exportToExcel();
        });
    }
    
    // Image Export
    const exportImageBtn = document.getElementById('exportImage');
    if (exportImageBtn) {
        exportImageBtn.addEventListener('click', function() {
            exportToImage();
        });
    }
}

async function exportToPDF() {
    // Show loading state
    showExportLoading('PDF');
    
    try {
        // Create new PDF document
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('p', 'mm', 'a4');
        
        // Add company header
        doc.setFontSize(20);
        doc.setFont('helvetica', 'bold');
        doc.text('NOV-RECO Dashboard Report', 20, 20);
        
        // Add report info
        doc.setFontSize(12);
        doc.setFont('helvetica', 'normal');
        doc.text(`Generated on: ${new Date().toLocaleDateString('vi-VN')}`, 20, 30);
        doc.text(`User: ${document.querySelector('.page-title h1')?.textContent || 'Dashboard User'}`, 20, 35);
        
        // Add stats summary
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Dashboard Summary', 20, 50);
        
        // Get stats data
        const stats = getDashboardStats();
        let yPos = 60;
        
        stats.forEach((stat, index) => {
            doc.setFontSize(10);
            doc.setFont('helvetica', 'normal');
            doc.text(`${stat.label}: ${stat.value}`, 20, yPos);
            yPos += 6;
        });
        
        // Add charts
        yPos += 10;
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Charts & Analytics', 20, yPos);
        
        // Capture and add charts
        const charts = [mainChart, departmentChart, timeChart];
        for (let i = 0; i < charts.length; i++) {
            if (charts[i] && charts[i].canvas) {
                yPos += 10;
                if (yPos > 250) {
                    doc.addPage();
                    yPos = 20;
                }
                
                const chartDataURL = charts[i].canvas.toDataURL('image/png');
                doc.addImage(chartDataURL, 'PNG', 20, yPos, 160, 80);
                yPos += 90;
            }
        }
        
        // Add detailed data table
        yPos += 10;
        if (yPos > 200) {
            doc.addPage();
            yPos = 20;
        }
        
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('Detailed Data', 20, yPos);
        
        // Add check-in data table
        const checkinData = getCheckinData();
        yPos += 10;
        
        // Table headers
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.text('Date', 20, yPos);
        doc.text('Check-ins', 60, yPos);
        doc.text('Department', 100, yPos);
        doc.text('Time', 150, yPos);
        yPos += 5;
        
        // Table data
        doc.setFont('helvetica', 'normal');
        checkinData.slice(0, 20).forEach(row => {
            if (yPos > 280) {
                doc.addPage();
                yPos = 20;
            }
            doc.text(row.date, 20, yPos);
            doc.text(row.checkins.toString(), 60, yPos);
            doc.text(row.department, 100, yPos);
            doc.text(row.time, 150, yPos);
            yPos += 5;
        });
        
        // Save PDF
        doc.save(`dashboard-report-${new Date().toISOString().split('T')[0]}.pdf`);
        
        hideExportLoading();
        showExportSuccess('PDF');
    } catch (error) {
        console.error('PDF export error:', error);
        hideExportLoading();
        showExportError('PDF');
    }
}

async function exportToExcel() {
    // Show loading state
    showExportLoading('Excel');
    
    try {
        // Create new workbook
        const wb = XLSX.utils.book_new();
        
        // Sheet 1: Dashboard Summary
        const summaryData = [
            ['NOV-RECO Dashboard Report'],
            [`Generated on: ${new Date().toLocaleDateString('vi-VN')}`],
            [`User: ${document.querySelector('.page-title h1')?.textContent || 'Dashboard User'}`],
            [''],
            ['Dashboard Summary'],
            ['Metric', 'Value', 'Description'],
            ...getDashboardStats().map(stat => [stat.label, stat.value, stat.description || ''])
        ];
        
        const ws1 = XLSX.utils.aoa_to_sheet(summaryData);
        ws1['!cols'] = [{ width: 20 }, { width: 15 }, { width: 30 }];
        XLSX.utils.book_append_sheet(wb, ws1, 'Summary');
        
        // Sheet 2: Check-in Data
        const checkinData = getCheckinData();
        const checkinHeaders = ['Date', 'Check-ins', 'Department', 'Time', 'Area', 'User Count'];
        const checkinSheetData = [checkinHeaders, ...checkinData];
        
        const ws2 = XLSX.utils.aoa_to_sheet(checkinSheetData);
        ws2['!cols'] = [
            { width: 12 }, { width: 12 }, { width: 15 }, 
            { width: 10 }, { width: 15 }, { width: 12 }
        ];
        XLSX.utils.book_append_sheet(wb, ws2, 'Check-in Data');
        
        // Sheet 3: Department Statistics
        const deptData = getDepartmentData();
        const deptHeaders = ['Department', 'Employee Count', 'Office', 'Manager', 'Check-ins Today', 'Check-ins This Week'];
        const deptSheetData = [deptHeaders, ...deptData];
        
        const ws3 = XLSX.utils.aoa_to_sheet(deptSheetData);
        ws3['!cols'] = [
            { width: 20 }, { width: 15 }, { width: 15 }, 
            { width: 20 }, { width: 15 }, { width: 15 }
        ];
        XLSX.utils.book_append_sheet(wb, ws3, 'Department Stats');
        
        // Sheet 4: Time Analytics
        const timeData = getTimeAnalytics();
        const timeHeaders = ['Time Period', 'Check-ins', 'Percentage', 'Trend'];
        const timeSheetData = [timeHeaders, ...timeData];
        
        const ws4 = XLSX.utils.aoa_to_sheet(timeSheetData);
        ws4['!cols'] = [
            { width: 20 }, { width: 15 }, { width: 15 }, { width: 10 }
        ];
        XLSX.utils.book_append_sheet(wb, ws4, 'Time Analytics');
        
        // Sheet 5: Recent Activity
        const activityData = getActivityData();
        const activityHeaders = ['Time', 'User', 'Action', 'Location', 'Type'];
        const activitySheetData = [activityHeaders, ...activityData];
        
        const ws5 = XLSX.utils.aoa_to_sheet(activitySheetData);
        ws5['!cols'] = [
            { width: 20 }, { width: 20 }, { width: 15 }, { width: 20 }, { width: 10 }
        ];
        XLSX.utils.book_append_sheet(wb, ws5, 'Recent Activity');
        
        // Add charts as images (if possible)
        try {
            const chartImages = await captureChartsAsImages();
            if (chartImages.length > 0) {
                // Create a sheet for chart images
                const chartSheetData = [
                    ['Dashboard Charts'],
                    ['Chart Type', 'Description', 'Image Reference'],
                    ['Attendance Trend', 'Daily check-in trends over time', 'Chart1'],
                    ['Department Distribution', 'Employee distribution by department', 'Chart2'],
                    ['Time Analysis', 'Check-in patterns by time of day', 'Chart3']
                ];
                
                const ws6 = XLSX.utils.aoa_to_sheet(chartSheetData);
                ws6['!cols'] = [{ width: 25 }, { width: 40 }, { width: 20 }];
                XLSX.utils.book_append_sheet(wb, ws6, 'Charts');
            }
        } catch (error) {
            console.log('Chart capture not available:', error);
        }
        
        // Save Excel file
        XLSX.writeFile(wb, `dashboard-report-${new Date().toISOString().split('T')[0]}.xlsx`);
        
        hideExportLoading();
        showExportSuccess('Excel');
    } catch (error) {
        console.error('Excel export error:', error);
        hideExportLoading();
        showExportError('Excel');
    }
}

async function exportToImage() {
    // Show loading state
    showExportLoading('Image');
    
    try {
        // Capture all charts as high-resolution images
        const charts = [mainChart, departmentChart, timeChart];
        const chartNames = ['Attendance Trend', 'Department Distribution', 'Time Analysis'];
        const images = [];
        
        for (let i = 0; i < charts.length; i++) {
            if (charts[i] && charts[i].canvas) {
                // Set high DPI for better quality
                const canvas = charts[i].canvas;
                const originalWidth = canvas.width;
                const originalHeight = canvas.height;
                
                // Create high-resolution canvas
                const highResCanvas = document.createElement('canvas');
                const ctx = highResCanvas.getContext('2d');
                const scale = 2; // 2x resolution
                
                highResCanvas.width = originalWidth * scale;
                highResCanvas.height = originalHeight * scale;
                
                // Scale the context
                ctx.scale(scale, scale);
                
                // Draw the chart with high resolution
                ctx.drawImage(canvas, 0, 0);
                
                // Convert to image
                const imageData = highResCanvas.toDataURL('image/png', 1.0);
                images.push({
                    data: imageData,
                    name: chartNames[i],
                    filename: `dashboard-${chartNames[i].toLowerCase().replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.png`
                });
            }
        }
        
        // Download each chart as separate image
        images.forEach((image, index) => {
            const element = document.createElement('a');
            element.href = image.data;
            element.download = image.filename;
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        });
        
        // Also create a combined dashboard screenshot
        try {
            const dashboardElement = document.querySelector('.dashboard-main');
            if (dashboardElement) {
                const canvas = await html2canvas(dashboardElement, {
                    scale: 2,
                    useCORS: true,
                    allowTaint: true,
                    backgroundColor: '#ffffff',
                    width: dashboardElement.scrollWidth,
                    height: dashboardElement.scrollHeight
                });
                
                const combinedImage = canvas.toDataURL('image/png', 1.0);
                const element = document.createElement('a');
                element.href = combinedImage;
                element.download = `dashboard-complete-${new Date().toISOString().split('T')[0]}.png`;
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
            }
        } catch (error) {
            console.log('Combined screenshot not available:', error);
        }
        
        hideExportLoading();
        showExportSuccess('Image');
    } catch (error) {
        console.error('Image export error:', error);
        hideExportLoading();
        showExportError('Image');
    }
}

// Helper functions for data extraction
function getDashboardStats() {
    const stats = [];
    
    // Get stats from DOM elements
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        const value = card.querySelector('.stat-content h3')?.textContent || '0';
        const label = card.querySelector('.stat-content p')?.textContent || 'Unknown';
        stats.push({
            label: label,
            value: value,
            description: `Current ${label.toLowerCase()} value`
        });
    });
    
    return stats;
}

function getCheckinData() {
    // Get data from test data or generate sample data
    if (window.DashboardTestData && window.DashboardTestData.exportAllData) {
        const data = window.DashboardTestData.exportAllData();
        return data.checkins.map(checkin => [
            new Date(checkin.created_at).toLocaleDateString('vi-VN'),
            Math.floor(Math.random() * 50) + 10, // Simulated check-in count
            checkin.area_name || 'Unknown Area',
            new Date(checkin.created_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
            checkin.area_name || 'Unknown Area',
            Math.floor(Math.random() * 20) + 5 // Simulated user count
        ]);
    }
    
    // Fallback sample data
    const sampleData = [];
    for (let i = 0; i < 30; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        sampleData.push([
            date.toLocaleDateString('vi-VN'),
            Math.floor(Math.random() * 50) + 10,
            ['Kỹ thuật', 'Kinh doanh', 'Nhân sự', 'Kế toán'][Math.floor(Math.random() * 4)],
            `${String(Math.floor(Math.random() * 3) + 8).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
            ['Main Office', 'Branch A', 'Warehouse'][Math.floor(Math.random() * 3)],
            Math.floor(Math.random() * 20) + 5
        ]);
    }
    return sampleData;
}

function getDepartmentData() {
    if (window.DashboardTestData && window.DashboardTestData.exportAllData) {
        const data = window.DashboardTestData.exportAllData();
        return data.departments.map(dept => [
            dept.name,
            dept.employee_count,
            dept.office,
            dept.manager,
            Math.floor(Math.random() * 20) + 5, // Today's check-ins
            Math.floor(Math.random() * 100) + 20 // This week's check-ins
        ]);
    }
    
    // Fallback sample data
    return [
        ['Kỹ thuật', 25, 'Main Office', 'Nguyễn Văn A', 18, 85],
        ['Kinh doanh', 20, 'Main Office', 'Trần Thị B', 15, 70],
        ['Nhân sự', 12, 'Branch A', 'Lê Văn C', 10, 45],
        ['Kế toán', 15, 'Main Office', 'Phạm Thị D', 12, 55],
        ['Marketing', 18, 'Branch A', 'Hoàng Văn E', 14, 65]
    ];
}

function getTimeAnalytics() {
    const timePeriods = [
        'Sáng sớm (6-9h)',
        'Buổi sáng (9-12h)', 
        'Buổi chiều (12-17h)',
        'Buổi tối (17-22h)',
        'Đêm (22-6h)'
    ];
    
    const totalCheckins = 1000; // Simulated total
    
    return timePeriods.map(period => {
        const checkins = Math.floor(Math.random() * 200) + 50;
        const percentage = ((checkins / totalCheckins) * 100).toFixed(1);
        const trend = Math.random() > 0.5 ? '↗' : '↘';
        
        return [period, checkins, `${percentage}%`, trend];
    });
}

function getActivityData() {
    if (window.DashboardTestData && window.DashboardTestData.exportAllData) {
        const data = window.DashboardTestData.exportAllData();
        return data.checkins.slice(0, 50).map(checkin => [
            new Date(checkin.created_at).toLocaleString('vi-VN'),
            checkin.user_name,
            checkin.checkin_type === 'check-in' ? 'Check-in' : 'Check-out',
            checkin.area_name,
            checkin.checkin_type
        ]);
    }
    
    // Fallback sample data
    const activities = [];
    for (let i = 0; i < 30; i++) {
        const time = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000);
        activities.push([
            time.toLocaleString('vi-VN'),
            `User ${Math.floor(Math.random() * 20) + 1}`,
            Math.random() > 0.5 ? 'Check-in' : 'Check-out',
            ['Main Office', 'Branch A', 'Warehouse'][Math.floor(Math.random() * 3)],
            Math.random() > 0.5 ? 'check-in' : 'check-out'
        ]);
    }
    return activities;
}

async function captureChartsAsImages() {
    const charts = [mainChart, departmentChart, timeChart];
    const images = [];
    
    for (let i = 0; i < charts.length; i++) {
        if (charts[i] && charts[i].canvas) {
            const canvas = charts[i].canvas;
            const imageData = canvas.toDataURL('image/png', 1.0);
            images.push({
                name: `Chart${i + 1}`,
                data: imageData
            });
        }
    }
    
    return images;
}

function showExportError(type) {
    const notification = document.createElement('div');
    notification.className = 'export-notification error';
    notification.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>Lỗi khi xuất ${type}. Vui lòng thử lại.</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function generateCSVContent() {
    const headers = ['Date', 'Check-ins', 'Department', 'Time'];
    const data = [
        ['2024-01-01', '25', 'Kỹ thuật', '08:00'],
        ['2024-01-02', '30', 'Kinh doanh', '08:15'],
        ['2024-01-03', '22', 'Nhân sự', '08:30'],
        ['2024-01-04', '28', 'Kế toán', '08:45'],
        ['2024-01-05', '35', 'Marketing', '09:00']
    ];
    
    const csvContent = [headers, ...data]
        .map(row => row.map(cell => `"${cell}"`).join(','))
        .join('\n');
    
    return csvContent;
}

function showExportLoading(format) {
    const btn = document.getElementById(`export${format}`);
    if (btn) {
        btn.disabled = true;
        btn.classList.add('loading');
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i><span>Đang xuất ${format}...</span>`;
    }
}

function hideExportLoading() {
    const exportBtns = document.querySelectorAll('.export-btn');
    exportBtns.forEach(btn => {
        btn.disabled = false;
        btn.classList.remove('loading');
        const icon = btn.querySelector('i');
        const span = btn.querySelector('span');
        
        if (icon && span) {
            if (btn.id === 'exportPDF') {
                icon.className = 'fas fa-file-pdf';
                span.textContent = 'Xuất PDF';
            } else if (btn.id === 'exportExcel') {
                icon.className = 'fas fa-file-excel';
                span.textContent = 'Xuất Excel';
            } else if (btn.id === 'exportImage') {
                icon.className = 'fas fa-image';
                span.textContent = 'Xuất ảnh';
            }
        }
    });
}

function showExportSuccess(format) {
    const notification = document.createElement('div');
    notification.className = 'export-notification';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>Xuất ${format} thành công! File đã được tải xuống.</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function setupCustomizationSystem() {
    // Load saved preferences
    loadUserPreferences();
    
    // Setup theme switching
    setupThemeSwitching();
    
    // Setup layout switching
    setupLayoutSwitching();
    
    // Setup refresh rate control
    setupRefreshRateControl();
    
    // Setup reset functionality
    setupResetFunctionality();
}

function loadUserPreferences() {
    const preferences = JSON.parse(localStorage.getItem('dashboardPreferences') || '{}');
    
    // Apply theme
    if (preferences.theme) {
        applyTheme(preferences.theme);
        document.getElementById('themeSelect').value = preferences.theme;
    }
    
    // Apply layout
    if (preferences.layout) {
        applyLayout(preferences.layout);
        document.getElementById('layoutSelect').value = preferences.layout;
    }
    
    // Apply refresh rate
    if (preferences.refreshRate !== undefined) {
        updateRefreshRate(preferences.refreshRate);
        document.getElementById('refreshRate').value = preferences.refreshRate;
    }
}

function setupThemeSwitching() {
    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
        themeSelect.addEventListener('change', function() {
            const theme = this.value;
            applyTheme(theme);
            saveUserPreferences({ theme });
        });
    }
}

function setupLayoutSwitching() {
    const layoutSelect = document.getElementById('layoutSelect');
    if (layoutSelect) {
        layoutSelect.addEventListener('change', function() {
            const layout = this.value;
            applyLayout(layout);
            saveUserPreferences({ layout });
        });
    }
}

function setupRefreshRateControl() {
    const refreshRateSelect = document.getElementById('refreshRate');
    if (refreshRateSelect) {
        refreshRateSelect.addEventListener('change', function() {
            const refreshRate = parseInt(this.value);
            updateRefreshRate(refreshRate);
            saveUserPreferences({ refreshRate });
        });
    }
}

function setupResetFunctionality() {
    const resetBtn = document.getElementById('resetSettings');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            resetToDefaults();
        });
    }
}

function applyTheme(theme) {
    const dashboard = document.querySelector('.dashboard-main');
    if (!dashboard) return;
    
    // Remove existing theme classes
    dashboard.classList.remove('theme-dark', 'theme-light', 'theme-colorful');
    
    // Add new theme class
    if (theme !== 'default') {
        dashboard.classList.add(`theme-${theme}`);
    }
}

function applyLayout(layout) {
    const dashboard = document.querySelector('.dashboard-main');
    if (!dashboard) return;
    
    // Remove existing layout classes
    dashboard.classList.remove('layout-list', 'layout-compact');
    
    // Add new layout class
    if (layout !== 'grid') {
        dashboard.classList.add(`layout-${layout}`);
    }
}

function updateRefreshRate(seconds) {
    // Clear existing interval
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
    
    // Set new interval if not disabled
    if (seconds > 0) {
        updateInterval = setInterval(updateStats, seconds * 1000);
        console.log(`Refresh rate set to ${seconds} seconds`);
    } else {
        console.log('Auto-refresh disabled');
    }
}

function saveUserPreferences(preferences) {
    const currentPreferences = JSON.parse(localStorage.getItem('dashboardPreferences') || '{}');
    const newPreferences = { ...currentPreferences, ...preferences };
    localStorage.setItem('dashboardPreferences', JSON.stringify(newPreferences));
}

function resetToDefaults() {
    // Clear saved preferences
    localStorage.removeItem('dashboardPreferences');
    
    // Reset form values
    document.getElementById('themeSelect').value = 'default';
    document.getElementById('layoutSelect').value = 'grid';
    document.getElementById('refreshRate').value = '30';
    
    // Apply default theme and layout
    applyTheme('default');
    applyLayout('grid');
    updateRefreshRate(30);
    
    // Show success message
    showCustomizationSuccess('Đã đặt lại về mặc định');
}

function showCustomizationSuccess(message) {
    const notification = document.createElement('div');
    notification.className = 'customization-success';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #48bb78;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentElement) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function setupModuleIntegration() {
    // Setup add module button
    const addModuleBtn = document.getElementById('addModuleBtn');
    if (addModuleBtn) {
        addModuleBtn.addEventListener('click', function() {
            showModuleIntegrationModal();
        });
    }
    
    // Setup example modules
    setupExampleModules();
}

function showModuleIntegrationModal() {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'module-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-puzzle-piece"></i> Tích hợp Module</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="module-form">
                    <div class="form-group">
                        <label for="moduleName">Tên Module:</label>
                        <input type="text" id="moduleName" placeholder="Ví dụ: sales, marketing, hr">
                    </div>
                    <div class="form-group">
                        <label for="moduleTitle">Tiêu đề hiển thị:</label>
                        <input type="text" id="moduleTitle" placeholder="Ví dụ: Bán hàng, Marketing, Nhân sự">
                    </div>
                    <div class="form-group">
                        <label for="moduleType">Loại Module:</label>
                        <select id="moduleType">
                            <option value="chart">Biểu đồ</option>
                            <option value="table">Bảng dữ liệu</option>
                            <option value="metric">Số liệu</option>
                            <option value="custom">Tùy chỉnh</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="moduleDescription">Mô tả:</label>
                        <textarea id="moduleDescription" placeholder="Mô tả chức năng của module"></textarea>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancelModule">Hủy</button>
                <button class="btn btn-primary" id="addModule">Thêm Module</button>
            </div>
        </div>
    `;
    
    // Add styles
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    `;
    
    document.body.appendChild(modal);
    
    // Setup event listeners
    const closeBtn = modal.querySelector('.modal-close');
    const cancelBtn = modal.querySelector('#cancelModule');
    const addBtn = modal.querySelector('#addModule');
    
    closeBtn.addEventListener('click', () => modal.remove());
    cancelBtn.addEventListener('click', () => modal.remove());
    addBtn.addEventListener('click', () => addNewModule(modal));
    
    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

function addNewModule(modal) {
    const moduleName = modal.querySelector('#moduleName').value;
    const moduleTitle = modal.querySelector('#moduleTitle').value;
    const moduleType = modal.querySelector('#moduleType').value;
    const moduleDescription = modal.querySelector('#moduleDescription').value;
    
    if (!moduleName || !moduleTitle) {
        alert('Vui lòng điền đầy đủ thông tin');
        return;
    }
    
    // Create module configuration
    const moduleConfig = {
        title: moduleTitle,
        type: moduleType,
        description: moduleDescription,
        api: {
            getData: function() {
                return new Promise((resolve) => {
                    // Simulate API call
                    setTimeout(() => {
                        resolve({
                            success: true,
                            data: generateSampleData(moduleType)
                        });
                    }, 1000);
                });
            }
        },
        permissions: ['dashboard.view']
    };
    
    // Register module
    const module = window.DashboardModuleFramework.registerModule(moduleName, moduleConfig);
    
    // Activate module
    window.DashboardModuleFramework.activateModule(moduleName);
    
    // Register widget
    const widget = window.DashboardModuleFramework.registerWidget(moduleName, `${moduleName}_widget`, {
        title: moduleTitle,
        type: moduleType,
        description: moduleDescription
    });
    
    // Render widget
    const container = createWidgetContainer(moduleName);
    window.DashboardModuleFramework.renderWidget(moduleName, `${moduleName}_widget`, container.id);
    
    // Close modal
    modal.remove();
    
    // Show success message
    showCustomizationSuccess(`Module "${moduleTitle}" đã được thêm thành công`);
}

function createWidgetContainer(moduleName) {
    // Create container for the widget
    const container = document.createElement('div');
    container.id = `widget-container-${moduleName}`;
    container.className = 'widget-container';
    
    // Add to dashboard
    const dashboardRight = document.querySelector('.dashboard-right');
    if (dashboardRight) {
        dashboardRight.appendChild(container);
    }
    
    return container;
}

function generateSampleData(type) {
    switch (type) {
        case 'chart':
            return {
                labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
                datasets: [{
                    label: 'Dữ liệu mẫu',
                    data: [12, 19, 15, 25, 22, 8, 3],
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)'
                }]
            };
        case 'table':
            return [
                { name: 'Item 1', value: 100, status: 'Active' },
                { name: 'Item 2', value: 200, status: 'Inactive' },
                { name: 'Item 3', value: 150, status: 'Active' }
            ];
        case 'metric':
            return {
                value: Math.floor(Math.random() * 1000),
                label: 'Tổng số',
                change: '+12%'
            };
        default:
            return { message: 'Dữ liệu mẫu' };
    }
}

function setupExampleModules() {
    // Register example modules
    const exampleModules = [
        {
            name: 'sales',
            config: {
                title: 'Bán hàng',
                type: 'chart',
                description: 'Thống kê doanh số bán hàng',
                api: {
                    getData: function() {
                        return Promise.resolve({
                            success: true,
                            data: generateSampleData('chart')
                        });
                    }
                }
            }
        },
        {
            name: 'hr',
            config: {
                title: 'Nhân sự',
                type: 'table',
                description: 'Quản lý nhân viên',
                api: {
                    getData: function() {
                        return Promise.resolve({
                            success: true,
                            data: generateSampleData('table')
                        });
                    }
                }
            }
        }
    ];
    
    // Register example modules
    exampleModules.forEach(module => {
        window.DashboardModuleFramework.registerModule(module.name, module.config);
    });
}

function setupSwipeGestures() {
    // Only setup swipe gestures on mobile devices
    if (!isMobile) return;
    
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
    
    // Use DocumentFragment for better performance
    const fragment = document.createDocumentFragment();
    
    if (!activities || activities.length === 0) {
        const emptyState = document.createElement('div');
        emptyState.className = 'empty-state';
        emptyState.innerHTML = `
            <i class="fas fa-inbox"></i>
            <p>Chưa có hoạt động nào</p>
        `;
        fragment.appendChild(emptyState);
    } else {
        // Add new activities
        activities.forEach(activity => {
            const activityItem = createActivityItem(activity);
            fragment.appendChild(activityItem);
        });
    }
    
    // Single DOM update
    activityList.innerHTML = '';
    activityList.appendChild(fragment);
}

function createActivityItem(activity) {
    const item = document.createElement('div');
    item.classList.add('activity-item');
    
    // Handle different data structures
    const userName = activity.user_name || (activity.user && activity.user.name) || 'Unknown User';
    const areaName = activity.area_name || (activity.area && activity.area.name) || 'Unknown Area';
    const timeAgo = activity.time_ago || formatDateTime(activity.created_at);
    const checkinType = activity.checkin_type || 'check-in';
    
    if (checkinType === 'check-in') {
        item.innerHTML = `
            <div class="activity-avatar">
                <i class="fas fa-user-circle"></i>
            </div>
            <div class="activity-content">
                <p><strong>${userName}</strong> đã check-in tại <strong>${areaName}</strong></p>
                <span class="activity-time">${timeAgo}</span>
            </div>
        `;
    } else {
        item.innerHTML = `
            <div class="activity-icon">
                <i class="fas fa-map-marker-alt"></i>
            </div>
            <div class="activity-content">
                <p><strong>${userName}</strong> đã check-out tại <strong>${areaName}</strong></p>
                <span class="activity-time">${timeAgo}</span>
            </div>
        `;
    }
    
    return item;
}

function formatDateTime(dateString) {
    if (!dateString) return 'Vừa xong';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Vừa xong';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} phút trước`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} giờ trước`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} ngày trước`;
    }
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
