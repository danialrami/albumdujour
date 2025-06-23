// Album du Jour - Interactive Functionality with Fixed Collapsible Sections
class AlbumSections {
    constructor() {
        this.initializeCollapsibleSections();
        this.initializeLazyLoading();
        this.initializeAccessibility();
    }
    
    initializeCollapsibleSections() {
        const toggleButtons = document.querySelectorAll('.section-toggle');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.toggleSection(e.currentTarget);
            });
        });
        
        // Restore saved states after a short delay
        setTimeout(() => {
            this.restoreSectionStates();
        }, 100);
    }
    
    toggleSection(button) {
        const section = button.closest('.collapsible-section');
        const content = section.querySelector('.section-content');
        const icon = section.querySelector('.toggle-icon');
        const isExpanded = button.getAttribute('aria-expanded') === 'true';
        
        // Toggle expanded state
        button.setAttribute('aria-expanded', !isExpanded);
        
        if (!isExpanded) {
            // Expanding
            content.style.maxHeight = 'none';
            content.style.overflow = 'visible';
            icon.style.transform = 'rotate(180deg)';
            
            // Load any lazy embeds in this section
            this.loadLazyEmbedsInSection(section);
        } else {
            // Collapsing
            content.style.maxHeight = '0';
            content.style.overflow = 'hidden';
            icon.style.transform = 'rotate(0deg)';
        }
        
        // Save state to localStorage
        localStorage.setItem(`section-${section.dataset.section}`, !isExpanded);
    }
    
    restoreSectionStates() {
        const sections = document.querySelectorAll('.collapsible-section');
        sections.forEach(section => {
            const savedState = localStorage.getItem(`section-${section.dataset.section}`);
            if (savedState === 'true') {
                const button = section.querySelector('.section-toggle');
                if (button && button.getAttribute('aria-expanded') !== 'true') {
                    this.toggleSection(button);
                }
            }
        });
    }
    
    initializeLazyLoading() {
        // Intersection Observer for lazy loading embeds
        const embedObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadEmbed(entry.target);
                    embedObserver.unobserve(entry.target);
                }
            });
        }, { 
            rootMargin: '100px',
            threshold: 0.1
        });
        
        // Observe all lazy embeds
        document.querySelectorAll('.lazy-embed').forEach(iframe => {
            embedObserver.observe(iframe);
        });
    }
    
    loadEmbed(iframe) {
        if (iframe.dataset.src) {
            iframe.src = iframe.dataset.src;
            iframe.removeAttribute('data-src');
            iframe.classList.remove('lazy-embed');
            
            // Add loading indicator
            iframe.style.opacity = '0';
            iframe.addEventListener('load', () => {
                iframe.style.transition = 'opacity 0.3s ease';
                iframe.style.opacity = '1';
            });
        }
    }
    
    loadLazyEmbedsInSection(section) {
        const lazyEmbeds = section.querySelectorAll('.lazy-embed');
        lazyEmbeds.forEach(iframe => {
            this.loadEmbed(iframe);
        });
    }
    
    initializeAccessibility() {
        // Keyboard navigation for collapsible sections
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                if (e.target.classList.contains('section-toggle')) {
                    e.preventDefault();
                    this.toggleSection(e.target);
                }
            }
        });
        
        // Focus management
        const toggleButtons = document.querySelectorAll('.section-toggle');
        toggleButtons.forEach(button => {
            button.addEventListener('focus', () => {
                button.style.outline = '2px solid var(--lufs-teal)';
                button.style.outlineOffset = '2px';
            });
            
            button.addEventListener('blur', () => {
                button.style.outline = 'none';
            });
        });
    }
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Performance monitoring
function initializePerformanceMonitoring() {
    // Log page load time
    window.addEventListener('load', () => {
        const loadTime = performance.now();
        console.log(`Album du Jour loaded in ${Math.round(loadTime)}ms`);
        
        // Track largest contentful paint
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log(`LCP: ${Math.round(lastEntry.startTime)}ms`);
            });
            observer.observe({ entryTypes: ['largest-contentful-paint'] });
        }
    });
}

// Error handling for embeds
function initializeEmbedErrorHandling() {
    document.addEventListener('error', (e) => {
        if (e.target.tagName === 'IFRAME') {
            const iframe = e.target;
            const container = iframe.closest('.embed-container');
            if (container) {
                container.innerHTML = '<p class="no-embed">Embed failed to load</p>';
            }
        }
    }, true);
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎵 Album du Jour - Initializing with fixed collapsible sections...');
    
    try {
        new AlbumSections();
        initializeSmoothScrolling();
        initializePerformanceMonitoring();
        initializeEmbedErrorHandling();
        
        console.log('✅ Album du Jour - Initialized successfully');
    } catch (error) {
        console.error('❌ Album du Jour - Initialization error:', error);
    }
});
