const container = document.getElementById("container");
const registerbtn = document.getElementById("register");
const loginbtn = document.getElementById("login");
const loginForm = document.getElementById("login-form");

registerbtn.addEventListener("click", () => {
    container.classList.add("active");
});

loginbtn.addEventListener("click", () => {
    container.classList.remove("active");
});


document.addEventListener('DOMContentLoaded', function() {
    const registrationForm = document.getElementById("registration-form");
    
    if (registrationForm) {
        registrationForm.addEventListener('submit', handleRegistration);
    } 

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    async function handleRegistration(e) {
        e.preventDefault();
        
        // Clear any existing error messages
        clearErrors(registrationForm);
        
        // Get form data
        const formData = new FormData(registrationForm);
        const data = {
            first_name: formData.get('first_name').trim(),
            last_name: formData.get('last_name').trim(),
            email: formData.get('email').trim(),
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
            
            if (response.ok && result.success) {
                // Handle successful registration
                displaySuccessMessage(registrationForm, result.message || "Registration successful!");
                setTimeout(() => {
                    window.location.href = "http://127.0.0.1:8000/search";  // Redirect to home page after 2 seconds
                }, 2000);
                return;
            }
            
            // Handle errors
            if (!response.ok) {
                if (result.non_field_errors) {
                    displayGeneralError(registrationForm, result.non_field_errors[0]);
                } else {
                    displayErrors(registrationForm, result);
                }
            }
        } catch (error) {
            console.error('Error during registration:', error);
            displayGeneralError(registrationForm, 'An error occurred. Please try again.');
        }
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
                window.location.href = "http://127.0.0.1:8000/search";  // Redirect to index page
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
    // Function to display field-specific error message
    function displayFieldError(form, field, message) {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.style.color = 'red';
            errorDiv.style.fontSize = '12px';
            errorDiv.style.marginTop = '5px';
            errorDiv.textContent = typeof message === 'string' ? message : message[0];
            
            // Remove any existing error message for this field
            const existingError = input.parentNode.querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }
            
            // Add error message after the input field
            input.parentNode.insertBefore(errorDiv, input.nextSibling);
            input.style.borderColor = 'red';
        }
    }

    // Function to display multiple field errors
    function displayErrors(form, errors) {
        Object.entries(errors).forEach(([field, messages]) => {
            if (field !== 'non_field_errors') {
                const message = Array.isArray(messages) ? messages[0] : messages;
                displayFieldError(form, field, message);
            }
        });
    }

    // Function to display general error message at the top of the form
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
        
        // Remove any existing success message
        const existingSuccess = form.querySelector('.success-message');
        if (existingSuccess) {
            existingSuccess.remove();
        }
        
        form.insertBefore(successDiv, form.firstChild);
    }

    // Function to clear all error messages
    function clearErrors(form) {
        const errorMessages = form.querySelectorAll('.error-message, .success-message');
        errorMessages.forEach(error => error.remove());
        
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => input.style.borderColor = '');
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
});




















