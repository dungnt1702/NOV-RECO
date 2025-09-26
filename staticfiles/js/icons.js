// FontAwesome Icons - Inline definitions
// This replaces the external heroicons script to avoid CORS issues

// Define common icons used in the application
const icons = {
    // Navigation icons
    'menu': `<i class="fas fa-bars"></i>`,
    'home': `<i class="fas fa-home"></i>`,
    'plus': `<i class="fas fa-plus"></i>`,
    'clock': `<i class="fas fa-clock"></i>`,
    'users': `<i class="fas fa-users"></i>`,
    'logout': `<i class="fas fa-sign-out-alt"></i>`,
    'login': `<i class="fas fa-sign-in-alt"></i>`,
    'settings': `<i class="fas fa-cog"></i>`,
    'location': `<i class="fas fa-map-marker-alt"></i>`,
    'camera': `<i class="fas fa-camera"></i>`,
    'chart': `<i class="fas fa-chart-bar"></i>`,
    'building': `<i class="fas fa-building"></i>`,
    'shield': `<i class="fas fa-shield-alt"></i>`,
    'clipboard': `<i class="fas fa-clipboard"></i>`,
    'arrow-down': `<i class="fas fa-arrow-down"></i>`,
    'arrow-up': `<i class="fas fa-arrow-up"></i>`,
    'search': `<i class="fas fa-search"></i>`,
    'edit': `<i class="fas fa-edit"></i>`,
    'trash': `<i class="fas fa-trash"></i>`,
    'arrow-left': `<i class="fas fa-arrow-left"></i>`,
    'arrow-right': `<i class="fas fa-arrow-right"></i>`,
    'chevron-left': `<i class="fas fa-chevron-left"></i>`,
    'chevron-right': `<i class="fas fa-chevron-right"></i>`,
    'chevron-double-left': `<i class="fas fa-angle-double-left"></i>`,
    'chevron-double-right': `<i class="fas fa-angle-double-right"></i>`
};

// Function to get icon HTML
function getIcon(iconName) {
    return icons[iconName] || `<span class="icon-placeholder">${iconName}</span>`;
}

// Function to replace icon placeholders in DOM
function initializeIcons() {
    // This function can be used to dynamically replace icon placeholders
    // if needed in the future
    console.log('Icons initialized');
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { icons, getIcon, initializeIcons };
}