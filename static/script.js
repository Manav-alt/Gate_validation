// script.js

// Example: Simple form validation
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const submitButton = form.querySelector('button[type="submit"]');
    
    form.addEventListener('submit', function (event) {
        const inputs = form.querySelectorAll('input[type="text"], input[type="date"]');
        let valid = true;
        
        inputs.forEach(input => {
            if (input.value.trim() === '') {
                valid = false;
                input.style.borderColor = 'red';
            } else {
                input.style.borderColor = '#ccc';
            }
        });
        
        if (!valid) {
            event.preventDefault();
            alert('Please fill in all required fields.');
        }
    });
});
