// Album du Jour - Enhanced Interactions
document.addEventListener('DOMContentLoaded', function() {
    initializeCollapsibleSections();
    initializeAccessibility();
});

function initializeCollapsibleSections() {
    const toggles = document.querySelectorAll('.section-toggle');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const section = this.closest('.collapsible-section');
            const content = section.querySelector('.section-content');
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Toggle state
            this.setAttribute('aria-expanded', !isExpanded);
            
            if (!isExpanded) {
                content.classList.add('expanded');
                content.style.maxHeight = content.scrollHeight + 'px';
                
                // Save state
                localStorage.setItem(`section-${section.dataset.section}`, 'expanded');
            } else {
                content.classList.remove('expanded');
                content.style.maxHeight = '0';
                
                // Save state
                localStorage.setItem(`section-${section.dataset.section}`, 'collapsed');
            }
        });
        
        // Restore saved state
        const section = toggle.closest('.collapsible-section');
        const savedState = localStorage.getItem(`section-${section.dataset.section}`);
        
        if (savedState === 'expanded') {
            // Simulate click to expand
            setTimeout(() => toggle.click(), 100);
        }
    });
}

function initializeAccessibility() {
    // Add keyboard navigation for collapsible sections
    document.querySelectorAll('.section-toggle').forEach(toggle => {
        toggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Add focus management
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });
}

// Utility function to handle window resize
window.addEventListener('resize', debounce(function() {
    // Recalculate expanded section heights
    document.querySelectorAll('.section-content.expanded').forEach(content => {
        content.style.maxHeight = content.scrollHeight + 'px';
    });
}, 250));

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
