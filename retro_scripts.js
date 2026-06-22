// Album du Jour — Quiet Catalog
// LUFS Audio · dark-editorial / Swiss-modernist
// Custom cursor, brand scroll-reveal (with force-show fallback),
// refined moving background, sticky header, collapsible sections.

var REDUCE_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var FINE_POINTER  = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

document.addEventListener('DOMContentLoaded', function () {
    initCursor();
    initStickyHeader();
    initProgressBar();
    initScrollReveal();
    initCollapsibleSections();
    initAnimatedBackground();
    setCurrentYear();
});

// ---------- Custom cursor (dot + lagging ring) ----------
function initCursor() {
    if (!FINE_POINTER) return;
    var dot = document.querySelector('.cur-dot');
    var ring = document.querySelector('.cur-ring');
    if (!dot || !ring) return;

    var mx = innerWidth / 2, my = innerHeight / 2, rx = mx, ry = my;

    addEventListener('mousemove', function (e) {
        mx = e.clientX; my = e.clientY;
        dot.style.transform = 'translate(' + mx + 'px,' + my + 'px) translate(-50%,-50%)';
    });

    (function loop() {
        rx += (mx - rx) * 0.18;
        ry += (my - ry) * 0.18;
        ring.style.transform = 'translate(' + rx + 'px,' + ry + 'px) translate(-50%,-50%)';
        requestAnimationFrame(loop);
    })();

    addEventListener('mouseover', function (e) {
        if (e.target.closest('[data-hover], a, button')) ring.classList.add('hot');
    });
    addEventListener('mouseout', function (e) {
        if (e.target.closest('[data-hover], a, button')) ring.classList.remove('hot');
    });
}

// ---------- Sticky header ----------
function initStickyHeader() {
    var stickyHeader = document.getElementById('sticky-header');
    var mainHeader = document.querySelector('.main-header');
    if (!stickyHeader || !mainHeader) return;

    var headerVisible = false;

    function update() {
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        var mainHeaderBottom = mainHeader.offsetTop + mainHeader.offsetHeight;
        if (scrollTop > mainHeaderBottom && !headerVisible) {
            stickyHeader.classList.add('visible');
            headerVisible = true;
        } else if (scrollTop <= mainHeaderBottom && headerVisible) {
            stickyHeader.classList.remove('visible');
            headerVisible = false;
        }
    }

    var ticking = false;
    window.addEventListener('scroll', function () {
        if (!ticking) {
            requestAnimationFrame(function () { update(); ticking = false; });
            ticking = true;
        }
    });

    document.querySelectorAll('.logo-link').forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: REDUCE_MOTION ? 'auto' : 'smooth' });
        });
    });
}

// ---------- Scroll progress bar ----------
function initProgressBar() {
    var bar = document.getElementById('scroll-progress');
    if (!bar) return;
    window.addEventListener('scroll', function () {
        var scrollTop = window.pageYOffset;
        var docHeight = document.body.scrollHeight - window.innerHeight;
        var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        bar.style.width = pct + '%';
    });
}

// ---------- Scroll reveal (force-show fallback, never stuck hidden) ----------
function initScrollReveal() {
    var targets = document.querySelectorAll(
        '.stats-section, .currently-listening, .collapsible-section, .retro-buttons, .footer'
    );
    if (!targets.length) return;

    if (REDUCE_MOTION || !('IntersectionObserver' in window)) {
        targets.forEach(function (el) { el.classList.add('reveal', 'in'); });
        return;
    }

    targets.forEach(function (el) { el.classList.add('reveal'); });

    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (x) {
            if (x.isIntersecting) {
                x.target.classList.add('in');
                io.unobserve(x.target);
            }
        });
    }, { threshold: 0.12 });

    targets.forEach(function (el) { io.observe(el); });

    // Safety net: nothing stays hidden for non-scroll / SEO / observer misses.
    setTimeout(function () {
        targets.forEach(function (el) { el.classList.add('in'); });
    }, 900);
}

