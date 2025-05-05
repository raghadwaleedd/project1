// rating_system.js
document.addEventListener('DOMContentLoaded', function() {
    // Check for rating popup when page loads
    checkRatingStatus();
    
    // Set cookie to track when we last showed the popup
    function setLastShownCookie() {
        const now = new Date();
        const expiryDate = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000); // 30 days
        document.cookie = `rating_popup_shown=${now.toISOString()}; expires=${expiryDate.toUTCString()}; path=/`;
    }
    
    // Get when popup was last shown
    function getLastShownDate() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith('rating_popup_shown=')) {
                return new Date(cookie.substring('rating_popup_shown='.length));
            }
        }
        return null;
    }
    
    // Check if we should show the rating popup
    function checkRatingStatus() {
        // Don't show more than once per day even if user refreshes
       
        
        fetch('auth/ratings/status/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.should_show_popup) {
                showRatingPopup();
                setLastShownCookie();
            }
        })
        .catch(error => console.error('Error checking rating status:', error));
    }
    
    // Get CSRF token from cookies
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length);
            }
        }
        return '';
    }
    
    // Show the rating popup
    function showRatingPopup() {
        const popup = document.getElementById('rating-popup-container');
        if (popup) {
            popup.classList.remove('hidden');
        } else {
            // Create popup if it doesn't exist in the DOM
            createRatingPopup();
        }
    }
    
    // Create the rating popup dynamically
    function createRatingPopup() {
        const popupHTML = `
            <div id="rating-popup-container" class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
                <div id="rating-popup" class="bg-white rounded-xl shadow-2xl p-8 max-w-md mx-4 animate-fadeIn">
                    <div class="flex justify-between items-center mb-6">
                        <h3 class="text-2xl font-bold text-gray-800">We Value Your Feedback</h3>
                        <button id="close-rating" class="text-gray-400 hover:text-gray-600 transition-colors">
                            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <p class="text-gray-600 mb-6 text-lg">Please rate your experience with our service:</p>
                    
                    <div class="flex justify-center mb-6 stars-container">
                        <button class="star-btn mx-1" data-rating="1">
                            <svg class="h-10 w-10 text-gray-300 hover:text-yellow-400 transition-colors" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
                            </svg>
                        </button>
                        <button class="star-btn mx-1" data-rating="2">
                            <svg class="h-10 w-10 text-gray-300 hover:text-yellow-400 transition-colors" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
                            </svg>
                        </button>
                        <button class="star-btn mx-1" data-rating="3">
                            <svg class="h-10 w-10 text-gray-300 hover:text-yellow-400 transition-colors" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
                            </svg>
                        </button>
                        <button class="star-btn mx-1" data-rating="4">
                            <svg class="h-10 w-10 text-gray-300 hover:text-yellow-400 transition-colors" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
                            </svg>
                        </button>
                        <button class="star-btn mx-1" data-rating="5">
                            <svg class="h-10 w-10 text-gray-300 hover:text-yellow-400 transition-colors" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="mb-6">
                        <label for="feedback-text" class="block text-gray-700 mb-2">Your comments:</label>
                        <textarea id="feedback-text" placeholder="Please share your feedback (max 100 words)" class="w-full border border-gray-300 rounded-lg px-4 py-3 mb-1 h-32 resize-none focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 transition-colors"></textarea>
                        <div class="text-right text-gray-500 text-sm">Max 100 words</div>
                    </div>
                    
                    <div class="flex justify-end">
                        <button id="cancel-rating" class="mr-4 px-6 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors">Cancel</button>
                        <button id="submit-rating" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 focus:ring-opacity-50 transition-all">Submit Feedback</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add custom CSS for animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .animate-fadeIn {
                animation: fadeIn 0.3s ease-out forwards;
            }  

            #feedback-text {
            color: #333; /* Ensure text is visible */
            background-color: #fff; /* Ensure background is white */
            opacity: 1; /* Ensure element is visible */
            pointer-events: auto; /* Ensure element is interactive */
            } 

            #feedback-text::placeholder {
            color: #9ca3af; /* Ensure placeholder text is visible */
            opacity: 1; /* Ensure placeholder is visible */
            }
        `;
        document.head.appendChild(style);
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = popupHTML;
        document.body.appendChild(tempDiv.firstElementChild);
        
        // Add event listeners
        setupRatingEvents();
    }
    
    // Setup event listeners for the rating popup
    function setupRatingEvents() {
        const popup = document.getElementById('rating-popup-container');
        const closeBtn = document.getElementById('close-rating');
        const cancelBtn = document.getElementById('cancel-rating');
        const submitBtn = document.getElementById('submit-rating');
        const starBtns = document.querySelectorAll('.star-btn');
        
        let selectedRating = 0;
        
        // Close button events
        closeBtn.addEventListener('click', function() {
            popup.classList.add('hidden');
        });
        
        cancelBtn.addEventListener('click', function() {
            popup.classList.add('hidden');
        });
        
        // Close on background click
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                popup.classList.add('hidden');
            }
        });
        
        // Star rating buttons
        starBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                selectedRating = parseInt(this.getAttribute('data-rating'));
                
                // Reset all stars
                starBtns.forEach(star => {
                    star.querySelector('svg').classList.remove('text-yellow-400');
                    star.querySelector('svg').classList.add('text-gray-300');
                });
                
                // Highlight selected stars
                for (let i = 0; i < selectedRating; i++) {
                    starBtns[i].querySelector('svg').classList.remove('text-gray-300');
                    starBtns[i].querySelector('svg').classList.add('text-yellow-400');
                }
            });
            
            // Hover effects for preview
            btn.addEventListener('mouseenter', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                
                for (let i = 0; i < rating; i++) {
                    if (!starBtns[i].querySelector('svg').classList.contains('text-yellow-400')) {
                        starBtns[i].querySelector('svg').classList.add('text-yellow-100');
                    }
                }
            });
            
            btn.addEventListener('mouseleave', function() {
                starBtns.forEach(star => {
                    star.querySelector('svg').classList.remove('text-yellow-100');
                });
            });
        });
        
        // Submit button event
        submitBtn.addEventListener('click', function() {
            if (selectedRating === 0) {
                // Show validation message
                const starsContainer = document.querySelector('.stars-container');
                
                // Create error message if it doesn't exist
                if (!document.getElementById('stars-error')) {
                    const errorMsg = document.createElement('div');
                    errorMsg.id = 'stars-error';
                    errorMsg.className = 'text-red-500 text-center mt-2 animate-fadeIn';
                    errorMsg.textContent = 'Please select a rating';
                    starsContainer.insertAdjacentElement('afterend', errorMsg);
                    
                    // Remove after 3 seconds
                    setTimeout(() => {
                        if (document.getElementById('stars-error')) {
                            document.getElementById('stars-error').remove();
                        }
                    }, 3000);
                }
                
                return;
            }
            
            const feedback = document.getElementById('feedback-text').value;
            
            submitRating(selectedRating, feedback);
        });
    }
    
    // Submit the rating to the API
    function submitRating(rating, feedback) {
        // Show loading state
        const submitBtn = document.getElementById('submit-rating');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
        
        fetch('auth/ratings/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                rating: rating,
                feedback: feedback
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to submit rating');
                });
            }
            return response.json();
        })
        .then(data => {
            // Show success message
            const popupContainer = document.getElementById('rating-popup-container');
            const popup = document.getElementById('rating-popup');
            
            popup.innerHTML = `
                <div class="text-center py-6">
                    <div class="mb-4 inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100">
                        <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                    </div>
                    <h3 class="text-2xl font-bold text-green-600 mb-2">Thank You!</h3>
                    <p class="text-gray-600 mb-6">Your feedback has been submitted successfully.</p>
                    <button id="close-success" class="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition-colors">Close</button>
                </div>
            `;
            
            document.getElementById('close-success').addEventListener('click', function() {
                popupContainer.classList.add('hidden');
            });
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                popupContainer.classList.add('hidden');
            }, 5000);
        })
        .catch(error => {
            // Reset button
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
            
            // Show error message
            alert(error.message);
            console.error('Error submitting rating:', error);
        });
    }
});