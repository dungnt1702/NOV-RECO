// Session Detail JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const errorModal = document.getElementById('errorModal');
    const logContainer = document.getElementById('logContainer');
    
    // Handle error modal
    errorModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const errorMessage = button.getAttribute('data-error');
        const stackTrace = button.getAttribute('data-stack');
        
        document.getElementById('errorMessage').textContent = errorMessage || 'No error message available';
        document.getElementById('stackTrace').textContent = stackTrace || 'No stack trace available';
    });

    // Auto-scroll log container to bottom
    function scrollLogsToBottom() {
        if (logContainer) {
            logContainer.scrollTop = logContainer.scrollHeight;
        }
    }

    // Initialize log scrolling
    scrollLogsToBottom();

    // Add smooth scrolling and click handlers to log entries
    const logEntries = document.querySelectorAll('.log-entry');
    logEntries.forEach(entry => {
        entry.style.transition = 'background-color 0.3s ease';
        entry.style.cursor = 'pointer';
        entry.title = 'Click to copy log message';
        
        entry.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        });
        
        entry.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
        });
        
        entry.addEventListener('click', function() {
            const message = this.querySelector('.log-message').textContent;
            copyToClipboard(message);
            showToast('Log message copied to clipboard', 'info');
        });
    });

    // Add copy functionality to error details
    const errorMessage = document.getElementById('errorMessage');
    const stackTrace = document.getElementById('stackTrace');
    
    if (errorMessage) {
        errorMessage.addEventListener('click', function() {
            copyToClipboard(this.textContent);
            showToast('Error message copied to clipboard', 'info');
        });
    }
    
    if (stackTrace) {
        stackTrace.addEventListener('click', function() {
            copyToClipboard(this.textContent);
            showToast('Stack trace copied to clipboard', 'info');
        });
    }

    // Copy to clipboard function
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).catch(err => {
                console.error('Failed to copy text: ', err);
                fallbackCopyTextToClipboard(text);
            });
        } else {
            fallbackCopyTextToClipboard(text);
        }
    }

    // Fallback copy function
    function fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
        }
        
        document.body.removeChild(textArea);
    }

    // Show toast notification
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'info' ? 'info' : 'success'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }

    // Add click handlers to log entries for better interaction
    logEntries.forEach(entry => {
        entry.style.cursor = 'pointer';
        entry.title = 'Click to copy log message';
        
        entry.addEventListener('click', function() {
            const message = this.querySelector('.log-message').textContent;
            copyToClipboard(message);
            showToast('Log message copied to clipboard', 'info');
        });
    });

    // Add search functionality to logs
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Search logs...';
    searchInput.id = 'logSearch';
    
    if (logContainer && logContainer.parentNode) {
        logContainer.parentNode.insertBefore(searchInput, logContainer);
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const entries = logContainer.querySelectorAll('.log-entry');
            
            entries.forEach(entry => {
                const text = entry.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    entry.style.display = 'flex';
                } else {
                    entry.style.display = 'none';
                }
            });
        });
    }

    // Add filter buttons for log levels
    const filterContainer = document.createElement('div');
    filterContainer.className = 'mb-3';
    filterContainer.innerHTML = `
        <div class="btn-group" role="group">
            <button type="button" class="btn btn-outline-secondary btn-sm active" data-level="all">All</button>
            <button type="button" class="btn btn-outline-info btn-sm" data-level="info">Info</button>
            <button type="button" class="btn btn-outline-warning btn-sm" data-level="warning">Warning</button>
            <button type="button" class="btn btn-outline-danger btn-sm" data-level="error">Error</button>
            <button type="button" class="btn btn-outline-secondary btn-sm" data-level="debug">Debug</button>
        </div>
    `;
    
    if (logContainer && logContainer.parentNode) {
        logContainer.parentNode.insertBefore(filterContainer, searchInput);
        
        // Add filter functionality
        const filterButtons = filterContainer.querySelectorAll('button');
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                const level = this.getAttribute('data-level');
                const entries = logContainer.querySelectorAll('.log-entry');
                
                entries.forEach(entry => {
                    if (level === 'all') {
                        entry.style.display = 'flex';
                    } else {
                        const entryLevel = entry.classList.contains(`log-${level}`);
                        entry.style.display = entryLevel ? 'flex' : 'none';
                    }
                });
            });
        });
    }

    // Add export functionality
    const exportBtn = document.createElement('button');
    exportBtn.className = 'btn btn-outline-primary btn-sm';
    exportBtn.innerHTML = '<i class="fas fa-download"></i> Export Logs';
    exportBtn.addEventListener('click', function() {
        exportLogs();
    });
    
    if (logContainer && logContainer.parentNode) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'd-flex justify-content-between align-items-center mb-3';
        buttonContainer.appendChild(filterContainer);
        buttonContainer.appendChild(exportBtn);
        
        logContainer.parentNode.insertBefore(buttonContainer, searchInput);
    }

    // Export logs function
    function exportLogs() {
        const entries = logContainer.querySelectorAll('.log-entry');
        let logText = `Test Session Logs - ${new Date().toLocaleString()}\n`;
        logText += '='.repeat(50) + '\n\n';
        
        entries.forEach(entry => {
            const timestamp = entry.querySelector('.log-timestamp').textContent;
            const level = entry.querySelector('.log-level').textContent;
            const test = entry.querySelector('.log-test');
            const message = entry.querySelector('.log-message').textContent;
            
            const testName = test ? test.textContent : '';
            logText += `[${timestamp}] [${level}] ${testName ? `[${testName}] ` : ''}${message}\n`;
        });
        
        // Create and download file
        const blob = new Blob([logText], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `test_logs_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showToast('Logs exported successfully', 'success');
    }
});
