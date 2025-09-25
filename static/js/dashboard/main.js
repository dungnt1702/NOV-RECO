// Dashboard Main JavaScript
let attendanceChart = null;
let departmentChart = null;
let timeChart = null;
let mainChart = null;
let isMobile = window.innerWidth <= 768;
let updateInterval = null;
let currentChartType = 'attendance';
let currentDateRange = '7';
let websocket = null;
let reconnectAttempts = 0;
let maxReconnectAttempts = 5;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard Main loaded');
    
    // Initialize dashboard
    initializeDashboard();
    
    // Setup real-time updates (only on desktop)
    if (!isMobile) {
        setupRealTimeUpdates();
        setupWebSocketConnection();
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

function setupWebSocketConnection() {
    // Check if WebSocket is supported
    if (!window.WebSocket) {
        console.log('WebSocket not supported, falling back to polling');
        return;
    }
    
    // Connect to WebSocket
    connectWebSocket();
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
    // Initialize main chart
    createMainChart();
    
    // Initialize additional charts
    createDepartmentChart();
    createTimeChart();
    
    // Add color coding to stat cards
    addColorCodingToStats();
    
    // Setup chart controls
    setupChartControls();
    
    // Setup export functionality
    setupExportFunctionality();
    
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
    if (!ctx) return;
    
    const data = {
        labels: ['Kỹ thuật', 'Kinh doanh', 'Nhân sự', 'Kế toán'],
        datasets: [{
            data: [35, 28, 22, 15],
            backgroundColor: [
                'rgba(102, 126, 234, 0.8)',
                'rgba(240, 147, 251, 0.8)',
                'rgba(79, 172, 254, 0.8)',
                'rgba(67, 233, 123, 0.8)'
            ],
            borderColor: [
                'rgb(102, 126, 234)',
                'rgb(240, 147, 251)',
                'rgb(79, 172, 254)',
                'rgb(67, 233, 123)'
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
                    cornerRadius: 8
                }
            }
        }
    };
    
    departmentChart = new Chart(ctx, config);
}

function createTimeChart() {
    const ctx = document.getElementById('timeChart');
    if (!ctx) return;
    
    const data = {
        labels: ['Sáng', 'Chiều', 'Tối'],
        datasets: [{
            data: [45, 35, 20],
            backgroundColor: [
                'rgba(67, 233, 123, 0.8)',
                'rgba(79, 172, 254, 0.8)',
                'rgba(240, 147, 251, 0.8)'
            ],
            borderColor: [
                'rgb(67, 233, 123)',
                'rgb(79, 172, 254)',
                'rgb(240, 147, 251)'
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
                    cornerRadius: 8
                }
            }
        }
    };
    
    timeChart = new Chart(ctx, config);
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

function exportToPDF() {
    // Show loading state
    showExportLoading('PDF');
    
    // Simulate PDF generation (in real implementation, this would call an API)
    setTimeout(() => {
        // Create a simple PDF content
        const content = generatePDFContent();
        
        // Create and download PDF
        const element = document.createElement('a');
        const file = new Blob([content], { type: 'application/pdf' });
        element.href = URL.createObjectURL(file);
        element.download = `dashboard-report-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        
        hideExportLoading();
        showExportSuccess('PDF');
    }, 2000);
}

function exportToExcel() {
    // Show loading state
    showExportLoading('Excel');
    
    // Simulate Excel generation
    setTimeout(() => {
        // Create CSV content (simplified Excel export)
        const csvContent = generateCSVContent();
        
        // Create and download CSV
        const element = document.createElement('a');
        const file = new Blob([csvContent], { type: 'text/csv' });
        element.href = URL.createObjectURL(file);
        element.download = `dashboard-report-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        
        hideExportLoading();
        showExportSuccess('Excel');
    }, 1500);
}

function exportToImage() {
    // Show loading state
    showExportLoading('Image');
    
    // Export charts as images
    setTimeout(() => {
        const charts = [mainChart, departmentChart, timeChart];
        const images = [];
        
        charts.forEach((chart, index) => {
            if (chart) {
                const canvas = chart.canvas;
                const imageData = canvas.toDataURL('image/png');
                images.push(imageData);
            }
        });
        
        // Create a combined image (simplified)
        if (images.length > 0) {
            const element = document.createElement('a');
            element.href = images[0]; // Use first chart as main image
            element.download = `dashboard-chart-${new Date().toISOString().split('T')[0]}.png`;
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }
        
        hideExportLoading();
        showExportSuccess('Image');
    }, 1000);
}

function generatePDFContent() {
    // This is a simplified PDF content generation
    // In real implementation, you would use a library like jsPDF
    return `%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Dashboard Report) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF`;
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
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i><span>Đang xuất ${format}...</span>`;
    }
}

function hideExportLoading() {
    const exportBtns = document.querySelectorAll('.export-btn');
    exportBtns.forEach(btn => {
        btn.disabled = false;
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
    // Show success notification
    const notification = document.createElement('div');
    notification.className = 'export-success';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>Xuất ${format} thành công!</span>
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
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
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
