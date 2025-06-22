// Music Library Website JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎵 Music Library loaded');
    
    // Add any interactive functionality here
    // For now, this is mainly for future enhancements
    
    // Smooth scrolling for any internal links
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
    
    // Add loading states for iframes
    const iframes = document.querySelectorAll('iframe');
    iframes.forEach(iframe => {
        iframe.addEventListener('load', function() {
            this.style.opacity = '1';
        });
        iframe.style.opacity = '0.8';
        iframe.style.transition = 'opacity 0.3s ease';
    });
});
