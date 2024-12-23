const container = document.getElementById("container");
const registerbtn = document.getElementById("register");
const loginbtn = document.getElementById("login");
const registrationForm = document.getElementById("registration-form");
const loginForm = document.getElementById("login-form");

registerbtn.addEventListener("click", () => {
    container.classList.add("active");
});

loginbtn.addEventListener("click", () => {
    container.classList.remove("active");
});

document.addEventListener('DOMContentLoaded', function() {
    // Registration Form Handler
    if (registrationForm) {
        registrationForm.addEventListener('submit', handleRegistration);
    }

    // Login Form Handler
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    async function handleLogin(e) {
        e.preventDefault();
        
        // Clear any existing error messages
        clearErrors(loginForm);
        
        // Get form data
        const formData = new FormData(loginForm);
        const data = {
            email: formData.get('email'),
            password: formData.get('password')
        };
        
        try {
            const response = await fetch("/auth/login/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                // Handle successful login
                window.location.href = "";  // Redirect to index page
                return;
            }
            
            if (!response.ok) {
                if (result.error) {
                    // Handle specific error messages from the backend
                    if (result.error.includes("DoesNotExist")) {
                        displayFieldError(loginForm, 'email', 'This email does not exist.');
                    } else if (result.error.includes("password is wrong")) {
                        displayFieldError(loginForm, 'password', result.error);
                    } else if (result.error.includes("Account is temporarily locked")) {
                        displayGeneralError(loginForm, result.error);
                    } else {
                        displayGeneralError(loginForm, result.error);
                    }
                } else {
                    // Handle validation errors
                    displayErrors(loginForm, result);
                }
            }
        } catch (error) {
            console.error('Error during login:', error);
            displayGeneralError(loginForm, 'An error occurred. Please try again.');
        }
    }

    async function handleRegistration(e) {
        e.preventDefault();
        
        // Clear any existing error messages
        clearErrors(registrationForm);
        
        // Get form data
        const formData = new FormData(registrationForm);
        const data = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password'),
            password2: formData.get('password2')
        };
        
        try {
            const response = await fetch("/auth/register/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                displayErrors(registrationForm, result);
                
                if (result.non_field_errors) {
                    displayGeneralError(registrationForm, result.non_field_errors[0]);
                }
            } else {
                displaySuccessMessage(registrationForm, "User registered successfully.");
                setTimeout(() => {
                    window.location.href = "";
                }, 2000);
            }
        } catch (error) {
            displayGeneralError(registrationForm, 'An error occurred. Please try again.');
        }
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Function to display field-specific error message
    function displayFieldError(form, field, message) {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.color = 'red';
            errorDiv.style.fontSize = '12px';
            errorDiv.style.marginTop = '5px';
            errorDiv.textContent = message;
            
            // Remove any existing error message
            const existingError = input.parentNode.querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }
            
            // Insert error message after the input field
            input.parentNode.insertBefore(errorDiv, input.nextSibling);
            
            // Add red border to input field
            input.style.borderColor = 'red';
        }
    }
    
    // Function to display multiple field errors
    function displayErrors(form, errors) {
        for (const [field, errorMessages] of Object.entries(errors)) {
            if (field !== 'error') {  // Skip the general error field
                displayFieldError(form, field, Array.isArray(errorMessages) ? errorMessages[0] : errorMessages);
            }
        }
    }
    
    // Function to display general error message
    function displayGeneralError(form, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message general-error';
        errorDiv.style.color = 'red';
        errorDiv.style.marginBottom = '10px';
        errorDiv.style.textAlign = 'center';
        errorDiv.textContent = message;
        
        // Remove any existing general error
        const existingError = form.querySelector('.general-error');
        if (existingError) {
            existingError.remove();
        }
        
        form.insertBefore(errorDiv, form.firstChild);
    }
    
    // Function to display success message
    function displaySuccessMessage(form, message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.style.color = 'green';
        successDiv.style.marginBottom = '10px';
        successDiv.style.textAlign = 'center';
        successDiv.textContent = message;
        
        form.insertBefore(successDiv, form.firstChild);
    }
    
    // Function to clear all error messages
    function clearErrors(form) {
        // Remove all error message elements
        const errorMessages = form.querySelectorAll('.error-message, .success-message');
        errorMessages.forEach(error => error.remove());
        
        // Reset input field borders
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => input.style.borderColor = '');
    }
});







