// Modern UI Enhancements for Site24x7 CLI AI Agent

// Initialize modern UI features
document.addEventListener('DOMContentLoaded', function() {
    initializeModernFeatures();
    setupAdvancedInteractions();
    addProgressiveEnhancements();
});

function initializeModernFeatures() {
    // Add modern animations to elements
    addFadeInAnimations();
    addHoverEffects();
    setupRippleEffects();
    initializeTooltips();
}

function addFadeInAnimations() {
    const cards = document.querySelectorAll('.card');
    const statusItems = document.querySelectorAll('.status-item');
    
    // Stagger card animations
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Animate status items
    statusItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, index * 150);
    });
}

function addHoverEffects() {
    // Enhanced card hover effects
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)';
        });
    });
}

function setupRippleEffects() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

function initializeTooltips() {
    // Add modern tooltips to elements with title attributes
    const elementsWithTooltips = document.querySelectorAll('[title]');
    
    elementsWithTooltips.forEach(element => {
        const title = element.getAttribute('title');
        element.removeAttribute('title');
        
        // Create tooltip wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'tooltip-modern';
        element.parentNode.insertBefore(wrapper, element);
        wrapper.appendChild(element);
        
        // Create tooltip text
        const tooltipText = document.createElement('span');
        tooltipText.className = 'tooltip-text';
        tooltipText.textContent = title;
        wrapper.appendChild(tooltipText);
    });
}

function setupAdvancedInteractions() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Modern loading states
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.classList.add('loading');
                submitButton.disabled = true;
                
                // Re-enable after a delay (or handle in actual response)
                setTimeout(() => {
                    submitButton.classList.remove('loading');
                    submitButton.disabled = false;
                }, 3000);
            }
        });
    });
}

function addProgressiveEnhancements() {
    // Add skeleton loading for dynamic content
    const dynamicElements = document.querySelectorAll('[data-dynamic="true"]');
    dynamicElements.forEach(element => {
        if (!element.innerHTML.trim()) {
            element.classList.add('skeleton');
            element.style.height = '20px';
            element.style.borderRadius = '4px';
        }
    });
    
    // Enhanced focus indicators
    const focusableElements = document.querySelectorAll('button, input, select, textarea, a[href]');
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid var(--primary)';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = 'none';
        });
    });
    
    // Add modern progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        bar.parentElement.classList.add('progress-modern');
    });
}

// Modern notification system
function showModernNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} modern-notification`;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getIconForType(type)} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    // Style the notification
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.maxWidth = '500px';
    notification.style.transform = 'translateX(100%)';
    notification.style.transition = 'transform 0.3s ease';
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'primary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Enhanced refresh functionality
function refreshWithModernFeedback() {
    // Add visual feedback
    const refreshButtons = document.querySelectorAll('[onclick*="refresh"]');
    refreshButtons.forEach(button => {
        button.classList.add('loading');
        const icon = button.querySelector('i');
        if (icon) {
            icon.classList.add('fa-spin');
        }
    });
    
    // Show progress indicator
    const progressIndicator = document.createElement('div');
    progressIndicator.className = 'progress-modern';
    progressIndicator.style.position = 'fixed';
    progressIndicator.style.top = '0';
    progressIndicator.style.left = '0';
    progressIndicator.style.width = '100%';
    progressIndicator.style.height = '3px';
    progressIndicator.style.zIndex = '9999';
    progressIndicator.innerHTML = '<div class="progress-bar" style="width: 0%"></div>';
    
    document.body.appendChild(progressIndicator);
    
    // Animate progress
    const progressBar = progressIndicator.querySelector('.progress-bar');
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressBar.style.width = progress + '%';
    }, 200);
    
    // Complete after actual refresh (this would be called from the refresh function)
    setTimeout(() => {
        clearInterval(interval);
        progressBar.style.width = '100%';
        
        setTimeout(() => {
            progressIndicator.remove();
            refreshButtons.forEach(button => {
                button.classList.remove('loading');
                const icon = button.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-spin');
                }
            });
        }, 500);
    }, 2000);
}

// Export functions for use in other scripts
window.modernUI = {
    showNotification: showModernNotification,
    refreshWithFeedback: refreshWithModernFeedback
};