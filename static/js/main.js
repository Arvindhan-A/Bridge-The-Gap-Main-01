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
