// Personal Profile JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Avatar hover effects
    const avatarContainer = document.querySelector('.profile-avatar');
    if (avatarContainer) {
        avatarContainer.addEventListener('mouseenter', function() {
            this.querySelector('.avatar-overlay').style.opacity = '1';
        });
        
        avatarContainer.addEventListener('mouseleave', function() {
            this.querySelector('.avatar-overlay').style.opacity = '0';
        });
    }
    
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states to buttons
    const actionButtons = document.querySelectorAll('.profile-actions .btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.href && !this.href.includes('#')) {
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang tải...';
                this.style.pointerEvents = 'none';
            }
        });
    });
    
    // Add animation to profile sections
    const sections = document.querySelectorAll('.profile-section');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
    
    // Add tooltip for status badges
    const statusBadges = document.querySelectorAll('.status-badge');
    statusBadges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.classList.contains('active') 
                ? 'Tài khoản đang hoạt động bình thường' 
                : 'Tài khoản tạm thời bị vô hiệu hóa';
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
                z-index: 1000;
                pointer-events: none;
                white-space: nowrap;
            `;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
        });
        
        badge.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
});
