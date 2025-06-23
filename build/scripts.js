// Album du Jour - Enhanced Interactions
document.addEventListener('DOMContentLoaded', function() {
    initializeCollapsibleSections();
    initializeLazyLoading();
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
                
                // Load lazy embeds when section is expanded
                loadLazyEmbedsInSection(section);
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

function initializeLazyLoading() {
    // Load embeds that are currently visible
    loadVisibleEmbeds();
    
    // Set up intersection observer for lazy loading
    if ('IntersectionObserver' in window) {
        const embedObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    loadEmbed(entry.target);
                    embedObserver.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '50px'
        });
        
        // Observe all lazy embeds
        document.querySelectorAll('.lazy-embed[data-src]').forEach(embed => {
            embedObserver.observe(embed);
        });
    } else {
        // Fallback for browsers without IntersectionObserver
        document.querySelectorAll('.lazy-embed[data-src]').forEach(loadEmbed);
    }
}

function loadVisibleEmbeds() {
    // Load embeds in currently visible sections (like Currently Listening)
    document.querySelectorAll('.currently-listening .lazy-embed[data-src]').forEach(loadEmbed);
}

function loadLazyEmbedsInSection(section) {
    // Load all lazy embeds in a specific section
    section.querySelectorAll('.lazy-embed[data-src]').forEach(loadEmbed);
}

function loadEmbed(embed) {
    const src = embed.getAttribute('data-src');
    if (src) {
        embed.src = src;
        embed.removeAttribute('data-src');
        embed.classList.remove('lazy-embed');
    }
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
