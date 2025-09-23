// JavaScript for user update form
document.addEventListener('DOMContentLoaded', function() {
  // Add Bootstrap classes to form fields
  // Add classes to all input elements
  const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="number"]');
  inputs.forEach(input => {
    input.classList.add('form-control');
  });
  
  // Add classes to select elements
  const selects = document.querySelectorAll('select');
  selects.forEach(select => {
    select.classList.add('form-select');
  });
  
  // Add classes to checkbox
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach(checkbox => {
    checkbox.classList.add('form-check-input');
  });
});
