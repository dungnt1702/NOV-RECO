/**
 * Checkout History JavaScript
 * Handles checkout history page functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Checkout History page loaded');
    
    // Initialize checkout history functionality
    initializeCheckoutHistory();
});

function initializeCheckoutHistory() {
    console.log('Initializing checkout history...');
    
    // Add any specific functionality for checkout history page
    // For example: filtering, searching, pagination controls, etc.
    
    // Example: Add click handlers for checkout items
    const checkoutItems = document.querySelectorAll('.history-item');
    checkoutItems.forEach(item => {
        item.addEventListener('click', function() {
            console.log('Checkout item clicked');
            // Add any click functionality here
        });
    });
    
    // Example: Add photo preview functionality
    const photoThumbnails = document.querySelectorAll('.photo-thumbnail');
    photoThumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            showPhotoPreview(this.src);
        });
    });
}

function showPhotoPreview(imageSrc) {
    // Create modal for photo preview
    const modal = document.createElement('div');
    modal.className = 'photo-modal';
    modal.innerHTML = `
        <div class="photo-modal-content">
            <span class="photo-modal-close">&times;</span>
            <img src="${imageSrc}" alt="Checkout photo" class="photo-modal-image">
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close modal functionality
    const closeBtn = modal.querySelector('.photo-modal-close');
    closeBtn.addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Close on background click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// Export functions for potential use by other scripts
window.CheckoutHistory = {
    initializeCheckoutHistory,
    showPhotoPreview
};
