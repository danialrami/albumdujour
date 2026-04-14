// Album du Jour - Retro Brutalist Styling
// Based on echo-bridge-manual
// LUFS Audio

document.addEventListener('DOMContentLoaded', function() {
    initializeStickyHeader();
    initializeScrollEffects();
    initializeCollapsibleSections();
    initializeRetroButtons();
    initializeAnimatedBackground();
    setCurrentYear();
});

// Sticky Header Functionality
function initializeStickyHeader() {
    const stickyHeader = document.getElementById('sticky-header');
    const mainHeader = document.querySelector('.main-header');
    if (!stickyHeader || !mainHeader) return;
    
    let lastScrollTop = 0;
    let headerVisible = false;

    function updateStickyHeader() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const mainHeaderBottom = mainHeader.offsetTop + mainHeader.offsetHeight;
        
        if (scrollTop > mainHeaderBottom && !headerVisible) {
            stickyHeader.classList.add('visible');
            headerVisible = true;
        } else if (scrollTop <= mainHeaderBottom && headerVisible) {
            stickyHeader.classList.remove('visible');
            headerVisible = false;
        }
        
        lastScrollTop = scrollTop;
    }

    let ticking = false;
    function handleScroll() {
        if (!ticking) {
            requestAnimationFrame(function() {
                updateStickyHeader();
                ticking = false;
            });
            ticking = true;
        }
    }

    window.addEventListener('scroll', handleScroll);
    
    // Smooth scroll to top functionality
    const logoLinks = document.querySelectorAll('.logo-link');
    logoLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    });
}

// Scroll Effects
function initializeScrollEffects() {
    initializeScrollReveal();
    initializeProgressBar();
}

// Simple scroll reveal
function initializeScrollReveal() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    const elementsToReveal = document.querySelectorAll('.collapsible-section h2, .currently-listening h2');
    
    elementsToReveal.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(10px)';
        element.style.transition = 'all 0.3s ease';
        observer.observe(element);
    });
}

// Progress Bar
function initializeProgressBar() {
    const progressBar = document.getElementById('scroll-progress');
    if (!progressBar) return;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.body.scrollHeight - window.innerHeight;
        const scrollPercent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        progressBar.style.width = scrollPercent + '%';
    });
}

// Collapsible Sections (from original albumdujour)
function initializeCollapsibleSections() {
    const toggles = document.querySelectorAll('.section-toggle');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const section = this.closest('.collapsible-section');
            const content = section.querySelector('.section-content');
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            this.setAttribute('aria-expanded', !isExpanded);
            
            if (!isExpanded) {
                content.classList.add('expanded');
                content.style.maxHeight = content.scrollHeight + 'px';
                localStorage.setItem(`section-${section.dataset.section}`, 'expanded');
            } else {
                content.classList.remove('expanded');
                content.style.maxHeight = '0';
                localStorage.setItem(`section-${section.dataset.section}`, 'collapsed');
            }
        });
        
        const section = toggle.closest('.collapsible-section');
        const savedState = localStorage.getItem(`section-${section.dataset.section}`);
        
        if (savedState === 'expanded') {
            setTimeout(() => toggle.click(), 100);
        }
    });
    
    // Add keyboard navigation
    document.querySelectorAll('.section-toggle').forEach(toggle => {
        toggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

// Retro Button Effects
function initializeRetroButtons() {
    const buttons = document.querySelectorAll('.webring-button');
    
    buttons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.style.transform = 'translate(2px, 2px)';
            this.style.boxShadow = 'none';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = '';
            this.style.boxShadow = '2px 2px 0 #888888';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '2px 2px 0 #888888';
        });
        
        // Add sparkles to button images (except text buttons)
        if (button.querySelector('svg') && !button.classList.contains('library-button')) {
            addSparklesToButton(button);
        }
    });
}

// Add sparkle effects to button
function addSparklesToButton(button) {
    const sparkleCount = 5;
    for (let i = 0; i < sparkleCount; i++) {
        const sparkle = document.createElement('div');
        sparkle.className = 'sparkle';
        
        // Random position
        const left = 10 + Math.floor(Math.random() * 70);
        const top = 5 + Math.floor(Math.random() * 20);
        sparkle.style.left = left + 'px';
        sparkle.style.top = top + 'px';
        sparkle.style.animationDelay = (i * 0.4) + 's';
        
        button.appendChild(sparkle);
    }
}

// Animated Background with Floating Shapes
function initializeAnimatedBackground() {
    const background = document.getElementById('animated-background');
    if (!background) return;
    
    createFloatingShapes(background);
    createPulsingElements(background);
}

function createFloatingShapes(container) {
    const shapes = ['square', 'circle', 'triangle', 'diamond'];
    const animations = ['floatAround', 'floatSlow', 'floatFast'];
    
    for (let i = 0; i < 15; i++) {
        const shape = document.createElement('div');
        const shapeType = shapes[Math.floor(Math.random() * shapes.length)];
        const animation = animations[Math.floor(Math.random() * animations.length)];
        
        shape.className = `floating-shape ${shapeType}`;
        
        const size = Math.random() * 17 + 8;
        if (shapeType !== 'triangle') {
            shape.style.width = size + 'px';
            shape.style.height = size + 'px';
        }
        
        shape.style.left = Math.random() * 100 + '%';
        shape.style.top = Math.random() * 100 + '%';
        
        const duration = Math.random() * 10 + 10;
        const delay = Math.random() * 5;
        
        shape.style.animation = `${animation} ${duration}s ease-in-out infinite`;
        shape.style.animationDelay = delay + 's';
        
        container.appendChild(shape);
    }
}

function createPulsingElements(container) {
    for (let i = 0; i < 5; i++) {
        const pulse = document.createElement('div');
        pulse.className = 'pulse-element';
        
        const size = Math.random() * 100 + 50;
        pulse.style.width = size + 'px';
        pulse.style.height = size + 'px';
        
        pulse.style.left = Math.random() * 100 + '%';
        pulse.style.top = Math.random() * 100 + '%';
        
        const delay = Math.random() * 8;
        pulse.style.animationDelay = delay + 's';
        
        container.appendChild(pulse);
    }
}

// Set current year
function setCurrentYear() {
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowUp' && e.ctrlKey) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    if (e.key === 'ArrowDown' && e.ctrlKey) {
        e.preventDefault();
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
});

// Debounce utility
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

// Resize handler
window.addEventListener('resize', debounce(function() {
    document.querySelectorAll('.section-content.expanded').forEach(content => {
        content.style.maxHeight = content.scrollHeight + 'px';
    });
}, 250));

// Console message
console.log(`
╔══════════════════════════════════════╗
║  Album du Jour - Retro Edition        ║
║  ────────────────────────────────     ║
║  LUFS Audio - Brutalist Style         ║
║                                      ║
║  Features:                           ║
║  • Sticky header navigation          ║
║  • Animated floating shapes          ║
║  • Scroll progress bar               ║
║  • Retro brutalist styling           ║
║                                      ║
║  Keyboard shortcuts:                 ║
║  Ctrl + ↑  : Scroll to top           ║
║  Ctrl + ↓  : Scroll to bottom        ║
╚══════════════════════════════════════╝

Built with ♥ by LUFS Audio
`);