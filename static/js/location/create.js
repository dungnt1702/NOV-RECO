// JavaScript for location create form
document.addEventListener('DOMContentLoaded', function() {
    // Add Bootstrap classes to form fields
    const formControls = document.querySelectorAll('input[type="text"], input[type="number"], input[type="email"], textlocation, select');
    formControls.forEach(function(control) {
        if (control.type === 'checkbox') {
            control.classList.add('form-check-input');
        } else {
            control.classList.add('form-control');
        }
    });
    
    // Add form wrapper class for custom styles
    const form = document.querySelector('form');
    if (form) {
        form.classList.add('location-create-form');
    }
});
