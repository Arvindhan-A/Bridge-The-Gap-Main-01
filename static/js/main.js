document.addEventListener('DOMContentLoaded', () => {
    // Mobile nav
    const navToggle = document.querySelector('.nav-toggle');
    const siteHeader = document.querySelector('.site-header');
    const navLinks = document.querySelector('.nav-links');
    if (navToggle && navLinks) {
        function syncHeaderHeight() {
            if (!siteHeader) return;
            document.documentElement.style.setProperty('--nav-h', `${siteHeader.offsetHeight}px`);
        }
        function openMenu() {
            // Reset the page position immediately so the drawer is always
            // presented from the top of the page on mobile.
            window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
            // Fallback for browsers that do not support the `instant` value.
            document.documentElement.scrollTop = 0;
            document.body.scrollTop = 0;
            syncHeaderHeight();
            navLinks.classList.add('open');
            navToggle.classList.add('active');
            navToggle.setAttribute('aria-expanded', 'true');
            document.documentElement.classList.add('nav-open');
            document.body.style.overflow = 'hidden';
        }
        function closeMenu() {
            navLinks.classList.remove('open');
            navToggle.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
            document.documentElement.classList.remove('nav-open');
            document.body.style.overflow = '';
        }
        function toggleMenu() {
            navLinks.classList.contains('open') ? closeMenu() : openMenu();
        }

        syncHeaderHeight();
        navToggle.addEventListener('click', toggleMenu);

        // Close on link click
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeMenu);
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                closeMenu();
            }
        });

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && navLinks.classList.contains('open')) {
                closeMenu();
            }
        });

        // Close once the viewport is wide enough for the full nav bar.
        // 1024px is where the CSS collapses the links into the drawer; the
        // old 768px check left the drawer stuck open across that gap.
        const wide = window.matchMedia('(min-width: 1025px)');
        const onWide = (e) => { if (e.matches) closeMenu(); };
        wide.addEventListener ? wide.addEventListener('change', onWide)
                              : wide.addListener(onWide);
        window.addEventListener('resize', syncHeaderHeight, { passive: true });
        window.addEventListener('orientationchange', syncHeaderHeight);
    }

    // Scroll reveal
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.section, .chapter-card').forEach(s => observer.observe(s));

    // Active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Blog search
    const searchInput = document.querySelector('.blog-search input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase();
            document.querySelectorAll('.post-card').forEach(card => {
                const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
                const text = card.querySelector('p')?.textContent.toLowerCase() || '';
                card.style.display = (title.includes(q) || text.includes(q)) ? '' : 'none';
            });
        });
    }

    // Lightbox
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightboxImg');
    const lightboxClose = document.getElementById('lightboxClose');
    const lightboxPrev = document.getElementById('lightboxPrev');
    const lightboxNext = document.getElementById('lightboxNext');
    const lightboxCounter = document.getElementById('lightboxCounter');

    let currentImages = [];
    let currentIndex = 0;

    function openLightbox(images, index) {
        currentImages = images;
        currentIndex = index;
        lightboxImg.src = images[index];
        updateCounter();
        lightbox.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('open');
        document.body.style.overflow = '';
    }

    function updateCounter() {
        if (currentImages.length <= 1) {
            lightboxCounter.textContent = '';
        } else {
            lightboxCounter.textContent = `${currentIndex + 1} / ${currentImages.length}`;
        }
    }

    function navigate(direction) {
        currentIndex = (currentIndex + direction + currentImages.length) % currentImages.length;
        lightboxImg.src = currentImages[currentIndex];
        updateCounter();
    }

    // Expose openLightbox globally for page-specific scripts
    window.openLightbox = openLightbox;

    // Attach click events to chapter slides
    document.querySelectorAll('.chapter-track').forEach(track => {
        const slides = track.querySelectorAll('.chapter-slide');
        const images = Array.from(slides).map(s => s.dataset.src);

        slides.forEach((slide, i) => {
            slide.addEventListener('click', () => openLightbox(images, i));
        });
    });

    if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
    if (lightboxPrev) lightboxPrev.addEventListener('click', () => navigate(-1));
    if (lightboxNext) lightboxNext.addEventListener('click', () => navigate(1));

    if (lightbox) {
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) closeLightbox();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (!lightbox || !lightbox.classList.contains('open')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') navigate(-1);
        if (e.key === 'ArrowRight') navigate(1);
    });
});

/* ===== SCROLL REVEAL =====
   Tags section content with .s-reveal and eases it in once. Skipped entirely
   when the visitor asks for reduced motion, and anything already on screen at
   load is shown immediately so nothing waits for a scroll that never comes. */
document.addEventListener('DOMContentLoaded', function () {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var blocks = document.querySelectorAll(
        '.s-section .s-head, .s-band .s-head, .s-grid > *, .s-media-grid > *, ' +
        '.s-stats > *, .s-nums > *, .s-quotes > *, .s-tiles > *, .s-steps > *, ' +
        '.s-feature > *, .s-contact > *, .s-faq > *'
    );
    if (!blocks.length) return;

    blocks.forEach(function (el) { el.classList.add('s-reveal'); });

    function show(el, i) {
        el.style.setProperty('--s-delay', Math.min(i * 60, 300) + 'ms');
        el.classList.add('is-in');
    }

    // group siblings so a row of cards staggers together rather than by document order
    var seen = new Map();
    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            var el = entry.target;
            var parent = el.parentElement;
            var n = seen.get(parent) || 0;
            seen.set(parent, n + 1);
            show(el, n);
            io.unobserve(el);
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    blocks.forEach(function (el) { io.observe(el); });

    requestAnimationFrame(function () {
        blocks.forEach(function (el) {
            var r = el.getBoundingClientRect();
            if (r.top < window.innerHeight && r.bottom > 0) {
                el.classList.add('is-in');
                io.unobserve(el);
            }
        });
    });
});

