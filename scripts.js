// Album du Jour - Interactive Functionality with Dynamic Responsive Embeds
class AlbumSections {
    constructor() {
        this.initializeCollapsibleSections();
        this.initializeLazyLoading();
        this.initializeAccessibility();
        this.initializeDynamicEmbeds();
    }
    
    initializeCollapsibleSections() {
        const toggleButtons = document.querySelectorAll('.section-toggle');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.toggleSection(e.currentTarget);
            });
        });
        
        // Restore saved states
        this.restoreSectionStates();
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
            content.style.maxHeight = content.scrollHeight + 'px';
            icon.style.transform = 'rotate(180deg)';
            
            // Load any lazy embeds in this section
            this.loadLazyEmbedsInSection(section);
            
            // Trigger dynamic embed resize after content is visible
            setTimeout(() => {
                this.resizeDynamicEmbeds(section);
            }, 300);
        } else {
            // Collapsing
            content.style.maxHeight = '0';
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
                // Delay to ensure DOM is ready
                setTimeout(() => {
                    this.toggleSection(button);
                }, 100);
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
                
                // Resize embed after load
                this.resizeSingleEmbed(iframe);
            });
        }
    }
    
    loadLazyEmbedsInSection(section) {
        const lazyEmbeds = section.querySelectorAll('.lazy-embed');
        lazyEmbeds.forEach(iframe => {
            this.loadEmbed(iframe);
        });
    }
    
    initializeDynamicEmbeds() {
        // Handle responsive embed sizing on window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.resizeDynamicEmbeds();
            }, 150);
        });
        
        // Initial resize after page load
        window.addEventListener('load', () => {
            setTimeout(() => {
                this.resizeDynamicEmbeds();
            }, 500);
        });
        
        // Initial adjustment
        this.resizeDynamicEmbeds();
    }
    
    resizeDynamicEmbeds(container = document) {
        const embedContainers = container.querySelectorAll('.embed-container');
        
        embedContainers.forEach(embedContainer => {
            const iframe = embedContainer.querySelector('.dynamic-embed');
            if (iframe) {
                this.resizeSingleEmbed(iframe);
            }
        });
    }
    
    resizeSingleEmbed(iframe) {
        const embedContainer = iframe.closest('.embed-container');
        if (!embedContainer) return;
        
        const albumCard = iframe.closest('.album-card');
        if (!albumCard) return;
        
        // Calculate available space
        const cardHeight = albumCard.offsetHeight;
        const header = albumCard.querySelector('.card-header');
        const links = albumCard.querySelector('.card-links');
        
        const headerHeight = header ? header.offsetHeight : 0;
        const linksHeight = links ? links.offsetHeight : 0;
        const padding = 32; // Account for card padding and margins
        
        // Calculate ideal embed height
        const availableHeight = cardHeight - headerHeight - linksHeight - padding;
        const minHeight = iframe.classList.contains('current-embed') ? 300 : 160;
        const maxHeight = iframe.classList.contains('current-embed') ? 500 : 300;
        
        const idealHeight = Math.max(minHeight, Math.min(maxHeight, availableHeight));
        
        // Apply the calculated height
        embedContainer.style.height = idealHeight + 'px';
        iframe.style.height = idealHeight + 'px';
        
        // Log for debugging (remove in production)
        console.log(`Resized embed: ${idealHeight}px (card: ${cardHeight}px, available: ${availableHeight}px)`);
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
    console.log('🎵 Album du Jour - Initializing with dynamic responsive embeds...');
    
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