// ---------- Collapsible sections (localStorage persistence) ----------
function initCollapsibleSections() {
    var toggles = document.querySelectorAll('.section-toggle');

    toggles.forEach(function (toggle) {
        toggle.addEventListener('click', function () {
            var section = this.closest('.collapsible-section');
            var content = section.querySelector('.section-content');
            var isExpanded = this.getAttribute('aria-expanded') === 'true';

            this.setAttribute('aria-expanded', String(!isExpanded));

            if (!isExpanded) {
                content.classList.add('expanded');
                content.style.maxHeight = content.scrollHeight + 'px';
                localStorage.setItem('section-' + section.dataset.section, 'expanded');
            } else {
                content.classList.remove('expanded');
                content.style.maxHeight = '0';
                localStorage.setItem('section-' + section.dataset.section, 'collapsed');
            }
        });

        toggle.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.click(); }
        });

        var section = toggle.closest('.collapsible-section');
        if (localStorage.getItem('section-' + section.dataset.section) === 'expanded') {
            setTimeout(function () { toggle.click(); }, 100);
        }
    });
}

// ---------- Moving background (subtle, brand-disciplined) ----------
function initAnimatedBackground() {
    var bg = document.getElementById('animated-background');
    if (!bg) return;

    var shapes = ['square', 'circle', 'triangle', 'diamond'];
    var shapeCount = REDUCE_MOTION ? 6 : 12;

    for (var i = 0; i < shapeCount; i++) {
        var shape = document.createElement('div');
        var type = shapes[Math.floor(Math.random() * shapes.length)];
        shape.className = 'floating-shape ' + type;

        var size = Math.random() * 16 + 10;
        if (type !== 'triangle') { shape.style.width = size + 'px'; shape.style.height = size + 'px'; }

        shape.style.left = (Math.random() * 100) + '%';
        shape.style.top = (Math.random() * 100) + '%';

        if (!REDUCE_MOTION) {
            var anim = Math.random() > 0.5 ? 'drift' : 'driftSlow';
            var dur = Math.random() * 14 + 18; // 18–32s, calm
            shape.style.animation = anim + ' ' + dur + 's ease-in-out infinite';
            shape.style.animationDelay = (Math.random() * 8) + 's';
        }
        bg.appendChild(shape);
    }

    var pulseCount = REDUCE_MOTION ? 2 : 4;
    for (var j = 0; j < pulseCount; j++) {
        var pulse = document.createElement('div');
        pulse.className = 'pulse-element';
        var psize = Math.random() * 120 + 80;
        pulse.style.width = psize + 'px';
        pulse.style.height = psize + 'px';
        pulse.style.left = (Math.random() * 100) + '%';
        pulse.style.top = (Math.random() * 100) + '%';
        if (!REDUCE_MOTION) {
            pulse.style.animation = 'pulseGlow ' + (Math.random() * 6 + 10) + 's ease-in-out infinite';
            pulse.style.animationDelay = (Math.random() * 8) + 's';
        }
        bg.appendChild(pulse);
    }
}

// ---------- Current year ----------
function setCurrentYear() {
    var el = document.getElementById('current-year');
    if (el) el.textContent = new Date().getFullYear();
}

// ---------- Keyboard shortcuts ----------
document.addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.key === 'ArrowUp') {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: REDUCE_MOTION ? 'auto' : 'smooth' });
    }
    if (e.ctrlKey && e.key === 'ArrowDown') {
        e.preventDefault();
        window.scrollTo({ top: document.body.scrollHeight, behavior: REDUCE_MOTION ? 'auto' : 'smooth' });
    }
});

// ---------- Resize: keep expanded sections sized ----------
function debounce(fn, wait) {
    var t;
    return function () {
        var ctx = this, args = arguments;
        clearTimeout(t);
        t = setTimeout(function () { fn.apply(ctx, args); }, wait);
    };
}
window.addEventListener('resize', debounce(function () {
    document.querySelectorAll('.section-content.expanded').forEach(function (content) {
        content.style.maxHeight = content.scrollHeight + 'px';
    });
}, 250));

console.log('%cAlbum du Jour — Quiet Catalog', 'color:#78BEBA;font-weight:700');
console.log('%cLUFS Audio · dark-editorial', 'color:#888');
