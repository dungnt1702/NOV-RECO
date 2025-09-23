// JavaScript for user create form
document.addEventListener('DOMContentLoaded', function() {
    // Add Bootstrap classes to form fields
    const formControls = document.querySelectorAll('input[type="text"], input[type="number"], input[type="email"], input[type="password"], textarea, select');
    formControls.forEach(function(control) {
        control.classList.add('form-control');
    });
    
    // Add form wrapper class for custom styles
    const form = document.querySelector('form');
    if (form) {
        form.classList.add('user-create-form');
    }
});