/* ===== HEADER: condensed state once the page scrolls ===== */
document.addEventListener('DOMContentLoaded', function () {
    var header = document.querySelector('.site-header');
    if (!header) return;
    var ticking = false;
    // hysteresis: separate on/off thresholds so a value hovering at the
    // boundary cannot flip the class back and forth every frame
    function sync() {
        var y = window.scrollY;
        if (y > 24) header.classList.add('is-scrolled');
        else if (y < 8) header.classList.remove('is-scrolled');
        ticking = false;
    }
    window.addEventListener('scroll', function () {
        if (!ticking) { ticking = true; requestAnimationFrame(sync); }
    }, { passive: true });
    sync();

    // stagger the drawer rows
    var links = document.querySelectorAll('.nav-links .nav-link');
    links.forEach(function (el, i) { el.style.setProperty('--i', i); });
});

/* ===== BACK TO TOP =====
   The control stays out of the tab order until it is useful, then uses the
   browser's native smooth scrolling (or instant motion when reduced motion is
   requested). */
document.addEventListener('DOMContentLoaded', function () {
    var button = document.querySelector('.scroll-top');
    if (!button) return;

    var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    var ticking = false;
    function updateVisibility() {
        button.classList.toggle('is-visible', window.scrollY > 360);
        button.tabIndex = window.scrollY > 360 ? 0 : -1;
        ticking = false;
    }
    window.addEventListener('scroll', function () {
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(updateVisibility);
        }
    }, { passive: true });
    button.addEventListener('click', function () {
        window.scrollTo({ top: 0, left: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
    });
    updateVisibility();
});

/* ===== SHARED CARD VARIANTS =====
   Legacy semantic names remain intact, while every card gets one of the three
   shared visual behaviours: standard, media, or compact. */
document.addEventListener('DOMContentLoaded', function () {
    var variants = {
        standard: '.card, .kit-card, .partner-card, .why-card, .serve-card, .impact-card, .step-card, .scroll-card, .post-card, .advisor-card, .initiative-card, .team-card, .announcement-card, .sidebar-card, .home-card, .s-card, .s-tile, .s-contact-card, .org-card, .list-tile, .user-card, .stat-card, .role-card, .role-create-card, .form-card, .ch-card, .pu-card',
        media: '.hl-card, .s-media-card, .event-card, .chapter-preview, .masonry-item, .photo-card',
        compact: '.hero-stat-card, .pillar, .event-row, .admin-section, .event-card-empty'
    };
    Object.keys(variants).forEach(function (variant) {
        document.querySelectorAll(variants[variant]).forEach(function (card) {
            card.classList.add('c-card', 'c-card--' + variant);
        });
    });
});

/* ===== FAQ ACCORDION =====
   Native details elements keep their keyboard and screen-reader behaviour;
   this only supplies a measured height animation for both opening and closing. */
document.addEventListener('DOMContentLoaded', function () {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.querySelectorAll('.s-faq details').forEach(function (details) {
        var summary = details.querySelector('summary');
        var body = details.querySelector('.s-faq-body');
        if (!summary || !body) return;

        var animation = null;
        function finish(closing) {
            if (closing) details.open = false;
            details.style.height = '';
            details.style.overflow = '';
            details.classList.remove('is-animating');
            animation = null;
        }
        function open() {
            details.open = true;
            var start = summary.offsetHeight;
            var end = start + body.offsetHeight;
            details.style.height = start + 'px';
            details.style.overflow = 'hidden';
            details.classList.add('is-animating');
            animation = details.animate(
                { height: [start + 'px', end + 'px'] },
                { duration: 460, easing: 'cubic-bezier(.16, 1, .3, 1)' }
            );
            body.animate(
                { opacity: [0, 1], transform: ['translateY(-8px)', 'translateY(0)'] },
                { duration: 360, delay: 70, easing: 'cubic-bezier(.16, 1, .3, 1)', fill: 'both' }
            );
            animation.onfinish = function () { finish(false); };
        }
        function close() {
            var start = details.offsetHeight;
            var end = summary.offsetHeight;
            details.style.height = start + 'px';
            details.style.overflow = 'hidden';
            details.classList.add('is-animating');
            animation = details.animate(
                { height: [start + 'px', end + 'px'] },
                { duration: 360, easing: 'cubic-bezier(.4, 0, 1, 1)' }
            );
            body.animate(
                { opacity: [1, 0], transform: ['translateY(0)', 'translateY(-6px)'] },
                { duration: 220, easing: 'ease-in', fill: 'both' }
            );
            animation.onfinish = function () { finish(true); };
        }
        summary.addEventListener('click', function (event) {
            event.preventDefault();
            if (animation) animation.cancel();
            details.open ? close() : open();
        });
    });
});
