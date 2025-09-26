/**
 * Checkout Detail JavaScript
 * Handles checkout detail page functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Checkout Detail page loaded');
    
    // Initialize checkout detail functionality
    initializeCheckoutDetail();
});

function initializeCheckoutDetail() {
    console.log('Initializing checkout detail...');
    
    // Add photo click handlers for modal preview
    const photos = document.querySelectorAll('.detail-photo');
    photos.forEach(photo => {
        photo.addEventListener('click', function() {
            showPhotoModal(this.src);
        });
    });
    
    // Add any other specific functionality for checkout detail page
}

function showPhotoModal(imageSrc) {
    // Create modal for photo preview
    const modal = document.createElement('div');
    modal.className = 'photo-modal';
    modal.innerHTML = `
        <div class="photo-modal-content">
            <span class="photo-modal-close">&times;</span>
            <img src="${imageSrc}" alt="Photo preview" class="photo-modal-image">
        </div>
    `;
    
    // Add modal styles
    const style = document.createElement('style');
    style.textContent = `
        .photo-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            animation: fadeIn 0.3s ease;
        }
        
        .photo-modal-content {
            position: relative;
            max-width: 90%;
            max-height: 90%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .photo-modal-close {
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 30px;
            color: white;
            cursor: pointer;
            background: rgba(0, 0, 0, 0.5);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
            transition: background 0.3s ease;
        }
        
        .photo-modal-close:hover {
            background: rgba(0, 0, 0, 0.7);
        }
        
        .photo-modal-image {
            max-width: 100%;
            max-height: 100%;
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(modal);
    
    // Close modal functionality
    const closeBtn = modal.querySelector('.photo-modal-close');
    closeBtn.addEventListener('click', function() {
        document.body.removeChild(modal);
        document.head.removeChild(style);
    });
    
    // Close on background click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
            document.head.removeChild(style);
        }
    });
    
    // Close on Escape key
    const handleEscape = function(e) {
        if (e.key === 'Escape') {
            document.body.removeChild(modal);
            document.head.removeChild(style);
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
}

// Export functions for potential use by other scripts
window.CheckoutDetail = {
    initializeCheckoutDetail,
    showPhotoModal
};
