// ===================================
// MediPlus - Main JavaScript
// ===================================

/**
 * Mobile Navigation Toggle
 */
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // Close menu when clicking on a link
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navMenu.classList.remove('active');
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNav = navToggle && navToggle.contains(event.target);
        const isClickInsideMenu = navMenu && navMenu.contains(event.target);
        
        if (!isClickInsideNav && !isClickInsideMenu && navMenu) {
            navMenu.classList.remove('active');
        }
    });
});

/**
 * Smooth Scroll for Anchor Links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#' && document.querySelector(href)) {
            e.preventDefault();
            const target = document.querySelector(href);
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

/**
 * Form Submission Handler
 */
const appointmentForm = document.querySelector('form');
if (appointmentForm) {
    appointmentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = {
            fullname: document.getElementById('fullname').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            specialty: document.getElementById('specialty').value,
            date: document.getElementById('date').value,
            time: document.getElementById('time').value,
            message: document.getElementById('message').value,
        };

        // Validate form
        if (!formData.fullname || !formData.email || !formData.phone || 
            !formData.specialty || !formData.date || !formData.time) {
            showAlert('Please fill in all required fields', 'warning');
            return;
        }

        // Validate email
        if (!isValidEmail(formData.email)) {
            showAlert('Please enter a valid email address', 'warning');
            return;
        }

        // Show success message
        showAlert('Appointment requested successfully! We will contact you shortly.', 'success');
        
        // Reset form
        this.reset();
    });
}

/**
 * Validate Email Format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Show Alert Message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.maxWidth = '400px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.animation = 'slideIn 0.3s ease-out';

    document.body.appendChild(alertDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, 5000);
}

/**
 * Scroll Animation for Elements
 */
function observeElements() {
    const options = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, options);

    // Observe all cards and features
    document.querySelectorAll('.card, .feature').forEach(element => {
        observer.observe(element);
    });
}

// Add animation styles dynamically
if (!document.getElementById('animations-style')) {
    const style = document.createElement('style');
    style.id = 'animations-style';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }

        @keyframes fadeInUp {
            from {
                transform: translateY(30px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize animations on page load
window.addEventListener('load', observeElements);

/**
 * Lazy Load Images
 */
function lazyLoadImages() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Initialize lazy loading
window.addEventListener('load', lazyLoadImages);

/**
 * Prevent multiple form submissions
 */
if (appointmentForm) {
    let isSubmitting = false;
    appointmentForm.addEventListener('submit', function(e) {
        if (isSubmitting) {
            e.preventDefault();
            return;
        }
        isSubmitting = true;
        setTimeout(() => {
            isSubmitting = false;
        }, 2000);
    });
}

console.log('MediPlus JavaScript loaded successfully');
