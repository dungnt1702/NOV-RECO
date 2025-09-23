// Employee List JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize employee list
    initializeEmployeeList();
    
    // Setup filters
    setupFilters();
    
    // Setup pagination
    setupPagination();
    
    // Setup mobile cards
    setupMobileCards();
});

function initializeEmployeeList() {
    console.log('Employee List initialized');
    
    // Add animation to table rows
    const tableRows = document.querySelectorAll('.employee-table tbody tr');
    tableRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        row.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            row.style.opacity = '1';
            row.style.transform = 'translateX(0)';
        }, index * 100);
    });
    
    // Add animation to mobile cards
    const mobileCards = document.querySelectorAll('.mobile-card');
    mobileCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 150);
    });
}

function setupFilters() {
    const searchInput = document.getElementById('search');
    const roleFilter = document.getElementById('role');
    const departmentFilter = document.getElementById('department');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterEmployees();
        });
    }
    
    if (roleFilter) {
        roleFilter.addEventListener('change', function() {
            filterEmployees();
        });
    }
    
    if (departmentFilter) {
        departmentFilter.addEventListener('change', function() {
            filterEmployees();
        });
    }
}

function filterEmployees() {
    const searchTerm = document.getElementById('search')?.value.toLowerCase() || '';
    const roleFilter = document.getElementById('role')?.value || '';
    const departmentFilter = document.getElementById('department')?.value || '';
    
    const tableRows = document.querySelectorAll('.employee-table tbody tr');
    const mobileCards = document.querySelectorAll('.mobile-card');
    
    // Filter table rows
    tableRows.forEach(row => {
        const name = row.querySelector('.employee-name')?.textContent.toLowerCase() || '';
        const email = row.querySelector('.employee-email')?.textContent.toLowerCase() || '';
        const role = row.querySelector('.employee-role')?.textContent.toLowerCase() || '';
        const department = row.querySelector('.employee-department')?.textContent.toLowerCase() || '';
        
        const matchesSearch = name.includes(searchTerm) || email.includes(searchTerm);
        const matchesRole = !roleFilter || role.includes(roleFilter);
        const matchesDepartment = !departmentFilter || department.includes(departmentFilter);
        
        if (matchesSearch && matchesRole && matchesDepartment) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Filter mobile cards
    mobileCards.forEach(card => {
        const name = card.querySelector('.mobile-card-name')?.textContent.toLowerCase() || '';
        const email = card.querySelector('.mobile-card-email')?.textContent.toLowerCase() || '';
        const role = card.querySelector('.mobile-card-role')?.textContent.toLowerCase() || '';
        const department = card.querySelector('.mobile-card-department')?.textContent.toLowerCase() || '';
        
        const matchesSearch = name.includes(searchTerm) || email.includes(searchTerm);
        const matchesRole = !roleFilter || role.includes(roleFilter);
        const matchesDepartment = !departmentFilter || department.includes(departmentFilter);
        
        if (matchesSearch && matchesRole && matchesDepartment) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

function setupPagination() {
    const paginationLinks = document.querySelectorAll('.pagination a');
    
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Add loading state
            const tableContainer = document.querySelector('.employee-table-container');
            const mobileCards = document.querySelector('.mobile-cards');
            
            if (tableContainer) {
                tableContainer.style.opacity = '0.5';
            }
            if (mobileCards) {
                mobileCards.style.opacity = '0.5';
            }
            
            // Simulate loading
            setTimeout(() => {
                if (tableContainer) {
                    tableContainer.style.opacity = '1';
                }
                if (mobileCards) {
                    mobileCards.style.opacity = '1';
                }
            }, 500);
        });
    });
}

function setupMobileCards() {
    // Add hover effects to mobile cards
    const mobileCards = document.querySelectorAll('.mobile-card');
    
    mobileCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Add click tracking for actions
document.addEventListener('DOMContentLoaded', function() {
    const actionButtons = document.querySelectorAll('.btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.textContent.trim();
            console.log(`Employee action clicked: ${action}`);
            
            // Add click animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
    });
});

// Add real-time updates simulation
function simulateRealTimeUpdates() {
    setInterval(() => {
        // Simulate new employee added
        const tableBody = document.querySelector('.employee-table tbody');
        const mobileCards = document.querySelector('.mobile-cards');
        
        if (tableBody && Math.random() < 0.1) { // 10% chance every 30 seconds
            console.log('New employee added (simulated)');
            // In real implementation, this would reload the data
        }
    }, 30000); // Check every 30 seconds
}

// Start real-time updates after 5 seconds
setTimeout(simulateRealTimeUpdates, 5000);
