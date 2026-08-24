document.addEventListener('DOMContentLoaded', () => {
    // Mobile nav
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    const navClose = document.querySelector('.nav-close');
    if (navToggle && navLinks) {
        function openMenu() {
            navLinks.classList.add('open');
            navToggle.classList.add('active');
            navToggle.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden';
        }
        function closeMenu() {
            navLinks.classList.remove('open');
            navToggle.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        }
        function toggleMenu() {
            navLinks.classList.contains('open') ? closeMenu() : openMenu();
        }

        navToggle.addEventListener('click', toggleMenu);
        if (navClose) navClose.addEventListener('click', closeMenu);

        // Close on link click
        navLinks.querySelectorAll('.nav-link').forEach(link => {
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

        // Close on resize to desktop
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) closeMenu();
        });
    }

    // Scroll reveal (with staggered children)
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const revealTargets = document.querySelectorAll('.section, .band, .chapter-card');

    // Tag direct children of card grids so they can fade in one after another.
    // Only do this when the grid sits inside something we actually observe,
    // otherwise the children would be hidden with nothing to reveal them.
    if (!reduceMotion) {
        document.querySelectorAll(
            '.home-grid-2, .home-grid-3, .home-grid-4, .home-grid-5, .big-stats, ' +
            '.how-strip, .quote-grid, .pillar-grid, .list-tiles, .steps-grid, ' +
            '.kit-grid, .advisor-grid, .lp-wwd-cards, .lp-stats-right'
        ).forEach(grid => {
            if (!grid.closest('.section, .band, .chapter-card')) return;
            Array.from(grid.children).forEach((child, i) => {
                child.classList.add('reveal-child');
                child.style.setProperty('--stagger', Math.min(i * 70, 420) + 'ms');
            });
        });
    }

    if (reduceMotion) {
        // Show everything immediately; the CSS also guards this.
        revealTargets.forEach(s => s.classList.add('visible'));
    } else {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);  // reveal once, then stop watching
                }
            });
            // rootMargin fires slightly before the section scrolls into view, and
            // a low threshold keeps very tall sections from never qualifying.
        }, { threshold: 0.05, rootMargin: '0px 0px -40px 0px' });

        revealTargets.forEach(s => observer.observe(s));

        // Anything already on screen at load should not wait for a scroll event
        requestAnimationFrame(() => {
            revealTargets.forEach(s => {
                const r = s.getBoundingClientRect();
                if (r.top < window.innerHeight && r.bottom > 0) s.classList.add('visible');
            });
        });
    }

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
