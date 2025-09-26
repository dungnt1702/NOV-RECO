// Automation Test Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const startTestBtn = document.getElementById('startTestBtn');
    const currentTestSection = document.getElementById('currentTestSection');
    
    let currentSessionId = null;
    let statusCheckInterval = null;
    let currentTestType = 'comprehensive';

    // Start test button click - run test directly
    startTestBtn.addEventListener('click', function() {
        startTest(currentTestType);
    });

    // Dropdown menu click handlers
    document.querySelectorAll('[data-test-type]').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const testType = this.getAttribute('data-test-type');
            currentTestType = testType;
            
            // Update button text
            const buttonText = getTestTypeText(testType);
            startTestBtn.innerHTML = `<i class="fas fa-play me-2"></i>${buttonText}`;
            
            // Start test
            startTest(testType);
        });
    });

    // Start test function
    function startTest(testType = 'comprehensive') {
        // Disable button and show loading
        startTestBtn.disabled = true;
        const buttonText = getTestTypeText(testType);
        startTestBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Starting ${buttonText}...`;
        
        fetch('/automation-test/api/start-session/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ 
                notes: '',
                test_type: testType
            })
        })
        .then(response => response.json())
        .then(data => {
                if (data.success) {
                    currentSessionId = data.session_id;
                    showCurrentTestSection();
                    startStatusCheck();
                    simulateTestProgress(); // Start simulation
                    showNotification(`${buttonText} started successfully!`, 'success');
                } else {
                    showNotification('Error starting test: ' + data.error, 'error');
                }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error starting test: ' + error.message, 'error');
        })
        .finally(() => {
            // Re-enable button
            startTestBtn.disabled = false;
            startTestBtn.innerHTML = `<i class="fas fa-play me-2"></i>${buttonText}`;
        });
    }

    // Get test type display text
    function getTestTypeText(testType) {
        const texts = {
            'display': 'Start Display Test',
            'links': 'Start Link Test', 
            'comprehensive': 'Start Comprehensive Test',
            'django': 'Start Django Tests'
        };
        return texts[testType] || 'Start Test';
    }

    // Show current test section
    function showCurrentTestSection() {
        currentTestSection.style.display = 'block';
        document.getElementById('currentSessionId').textContent = currentSessionId;
        document.getElementById('currentStatus').innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Running';
        document.getElementById('currentStatus').className = 'badge badge-warning pulse-animation';
        document.getElementById('currentStarted').textContent = new Date().toLocaleString();
        document.getElementById('testCounts').textContent = '0 / 0';
        
        // Initialize progress bars
        updateProgressBar(0);
        document.getElementById('passedCount').textContent = '0';
        document.getElementById('failedCount').textContent = '0';
        document.getElementById('skippedCount').textContent = '0';
        
        // Initialize checklist
        initializeChecklist();
    }

    // Start status check
    function startStatusCheck() {
        statusCheckInterval = setInterval(checkTestStatus, 2000); // Check every 2 seconds
    }

    // Stop status check
    function stopStatusCheck() {
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
            statusCheckInterval = null;
        }
    }

    // Check test status
    function checkTestStatus() {
        if (!currentSessionId) return;

        fetch(`/automation-test/api/session-status/${currentSessionId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateTestStatus(data.session);
                
                // Stop checking if test is completed or failed
                if (data.session.status === 'completed' || data.session.status === 'failed') {
                    stopStatusCheck();
                    refreshPage();
                }
            }
        })
        .catch(error => {
            console.error('Error checking status:', error);
        });
    }

    // Update progress bar and circular progress
    function updateProgressBar(progress) {
        const progressBar = document.getElementById('progressBar');
        const circularProgress = document.getElementById('circularProgress');
        const circularProgressText = document.getElementById('circularProgressText');
        
        if (progressBar) {
            progressBar.style.width = progress + '%';
            progressBar.setAttribute('aria-valuenow', progress);
        }
        
        if (circularProgress) {
            circularProgress.style.setProperty('--progress', progress);
        }
        
        if (circularProgressText) {
            circularProgressText.textContent = Math.round(progress) + '%';
        }
    }

    // Update test status display
    function updateTestStatus(session) {
        document.getElementById('currentStatus').textContent = session.status.charAt(0).toUpperCase() + session.status.slice(1);
        
        // Update status badge
        const statusBadge = document.getElementById('currentStatus');
        statusBadge.className = 'badge ';
        if (session.status === 'completed') {
            statusBadge.className += 'badge-success';
        } else if (session.status === 'failed') {
            statusBadge.className += 'badge-danger';
        } else if (session.status === 'running') {
            statusBadge.className += 'badge-warning status-running';
        } else {
            statusBadge.className += 'badge-secondary';
        }

        // Update test counts
        document.getElementById('testCounts').textContent = `${session.passed_tests + session.failed_tests} / ${session.total_tests}`;
        
        // Update progress bar and circular progress
        if (session.total_tests > 0) {
            const progress = ((session.passed_tests + session.failed_tests) / session.total_tests) * 100;
            updateProgressBar(progress);
        }
        
        // Update individual test counts
        document.getElementById('passedCount').textContent = session.passed_tests || 0;
        document.getElementById('failedCount').textContent = session.failed_tests || 0;
        document.getElementById('skippedCount').textContent = session.skipped_tests || 0;

        // Update success rate
        document.getElementById('successRate').textContent = session.success_rate.toFixed(1) + '%';
        
        // Update running animations based on status
        updateRunningAnimations(session.status);
        
        // Update checklist if test results are available
        if (session.test_results) {
            updateChecklist(session.test_results);
        }
    }

    // Update running animations based on status
    function updateRunningAnimations(status) {
        const progressBar = document.getElementById('progressBar');
        const circularProgress = document.getElementById('circularProgress');
        const testProgressCard = document.getElementById('currentTestSection');
        
        if (status === 'running') {
            // Add running class for animations
            if (progressBar) progressBar.classList.add('running');
            if (circularProgress) circularProgress.classList.add('running');
            if (testProgressCard) testProgressCard.classList.add('running');
        } else {
            // Remove running class to stop animations
            if (progressBar) progressBar.classList.remove('running');
            if (circularProgress) circularProgress.classList.remove('running');
            if (testProgressCard) testProgressCard.classList.remove('running');
        }
    }

    // Initialize checklist with mock tests
    function initializeChecklist() {
        const checklistContainer = document.getElementById('testChecklist');
        if (!checklistContainer) return;

        // Mock test data
        const mockTests = [
            { name: 'User Creation', module: 'users', status: 'pending' },
            { name: 'User Auth', module: 'users', status: 'pending' },
            { name: 'User Permissions', module: 'users', status: 'pending' },
            { name: 'Area Creation', module: 'area', status: 'pending' },
            { name: 'Area Validation', module: 'area', status: 'pending' },
            { name: 'Check-in Submit', module: 'checkin', status: 'pending' },
            { name: 'Check-in Validation', module: 'checkin', status: 'pending' },
            { name: 'Check-in History', module: 'checkin', status: 'pending' },
            { name: 'Dashboard Access', module: 'dashboard', status: 'pending' },
            { name: 'API Endpoints', module: 'api', status: 'pending' }
        ];

        checklistContainer.innerHTML = '';
        mockTests.forEach((test, index) => {
            const testItem = createChecklistItem(test, index);
            checklistContainer.appendChild(testItem);
        });
    }

    // Create checklist item
    function createChecklistItem(test, index) {
        const item = document.createElement('div');
        item.className = `checklist-item ${test.status}`;
        item.dataset.testIndex = index;
        item.dataset.testName = test.name;
        item.dataset.testModule = test.module;

        item.innerHTML = `
            <div class="checklist-icon ${test.status}">
                ${getStatusIcon(test.status)}
            </div>
            <div class="checklist-content">
                <div class="checklist-title">${test.name}</div>
                <div class="checklist-module">${test.module}</div>
            </div>
            <div class="checklist-status ${test.status}">
                ${test.status.toUpperCase()}
            </div>
        `;

        return item;
    }

    // Get status icon
    function getStatusIcon(status) {
        switch (status) {
            case 'pending':
                return '⏳';
            case 'running':
                return '🔄';
            case 'passed':
                return '✓';
            case 'failed':
                return '✗';
            case 'skipped':
                return '⏭';
            default:
                return '⏳';
        }
    }

    // Update checklist item status
    function updateChecklistItem(testName, status) {
        const checklistContainer = document.getElementById('testChecklist');
        if (!checklistContainer) return;

        const items = checklistContainer.querySelectorAll('.checklist-item');
        items.forEach(item => {
            if (item.dataset.testName === testName) {
                // Update classes
                item.className = `checklist-item ${status}`;
                
                // Update icon
                const icon = item.querySelector('.checklist-icon');
                icon.className = `checklist-icon ${status}`;
                icon.textContent = getStatusIcon(status);
                
                // Update status text
                const statusText = item.querySelector('.checklist-status');
                statusText.className = `checklist-status ${status}`;
                statusText.textContent = status.toUpperCase();
            }
        });
    }

    // Update checklist based on test results
    function updateChecklist(testResults) {
        if (!testResults || !Array.isArray(testResults)) return;

        testResults.forEach(result => {
            updateChecklistItem(result.test_name, result.status);
        });
    }

    // Simulate test progress for demo
    function simulateTestProgress() {
        const mockTests = [
            'User Creation',
            'User Auth', 
            'User Permissions',
            'Area Creation',
            'Area Validation',
            'Check-in Submit',
            'Check-in Validation',
            'Check-in History',
            'Dashboard Access',
            'API Endpoints'
        ];

        let currentIndex = 0;
        const progressInterval = setInterval(() => {
            if (currentIndex < mockTests.length) {
                // Mark current test as running
                updateChecklistItem(mockTests[currentIndex], 'running');
                
                // Simulate test execution time
                setTimeout(() => {
                    // Randomly assign result (80% pass, 15% fail, 5% skip)
                    const rand = Math.random();
                    let status = 'passed';
                    if (rand < 0.15) status = 'failed';
                    else if (rand < 0.20) status = 'skipped';
                    
                    updateChecklistItem(mockTests[currentIndex], status);
                    currentIndex++;
                }, 1000 + Math.random() * 2000); // 1-3 seconds per test
            } else {
                clearInterval(progressInterval);
            }
        }, 2000); // Start new test every 2 seconds
    }

    // Refresh page
    function refreshPage() {
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    }

    // Show notification
    function showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Auto-refresh page every 30 seconds if no active test
    setInterval(() => {
        if (!currentSessionId) {
            // Only refresh if we're not in the middle of a test
            const activeTests = document.querySelectorAll('.badge-warning.status-running');
            if (activeTests.length === 0) {
                window.location.reload();
            }
        }
    }, 30000);

    // Initialize page
    function init() {
        // Add fade-in animation to cards
        const cards = document.querySelectorAll('.card, .stats-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
        });

        // Check if there are any running tests
        const runningTests = document.querySelectorAll('.badge-warning');
        if (runningTests.length > 0) {
            // Find the first running test and start monitoring
            const firstRunningRow = document.querySelector('tr:has(.badge-warning)');
            if (firstRunningRow) {
                const sessionLink = firstRunningRow.querySelector('a[href*="session/"]');
                if (sessionLink) {
                    const sessionId = sessionLink.href.split('/').pop();
                    currentSessionId = sessionId;
                    showCurrentTestSection();
                    startStatusCheck();
                }
            }
        }

        // Add hover effects to stats cards
        const statsCards = document.querySelectorAll('.stats-card');
        statsCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    // Initialize on page load
    init();
});
